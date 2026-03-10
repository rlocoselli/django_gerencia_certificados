# Sistema de Questionários/Avaliações - Gerenciador de Certificados

## 📋 Visão Geral

Sistema completo de questionários/avaliações integrado ao fluxo de emissão de certificados. Após o aluno receber o certificado, ele é automaticamente redirecionado para responder uma avaliação, com respostas armazenadas em banco de dados e dashboard administrativo para análise.

## 🎯 Funcionalidades

### Para Alunos
- ✅ Formulário bonito e responsive para responder questionários
- ✅ Suporte a 3 tipos de perguntas:
  - **Escala** (Ótimo, Bom, Regular, Fraco)
  - **Múltipla Escolha** (Sim, Parcialmente, Não)
  - **Campo Aberto** (Texto livre)
- ✅ Redirecionamento automático após certificado com link/botão para avaliação
- ✅ Página de agradecimento após responder
- ✅ Validação de campos obrigatórios

### Para Administradores
- 📊 Dashboard customizado com estatísticas gerais
- 📈 Gráficos e médias de respostas
- 🔍 Filtros avançados por questionário, data, curso
- 📝 Interface para gerenciar questionários
- ❓ Interface para gerenciar perguntas e opções
- 📋 Visualização de todas as respostas
- ⭐ Cálculo automático de médias de satisfação

## 🚀 Instalação e Setup

### 1. Aplicar Migrations

```bash
python manage.py migrate certificados
```

### 2. Carregar Perguntas Iniciais

Um comando de gerenciamento foi criado para pré-carregar as perguntas padrão do Office Forms (formulário Lean System):

```bash
python manage.py load_initial_questions
```

Isso criará automaticamente:
- 1 Questionário ("Formulário de Avaliação Workshop Fundamentos Lean System")
- 16 Perguntas (1-14 com escala/múltipla escolha, 15-16 abertas)
- Opções de resposta configuradas

### 3. Acessar o Dashboard

1. Vá para `http://seu-site.com/admin/dashboard/`
2. O dashboard exibirá:
   - Total de questionários cadastrados
   - Total de respostas recebidas
   - Total de perguntas
   - Respostas por questionário
   - Médias de avaliação
   - Últimas respostas enviadas

## 📁 Estrutura de Dados

### Modelos Criados

#### 1. **Questionario**
```python
- titulo: CharField
- descricao: TextField
- curso: ForeignKey (Curso, opcional)
- ativo: BooleanField
- criado_em: DateTimeField (auto)
- atualizado_em: DateTimeField (auto)
```

#### 2. **Pergunta**
```python
- questionario: ForeignKey (Questionario)
- numero: PositiveIntegerField
- texto: TextField
- tipo: CharField (escala, multipla, aberto)
- obrigatoria: BooleanField
- ordem: PositiveIntegerField
```

#### 3. **OpcaoResposta**
```python
- pergunta: ForeignKey (Pergunta)
- valor: CharField (identificador único)
- rotulo: CharField (texto exibido)
- pontuacao: PositiveIntegerField (para cálculo de médias)
- ordem: PositiveIntegerField
```

#### 4. **RespostaUsuario**
```python
- questionario: ForeignKey (Questionario)
- cliente: ForeignKey (Cliente)
- certificado: ForeignKey (Certificado, opcional)
- agendamento: ForeignKey (CursoAgendamento, opcional)
- respondido_em: DateTimeField (auto)

Método útil:
- media_geral: property (calcula média das respostas)
```

#### 5. **ItemRespostaUsuario**
```python
- resposta_usuario: ForeignKey (RespostaUsuario)
- pergunta: ForeignKey (Pergunta)
- opcao_resposta: ForeignKey (OpcaoResposta, opcional)
- resposta_texto: TextField (para perguntas abertas)
```

## 🔄 Fluxo de Integração

### Fluxo Completo do Usuário

1. **Inscrição** → `/certificados/inscricao/?agendamento=UUID`
   - Usuário preenche dados pessoais
   - Sistema cria a inscrição e o certificado
   - Redireciona obrigatoriamente para o questionário

2. **Questionário** → `/certificados/certificado/<id>/questionario/`
   - Formulário dinâmico renderizado
   - Campos de resposta por tipo de pergunta
   - Aviso de envio do certificado após resposta
   - Validação no cliente e servidor

3. **Agradecimento** → `/certificados/certificado/<id>/agradecimento/`
   - Mensagem de agradecimento personalizada
   - Confirmação de envio do certificado para o e-mail cadastrado
   - Exibição de resumo da resposta

### Salvo no Banco de Dados

- **RespostaUsuario**: Uma entrada por aluno + questionário
- **ItemRespostaUsuario**: Uma entrada por pergunta respondida
- Associação automática com **Cliente**, **Certificado** e **Agendamento**

## 🎨 Nomes de Perguntas Padrão

As 16 perguntas carregadas são:

