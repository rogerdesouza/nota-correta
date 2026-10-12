"""Simula a nota de 6 páginas do Banco Inter exatamente como no diagnóstico do usuário:
- Páginas 1 a 5: dezenas de operações de AXIA ENERGIA, ENGIE BRASIL e VALE.
- Página 6: SEM cabeçalho de número de nota, contendo apenas o resumo financeiro com as taxas.
"""
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

libs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "libs")
if os.path.exists(libs_dir):
    sys.path.insert(0, libs_dir)

from src.parser import SinacorParser
from src.calculator import CalculadoraNota
from src.exporter import exportar_relatorio_completo_csv

def gerar_pdf_6_paginas(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Páginas 1 a 5 com cabeçalho e operações
    for pag in range(1, 6):
        y = height - 40
        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y, "NOTA DE CORRETAGEM")
        y -= 12
        c.setFont("Helvetica", 8)
        c.drawString(40, y, "Nr. nota Folha Data pregão")
        y -= 12
        c.drawString(40, y, f"43954102 {pag} 09/10/2026")
        y -= 15
        c.drawString(40, y, "INTER DTVM LTDA.")
        y -= 15
        c.drawString(40, y, "Cliente 65465 C.P.F./C.N.P.J./C.V.M./C.O.")
        y -= 12
        c.drawString(40, y, "ROGER STEVE DE SOUZA 000.000.000-00")
        y -= 25

        c.setFont("Helvetica", 7)
        c.drawString(40, y, "Q Negociação C/V Tipo mercado Prazo Especificação do titulo Obs (*) Quantidade Preço/Ajuste Valor operação/Ajuste D/C")
        y -= 12

        if pag == 1:
            ops = [
                "Bovespa V FRA ON NM AXIA ENERGIA 5 59,56 297,80 C",
                "Bovespa V FRA ON NM ENGIE BRASIL 10 31,65 316,50 C",
                "Bovespa V FRA ON NM VALE 10 67,51 675,10 C",
                "Bovespa C VIS ON NM VALE 100 67,17 6.717,00 D",
                "Bovespa C VIS ON NM AXIA ENERGIA 100 59,75 5.975,00 D",
            ]
        elif pag == 2:
            ops = [
                "Bovespa C VIS ON NM ENGIE BRASIL 200 31,86 6.372,00 D",
                "Bovespa V VIS ON NM AXIA ENERGIA 100 59,55 5.955,00 C",
                "Bovespa C VIS ON NM VALE 100 67,47 6.747,00 D",
            ]
        elif pag == 3:
            ops = [
                "Bovespa C VIS ON NM VALE 100 67,37 6.737,00 D",
                "Bovespa V VIS ON NM AXIA ENERGIA 200 59,55 11.910,00 C",
            ]
        elif pag == 4:
            ops = [
                "Bovespa C VIS ON NM ENGIE BRASIL 400 31,66 12.664,00 D",
                "Bovespa V VIS ON NM ENGIE BRASIL 200 31,68 6.336,00 C",
            ]
        else: # pag == 5
            ops = [
                "Bovespa V VIS ON NM ENGIE BRASIL 100 31,68 3.168,00 C",
                "Bovespa V FRA ON NM VALE 24 67,50 1.620,00 C",
            ]

        for op in ops:
            c.drawString(40, y, op)
            y -= 12

        c.showPage()

    # Página 6: SEM cabeçalho de número de nota (exatamente como na nota real do usuário!)
    y = height - 40
    c.setFont("Helvetica", 7)
    c.drawString(40, y, "Resumo dos negócios Resumo financeiro D/C")
    y -= 12
    c.drawString(40, y, "Debêntures 0,00 Clearing")
    y -= 10
    c.drawString(40, y, "Vendas à vista 115.169,66 Valor líquido das operações 731,66 C")
    y -= 10
    c.drawString(40, y, "Compras à vista 114.438,00 Taxa de liquidação 41,35 D")
    y -= 10
    c.drawString(40, y, "Opções - compras 0,00 Taxa de Registro 0,00 D")
    y -= 10
    c.drawString(40, y, "Opções - vendas 0,00 Total 690,31 C")
    y -= 10
    c.drawString(40, y, "Emolumentos 11,47 D")
    y -= 10
    c.drawString(40, y, "Total 11,47 D")
    y -= 10
    c.drawString(40, y, "Líquido para 14/10/2026 678,81 C")

    c.save()

if __name__ == "__main__":
    pdf_path = "data/teste_6_paginas.pdf"
    gerar_pdf_6_paginas(pdf_path)
    print(f"PDF 6 páginas criado em: {pdf_path}")

    parser = SinacorParser()
    calc = CalculadoraNota()
    notas = parser.parse_pdf(pdf_path)

    print(f"Total de notas extraídas: {len(notas)}")
    for n in notas:
        print(f"Nota: {n.numero_nota} | Data: {n.data_pregao} | Operações: {len(n.operacoes)}")
        print(f"Taxa de Liquidação: R$ {n.custos.taxa_liquidacao}")
        print(f"Emolumentos:        R$ {n.custos.emolumentos}")
        print(f"Total Custos:       R$ {n.custos.total_custos}")

    resultados = calc.processar_notas(notas)
    exportar_relatorio_completo_csv(resultados, "data/resultado_6_paginas.csv")
    print("CSV gerado!")

