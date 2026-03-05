from django.db import models
from django.utils import timezone
import uuid


class Cliente(models.Model):
    cpf = models.CharField('CPF', max_length=14)
    nome = models.CharField('Nome', max_length=200)
    email = models.EmailField('E-mail', max_length=254)
    data_nascimento = models.DateField('Data de nascimento')
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    endereco = models.CharField('Endereço', max_length=255, blank=True)
    empresa = models.CharField('Empresa', max_length=200)

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


class Questionario(models.Model):
    """Modelo para armazenar questionários"""
    TIPO_ESCALA = 'escala'
    TIPO_MULTIPLA = 'multipla'
    TIPO_CAMPO_ABERTO = 'aberto'
    
    TIPOS_PERGUNTA = [
        (TIPO_ESCALA, 'Escala (Ótimo, Bom, Regular, Fraco)'),
        (TIPO_MULTIPLA, 'Múltipla Escolha (Sim, Parcialmente, Não)'),
        (TIPO_CAMPO_ABERTO, 'Campo Aberto (Texto)'),
    ]
    
    titulo = models.CharField('Título do Questionário', max_length=255)
    descricao = models.TextField('Descrição', blank=True)
    curso = models.ForeignKey(Curso, verbose_name='Curso', on_delete=models.CASCADE, related_name='questionarios', null=True, blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Questionário'
        verbose_name_plural = 'Questionários'
        ordering = ['-criado_em']

    def __str__(self) -> str:
        return self.titulo


class Pergunta(models.Model):
    """Modelo para armazenar perguntas do questionário"""
    TIPO_ESCALA = 'escala'
    TIPO_MULTIPLA = 'multipla'
    TIPO_CAMPO_ABERTO = 'aberto'
    
    TIPOS_PERGUNTA = [
        (TIPO_ESCALA, 'Escala (Ótimo, Bom, Regular, Fraco)'),
        (TIPO_MULTIPLA, 'Múltipla Escolha (Sim, Parcialmente, Não)'),
        (TIPO_CAMPO_ABERTO, 'Campo Aberto (Texto)'),
    ]
    
    questionario = models.ForeignKey(Questionario, verbose_name='Questionário', on_delete=models.CASCADE, related_name='perguntas')
    numero = models.PositiveIntegerField('Número da Pergunta')
    texto = models.TextField('Texto da Pergunta')
    tipo = models.CharField('Tipo de Pergunta', max_length=20, choices=TIPOS_PERGUNTA)
    obrigatoria = models.BooleanField('Obrigatória', default=True)
    ordem = models.PositiveIntegerField('Ordem', default=0)

    class Meta:
        verbose_name = 'Pergunta'
        verbose_name_plural = 'Perguntas'
        ordering = ['questionario', 'ordem', 'numero']
        unique_together = ('questionario', 'numero')

    def __str__(self) -> str:
        return f"{self.numero}. {self.texto[:50]}"


class OpcaoResposta(models.Model):
    """Modelo para armazenar opções de resposta para perguntas de escala e multipla escolha"""
    pergunta = models.ForeignKey(Pergunta, verbose_name='Pergunta', on_delete=models.CASCADE, related_name='opcoes')
    valor = models.CharField('Valor da Opção', max_length=100)
    rotulo = models.CharField('Rótulo de Exibição', max_length=100)
    pontuacao = models.PositiveIntegerField('Pontuação', default=1, help_text="Usado para cálculo de médias")
    ordem = models.PositiveIntegerField('Ordem', default=0)

    class Meta:
        verbose_name = 'Opção de Resposta'
        verbose_name_plural = 'Opções de Resposta'
        ordering = ['pergunta', 'ordem']
        unique_together = ('pergunta', 'valor')

    def __str__(self) -> str:
        return f"{self.pergunta.numero} - {self.rotulo}"


class RespostaUsuario(models.Model):
    """Modelo para armazenar as respostas dos usuários ao questionário"""
    questionario = models.ForeignKey(Questionario, verbose_name='Questionário', on_delete=models.CASCADE, related_name='respostas_usuarios')
    cliente = models.ForeignKey(Cliente, verbose_name='Aluno', on_delete=models.CASCADE, related_name='respostas_questionario')
    certificado = models.ForeignKey(Certificado, verbose_name='Certificado', on_delete=models.SET_NULL, null=True, blank=True, related_name='respostas_questionario')
    agendamento = models.ForeignKey(CursoAgendamento, verbose_name='Agendamento', on_delete=models.SET_NULL, null=True, blank=True, related_name='respostas_questionario')
    respondido_em = models.DateTimeField('Respondido em', auto_now_add=True)

    class Meta:
        verbose_name = 'Resposta do Usuário'
        verbose_name_plural = 'Respostas dos Usuários'
        ordering = ['-respondido_em']
        unique_together = ('questionario', 'cliente', 'certificado')

    def __str__(self) -> str:
        return f"{self.cliente} - {self.questionario.titulo}"

    @property
    def media_geral(self):
        """Calcula a média geral de pontuação do questionário"""
        itens = self.itens.filter(opcao_resposta__isnull=False)
        if not itens.exists():
            return 0
        total_pontuacao = sum(item.opcao_resposta.pontuacao for item in itens)
        return round(total_pontuacao / itens.count(), 2)


class ItemRespostaUsuario(models.Model):
    """Modelo para armazenar a resposta de cada pergunta"""
    resposta_usuario = models.ForeignKey(RespostaUsuario, verbose_name='Resposta do Usuário', on_delete=models.CASCADE, related_name='itens')
    pergunta = models.ForeignKey(Pergunta, verbose_name='Pergunta', on_delete=models.CASCADE)
    opcao_resposta = models.ForeignKey(OpcaoResposta, verbose_name='Opção Resposta', on_delete=models.SET_NULL, null=True, blank=True)
    resposta_texto = models.TextField('Resposta (Texto)', blank=True)

    class Meta:
        verbose_name = 'Item de Resposta do Usuário'
        verbose_name_plural = 'Itens de Resposta do Usuário'
        unique_together = ('resposta_usuario', 'pergunta')

    def __str__(self) -> str:
        return f"Pergunta {self.pergunta.numero} - {self.resposta_usuario.cliente}"
