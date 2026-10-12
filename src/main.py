"""Ponto de entrada principal do aplicativo NotaCorreta.
Pode ser executado com interface gráfica no navegador ou diretamente via linha de comando (CLI).
"""
import sys
import argparse
import os

# Adiciona o diretório raiz e libs ao sys.path para garantir portabilidade
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
libs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "libs")
if os.path.exists(libs_dir):
    sys.path.insert(0, libs_dir)

from src.parser import SinacorParser
from src.calculator import CalculadoraNota
from src.exporter import exportar_relatorio_completo_csv
from src.ui.server import iniciar_servidor_local

def modo_cli(pdf_paths: list, output_csv: str):
    """Executa o processamento via linha de comando."""
    print("=" * 60)
    print("NotaCorreta - Modo Linha de Comando")
    print("=" * 60)

    parser = SinacorParser()
    calc = CalculadoraNota()
    todas_notas = []

    for path in pdf_paths:
        if not os.path.exists(path):
            print(f"[ERRO] Arquivo não encontrado: {path}")
            continue
        print(f"-> Lendo arquivo: {path}")
        notas = parser.parse_pdf(path)
        todas_notas.extend(notas)

    if not todas_notas:
        print("[ERRO] Nenhuma nota de corretagem válida foi processada.")
        sys.exit(1)

    print(f"-> Calculando métricas e consolidados ({len(todas_notas)} notas encontradas)...")
    resultados = calc.processar_notas(todas_notas)

    print(f"-> Exportando para CSV: {output_csv}")
    exportar_relatorio_completo_csv(resultados, output_csv)

    print(f"[SUCESSO] Relatório gerado com sucesso em: {output_csv}\n")

def main():
    arg_parser = argparse.ArgumentParser(
        description="NotaCorreta - Extrator e Calculador de Notas de Corretagem B3/SINACOR",
        add_help=True
    )
    arg_parser.add_argument("pdf_files", nargs="*", help="Arquivos PDF das notas de corretagem (opcional)")
    arg_parser.add_argument("-o", "--output", default="relatorio_notas_corretagem.csv", help="Caminho do arquivo CSV de saída")
    arg_parser.add_argument("--no-browser", action="store_true", help="Não abre o navegador automaticamente ao iniciar o modo gráfico")

    args = arg_parser.parse_args()

    if args.pdf_files:
        modo_cli(args.pdf_files, args.output)
    else:
        # Se nenhum arquivo foi passado, abre a interface gráfica local
        iniciar_servidor_local(open_browser=not args.no_browser)

if __name__ == "__main__":
    main()

