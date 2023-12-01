"""
User models.
"""
import uuid
import os
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)
from django.conf import settings
from django.utils import timezone


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    """Manage for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must be an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class Transferencia(models.Model):
    """Transferencias entre contas."""
    value = models.DecimalField(max_digits=10, decimal_places=2)
    from_account = models.ForeignKey(
        'core.Conta',
        on_delete=models.DO_NOTHING,
        related_name='from_account'
    )
    to_account = models.ForeignKey(
        'core.Conta',
        on_delete=models.DO_NOTHING,
        related_name='to_account'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.from_account


class Conta(models.Model):
    """Conta para cada um dos clientes"""
    agencia = models.CharField(max_length=4)
    numero = models.CharField(max_length=8)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return self.agencia


class Cartao(models.Model):
    """Cartão associado a uma conta"""
    nome = models.CharField(max_length=255)
    cvv = models.CharField(max_length=3)
    numero = models.CharField(max_length=16)
    data_exp = models.DateField(null=True)
    limite = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=255)
    conta = models.ForeignKey(
        Conta,
        related_name='cartoes',
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.tipo} - {self.numero}"


class CartaoGasto(models.Model):
    """Tabela de gastos de um cartão"""
    cartao = models.ForeignKey(
        Cartao,
        related_name='gastos',
        on_delete=models.PROTECT
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    nome = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    
class Extrato(models.Model):
    conta = models.ForeignKey(
        Conta,
        related_name='extrato',
        on_delete=models.DO_NOTHING
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

class Emprestimo(models.Model):
    valorRequisitado = models.DecimalField(max_digits=10, decimal_places=2)
    valorTotal = models.DecimalField(max_digits=10, decimal_places=2)
    data_pedido = models.DateTimeField(default=timezone.now)
    qtd_parcelas = models.IntegerField()
    conta = models.ForeignKey(
        Conta,
        related_name='emprestimos',
        on_delete=models.DO_NOTHING
    )
    status = models.CharField(max_length=255, default='Em Análise')
    
    def __str__(self) -> str:
        return f"{self.data_pedido} - {self.valorTotal}"
    

class ParcelaEmprestimo(models.Model):
    valorParcela = models.DecimalField(max_digits=10, decimal_places=2)
    valorPago = models.DecimalField(max_digits=10, decimal_places=2)
    numParcela = models.IntegerField()
    dataVencimento = models.DateField(null=False)
    dataPaga = models.DateField(null=True)
    emprestimo = models.ForeignKey(
        Emprestimo,
        related_name='emprestimos_parcelas',
        on_delete=models.DO_NOTHING
    )
    
    def __str__(self) -> str:
        return f"{self.valorPago} - {self.valorParcela}"

class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=False)
    cpf = models.CharField(max_length=11, unique=True, null=False)
    url_image = models.ImageField(null=True, upload_to=recipe_image_file_path)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='Em Análise')
    created_at = models.DateTimeField(default=timezone.now)
    login_attempts = models.PositiveIntegerField(default=0)
    locked_at = models.DateTimeField(null=True, blank=True)
    unlocked_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return self.first_name
