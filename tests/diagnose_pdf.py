"""Script para diagnosticar qualquer PDF de nota de corretagem real.
Oculta dados sensíveis (CPF, nome, conta) e exibe a estrutura das linhas extraídas
para identificar exatamente por que o parser não reconheceu o padrão.
"""
import sys
import os
import re

# Garante acesso às libs locais
libs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "libs")
if os.path.exists(libs_dir):
    sys.path.insert(0, libs_dir)

import pdfplumber

def diagnosticar(pdf_path: str):
    if not os.path.exists(pdf_path):
        print(f"[ERRO] Arquivo não encontrado: {pdf_path}")
        return

    print("=" * 70)
    print(f"DIAGNÓSTICO DA NOTA REAL: {os.path.basename(pdf_path)}")
    print("=" * 70)

    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total de páginas no PDF: {len(pdf.pages)}\n")

        for i, page in enumerate(pdf.pages):
            print(f"--- PÁGINA {i + 1} ---")
            raw_text = page.extract_text() or ""
            if not raw_text.strip():
                print("[AVISO] Nenhum texto extraído nesta página (pode ser imagem/escaneado).")
                continue

            linhas = raw_text.split("\n")
            print(f"Total de linhas extraídas: {len(linhas)}")

            # Procura cabeçalho
            print("\n[Trechos de Cabeçalho Detectados]:")
            for l in linhas[:15]:
                # Mascara CPF e dados pessoais
                l_masked = re.sub(r"\d{3}\.\d{3}\.\d{3}-\d{2}", "XXX.XXX.XXX-XX", l)
                l_masked = re.sub(r"(Nome(?:\s+do\s+Cliente)?:\s*)([A-Z\s]+)", r"\1[NOME OCULTADO]", l_masked, flags=re.IGNORECASE)
                l_masked = re.sub(r"(Código(?:\s+do\s+Cliente)?:\s*)\d+", r"\1[CONTA OCULTADA]", l_masked, flags=re.IGNORECASE)
                print("  |", l_masked)

            # Procura linhas com potencial de operações
            print("\n[Linhas Candidatas a Operações]:")
            candidatas = 0
            for idx, l in enumerate(linhas):
                # Procura por BOVESPA ou C/V ou pregão
                l_upper = l.upper()
                if any(k in l_upper for k in ["BOVESPA", "VISTA", "FRACION", "OPCAO", "1-BOV"]) or re.search(r"\b[CV]\b", l):
                    candidatas += 1
                    print(f"  Linha {idx+1}: {l.strip()}")

            if candidatas == 0:
                print("  [AVISO] Nenhuma linha com termos típicos de negociação encontrada.")

            # Procura linhas de custos e resumo
            print("\n[Linhas de Resumo / Custos]:")
            for l in linhas:
                l_upper = l.upper()
                if any(k in l_upper for k in ["LIQUIDA", "EMOLUMENT", "CORRETAGEM", "LÍQUIDO", "TOTAL", "CUSTOS", "RESUMO"]):
                    print("  |", l.strip())

    print("\n" + "=" * 70)
    print("Fim do diagnóstico.")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 tests/diagnose_pdf.py caminho/para/sua_nota.pdf")
    else:
        diagnosticar(sys.argv[1])

