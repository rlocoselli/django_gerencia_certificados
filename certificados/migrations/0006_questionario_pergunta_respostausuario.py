# Generated migration file for Questionário models

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('certificados', '0005_cliente_empresa'),
    ]

    operations = [
        migrations.CreateModel(
            name='Questionario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255, verbose_name='Título do Questionário')),
                ('descricao', models.TextField(blank=True, verbose_name='Descrição')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('atualizado_em', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('curso', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questionarios', to='certificados.curso', verbose_name='Curso')),
            ],
            options={
                'verbose_name': 'Questionário',
                'verbose_name_plural': 'Questionários',
                'ordering': ['-criado_em'],
            },
        ),
        migrations.CreateModel(
            name='Pergunta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.PositiveIntegerField(verbose_name='Número da Pergunta')),
                ('texto', models.TextField(verbose_name='Texto da Pergunta')),
                ('tipo', models.CharField(choices=[('escala', 'Escala (Ótimo, Bom, Regular, Fraco)'), ('multipla', 'Múltipla Escolha (Sim, Parcialmente, Não)'), ('aberto', 'Campo Aberto (Texto)')], max_length=20, verbose_name='Tipo de Pergunta')),
                ('obrigatoria', models.BooleanField(default=True, verbose_name='Obrigatória')),
                ('ordem', models.PositiveIntegerField(default=0, verbose_name='Ordem')),
                ('questionario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='perguntas', to='certificados.questionario', verbose_name='Questionário')),
            ],
            options={
                'verbose_name': 'Pergunta',
                'verbose_name_plural': 'Perguntas',
                'ordering': ['questionario', 'ordem', 'numero'],
                'unique_together': {('questionario', 'numero')},
            },
        ),
        migrations.CreateModel(
            name='RespostaUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('respondido_em', models.DateTimeField(auto_now_add=True, verbose_name='Respondido em')),
                ('agendamento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='respostas_questionario', to='certificados.cursoagendamento', verbose_name='Agendamento')),
                ('certificado', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='respostas_questionario', to='certificados.certificado', verbose_name='Certificado')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respostas_questionario', to='certificados.cliente', verbose_name='Aluno')),
                ('questionario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respostas_usuarios', to='certificados.questionario', verbose_name='Questionário')),
            ],
            options={
                'verbose_name': 'Resposta do Usuário',
                'verbose_name_plural': 'Respostas dos Usuários',
                'ordering': ['-respondido_em'],
                'unique_together': {('questionario', 'cliente', 'certificado')},
            },
        ),
        migrations.CreateModel(
            name='OpcaoResposta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.CharField(max_length=100, verbose_name='Valor da Opção')),
                ('rotulo', models.CharField(max_length=100, verbose_name='Rótulo de Exibição')),
                ('pontuacao', models.PositiveIntegerField(default=1, help_text='Usado para cálculo de médias', verbose_name='Pontuação')),
                ('ordem', models.PositiveIntegerField(default=0, verbose_name='Ordem')),
                ('pergunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opcoes', to='certificados.pergunta', verbose_name='Pergunta')),
            ],
            options={
                'verbose_name': 'Opção de Resposta',
                'verbose_name_plural': 'Opções de Resposta',
                'ordering': ['pergunta', 'ordem'],
                'unique_together': {('pergunta', 'valor')},
            },
        ),
        migrations.CreateModel(
            name='ItemRespostaUsuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resposta_texto', models.TextField(blank=True, verbose_name='Resposta (Texto)')),
                ('opcao_resposta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='certificados.opcaoresposta', verbose_name='Opção Resposta')),
                ('pergunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='certificados.pergunta')),
                ('resposta_usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='certificados.respostausuario', verbose_name='Resposta do Usuário')),
            ],
            options={
                'verbose_name': 'Item de Resposta do Usuário',
                'verbose_name_plural': 'Itens de Resposta do Usuário',
                'unique_together': {('resposta_usuario', 'pergunta')},
            },
        ),
    ]
