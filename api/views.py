from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, DatabaseError, InternalError, transaction


from rest_framework_simplejwt import authentication as authenticationJWT
from core.models import Conta, Transferencia, Cartao, Emprestimo, CartaoGasto
from datetime import datetime, timedelta
from datetime import date
from api import serializers
import random


from rest_framework.decorators import action, api_view

from decimal import Decimal


class AccountViewSet(viewsets.ModelViewSet):
    """View for manage account APIs."""
    queryset = Conta.objects.all()
    authentication_classes = [authenticationJWT.JWTAuthentication]
    serializer_class = serializers.AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve conta for authenticated user."""
        queryset = self.queryset

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'retrieve':
            return serializers.AccountDetailSerializer

        return serializers.AccountSerializer

    def retrieve(self, request, *args, **kwargs):
        lookup_field = 'numero'
        lookup_value = self.kwargs.get(lookup_field) or self.kwargs.get('pk')
        queryset = self.get_queryset()

        try:
            if lookup_field == 'pk':
                instance = queryset.get(pk=lookup_value)
            else:
                instance = queryset.get(numero=lookup_value)
        except Conta.DoesNotExist:
            return Response({'message': 'Conta não encontrada'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            agencia = '0001'
            numero = ''
            for n in range(8):
                numero += str(random.randint(0, 9))

            conta = Conta(
                user=self.request.user,
                numero=numero,
                agencia=agencia,
                saldo=0
            )

            conta.save()

            return Response({"message": "created"},
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, url_path='depositar')
    def depositar(self, request, pk=None):
        conta = Conta.objects.filter(id=pk).first()
        serializer_recebido = serializers.DepositoSerializer(data=request.data)

        if serializer_recebido.is_valid() and conta:

            saldo = Decimal(serializer_recebido.validated_data.get('value'))
            valor_deposito = Decimal(conta.saldo)

            conta.saldo = saldo + valor_deposito
            conta.save()
            return Response({"saldo": conta.saldo}, status=status.HTTP_200_OK)

        return Response(serializer_recebido.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, url_path='sacar')
    def sacar(self, request, pk=None):
        conta = Conta.objects.filter(id=pk).first()
        serializer_recebido = serializers.SaqueSerializer(data=request.data)

        if serializer_recebido.is_valid() and conta:
            valor_saque = serializer_recebido.validated_data.get('value', 0)
            saldo = Decimal(conta.saldo)

            if saldo >= valor_saque:
                desconto = max(0, saldo - valor_saque)
                conta.saldo = desconto
                conta.save()
                return Response({"saldo": conta.saldo}, status=status.HTTP_200_OK)

            return Response({'message': 'Saldo insuficiente'}, status=status.HTTP_403_FORBIDDEN)

        return Response(serializer_recebido.errors, status=status.HTTP_400_BAD_REQUEST)


class TransferenciaViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin):

    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.TransferenciaSerializer
    queryset = Transferencia.objects.all()

    def get_queryset(self):
        queryset = self.queryset
        account = Conta.objects.filter(user=self.request.user).first()

        return queryset.filter(Q(from_account=account) | Q(to_account=account)).order_by('-id').distinct()

    def create(self, request):
        auth_user = request.user
        serializer = serializers.TransferenciaSerializer(data=request.data)

        if serializer.is_valid():
            sid = transaction.savepoint()
            from_account = Conta.objects.filter(user=auth_user).first()
            to_account = get_object_or_404(Conta.objects.filter(
                pk=serializer.validated_data.get('to_account_id')))
            try:
                if from_account.saldo > 0 and from_account.saldo > serializer.validated_data.get('value'):
                    from_account.saldo -= serializer.validated_data.get(
                        'value')
                    to_account.saldo += serializer.validated_data.get('value')
                else:
                    return Response({'message': "Saldo insuficiente"}, status=status.HTTP_403_FORBIDDEN)

                from_account.save()
                to_account.save()

                Transferencia.objects.create(
                    from_account=from_account,
                    to_account=to_account,
                    value=serializer.validated_data.get('value')
                )

                transaction.savepoint_commit(sid)
                return Response({'message': 'ok'}, status=status.HTTP_201_CREATED)
            except IntegrityError or DatabaseError or InternalError:
                transaction.savepoint_rollback(sid)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartaoViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Cartao.objects.all()
    serializer_class = serializers.CartaoSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='listar-cartoes')
    def listar_cartoes(self, request):
        """Lista os cartões de uma conta específica"""
        conta = Conta.objects.filter(user=request.user).first()
        cartoes = Cartao.objects.filter(conta=conta)
        serializer = self.get_serializer(cartoes, many=True)
        return Response(serializer.data)

    @api_view(http_method_names=['GET'],)
    def solicitar_cartao(request):
        """Solicita a criação de um novo cartão"""
        conta = Conta.objects.filter(user=request.user).first()
        nome = f"{request.user.first_name} {request.user.last_name}"
        numero = CartaoViewSet.gerar_numero_cartao()
        cvv = CartaoViewSet.gerar_cvv_cartao()
        limite = float(conta.saldo) + 250 * 1.25
        data_expiracao = (date.today() + timedelta(days=365 * 5))

        novo_cartao = Cartao.objects.create(
            nome=nome,
            numero=numero,
            cvv=cvv,
            limite=limite,
            data_exp=data_expiracao,
            tipo='Crédito',
            conta=conta
        )

        novo_cartao.save()
        serializer = serializers.CartaoSerializer(novo_cartao)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def gerar_numero_cartao():
        numeros_existentes = set(
            Cartao.objects.values_list('numero', flat=True))
        while True:
            numero = ''.join(str(random.randint(0, 9)) for _ in range(16))
            if numero not in numeros_existentes:
                break
        return numero

    @staticmethod
    def gerar_cvv_cartao():
        cvvs_existentes = set(Cartao.objects.values_list('cvv', flat=True))
        while True:
            cvv = ''.join(str(random.randint(0, 9)) for _ in range(3))
            if cvv not in cvvs_existentes:
                break
        return cvv


class CartaoGastoViewset(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = CartaoGasto.objects.all()
    serializer_class = serializers.CartaoGastoSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """Função para criar um gasto no cartão"""
        serializer = serializers.CartaoGastoSerializer(data=request.data)

        if serializer.is_valid():
            conta = Conta.objects.filter(user=request.user).first()
            cartao = serializer.validated_data.get("cartao")
            cartao_selecionado = get_object_or_404(Cartao.objects.filter(conta=conta).filter(
                numero=cartao["numero"]).filter(cvv=cartao["cvv"]).filter(nome=cartao["nome"]))

            
            if (serializer.validated_data.get("valor") > cartao_selecionado.limite):
                return Response({"message": "Limite insuficiente"}, status=status.HTTP_401_UNAUTHORIZED)

            gasto = CartaoGasto.objects.create(
                cartao=cartao_selecionado,
                valor=serializer.validated_data.get("valor"),
                nome=serializer.validated_data.get("nome")
            )
            gasto.save()
            
            return Response({"message": "Gasto salvo"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class EmprestimoViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Emprestimo.objects.all()
    serializer_class = serializers.EmprestimoSerializer
    authentication_classes = [authenticationJWT.JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='listar-emprestimos')
    def listar_emprestimos(self, request):
        """Lista os emprestimos de uma conta específica"""
        conta = Conta.objects.filter(user=request.user).first()
        emprestimos = Emprestimo.objects.filter(conta=conta)
        serializer = self.get_serializer(emprestimos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='solicitar-emprestimo')
    def solicitar_emprestimo(self, request):
        """Solicita um novo empréstimo"""
        serializer = serializers.EmprestimoSerializer(data=request.data)

        if serializer.is_valid():
            conta = Conta.objects.filter(user=request.user).first()

            if conta:
                # Se o saldo em conta vezes 3.2 for maior ou igual ao empréstimo desejado, aprovado
                condicao = float(
                    conta.saldo) * 3.2 >= serializer.validated_data['valorRequisitado']

                emprestimo = Emprestimo.objects.create(
                    valorRequisitado=serializer.validated_data['valorRequisitado'],
                    valorTotal=Decimal(
                        float(serializer.validated_data['valorRequisitado']) * 1.8),
                    qtd_parcelas=serializer.validated_data['qtd_parcelas'],
                    conta=conta,
                    status="Aprovado" if condicao else "Não Aprovado - O valor solicitado é muito para sua conta"
                )

                emprestimo.save()

                # Crie um novo serializer para o objeto do empréstimo
                emprestimo_serializer = serializers.EmprestimoSerializer(
                    emprestimo)

                return Response(emprestimo_serializer.data, status=status.HTTP_201_CREATED)

            return Response({"message": "Conta não encontrada"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
