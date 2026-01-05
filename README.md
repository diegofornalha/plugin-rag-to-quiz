# RAG to Quiz - Marketplace

Marketplace de plugin para Claude Code que transforma bancos RAG em quizzes interativos.

## 🎯 Sobre

Este marketplace disponibiliza um plugin especializado que permite gerar perguntas de múltipla escolha a partir de bancos de dados RAG (Retrieval-Augmented Generation) em SQLite.

## 🚀 Como Instalar

### Passo 1: Adicionar o Marketplace

No Claude Code, execute:

```bash
/plugin marketplace add 2a-io/plugin-rag-to-quiz
```

Ou via URL completa:

```bash
/plugin marketplace add https://github.com/2a-io/plugin-rag-to-quiz.git
```

### Passo 2: Instalar o Plugin

Após adicionar o marketplace, instale o plugin:

```bash
/plugin install gerar-quiz-rag@2a-marketplace
```

### Passo 3: Verificar Instalação

Confirme que o plugin está instalado:

```bash
/plugin list
```

## 📚 Plugin Disponível

### gerar-quiz-rag

**Gerador de quiz a partir de banco RAG SQLite**

Transforma documentos PDF processados em banco RAG (via `pdf_rag_sdk_python`) em quizzes de múltipla escolha de alta qualidade.

#### Comandos:

```bash
# Gerar perguntas do banco RAG
/gerar-quiz-rag gerar [quantidade]

# Exemplos:
/gerar-quiz-rag gerar          # Gera 10 perguntas
/gerar-quiz-rag gerar 50       # Gera 50 perguntas
/gerar-quiz-rag gerar 200      # Gera 200 perguntas (recomendado)

# Executar quiz interativo
/gerar-quiz-rag iniciar

# Ver estatísticas do banco de perguntas
/gerar-quiz-rag status
```

#### Recursos:

- ⚡ **Geração em paralelo** com múltiplos agentes Claude Opus
- 🎯 **Alta qualidade** - Perguntas específicas baseadas no conteúdo real
- 🔍 **Detecção de duplicatas** automática
- 📊 **Validação completa** de formato JSON
- 🎮 **Quiz interativo** com feedback imediato
- 🧩 **Integração com pdf_rag_sdk_python** - Usa chunks do banco RAG

## 📋 Requisitos

- **Claude Code** versão mais recente
- **Python 3.10+**
- **SQLite 3** com extensão `sqlite-vec`
- **pdf_rag_sdk_python** (para gerar o banco RAG)

## 🔧 Configuração

Após instalar, certifique-se de que o plugin está habilitado em `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "gerar-quiz-rag@2a-marketplace": true
  }
}
```

## 📖 Fluxo Completo de Uso

### 1. Prepare seu Banco RAG

Use o `pdf_rag_sdk_python` para processar PDFs:

```python
from pdf_rag_sdk_python import IngestEngine, ChunkingStrategy

engine = IngestEngine(
    db_path="data/regulamento.db",
    embedding_model="BAAI/bge-small-en-v1.5",
    chunk_size=350,
    chunk_overlap=70,
    chunking_strategy=ChunkingStrategy.FIXED
)

await engine.add_document("documento.pdf")
```

O banco terá esta estrutura:

```sql
-- Tabela chunks (usado pelo plugin)
CREATE TABLE chunks (
    id INTEGER PRIMARY KEY,
    doc_id INTEGER,
    chunk_index INTEGER,
    conteudo TEXT NOT NULL
);
```

### 2. Gere Perguntas

Execute o comando de geração:

```bash
/gerar-quiz-rag gerar 100
```

O Claude vai:
1. Ler chunks do banco RAG
2. Distribuir entre múltiplos agentes
3. Gerar perguntas em paralelo
4. Validar e remover duplicatas
5. Salvar no banco de perguntas

### 3. Execute Quiz

Teste seu conhecimento:

```bash
/gerar-quiz-rag iniciar
```

## 🎯 Casos de Uso

### Treinamento e Avaliação
- Gere quizzes de regulamentos corporativos
- Avalie conhecimento de equipes
- Treinamento interativo

### Educação
- Transforme apostilas em quizzes
- Avaliações baseadas em conteúdo PDF
- Estudo interativo

### Conformidade e Compliance
- Testes de conhecimento de regulamentos
- Certificação interna
- Auditoria de conhecimento

## 🛡️ Garantias de Qualidade

- ✅ Perguntas baseadas **exclusivamente** no conteúdo dos chunks
- ✅ Validação de formato JSON rigorosa
- ✅ Detecção de duplicatas automática
- ✅ Distribuição balanceada de chunks entre agentes
- ✅ Feedback detalhado durante geração

## 🤝 Suporte

Para reportar problemas ou sugerir melhorias, abra uma issue no repositório.

## 📄 Licença

MIT License - Sinta-se livre para usar e modificar.

## 🔄 Atualizações

Para atualizar o marketplace e seus plugins:

```bash
/plugin marketplace update 2a-marketplace
```

## 🔗 Projetos Relacionados

- **[pdf_rag_sdk_python](https://github.com/2a-io/pdf_rag_sdk_python)** - SDK para processar PDFs em banco RAG
- **[backend-quiz-rag](https://github.com/2a-io/backend-quiz-rag)** - Backend completo RAG + Quiz

---

**RAG → Quiz** | **Desenvolvido para Claude Code** | 
