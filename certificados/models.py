from django.db import models
from django.utils import timezone
import uuid


class Cliente(models.Model):
    cpf = models.CharField('CPF', max_length=14, unique=True)
    nome = models.CharField('Nome', max_length=200)
    email = models.EmailField('E-mail', max_length=254)
    data_nascimento = models.DateField('Data de nascimento')
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    endereco = models.CharField('Endereço', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self) -> str:
        return f"{self.nome} ({self.cpf})"


class Curso(models.Model):
    nome = models.CharField('Nome do curso', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    carga_horaria_padrao = models.PositiveIntegerField('Carga horária (horas)', null=True, blank=True)

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

    def __str__(self) -> str:
        return self.nome


class CursoAgendamento(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    curso = models.ForeignKey(Curso, verbose_name='Curso', on_delete=models.PROTECT, related_name='agendamentos')
    data = models.DateField('Data do curso')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Agendamento de curso'
        verbose_name_plural = 'Agendamentos de cursos'
        ordering = ['-data']

    def __str__(self) -> str:
        return f"{self.curso} - {self.data:%d/%m/%Y}"


class Inscricao(models.Model):
    id = models.BigAutoField(primary_key=True)
    agendamento = models.ForeignKey(CursoAgendamento, verbose_name='Agendamento', on_delete=models.CASCADE, related_name='inscricoes')
    cliente = models.ForeignKey(Cliente, verbose_name='Aluno', on_delete=models.CASCADE, related_name='inscricoes')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        constraints = [
            models.UniqueConstraint(fields=['agendamento', 'cliente'], name='uniq_inscricao_agendamento_cliente')
        ]

    def __str__(self) -> str:
        return f"{self.cliente} @ {self.agendamento}"


class Certificado(models.Model):
    cliente = models.ForeignKey(Cliente, verbose_name='Aluno', on_delete=models.CASCADE, related_name='certificados')
    curso = models.ForeignKey(Curso, verbose_name='Curso', on_delete=models.PROTECT, related_name='certificados')
    agendamento = models.ForeignKey(CursoAgendamento, verbose_name='Agendamento', on_delete=models.SET_NULL, null=True, blank=True, related_name='certificados')
    data_emissao = models.DateField('Data de emissão', auto_now_add=True)
    codigo = models.UUIDField('Código do certificado', default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'
        ordering = ['-data_emissao']
        constraints = [
            models.UniqueConstraint(fields=['cliente', 'curso', 'agendamento'], name='uniq_cert_cliente_curso_agendamento')
        ]

    def __str__(self) -> str:
        return f"Certificado {self.curso} - {self.cliente}"
