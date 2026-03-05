"""
Fixture com dados iniciais de questionários
Execute com: python manage.py loaddata 0001_questionarios_iniciais.json
"""
import json
from django.core.management.base import BaseCommand
from certificados.models import Questionario, Pergunta, OpcaoResposta, Curso


class Command(BaseCommand):
    help = 'Carrega perguntas padrão de avaliação de workshop'

    def handle(self, *args, **options):
        # Criar ou obter o questionário
        questionario, created = Questionario.objects.get_or_create(
            titulo='Formulário de Avaliação Workshop Fundamentos Lean System',
            defaults={
                'descricao': 'Avaliação do workshop de Lean System - Riachuelo - Confecção, Fev/2026',
                'ativo': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Questionário criado'))
        else:
            self.stdout.write('Questionário já existe, pulando...')
            return

        # Dados das perguntas
        perguntas_data = [
            {
                'numero': 1,
                'texto': 'Seu conhecimento acerca do conteúdo antes do evento era?',
                'tipo': 'escala',
                'opcoes': [
                    {'valor': 'nenhum', 'rotulo': 'Nenhum', 'pontuacao': 1},
                    {'valor': 'pouco', 'rotulo': 'Pouco', 'pontuacao': 2},
                    {'valor': 'bom', 'rotulo': 'Bom', 'pontuacao': 3},
                    {'valor': 'dominava', 'rotulo': 'Dominava o assunto', 'pontuacao': 4},
                ]
            },
            {
                'numero': 2,
                'texto': 'Qual a sua avaliação geral do evento?',
                'tipo': 'escala',
                'opcoes': [
                    {'valor': 'otimo', 'rotulo': 'Ótimo', 'pontuacao': 4},
                    {'valor': 'bom', 'rotulo': 'Bom', 'pontuacao': 3},
                    {'valor': 'regular', 'rotulo': 'Regular', 'pontuacao': 2},
                    {'valor': 'fraco', 'rotulo': 'Fraco', 'pontuacao': 1},
                ]
            },
            {
                'numero': 3,
                'texto': 'As informações recebidas corresponderam à sua expectativa?',
                'tipo': 'multipla',
                'opcoes': [
                    {'valor': 'sim', 'rotulo': 'Sim', 'pontuacao': 3},
                    {'valor': 'parcialmente', 'rotulo': 'Parcialmente', 'pontuacao': 2},
                    {'valor': 'nao', 'rotulo': 'Não', 'pontuacao': 1},
                ]
            },
            {
                'numero': 4,
                'texto': 'Os conhecimentos adquiridos são úteis para a empresa?',
                'tipo': 'multipla',
                'opcoes': [
                    {'valor': 'sim', 'rotulo': 'Sim', 'pontuacao': 3},
                    {'valor': 'parcialmente', 'rotulo': 'Parcialmente', 'pontuacao': 2},
                    {'valor': 'nao', 'rotulo': 'Não', 'pontuacao': 1},
                ]
            },
            {
                'numero': 5,
                'texto': 'O conteúdo assimilado é aplicável no seu local de trabalho/setor?',
                'tipo': 'multipla',
                'opcoes': [
                    {'valor': 'sim', 'rotulo': 'Sim', 'pontuacao': 3},
                    {'valor': 'parcialmente', 'rotulo': 'Parcialmente', 'pontuacao': 2},
                    {'valor': 'nao', 'rotulo': 'Não', 'pontuacao': 1},
                ]
            },
            {
                'numero': 6,
                'texto': 'A conexão entre teoria e prática foi fluida?',
                'tipo': 'multipla',
                'opcoes': [
                    {'valor': 'sim', 'rotulo': 'Sim', 'pontuacao': 3},
                    {'valor': 'parcialmente', 'rotulo': 'Parcialmente', 'pontuacao': 2},
                    {'valor': 'nao', 'rotulo': 'Não', 'pontuacao': 1},
                ]
            },
            {
                'numero': 7,
                'texto': 'Material entregue cadernos/adesivos/canetas facilitou a interação no WS?',
                'tipo': 'escala',
                'opcoes': [
                    {'valor': 'otimo', 'rotulo': 'Ótimo', 'pontuacao': 4},
                    {'valor': 'bom', 'rotulo': 'Bom', 'pontuacao': 3},
                    {'valor': 'regular', 'rotulo': 'Regular', 'pontuacao': 2},
                    {'valor': 'fraco', 'rotulo': 'Fraco', 'pontuacao': 1},
                ]
            },
            {
                'numero': 8,
                'texto': 'Recursos multimídia (slides da apresentação)?',
                'tipo': 'escala',
                'opcoes': [
                    {'valor': 'otimo', 'rotulo': 'Ótimo', 'pontuacao': 4},
                    {'valor': 'bom', 'rotulo': 'Bom', 'pontuacao': 3},
                    {'valor': 'regular', 'rotulo': 'Regular', 'pontuacao': 2},
                    {'valor': 'fraco', 'rotulo': 'Fraco', 'pontuacao': 1},
                ]
            },
            {
                'numero': 9,
                'texto': 'Dinâmicas e exercícios?',
                'tipo': 'escala',
                'opcoes': [
                    {'valor': 'otimo', 'rotulo': 'Ótimo', 'pontuacao': 4},
                    {'valor': 'bom', 'rotulo': 'Bom', 'pontuacao': 3},
                    {'valor': 'regular', 'rotulo': 'Regular', 'pontuacao': 2},
                    {'valor': 'fraco', 'rotulo': 'Fraco', 'pontuacao': 1},
                ]
            },
            {
                'numero': 10,
                'texto': 'Avalie o(s) instrutor(es): Conhecimento técnico e confiança na transmissão do conhecimento',
                'tipo': 'escala',
                'opcoes': [
                    {'valor': 'otimo', 'rotulo': 'Ótimo', 'pontuacao': 4},
                    {'valor': 'bom', 'rotulo': 'Bom', 'pontuacao': 3},
                    {'valor': 'regular', 'rotulo': 'Regular', 'pontuacao': 2},
                    {'valor': 'fraco', 'rotulo': 'Fraco', 'pontuacao': 1},
                ]
            },
            {
                'numero': 11,
                'texto': 'Didática dos Consultores?',
                'tipo': 'escala',
                'opcoes': [
                    {'valor': 'otimo', 'rotulo': 'Ótimo', 'pontuacao': 4},
                    {'valor': 'bom', 'rotulo': 'Bom', 'pontuacao': 3},
                    {'valor': 'regular', 'rotulo': 'Regular', 'pontuacao': 2},
                    {'valor': 'fraco', 'rotulo': 'Fraco', 'pontuacao': 1},
                ]
            },
            {
                'numero': 12,
                'texto': 'Cumprimento do cronograma?',
                'tipo': 'escala',
                'opcoes': [
                    {'valor': 'otimo', 'rotulo': 'Ótimo', 'pontuacao': 4},
                    {'valor': 'bom', 'rotulo': 'Bom', 'pontuacao': 3},
                    {'valor': 'regular', 'rotulo': 'Regular', 'pontuacao': 2},
                    {'valor': 'fraco', 'rotulo': 'Fraco', 'pontuacao': 1},
                ]
            },
            {
                'numero': 13,
                'texto': 'Pontualidade?',
                'tipo': 'escala',
                'opcoes': [
                    {'valor': 'otimo', 'rotulo': 'Ótimo', 'pontuacao': 4},
                    {'valor': 'bom', 'rotulo': 'Bom', 'pontuacao': 3},
                    {'valor': 'regular', 'rotulo': 'Regular', 'pontuacao': 2},
                    {'valor': 'fraco', 'rotulo': 'Fraco', 'pontuacao': 1},
                ]
            },
            {
                'numero': 14,
                'texto': 'Clareza no esclarecimento de dúvidas?',
                'tipo': 'escala',
                'opcoes': [
                    {'valor': 'otimo', 'rotulo': 'Ótimo', 'pontuacao': 4},
                    {'valor': 'bom', 'rotulo': 'Bom', 'pontuacao': 3},
                    {'valor': 'regular', 'rotulo': 'Regular', 'pontuacao': 2},
                    {'valor': 'fraco', 'rotulo': 'Fraco', 'pontuacao': 1},
                ]
            },
            {
                'numero': 15,
                'texto': 'Quais foram os Pontos Fortes do treinamento?',
                'tipo': 'aberto',
                'opcoes': []
            },
            {
                'numero': 16,
                'texto': 'Quais foram os Pontos Fracos do treinamento?',
                'tipo': 'aberto',
                'opcoes': []
            },
        ]

        # Criar perguntas e opções
        for idx, pergunta_info in enumerate(perguntas_data):
            pergunta, created = Pergunta.objects.get_or_create(
                questionario=questionario,
                numero=pergunta_info['numero'],
                defaults={
                    'texto': pergunta_info['texto'],
                    'tipo': pergunta_info['tipo'],
                    'obrigatoria': True,
                    'ordem': idx + 1,
                }
            )
            
            if created:
                # Criar opções de resposta
                for ordem, opcao_info in enumerate(pergunta_info['opcoes'], start=1):
                    OpcaoResposta.objects.create(
                        pergunta=pergunta,
                        valor=opcao_info['valor'],
                        rotulo=opcao_info['rotulo'],
                        pontuacao=opcao_info['pontuacao'],
                        ordem=ordem,
                    )
                self.stdout.write(f'  Pergunta {pergunta_info["numero"]} criada')
            else:
                self.stdout.write(f'  Pergunta {pergunta_info["numero"]} já existe')

        self.stdout.write(self.style.SUCCESS('Perguntas carregadas com sucesso!'))
