from django import forms
from .models import Certificado, Curso, Cliente


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
