from rest_framework import serializers

from core.models import Conta, Transferencia, Cartao, Emprestimo, ParcelaEmprestimo, CartaoGasto, Extrato


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for accounts."""
    class Meta:
        model = Conta
        fields = ['id', 'agencia', 'numero',]
        read_only_fields = ['id', 'agencia', 'numero']


class AccountDetailSerializer(AccountSerializer):
    class Meta(AccountSerializer.Meta):
        fields = AccountSerializer.Meta.fields + ['id', 'saldo', 'created_at']
        read_only_fields = AccountSerializer.Meta.read_only_fields + \
            ['id', 'saldo', 'created_at']


class ExtratoSerializer(serializers.ModelSerializer):
    conta = AccountSerializer(read_only=True, many=False)
    class Meta:
        model = Extrato
        fields = ['id', 'conta', 'valor', 'tipo']
        read_only_fields = ['id', 'conta', 'valor', 'tipo']


class TransferenciaSerializer(serializers.ModelSerializer):
    from_account = AccountSerializer(read_only=True, many=False)
    to_account = AccountSerializer(read_only=True, many=False)
    to_account_id = serializers.IntegerField()

    class Meta:
        model = Transferencia
        fields = ['id', 'from_account', 'to_account_id',
                  'to_account', 'value', 'created_at']
        read_only_fields = ['id', 'from_account', 'created_at', 'to_account']
        

class EmprestimoSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True, many=False)
    
    class Meta:
        model = Emprestimo
        fields = ['valorRequisitado', 'valorTotal', 'data_pedido', 'qtd_parcelas', 'account', 'status']
        read_only_fields = ['valorTotal', 'data_pedido', 'account', 'status']


class ParcelaEmprestimoSerializer(serializers.ModelSerializer):
    emprestimo = EmprestimoSerializer(read_only=True, many=False)
    
    class Meta:
        model = ParcelaEmprestimo
        fields = ['valorParcela', 'valorPago', 'numParcela', 'dataVencimento', 'dataPaga', 'emprestimo']
        read_only_fields = fields


class DepositoSerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        fields = ['value']


class SaqueSerializer(serializers.Serializer):
    value = serializers.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        fields = ['value']


class CartaoSerializer(serializers.ModelSerializer):
    conta = AccountSerializer(read_only=True, many=False)
    class Meta:
        model = Cartao
        fields = ['id', 'nome', 'cvv', 'numero',
                  'data_exp', 'limite', 'tipo', 'conta']
        read_only_fields = fields

        extra_kwargs = {
            'data_exp': {'format': '%Y-%m-%dT%H:%M:%S'}
        }

    def validate_data_exp(self, value):
        """Valida se a data de expiração é no futuro"""
        if value <= serializers.DateTimeField().to_representation(serializers.DateTimeField().to_internal_value(self.context['request'].data.get('created_at'))):
            raise serializers.ValidationError(
                "A data de expiração deve ser no futuro.")
        return value


class SendCartaoGastoSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=255)
    cvv = serializers.CharField(max_length=3)
    numero = serializers.CharField(max_length=16)
    data_exp = serializers.DateField()


class CartaoGastoSerializer(serializers.ModelSerializer):
    cartao = SendCartaoGastoSerializer(many=False)
    
    class Meta:
        model = CartaoGasto
        fields = ['id', 'cartao', 'valor', 'nome', 'created_at']
        read_only_fields = ['id', 'created_at']

