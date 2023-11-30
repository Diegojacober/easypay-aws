"""
URL mappings for the api app.
"""
from django.urls import (
    path,
    include
)

from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register('accounts', views.AccountViewSet)
router.register('transferencias', views.TransferenciaViewSet)
router.register('cartoes', views.CartaoViewSet)
router.register('gastos', views.CartaoGastoViewset)
router.register('emprestimos', views.EmprestimoViewSet)

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('cartoes/solicitar-cartao', views.CartaoViewSet.solicitar_cartao, name='solicitar-cartao'),
]
