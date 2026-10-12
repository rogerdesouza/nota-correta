"""Testa a extração com a estrutura idêntica à nota real do Banco Inter fornecida pelo usuário.
"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import sys

# Garante acesso às libs
libs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "libs")
if os.path.exists(libs_dir):
    sys.path.insert(0, libs_dir)

from src.parser import SinacorParser
from src.calculator import CalculadoraNota
from src.exporter import exportar_relatorio_completo_csv

def gerar_pdf_padrao_real(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Página 1
    y = height - 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "NOTA DE CORRETAGEM")
    y -= 15
    c.setFont("Helvetica", 8)
    c.drawString(40, y, "Nr. nota Folha Data pregão")
    y -= 12
    c.drawString(40, y, "43921642 1 08/10/2026")
    y -= 15
    c.drawString(40, y, "INTER DTVM LTDA.")
    y -= 15
    c.drawString(40, y, "Cliente 65465 C.P.F./C.N.P.J./C.V.M./C.O.")
    y -= 12
    c.drawString(40, y, "ROGER STEVE DE SOUZA 000.000.000-00")
    
    y -= 30
    c.setFont("Helvetica", 7)
    c.drawString(40, y, "Q Negociação C/V Tipo mercado Prazo Especificação do titulo Obs (*) Quantidade Preço/Ajuste Valor operação/Ajuste D/C")
    y -= 12

    ops_p1 = [
        "Bovespa V FRA ON NM VALE 6 67,65 405,90 C",
        "Bovespa V FRA ON NM VALE 10 67,65 676,50 C",
        "Bovespa V FRA ON NM VALE 3 67,65 202,95 C",
        "Bovespa V FRA ON NM VALE 10 67,63 676,30 C",
        "Bovespa V FRA ON NM VALE 1 67,65 67,65 C",
        "Bovespa V FRA ON NM VALE 50 67,62 3.381,00 C",
        "Bovespa C VIS ON NM VALE 100 68,24 6.824,00 D",
        "Bovespa V FRA ON NM VALE 1 67,64 67,64 C",
        "Bovespa C VIS ON NM VALE 200 67,74 13.548,00 D",
        "Bovespa V FRA ON NM VALE 1 67,62 67,62 C",
        "Bovespa V FRA ON NM VALE 10 67,65 676,50 C",
        "Bovespa V FRA ON NM VALE 2 67,65 135,30 C",
        "Bovespa V FRA ON NM VALE 1 67,65 67,65 C",
        "Bovespa V FRA ON NM VALE 1 67,62 67,62 C",
        "Bovespa V FRA ON NM VALE 2 67,75 135,50 C",
        "Bovespa V FRA ON NM VALE 4 67,65 270,60 C",
        "Bovespa C VIS ON NM VALE 100 67,87 6.787,00 D",
        "Bovespa V FRA ON NM VALE 2 67,63 135,26 C",
        "Bovespa V FRA ON NM VALE 1 67,65 67,65 C",
        "Bovespa V FRA ON NM VALE 2 67,65 135,30 C",
        "Bovespa V FRA ON NM VALE 30 67,64 2.029,20 C",
        "Bovespa V FRA ON NM VALE 1 67,75 67,75 C",
        "Bovespa V FRA ON NM VALE 5 67,65 338,25 C",
        "Bovespa C VIS ON NM VALE 100 67,74 6.774,00 D",
        "Bovespa V FRA ON NM VALE 50 67,65 3.382,50 C",
        "Bovespa V FRA ON NM VALE 1 67,65 67,65 C",
        "Bovespa V FRA ON NM VALE 1 67,75 67,75 C",
        "Bovespa V FRA ON NM VALE 1 67,62 67,62 C",
        "Bovespa V FRA ON NM VALE 1 67,62 67,62 C",
        "Bovespa V FRA ON NM VALE 3 67,65 202,95 C",
        "Bovespa V VIS ON NM VALE 300 67,65 20.295,00 C",
        "Bovespa V FRA ON NM VALE 5 67,63 338,15 C",
        "Bovespa V FRA ON NM VALE 5 67,62 338,10 C",
        "Bovespa V FRA ON NM VALE 10 67,75 677,50 C",
        "Bovespa V FRA ON NM VALE 1 67,65 67,65 C",
        "Bovespa V FRA ON NM VALE 10 67,65 676,50 C",
        "Bovespa C VIS ON NM VALE 100 68,02 6.802,00 D",
        "Bovespa V FRA ON NM VALE 50 67,63 3.381,50 C",
        "Bovespa V FRA ON NM VALE 36 67,75 2.439,00 C",
    ]

    for op in ops_p1:
        c.drawString(40, y, op)
        y -= 11

    c.showPage()

    # Página 2
    y = height - 40
    c.setFont("Helvetica", 8)
    c.drawString(40, y, "Nr. nota Folha Data pregão")
    y -= 12
    c.drawString(40, y, "43921642 2 08/10/2026")
    y -= 25
    c.setFont("Helvetica", 7)
    c.drawString(40, y, "Q Negociação C/V Tipo mercado Prazo Especificação do titulo Obs (*) Quantidade Preço/Ajuste Valor operação/Ajuste D/C")
    y -= 12
    c.drawString(40, y, "Bovespa V FRA ON NM VALE 3 67,62 202,86 C")
    y -= 20

    c.drawString(40, y, "Resumo dos negócios Resumo financeiro D/C")
    y -= 12
    c.drawString(40, y, "Vendas à vista 41.944,49 Valor líquido das operações 1.209,49 C")
    y -= 10
    c.drawString(40, y, "Compras à vista 40.735,00 Taxa de liquidação 14,93 D")
    y -= 10
    c.drawString(40, y, "Opções - vendas 0,00 Total 1.194,56 C")
    y -= 10
    c.drawString(40, y, "Emolumentos 4,12 D")
    y -= 10
    c.drawString(40, y, "Total 4,12 D")
    y -= 10
    c.drawString(40, y, "Corretagem / Despesas")
    y -= 10
    c.drawString(40, y, "Total 0,00 D")
    y -= 10
    c.drawString(40, y, "Líquido para 13/10/2026 1.190,41 C")

    c.save()

if __name__ == "__main__":
    test_pdf = "data/teste_padrao_real_inter.pdf"
    gerar_pdf_padrao_real(test_pdf)
    print(f"PDF gerado em {test_pdf}")

    parser = SinacorParser()
    calc = CalculadoraNota()
    notas = parser.parse_pdf(test_pdf)
    print(f"Total de notas extraídas: {len(notas)}")

    for n in notas:
        print(f"\nNOTA Nº {n.numero_nota} | DATA: {n.data_pregao} | CORRETORA: {n.corretora}")
        print(f"Total de operações extraídas: {len(n.operacoes)}")
        print(f"Taxa de liquidação: R$ {n.custos.taxa_liquidacao}")
        print(f"Emolumentos: R$ {n.custos.emolumentos}")
        print(f"Total custos: R$ {n.custos.total_custos}")

    resultados = calc.processar_notas(notas)
    exportar_relatorio_completo_csv(resultados, "data/resultado_padrao_real.csv")
    print("\nCSV gerado com sucesso!")

