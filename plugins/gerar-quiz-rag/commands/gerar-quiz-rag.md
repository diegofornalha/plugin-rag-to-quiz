---
description: "Gera perguntas de quiz do banco RAG. Uso: /gerar-quiz-rag gerar [quantidade]"
argument-hint: [acao] [quantidade]
allowed-tools: Bash, Read, Write, Task, Glob, Grep
---

# Gerador de Quiz RAG

**Comando recebido:** `$ARGUMENTS`

## Ações Disponíveis

- `gerar [N]` - Gera N perguntas (padrão: 10, máximo recomendado: 200)
- `status` - Mostra estatísticas do banco de perguntas
- `iniciar` - Executa quiz de 10 perguntas

---

## Se ação = "gerar"

### Configuração Base
- **Banco RAG:** `/Users/2a/.claude/skills/gerar-quiz-rag/fonte-da-verdade-rag/regulamento.db`
- **Pasta temp:** `/Users/2a/.claude/skills/gerar-quiz-rag/temp-lotes/`
- **Banco final:** `/Users/2a/.claude/skills/gerar-quiz-rag/banco-perguntas.json`
- **Script merge:** `/Users/2a/.claude/skills/gerar-quiz-rag/coletar-e-merge-final.py`
- **Total chunks:** 59

### Processo OBRIGATÓRIO

1. **Criar pasta temp:**
   ```bash
   mkdir -p /Users/2a/.claude/skills/gerar-quiz-rag/temp-lotes/
   ```

2. **Calcular distribuição:**
   - Quantidade solicitada: `$2` (ou 10 se não informado)
   - Lotes necessários: quantidade / 10
   - Chunks por lote: 59 / num_lotes

3. **Lançar subagents EM PARALELO** usando Task tool:
   - subagent_type: `general-purpose`
   - model: `opus` (máxima qualidade nas perguntas)
   - run_in_background: `true`
   - Cada subagent gera 10 perguntas de chunks específicos

4. **Prompt para cada subagent:**
```
Gere 10 perguntas de múltipla escolha.

BANCO: /Users/2a/.claude/skills/gerar-quiz-rag/fonte-da-verdade-rag/regulamento.db
CHUNKS: [X] a [Y]
NUMERAÇÃO: [N] a [N+9]
SALVAR EM: /Users/2a/.claude/skills/gerar-quiz-rag/temp-lotes/temp-lote-[Z].json

PASSOS:
1. Ler chunks: sqlite3 [banco] "SELECT conteudo FROM chunks WHERE chunk_index BETWEEN X AND Y;"
2. Gerar 10 perguntas REAIS baseadas no conteúdo
3. Salvar array JSON no arquivo especificado

FORMATO OBRIGATÓRIO (array JSON):
[
  {
    "numero": N,
    "texto": "Pergunta específica?",
    "alternativas": {
      "A": {"texto": "Opção", "correta": false, "explicacao": "Razão"},
      "B": {"texto": "Opção", "correta": true, "explicacao": "Razão"},
      "C": {"texto": "Opção", "correta": false, "explicacao": "Razão"},
      "D": {"texto": "Opção", "correta": false, "explicacao": "Razão"}
    },
    "dificuldade": "facil|media|dificil",
    "topico": "Tópico",
    "fonte_chunk": "chunk_X"
  }
]
```

5. **Aguardar todos os subagents concluírem**

6. **Executar merge:**
   ```bash
   cd /Users/2a/.claude/skills/gerar-quiz-rag && python3 coletar-e-merge-final.py
   ```

7. **Mostrar resultado:**
   ```bash
   jq '.metadata' /Users/2a/.claude/skills/gerar-quiz-rag/banco-perguntas.json
   ```

---

## Se ação = "status"

Executar:
```bash
jq '.metadata' /Users/2a/.claude/skills/gerar-quiz-rag/banco-perguntas.json 2>/dev/null || echo "Banco não existe"
ls -la /Users/2a/.claude/skills/gerar-quiz-rag/temp-lotes/ 2>/dev/null | wc -l
```

---

## Se ação = "iniciar"

1. Ler banco de perguntas existente
2. Sortear 10 perguntas aleatórias
3. Apresentar 1 por vez
4. Aguardar resposta do usuário
5. Dar feedback imediato
6. Mostrar pontuação final

---

## Tabela de Distribuição (para 200 perguntas = 20 lotes)

| Lote | Chunks | Perguntas | Arquivo |
|------|--------|-----------|---------|
| 1 | 0-2 | 1-10 | temp-lote-1.json |
| 2 | 3-5 | 11-20 | temp-lote-2.json |
| 3 | 6-8 | 21-30 | temp-lote-3.json |
| ... | ... | ... | ... |
| 20 | 57-58 | 191-200 | temp-lote-20.json |
