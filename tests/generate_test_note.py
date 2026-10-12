"""Script para gerar uma nota de corretagem sintética do Banco Inter (padrão SINACOR)
para testes e validação do extrator.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def create_sample_inter_note(output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Top Margin: height - 40
    y = height - 40

    # Header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "INTER DISTRIBUIDORA DE TITULOS E VALORES MOBILIARIOS LTDA")
    c.setFont("Helvetica", 9)
    c.drawString(40, y - 14, "Av. Barbacena, 1219 - Santo Agostinho - Belo Horizonte - MG - CNPJ: 18.945.670/0001-46")

    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - 40, y, "NOTA DE CORRETAGEM")
    
    y -= 35
    c.setLineWidth(1)
    c.setStrokeColor(colors.gray)
    c.line(40, y, width - 40, y)

    # Info bar: Nr Nota, Folha, Data Pregão
    y -= 15
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y, "Nr. nota:")
    c.setFont("Helvetica", 9)
    c.drawString(90, y, "1049281")

    c.setFont("Helvetica-Bold", 9)
    c.drawString(200, y, "Folha:")
    c.setFont("Helvetica", 9)
    c.drawString(235, y, "1")

    c.setFont("Helvetica-Bold", 9)
    c.drawString(350, y, "Data pregão:")
    c.setFont("Helvetica", 9)
    c.drawString(420, y, "15/03/2024")

    # Client Info
    y -= 25
    c.rect(40, y - 20, width - 80, 25, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(45, y - 5, "Código do Cliente:")
    c.setFont("Helvetica", 8)
    c.drawString(130, y - 5, "1234567")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(220, y - 5, "Nome do Cliente:")
    c.setFont("Helvetica", 8)
    c.drawString(295, y - 5, "INVESTIDOR TESTE DA SILVA")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(45, y - 16, "C.P.F./C.N.P.J.:")
    c.setFont("Helvetica", 8)
    c.drawString(130, y - 16, "000.000.000-00")

    # Tabela de Negócios Realizados
    y -= 45
    c.setFont("Helvetica-Bold", 9)
    c.drawString(40, y, "Negócios realizados")
    y -= 15

    # Cabeçalho da tabela
    c.setFillColor(colors.HexColor("#f0f0f0"))
    c.rect(40, y - 5, width - 80, 16, stroke=0, fill=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 7)

    c.drawString(42, y, "Q")
    c.drawString(55, y, "Negociação")
    c.drawString(110, y, "C/V")
    c.drawString(135, y, "Tipo mercado")
    c.drawString(195, y, "Prazo")
    c.drawString(225, y, "Especificação do título")
    c.drawString(350, y, "Obs (*)")
    c.drawRightString(400, y, "Quantidade")
    c.drawRightString(465, y, "Preço / Ajuste")
    c.drawRightString(525, y, "Valor Operação")
    c.drawString(535, y, "D/C")

    y -= 12
    c.setStrokeColor(colors.lightgrey)
    c.line(40, y + 2, width - 40, y + 2)

    # Dados das Operações (Itens)
    operacoes = [
        ("1-BOVESPA", "C", "VISTA", "", "PETR4       PN      N2", "", "100", "36,50", "3.650,00", "D"),
        ("1-BOVESPA", "C", "FRACIONARIO", "", "VALE3       ON      NM", "", "50", "62,20", "3.110,00", "D"),
        ("1-BOVESPA", "C", "VISTA", "", "MXRF11      FII MAXI REN CI", "", "100", "10,50", "1.050,00", "D"),
        ("1-BOVESPA", "V", "VISTA", "", "ITUB4       PN  ED  N1", "", "200", "34,10", "6.820,00", "C"),
        ("1-BOVESPA", "C", "VISTA", "", "BBAS3       ON      NM", "D", "100", "28,40", "2.840,00", "D"),
        ("1-BOVESPA", "V", "VISTA", "", "BBAS3       ON      NM", "D", "100", "29,10", "2.910,00", "C"),
    ]

    c.setFont("Helvetica", 7)
    for op in operacoes:
        neg, cv, merc, prazo, espec, obs, qtd, preco, val, dc = op
        c.drawString(42, y, "1")
        c.drawString(55, y, neg)
        c.drawString(115, y, cv)
        c.drawString(135, y, merc)
        c.drawString(195, y, prazo)
        c.drawString(225, y, espec)
        c.drawString(355, y, obs)
        c.drawRightString(400, y, qtd)
        c.drawRightString(465, y, preco)
        c.drawRightString(525, y, val)
        c.drawString(535, y, dc)
        y -= 13

    # Linha separadora
    y -= 5
    c.setStrokeColor(colors.gray)
    c.line(40, y, width - 40, y)

    # Resumo dos Negócios e Resumo Financeiro (lado a lado padrão SINACOR)
    y -= 15
    y_topo_resumos = y

    # Coluna Esquerda: Resumo dos Negócios
    c.setFont("Helvetica-Bold", 8)
    c.drawString(40, y, "Resumo dos Negócios")
    y -= 12
    c.setFont("Helvetica", 7)

    resumo_negocios = [
        ("Debêntures", "0,00"),
        ("Vendas à vista", "9.730,00"),
        ("Compras à vista", "10.650,00"),
        ("Opções - compras", "0,00"),
        ("Opções - vendas", "0,00"),
        ("Operações à termo", "0,00"),
        ("Valor das oper. c/ títulos públicos", "0,00"),
        ("Valor das operações", "20.380,00"),
    ]

    for label, val in resumo_negocios:
        c.drawString(40, y, label)
        c.drawRightString(230, y, val)
        y -= 10

    # Coluna Direita: Resumo Financeiro / Custos
    y_dir = y_topo_resumos
    c.setFont("Helvetica-Bold", 8)
    c.drawString(270, y_dir, "Resumo Financeiro")
    y_dir -= 12
    c.setFont("Helvetica", 7)

    resumo_financeiro = [
        ("Clearing", ""),
        ("Valor líquido das operações", "920,00 D"),
        ("Taxa de liquidação", "5,09 D"),
        ("Taxa de Registro", "0,00 D"),
        ("Total Clearing", "925,09 D"),
        ("Bolsa", ""),
        ("Taxa de termo/opções", "0,00 D"),
        ("Taxa A.N.A.", "0,00 D"),
        ("Emolumentos", "1,02 D"),
        ("Total Bolsa", "1,02 D"),
        ("Custos / Despesas", ""),
        ("Corretagem", "0,00 D"),
        ("ISS / Impostos", "0,00 D"),
        ("I.R.R.F. s/ operações, base R$ 70,00", "0,00 D"),
        ("Outras Bovespa", "0,00 D"),
        ("Total Custos / Despesas", "6,11 D"),
        ("LÍQUIDO PARA 18/03/2024", "926,11 D"),
    ]

    for label, val in resumo_financeiro:
        if label in ["Clearing", "Bolsa", "Custos / Despesas"]:
            c.setFont("Helvetica-Bold", 7)
            c.drawString(270, y_dir, label)
        elif "LÍQUIDO PARA" in label:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(270, y_dir, label)
            c.drawRightString(width - 40, y_dir, val)
        else:
            c.setFont("Helvetica", 7)
            c.drawString(270, y_dir, label)
            c.drawRightString(width - 40, y_dir, val)
        y_dir -= 10

    # Rodapé
    c.setFont("Helvetica-Oblique", 7)
    c.drawString(40, 30, "(*) Observações: D = Day Trade | A = Posição | H = Home Broker")
    c.drawRightString(width - 40, 30, "Padrão SINACOR / B3")

    c.save()
    print(f"Nota de teste criada com sucesso em: {output_path}")

if __name__ == "__main__":
    create_sample_inter_note("data/nota_inter_teste.pdf")

