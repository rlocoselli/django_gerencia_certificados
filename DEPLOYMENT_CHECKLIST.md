# ✅ Checklist de Implementação - Sistema de Questionários

## ⚡ Passos para PR/Deployment

### 1️⃣ Verificar Arquivos Criados/Modificados

**Novos Arquivos (Criar):**
- ✅ `certificados/dashboard_admin.py` - Admin site customizado
- ✅ `certificados/management/commands/load_initial_questions.py` - Fixture
- ✅ `certificados/templates/certificados/questionario.html` - Formulário
- ✅ `certificados/templates/certificados/agradecimento_questionario.html` - Thanks page
- ✅ `certificados/templates/admin/dashboard_index.html` - Dashboard template
- ✅ `certificados/migrations/0006_questionario_pergunta_respostausuario.py` - Migration
- ✅ `README_QUESTIONARIOS.md` - Documentação
- ✅ `EXAMPLES_QUESTIONARIOS.py` - Exemplos de código
- ✅ `ARCHITECTURE_QUESTIONARIOS.md` - Arquitetura

**Arquivos Modificados:**
- ✅ `certificados/models.py` - 5 novos models adicionados
- ✅ `certificados/forms.py` - QuestionarioForm adicionado
- ✅ `certificados/views.py` - 2 novas views
- ✅ `certificados/urls.py` - 2 novas rotas
- ✅ `certificados/admin.py` - Registros e dashboard admin
- ✅ `certificados/templates/certificados/inscricao.html` - Aviso de questionário obrigatório
- ✅ `certificados/templates/certificados/questionario.html` - Aviso de envio de certificado após respostas
- ✅ `certificados/templates/certificados/agradecimento_questionario.html` - Confirmação de envio por e-mail
- ✅ `project/urls.py` - Dashboard URLs

### 2️⃣ Clonar no Ambiente de Produção

```bash
# Pullear código
git pull origin main

# Verificar arquivos
ls certificados/migrations/0006*.py
ls certificados/templates/certificados/questionario.html
ls certificados/dashboard_admin.py
```

### 3️⃣ Configurar Banco de Dados

```bash
# Criar as tabelas
python manage.py migrate certificados

# Carregar perguntas padrão
python manage.py load_initial_questions

# Verificar criação
python manage.py dbshell
# SELECT COUNT(*) FROM certificados_questionario;
# SELECT COUNT(*) FROM certificados_pergunta;
```

### 4️⃣ Coletar Estáticos (se necessário)

```bash
python manage.py collectstatic --noinput
```

### 5️⃣ Reiniciar Serviço

```bash
# Se usar Gunicorn
systemctl restart gunicorn_app

# Se usar outro app server
sudo systemctl restart seu_app
```

### 6️⃣ Testar no Dashboard

1. Acesse `/admin/dashboard/`
2. Deve mostrar:
   - Cards com métricas (próvavelmente 0 no início)
   - Links para administração
   - Tabelas vazias (sem respostas ainda)

### 7️⃣ Testar Fluxo Completo

1. Acesse `/certificados/inscricao/?agendamento=UUID_REAL`
2. Preencha o formulário
3. Submeta
4. Deve:
   - Criar certificado
   - Redirecionar obrigatoriamente para o questionário
   - Exibir aviso de envio do certificado após responder
5. Responda e envie o formulário
6. Deve redirecionar para agradecimento
7. Deve confirmar envio do certificado por e-mail (ou aviso de pendência)
8. Verifique em `/admin/dashboard/` → última resposta deve aparecer

### 8️⃣ Verificações de Segurança

- ✅ CSRF protection ativado (templates têm {% csrf_token %})
- ✅ Campos validam tipos de dados
- ✅ Constraints no banco impedem duplicatas
- ✅ Admin tem permissões padrão de Django

---

## 🔍 Verificação de Dados

### Tabelas Criadas

```sql
-- Listar tabelas novas
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'seu_db' 
AND table_name LIKE '%questionario%';

-- Deve retornar:
-- certificados_questionario
-- certificados_pergunta
-- certificados_opcaoresposta
-- certificados_respostausuario
-- certificados_itemrespostausuario
```

### Dados Iniciais Carregados

```python
# No shell Django
from certificados.models import Questionario, Pergunta

q = Questionario.objects.first()
print(f'Questionário: {q.titulo}')
print(f'Total de perguntas: {q.perguntas.count()}')

# Deve mostrar:
# Questionário: Formulário de Avaliação Workshop...
# Total de perguntas: 16
```

---

## 🐛 Troubleshooting

### Erro na Migration

```
django.db.migrations.exceptions.IrreversibleError
```

**Solução:**
- Deletar arquivo de migration parcial
- Deletar tabelas do banco
- Reexecutar `migrate`

### Import Error No Admin

```
ImportError: cannot import name 'QuestionarioAdmin'
```

**Solução:**
- Verificar se `certificados/admin.py` foi modificado corretamente
- Reiniciar Django dev server
- `python manage.py check`

### Dashboard Não Aparece

```
404 Not Found: /admin/dashboard/
```

**Solução:**
1. Verificar `project/urls.py`:
   ```python
   # Deve ter:
   from certificados.dashboard_admin import dashboard_admin_site
   path('admin/dashboard/', dashboard_admin_site.urls),
   ```
