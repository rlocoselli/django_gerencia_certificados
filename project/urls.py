from django.contrib import admin
from django.urls import path, include

from core.views import aluno_por_cpf
from certificados.dashboard_admin import dashboard_admin_site
from certificados.admin import (
    QuestionarioAdmin, PerguntaAdmin, OpcaoRespostaAdmin, 
    RespostaUsuarioAdmin, ItemRespostaUsuarioAdmin
)
from certificados.models import Questionario, Pergunta, OpcaoResposta, RespostaUsuario, ItemRespostaUsuario

# Registrar modelos no dashboard customizado
dashboard_admin_site.register(Questionario, QuestionarioAdmin)
dashboard_admin_site.register(Pergunta, PerguntaAdmin)
dashboard_admin_site.register(OpcaoResposta, OpcaoRespostaAdmin)
dashboard_admin_site.register(RespostaUsuario, RespostaUsuarioAdmin)
dashboard_admin_site.register(ItemRespostaUsuario, ItemRespostaUsuarioAdmin)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/dashboard/', dashboard_admin_site.urls),
    path('certificados/', include('certificados.urls')),
    path("api/aluno-por-cpf/", aluno_por_cpf, name="aluno_por_cpf"),
]

