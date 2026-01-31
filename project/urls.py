from django.contrib import admin
from django.urls import path, include

from core.views import aluno_por_cpf

urlpatterns = [
    path('admin/', admin.site.urls),
    path('certificados/', include('certificados.urls')),
    path("api/aluno-por-cpf/", aluno_por_cpf, name="aluno_por_cpf"),
]