2. Reiniciar servidor

### Perguntas Não Carregam

```
Command error: load_initial_questions
```

**Solução:**
1. Verificar se arquivo existe: `certificados/management/commands/load_initial_questions.py`
2. Verificar Django version: `python -m django --version`
3. Logs: `python manage.py load_initial_questions --verbosity 3`

### Formulário Não Exibe Perguntas

**Solução:**
1. Verificar `questionario.ativo = True`
2. Verificar `perguntas.count() > 0`
3. Verificar se perguntas tem `opcoes` se tipo é escala/multipla
4. Recarregar página (cache do navegador)

---

## 📝 Customizações Comuns

### Mudar Cores do Dashboard

Editar `certificados/templates/admin/dashboard_index.html`:
```css
/* Linha ~42: Cor primária */
.stat-card { border-left: 4px solid #YOUR_COLOR; }
```

### Adicionar Mais Perguntas Padrão

Editar `certificados/management/commands/load_initial_questions.py`:
```python
# Adicionar à lista perguntas_data:
{
    'numero': 17,
    'texto': 'Sua nova pergunta',
    'tipo': 'escala',
    'opcoes': [...]
}
```

### Mudar Texto do Fluxo Obrigatório

Editar `certificados/templates/certificados/inscricao.html`:
```html
<!-- Alerta sobre questionário obrigatório e envio do certificado -->
<div class="alert alert-primary small" role="alert">
```

### Exportar Respostas

Ver arquivo `EXAMPLES_QUESTIONARIOS.py`:
```python
# Função exportar_respostas_csv(questionario_id)
# Gera CSV com todas as respostas
```

---

## 📊 Monitoramento Pós-Deploy

### Métricas a Acompanhar

1. **Taxa de Resposta**
   ```python
   RespostaUsuario.objects.count() / Certificado.objects.count()
   ```

2. **Satisfação Média**
   ```python
   from django.db.models import Avg
   RespostaUsuario.objects.aggregate(avg=Avg('itens__opcao_resposta__pontuacao'))
   ```

3. **Performance da Página**
   - Verificar query count: Django Debug Toolbar
   - Otimizar com select_related/prefetch_related

### Logs a Monitorar

```bash
# Ver erros de formulário
tail -f logs/django.log | grep "Form validation|ItemRespostaUsuario"

# Verificar criação de objetos
tail -f logs/django.log | grep "Created|Saved"
```

---

## ✨ Próximas Melhorias (Roadmap)

### Curto Prazo (v1.1)
- [ ] Botão de "Editar Resposta" se ainda não caducou
- [ ] Email de confirmação ao responder
- [ ] Páginas de perguntas (se muitas perguntas)

### Médio Prazo (v2.0)
- [ ] API REST para integração externa
- [ ] Gráficos interativos no dashboard (Chart.js)
- [ ] Export para Excel/PDF automatizado
- [ ] Agendamento automático de notificações

### Longo Prazo (v3.0)
- [ ] Machine Learning para análise de sentimento (Q15, Q16)
- [ ] Webhooks para terceiros
- [ ] App mobile
- [ ] Internacionalização (i18n)

---

## 🎓 Documentação para Usuários Finais

### Criar um Guia em Português

Criar arquivo `GUIA_USUARIO_QUESTIONARIOS.md`:

```markdown
# Como Usar o Sistemas de Avaliações

## Para Alunos

1. Após receber o certificado, aparecerá um botão azul: "Clique aqui para responder a uma breve avaliação"

2. Clique no botão

3. Preencha as respostas:
   - Para perguntas com "Ótimo, Bom, Regular, Fraco": Clique em uma das opções
   - Para perguntas abertas: Digite sua opinião livremente

4. Sem pular nenhuma pergunta obrigatória, clique em "Enviar Respostas"

5. Uma mensagem de agradecimento aparecerá

## Para Administradores

...
```

---

## 📞 Contato & Suporte

Documentações criadas em:
- 📖 `README_QUESTIONARIOS.md` - Guia completo
- 🏗️ `ARCHITECTURE_QUESTIONARIOS.md` - Arquitetura técnica
- 💻 `EXAMPLES_QUESTIONARIOS.py` - Exemplos de código

---

## ✅ Checklist Final

Antes de fazer deploy:

- [ ] Todos os arquivos .py têm sintaxe correta (`python -m py_compile`)
- [ ] Migration pode ser revertida sem erros
- [ ] Model relationships estão correctas
- [ ] Templates HTML renderizam sem erros
- [ ] URLs estão todas registradas
- [ ] Admin está funcional
- [ ] Dashboard carrega sem JS errors (verificar console)
- [ ] Formulário valida campos obrigatórios
- [ ] Dados salvam no banco corretamente
- [ ] Médias calculam corretamente
- [ ] Filtros admin funcionam
- [ ] Link de sucesso → Avaliação funciona
- [ ] Avaliação → Agradecimento funciona
- [ ] Dashboard → Ultimas respostas aparece
- [ ] Documentação está atualizada

---

**Status**: ✅ Pronto para Deploy  
**Data**: Março 2026  
**Versão**: 1.0
