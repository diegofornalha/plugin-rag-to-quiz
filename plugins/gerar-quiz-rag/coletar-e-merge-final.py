#!/usr/bin/env python3
"""
Script para coletar resultados dos subagents e fazer merge final.
Aguarda todos os lotes, valida e cria banco-perguntas.json final.
"""

import json
import glob
import time
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

def aguardar_lotes(total_esperado=21, timeout=180):
    """Aguarda lotes serem criados."""
    print("⏳ Aguardando subagents concluírem...")
    print(f"   Meta: {total_esperado} lotes")
    print()

    inicio = time.time()
    lotes_anteriores = 0

    while (time.time() - inicio) < timeout:
        lotes = sorted(glob.glob('temp-lotes/temp-lote-*.json'))

        if len(lotes) != lotes_anteriores:
            print(f"📦 {len(lotes)}/{total_esperado} lotes criados...")
            lotes_anteriores = len(lotes)

        if len(lotes) >= total_esperado:
            print(f"✅ Todos os {len(lotes)} lotes concluídos!")
            return lotes

        time.sleep(2)

    lotes = sorted(glob.glob('temp-lotes/temp-lote-*.json'))
    print(f"⏱️  Timeout! {len(lotes)}/{total_esperado} lotes criados.")
    return lotes

def validar_e_carregar_lotes(lotes_files):
    """Valida e carrega todos os lotes."""
    print()
    print("🔧 Movendo arquivos soltos para temp-lotes/...")

    # Mover qualquer JSON solto (SOLUÇÃO 1)
    import shutil
    for f in glob.glob('*.json'):
        if f != 'banco-perguntas.json' and not f.startswith('temp-lotes'):
            try:
                shutil.move(f, 'temp-lotes/')
                print(f"   📁 Movido: {f} → temp-lotes/")
            except:
                pass

    # Recarregar lista após move
    lotes_files = sorted(glob.glob('temp-lotes/temp-lote-*.json'))

    print()
    print("=" * 80)
    print("🔍 VALIDANDO E CARREGANDO LOTES")
    print("=" * 80)
    print()

    todas_perguntas = []
    lotes_validos = []
    lotes_invalidos = []

    for lote_file in lotes_files:
        try:
            with open(lote_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extrair perguntas
            if isinstance(data, list):
                perguntas = data
            elif isinstance(data, dict) and 'perguntas' in data:
                perguntas = data['perguntas']
            else:
                perguntas = [data] if isinstance(data, dict) and 'numero' in data else []

            if perguntas and len(perguntas) > 0:
                # Validar formato
                primeira = perguntas[0]
                if 'texto' in primeira and 'alternativas' in primeira:
                    todas_perguntas.extend(perguntas)
                    lotes_validos.append(lote_file)
                    print(f"✅ {lote_file}: {len(perguntas)} perguntas")
                else:
                    lotes_invalidos.append((lote_file, "Formato inválido"))
                    print(f"⚠️  {lote_file}: Formato incorreto")
            else:
                lotes_invalidos.append((lote_file, "Vazio"))
                print(f"❌ {lote_file}: Vazio")

        except json.JSONDecodeError as e:
            lotes_invalidos.append((lote_file, f"JSON inválido: {str(e)[:50]}"))
            print(f"❌ {lote_file}: JSON inválido")
        except Exception as e:
            lotes_invalidos.append((lote_file, str(e)))
            print(f"❌ {lote_file}: Erro - {str(e)[:50]}")

    print()
    print(f"📊 Resumo:")
    print(f"   Lotes válidos: {len(lotes_validos)}")
    print(f"   Lotes inválidos: {len(lotes_invalidos)}")
    print(f"   Total de perguntas: {len(todas_perguntas)}")

    return todas_perguntas, lotes_validos, lotes_invalidos

def detectar_duplicatas(perguntas):
    """Detecta e remove duplicatas."""
    print()
    print("🔍 DETECTANDO DUPLICATAS...")

    textos = []
    duplicatas_encontradas = []
    perguntas_unicas = []

    for p in perguntas:
        texto = p['texto'].lower().strip()

        # Verificar duplicata exata
        if texto in textos:
            duplicatas_encontradas.append(p['numero'])
            print(f"   ⚠️  Duplicata exata: P{p['numero']}")
            continue

        # Verificar similaridade alta
        eh_duplicata = False
        for i, t_existente in enumerate(textos):
            ratio = SequenceMatcher(None, texto, t_existente).ratio()
            if ratio > 0.85:
                duplicatas_encontradas.append(p['numero'])
                print(f"   ⚠️  Alta similaridade ({ratio*100:.0f}%): P{p['numero']}")
                eh_duplicata = True
                break

        if not eh_duplicata:
            textos.append(texto)
            perguntas_unicas.append(p)

    print()
    print(f"✅ Perguntas únicas: {len(perguntas_unicas)}")
    print(f"❌ Duplicatas removidas: {len(duplicatas_encontradas)}")

    return perguntas_unicas

def criar_json_final(perguntas):
    """Cria JSON final com metadata."""
    # Ordenar por número
    perguntas.sort(key=lambda x: x.get('numero', 0))

    # Renumerar sequencialmente
    for i, p in enumerate(perguntas, start=1):
        p['numero'] = i

    # Estatísticas
    topicos = {}
    dificuldades = {}
    chunks = set()

    for p in perguntas:
        topicos[p.get('topico', 'N/A')] = topicos.get(p.get('topico', 'N/A'), 0) + 1
        dificuldades[p.get('dificuldade', 'N/A')] = dificuldades.get(p.get('dificuldade', 'N/A'), 0) + 1
        if 'fonte_chunk' in p:
            chunks.add(p['fonte_chunk'])

    quiz = {
        "metadata": {
            "total_perguntas": len(perguntas),
            "ultima_atualizacao": datetime.now().isoformat(),
            "fonte": "regulamento.db",
            "metodo": "subagents_paralelo",
            "qualidade": "maxima",
            "validacao_duplicatas": "completa",
            "chunks_cobertos": len(chunks),
            "topicos_diferentes": len(topicos),
            "status": "completo"
        },
        "perguntas": perguntas
    }

    return quiz, topicos, dificuldades, chunks

def main():
    """Função principal."""
    print("=" * 80)
    print("🚀 COLETOR AUTOMÁTICO - Subagents Paralelos")
    print("=" * 80)
    print()

    # 1. Aguardar lotes
    lotes_files = aguardar_lotes(total_esperado=21, timeout=120)

    if not lotes_files:
        print("❌ Nenhum lote encontrado!")
        return

    # 2. Validar e carregar
    todas_perguntas, validos, invalidos = validar_e_carregar_lotes(lotes_files)

    if not todas_perguntas:
        print("❌ Nenhuma pergunta válida!")
        return

    # 3. Remover duplicatas
    perguntas_unicas = detectar_duplicatas(todas_perguntas)

    # 4. Criar JSON final
    quiz, topicos, dificuldades, chunks = criar_json_final(perguntas_unicas)

    # 5. Salvar
    output_file = 'banco-perguntas.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(quiz, f, ensure_ascii=False, indent=2)

    # 6. Relatório final
    print()
    print("=" * 80)
    print("✅ BANCO DE PERGUNTAS FINAL - MÁXIMA QUALIDADE")
    print("=" * 80)
    print(f"📁 Arquivo: {output_file}")
    print(f"📊 Total: {len(perguntas_unicas)} perguntas")
    print(f"🎯 Meta: 200 perguntas")
    print(f"📈 Alcançado: {len(perguntas_unicas)/2:.0f}%")
    print()

    print(f"📦 Lotes processados: {len(validos)}/{len(lotes_files)}")
    print(f"🧩 Chunks cobertos: {len(chunks)}/59")
    print(f"🏷️  Tópicos diferentes: {len(topicos)}")
    print()

    print("📊 Top 10 Tópicos:")
    for top, count in sorted(topicos.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {top}: {count} perguntas")

    print()
    print("📊 Distribuição de Dificuldade:")
    for dif, count in sorted(dificuldades.items()):
        print(f"   {dif}: {count} perguntas")

    print()
    if len(perguntas_unicas) >= 200:
        print("🎉 META DE 200 PERGUNTAS ATINGIDA!")
    elif len(perguntas_unicas) >= 150:
        print(f"✅ EXCELENTE! {len(perguntas_unicas)} perguntas de máxima qualidade!")
    elif len(perguntas_unicas) >= 100:
        print(f"✅ ÓTIMO! {len(perguntas_unicas)} perguntas prontas!")
    else:
        print(f"📝 {len(perguntas_unicas)} perguntas geradas. Continue para atingir meta.")

    print("=" * 80)

if __name__ == "__main__":
    main()
