<!-- DIAGRAMA DE ARQUITETURA E FLUXO DO SISTEMA DE QUESTIONÁRIOS -->

# 📊 Arquitetura do Sistema de Questionários

## 🔄 Fluxo de Dados (Alta Nível)

```
┌─────────────────────────────────────────────────────────────────┐
│                     ALUNO / RESPONDENTE                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
            ┌──────────────────────────┐
            │  Formulário de Inscrição │
            │     (inscricao.html)     │
            └────────────┬─────────────┘
                         │
                         ▼
            ┌──────────────────────────┐
            │  Gerar Certificado       │
            │  (PDF + Email)           │
            └────────────┬─────────────┘
                         │
                         ▼
          ┌────────────────────────────┐
          │   Página de Sucesso       │  ◄── Link para Questionário
          │ (inscricao_sucesso.html)  │
          └────────────┬───────────────┘
                       │
                       ▼
         ┌─────────────────────────────────┐
         │   Sistema de Questionários     │
         │  (responder_questionario.html)  │
         └────────────┬────────────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │ Validar & Salvar │
            │ RespostaUsuario  │
            └────────┬─────────┘
                     │
                     ▼
          ┌────────────────────────┐
          │  Página de Sucesso    │
          │ (agradecimento.html)  │
          └────────────┬──────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │   Dashboard Admin      │
          │  (/admin/dashboard/)   │
          │  - Médias              │
          │  - Filtros             │
          │  - Estatísticas        │
          └────────────────────────┘
```

## 📐 Estrutura de Dados (Banco)

```
┌─────────────────┐
│  QUESTIONARIO   │
├─────────────────┤
│ id              │
│ titulo          │
│ descricao       │
│ curso_id (FK)   │
│ ativo           │
│ criado_em       │
│ atualizado_em   │
└────────┬────────┘
         │ 1:N
         ▼
    ┌──────────────────┐
    │    PERGUNTA      │
    ├──────────────────┤
    │ id               │
    │ questionario_id  │
    │ numero           │
    │ texto            │
    │ tipo (escala,    │
    │      multipla,   │
    │      aberto)     │
    │ obrigatoria      │
    │ ordem            │
    └────────┬─────────┘
             │ 1:N
             ▼
        ┌─────────────────────┐
        │  OPCAO_RESPOSTA     │
        ├─────────────────────┤
        │ id                  │
        │ pergunta_id         │
        │ valor               │
        │ rotulo ("Ótimo",...)│
        │ pontuacao (1-4)     │
        │ ordem               │
        └─────────────────────┘

┌─────────────────────┐
│  RESPOSTA_USUARIO   │ ◄─────┐ Unique: (questionario, cliente, certificado)
├─────────────────────┤       │
│ id                  │       │
│ questionario_id (FK)├───┐   │
│ cliente_id (FK)    ├───┼───┤
│ certificado_id (FK)├───┘   │
│ agendamento_id (FK)│       │
│ respondido_em      │       │
└────────┬────────────┘       │
         │ 1:N                │
         ▼                    │
    ┌─────────────────────────┼──────┐
    │ ITEM_RESPOSTA_USUARIO   │      │
    ├─────────────────────────┤      │
    │ id                      │      │
    │ resposta_usuario_id (FK)├──────┘
    │ pergunta_id (FK)        │
    │ opcao_resposta_id (FK)  │◄─ Se múltipla/escala
    │ resposta_texto          │◄─ Se aberta
    └─────────────────────────┘
```

## 🔗 Relacionamentos

```
Cliente ────┐
            │
            ├──► RESPOSTA_USUARIO ◄──┬─── Certificado
            │                        │
            └────────────────────────┘

Certificado ─┐
             ├──► RESPOSTA_USUARIO
Agendamento ─┘

Questionario ─┐
              ├──► RESPOSTA_USUARIO
Curso    ────►│

Questionario ──┐
               ├──► PERGUNTA ──┐
               │               ├──► ITEM_RESPOSTA_USUARIO
               │               │
               └── ITEM_RESPOSTA_USUARIO ◄──┴──► OPCAO_RESPOSTA
```

## 🎯 Fluxo Admin (Dashboard)

```
┌─────────────────────────────────────┐
│  Django Admin (/admin/)             │
└────────────┬────────────────────────┘
             │
         ┌───┴────────────────────────────────────┐
         │                                        │
         ▼                                        ▼
┌──────────────────────┐        ┌──────────────────────┐
│ Admin Padrão         │        │ Dashboard Customizado│
├──────────────────────┤        ├──────────────────────┤
│ - Questionarios      │        │ (/admin/dashboard/)  │
│ - Perguntas          │        │                      │
│ - Opcoes             │        │ Cards de Métricas:   │
│ - Respostas          │        │ - Total de Q'arios   │
│ - Itens de Resposta  │        │ - Total de Respostas │
└──────────────────────┘        │ - Total de Perguntas │
                                │                      │
                                │ Tabelas:             │
                                │ - Respostas/Q'ario   │
                                │ - Médias por Q'ario  │
                                │ - Últimas Respostas  │
                                │                      │
                                │ Filtros:             │
                                │ - Por questionário   │
                                │ - Por data           │
                                │ - Por curso          │
                                └──────────────────────┘
```

## 📁 Estrutura de Arquivos