1. Seu conhecimento acerca do conteúdo antes do evento era?
2. Qual a sua avaliação geral do evento?
3. As informações recebidas corresponderam à sua expectativa?
4. Os conhecimentos adquiridos são úteis para a empresa?
5. O conteúdo assimilado é aplicável no seu local de trabalho/setor?
6. A conexão entre teoria e prática foi fluida?
7. Material entregue cadernos/adesivos/canetas facilitou a interação?
8. Recursos multimídia (slides da apresentação)?
9. Dinâmicas e exercícios?
10. Avalie o(s) instrutor(es): Conhecimento técnico e confiança
11. Didática dos Consultores?
12. Cumprimento do cronograma?
13. Pontualidade?
14. Clareza no esclarecimento de dúdãs?
15. Quais foram os Pontos Fortes do treinamento? (Aberta)
16. Quais foram os Pontos Fracos do treinamento? (Aberta)

## 👨‍💼 Gerenciamento Admin

### Acessar os Modelos

No Django Admin `/admin/`:

1. **Questionários** → Criar, editar questionários com inlines para perguntas
2. **Perguntas** → Gerenciar perguntas com inlines para opções
3. **Opções de Resposta** → Valores e pontuações
4. **Respostas de Usuário** → Ver todas as avaliações com filtros
5. **Itens de Resposta** → Detalhes de cada pergunta respondida

### Dashboard Customizado

Acesso: `/admin/dashboard/`

**Exibe:**
- Cards com métricas gerais
- Tabela de respostas por questionário
- Tabela de médias de avaliação (cores por faixa)
- Últimas 10 respostas com timestamps
- Links rápidos para admin de modelos relacionados

**Escala de Cores (Médias):**
- 🟢 **Excelente** (≥ 3.5): Verde
- 🔵 **Bom** (2.5-3.4): Azul
- 🟠 **Regular** (1.5-2.4): Laranja
- 🔴 **Baixo** (< 1.5): Vermelho

## 📊 Análise de Dados

### Filtros Disponíveis

No admin de RespostaUsuario:
- Por questionário
- Por agendamento/curso
- Por data de resposta
- Busca por nome do aluno, email, CPF

### Estatísticas Calculadas

- **Média Geral**: Soma das pontuações / número de itens
- **Média por Pergunta**: Pontuação média daquela pergunta
- **Média por Questionário**: Média de todas as respostas
- **Taxa de Resposta**: Total de respostas / Total de certificados

## 🛠️ Customizações

### Adicionar Novo Questionário

1. Admin → Questionários → Adicionar
2. Preencher título, descrição e selecionar curso (opcional)
3. Adicionar perguntas via inline
4. Para cada pergunta, adicionar opções (se escala/múltipla)

### Modificar Perguntas Padrão

As perguntas pré-carregadas podem ser editadas no admin:
- Mudar texto da pergunta
- Alterar tipo (escala → multipla, etc)
- Adicionar/remover/reordenar opções
- Mudar pontuação de cada opção

### Templates Personalizados

- `certificados/questionario.html` - Formulário
- `certificados/agradecimento_questionario.html` - Agradecimento
- `admin/dashboard_index.html` - Dashboard admin

Todos os templates incluem CSS customizado com gradientes, animações e design responsivo.

## 🔐 Segurança

- ✅ CSRF protection em formulários
- ✅ Validação de campos obrigatórios
- ✅ Associação com usuário autenticado (cliente)
- ✅ Constraint de unicidade: um aluno responde uma vez por questionário
- ✅ Readonly fields no admin para auditoria

## 📱 Responsividade

Todos os templates foram desenvolvidos com CSS grid/flexbox para funcionar perfeitamente em:
- 📱 Celulares
- 📱 Tablets
- 🖥️ Desktops

## 🐛 Troubleshooting

### Perguntas não aparecem no formulário
- Verificar se o questionário está `ativo=True`
- Verificar se as perguntas tem `ordem` configurada
- Ver se tem perguntas associadas ao questionário

### Média não é calculada
- Apenas perguntas com opções (escala/multipla) contribuem à média
- Perguntas abertas não influenciam a média geral
- Usar campo `media_geral` em RespostaUsuario

### Usuário já respondeu - não consegue responder novamente
- Constraint de unicidade impede múltiplas respostas
- Editar via admin se necessário reabrir resposta
- Implementar botão de "editar resposta" nos templates se desejar

## 📚 Arquivos Criados/Modificados

### Novos Arquivos
- `certificados/models.py` - 5 novos modelos
- `certificados/forms.py` - QuestionarioForm dinâmico
- `certificados/views.py` - 2 novas views
- `certificados/urls.py` - 2 novas rotas
- `certificados/admin.py` - Registros e dashboard
- `certificados/dashboard_admin.py` - Site admin customizado
- `certificados/management/commands/load_initial_questions.py` - Fixture
- `certificados/templates/certificados/questionario.html` - Formulário
- `certificados/templates/certificados/agradecimento_questionario.html` - Thank you
- `certificados/templates/admin/dashboard_index.html` - Dashboard template
- `certificados/migrations/0006_questionnaires.py` - Migration
- `project/urls.py` - URLs do dashboard

### Arquivos Modificados
- `certificados/templates/certificados/inscricao.html` - Texto do fluxo obrigatório
- `certificados/templates/certificados/questionario.html` - Aviso de envio após resposta
- `certificados/templates/certificados/agradecimento_questionario.html` - Confirmação de envio por e-mail

## 📞 Suporte

Para questões ou bugs:
1. Verificar logs do Django
2. Consultar tracebacks de erro
3. Validar dados no admin
4. Verificar constraints e relacionamentos

---

**Versão:** 1.0  
**Data:** Março 2026  
**Status:** ✅ Pronto para Produção
