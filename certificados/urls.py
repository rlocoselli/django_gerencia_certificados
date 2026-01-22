from django.urls import path
from . import views

app_name = 'certificados'

urlpatterns = [
    # público
    path('inscricao/', views.inscricao_publica, name='inscricao'),

    # telas antigas (opcional)
    path('', views.listar_certificados, name='listar_certificados'),
    path('novo/', views.criar_certificado, name='criar_certificado'),
    path('<int:pk>/', views.visualizar_certificado, name='visualizar_certificado'),
]