```
certificados/
├── models.py
│   ├── Questionario
│   ├── Pergunta
│   ├── OpcaoResposta
│   ├── RespostaUsuario
│   └── ItemRespostaUsuario
│
├── views.py
│   ├── responder_questionario()
│   └── agradecimento_questionario()
│
├── forms.py
│   └── QuestionarioForm (dinâmico)
│
├── urls.py
│   ├── /certificado/<id>/questionario/
│   └── /certificado/<id>/agradecimento/
│
├── admin.py
│   ├── QuestionarioAdmin
│   ├── PerguntaAdmin
│   ├── OpcaoRespostaAdmin
│   ├── RespostaUsuarioAdmin
│   └── ItemRespostaUsuarioAdmin
│
├── dashboard_admin.py
│   └── QuestionarioDashboardAdminSite
│
├── templates/certificados/
│   ├── questionario.html (Formulário)
│   ├── agradecimento_questionario.html
│   └── inscricao_sucesso.html (Modificado)
│
├── templates/admin/
│   └── dashboard_index.html
│
├── management/commands/
│   └── load_initial_questions.py
│
└── migrations/
    └── 0006_questionario_pergunta_respostausuario.py
```

## 🎨 Tipos de Pergunta

```
┌─ ESCALA ──────────────────┐
│ Ótimo    → pontuacao: 4   │
│ Bom      → pontuacao: 3   │
│ Regular  → pontuacao: 2   │
│ Fraco    → pontuacao: 1   │
└───────────────────────────┘

┌─ MÚLTIPLA ────────────────┐
│ Sim         → pontuacao: 3 │
│ Parcialmente → pontuacao: 2 │
│ Não         → pontuacao: 1 │
└───────────────────────────┘

┌─ CAMPO ABERTO ────────────┐
│ Campo de Texto Livre      │
│ (Não contribui à média)   │
└───────────────────────────┘
```

## 📊 Cálculo de Médias

```
Para cada RespostaUsuario:
┌─────────────────────────────────────┐
│ Porém pergunta com opção:           │
│   Somam pontuações                  │
│                                     │
│ Perguntas abertas:                  │
│   Ignoradas no cálculo              │
│                                     │
│ Media Geral = (Σ pontuações) / 3    │
│   (dividido por número de itens)    │
└─────────────────────────────────────┘

Escala de Satisfação:
┌──────────────┬──────────────────┐
│ 3.5 - 4.0    │ 🟢 Excelente      │
│ 2.5 - 3.4    │ 🔵 Bom            │
│ 1.5 - 2.4    │ 🟠 Regular        │
│ 0.0 - 1.4    │ 🔴 Baixo          │
└──────────────┴──────────────────┘
```

## 🔐 Constraints e Validações

```
┌─ Banco de Dados ────────────────────────┐
│ Pergunta: UNIQUE(questionario, numero)  │
│ OpcaoResposta: UNIQUE(pergunta, valor)  │
│ RespostaUsuario:                        │
│   UNIQUE(questionario, cliente,         │
│           certificado)                  │
│ ItemRespostaUsuario:                    │
│   UNIQUE(resposta_usuario, pergunta)    │
└─────────────────────────────────────────┘

┌─ Aplicação (Forms) ──────────────────────┐
│ - Validação de campos obrigatórios      │
│ - Validar opcoes válidas para pergunta  │
│ - Previne duplicatas no Form            │
└──────────────────────────────────────────┘

┌─ Admin ──────────────────────────────────┐
│ - ItemRespostaUsuario: read-only         │
│ - RespostaUsuario: can_delete=False      │
│ - Inline editing para perguntas/opções   │
└──────────────────────────────────────────┘
```

## 🚀 Fluxo de Execução (Request)

```
1. GET /certificados/inscricao/?agendamento=UUID
   └─► Renderiza formulário de inscrição

2. POST /certificados/inscricao/
   ├─► Valida formulário
   ├─► Cria/atualiza Cliente
   ├─► Cria Inscricao
   ├─► Cria Certificado
   ├─► Gera PDF
   ├─► Envia email
   └─► Renderiza inscricao_sucesso.html

3. GET /certificados/certificado/{id}/questionario/
   ├─► Obtem Certificado, Cliente, Curso
   ├─► Busca Questionario do Curso
   ├─► Instancia QuestionarioForm
   ├─► Loop por perguntas:
   │   ├─ Se escala/multipla: RadioSelect
   │   └─ Se aberta: Textarea
   └─► Renderiza questionario.html

4. POST /certificados/certificado/{id}/questionario/
   ├─► Valida QuestionarioForm
   ├─► Loop por campos do form:
   │   ├─ campo.startswith('pergunta_')
   │   ├─ Busca Pergunta
   │   ├─ Se opção_resposta: busca OpcaoResposta
   │   └─ Se aberta: usa valor direto
   ├─► CREATE ou UPDATE RespostaUsuario
   ├─► CREATE ItemRespostaUsuario para cada Pergunta
   └─► REDIRECT /certificado/{id}/agradecimento/

5. GET /certificados/certificado/{id}/agradecimento/
   ├─► Obtem Certificado
   ├─► Renderiza agradecimento.html
   └─► Fim
```

## 🎯 Próximos Passos (Opcional)

```
1. API REST (DRF)
   ├─ GET /api/questionarios/
   ├─ POST /api/questionarios/{id}/respuestas/
   └─ GET /api/relatorios/

2. Exportação
   ├─ CSV
   ├─ Excel
   └─ PDF (relatórios)

3. Gráficos
   ├─ Chart.js para dashboard
   ├─ Gráficos de pizza (distribuição)
   └─ Gráficos de barras (comparação)

4. Notificações
   ├─ Email ao responder
   ├─ Alertas de baixa satisfação
   └─ Webhooks

5. Idiomas
   ├─ Internacionalização (i18n)
   └─ Múltiplos idiomas nos templates
```

---

**Documento**: Arquitetura de Questionários  
**Data**: Março 2026  
**Status**: ✅ Implementado
