from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import PermissionDenied

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(serializer)

        print("ta qaudsvyudfsvufsyu")

        if serializer.is_valid():
           
            user = serializer.user
            # Verifique as tentativas de login e bloqueie se necessário
            self.check_login_attempts(user)

            # Prossiga com a lógica de geração de token
            response = super().post(request, *args, **kwargs)

            if response.status_code == status.HTTP_200_OK:
                # Se o login for bem-sucedido, redefina as tentativas de login falhas
                user.login_attempts = 0
                user.save()

            return response

        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    def check_login_attempts(self, user):
        if user.login_attempts >= 3 and not user.locked_at:
            user.locked_at = timezone.now()
            user.unlocked_at = timezone.now() + timedelta(minutes=15)
            user.save()
            raise PermissionDenied("Conta bloqueada. Tente novamente após 15 minutos.")
