from django.urls import path
from . import views

app_name = 'certificados'

urlpatterns = [
    # público
    path('inscricao/', views.inscricao_publica, name='inscricao'),
    path('certificado/<int:certificado_id>/questionario/', views.responder_questionario, name='responder_questionario'),
    path('certificado/<int:certificado_id>/agradecimento/', views.agradecimento_questionario, name='agradecimento_questionario'),

    # telas antigas (opcional)
    path('', views.listar_certificados, name='listar_certificados'),
    path('novo/', views.criar_certificado, name='criar_certificado'),
    path('<int:pk>/', views.visualizar_certificado, name='visualizar_certificado'),
]
