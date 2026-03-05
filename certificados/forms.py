from django import forms
from .models import Certificado, Curso, Cliente, ItemRespostaUsuario, RespostaUsuario


class CertificadoForm(forms.ModelForm):
    class Meta:
        model = Certificado
        fields = ['cliente', 'curso', 'agendamento']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'].queryset = Curso.objects.all().order_by('nome')


class InscricaoPublicaForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['cpf', 'nome', 'email', 'data_nascimento', 'telefone', 'endereco', 'empresa']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }


class QuestionarioForm(forms.Form):
    """Formulário dinâmico para responder questionário"""
    
    def __init__(self, questionario, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.questionario = questionario
        
        # Criar campo dinâmico para cada pergunta (già carregado com prefetch)
        for pergunta in questionario.perguntas.all().order_by('ordem', 'numero'):
            self._criar_campo_pergunta(pergunta)
    
    def _criar_campo_pergunta(self, pergunta):
        """Cria um campo de formulário baseado no tipo de pergunta"""
        field_name = f'pergunta_{pergunta.id}'
        
        if pergunta.tipo == pergunta.TIPO_ESCALA:
            # Escala: usar opções já em cache (prefetch_related)
            try:
                opcoes = pergunta.opcoes.all().order_by('ordem')
                choices = [(opt.valor, opt.rotulo) for opt in opcoes]
            except:
                choices = []
            
            field = forms.ChoiceField(
                label=f"{pergunta.numero}. {pergunta.texto}",
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=pergunta.obrigatoria
            )
        
        elif pergunta.tipo == pergunta.TIPO_MULTIPLA:
            # Múltipla escolha
            try:
                opcoes = pergunta.opcoes.all().order_by('ordem')
                choices = [(opt.valor, opt.rotulo) for opt in opcoes]
            except:
                choices = []
            
            field = forms.ChoiceField(
                label=f"{pergunta.numero}. {pergunta.texto}",
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=pergunta.obrigatoria
            )
        
        elif pergunta.tipo == pergunta.TIPO_CAMPO_ABERTO:
            # Campo aberto: texto
            field = forms.CharField(
                label=f"{pergunta.numero}. {pergunta.texto}",
                widget=forms.Textarea(attrs={
                    'rows': 4,
                    'class': 'form-control',
                    'placeholder': 'Digite sua resposta aqui...'
                }),
                required=pergunta.obrigatoria
            )
        
        else:
            # Default
            field = forms.CharField(required=pergunta.obrigatoria)
        
        self.fields[field_name] = field
        self.pergunta_map = getattr(self, 'pergunta_map', {})
        self.pergunta_map[field_name] = pergunta
