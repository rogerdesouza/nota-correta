"""Módulo de exportação de dados para CSV com estrutura hierárquica solicitada pelo usuário.
"""
import csv
from typing import List
from src.models import ResultadoCalculoNota

def exportar_relatorio_completo_csv(
    resultados: List[ResultadoCalculoNota],
    output_csv_path: str,
    delimiter: str = ";"
):
    """Gera o arquivo CSV com:
    1. No topo: Resultado consolidado por modalidade (Swing Trade e Day Trade).
    2. Logo abaixo: Consolidado por cada ativo separado pelo tipo da operação.
       Ordem exata das colunas:
       Operação (C/V), Ativo, Data, Tipo, Qtd, Preço Médio, Modalidade, Custos, Resultado.
    """
    with open(output_csv_path, mode="w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file, delimiter=delimiter)

        # ==========================================
        # 1. TOPO: RESUMO CONSOLIDADO POR MODALIDADE
        # ==========================================
        writer.writerow(["=== RESUMO CONSOLIDADO POR MODALIDADE ==="])
        colunas_resumo = [
            "Modalidade",
            "Qtd Operações",
            "Total Compras (R$)",
            "Total Vendas (R$)",
            "Volume Total (R$)",
            "Resultado Bruto (R$)",
            "Taxas Rateadas (R$)",
            "Resultado Líquido (R$)",
        ]
        writer.writerow(colunas_resumo)

        for res in resultados:
            # Swing Trade
            if res.swing_trade.volume_total > 0:
                st = res.swing_trade
                res_bruto_st = f"{st.resultado_bruto:.2f}".replace(".", ",") if st.resultado_bruto is not None else "-"
                res_liq_st = f"{st.resultado_liquido:.2f}".replace(".", ",") if st.resultado_liquido is not None else "-"
                writer.writerow([
                    st.modalidade,
                    len(st.operacoes) or "-",
                    f"{st.total_compras:.2f}".replace(".", ","),
                    f"{st.total_vendas:.2f}".replace(".", ","),
                    f"{st.volume_total:.2f}".replace(".", ","),
                    res_bruto_st,
                    f"{st.taxas_proporcionais:.2f}".replace(".", ","),
                    res_liq_st,
                ])

            # Day Trade
            if res.day_trade.volume_total > 0:
                dt = res.day_trade
                res_bruto_dt = f"{dt.resultado_bruto:.2f}".replace(".", ",") if dt.resultado_bruto is not None else "-"
                res_liq_dt = f"{dt.resultado_liquido:.2f}".replace(".", ",") if dt.resultado_liquido is not None else "-"
                writer.writerow([
                    dt.modalidade,
                    len(dt.operacoes) or "-",
                    f"{dt.total_compras:.2f}".replace(".", ","),
                    f"{dt.total_vendas:.2f}".replace(".", ","),
                    f"{dt.volume_total:.2f}".replace(".", ","),
                    res_bruto_dt,
                    f"{dt.taxas_proporcionais:.2f}".replace(".", ","),
                    res_liq_dt,
                ])

        # Linha em branco para separar visualmente as seções
        writer.writerow([])

        # ==========================================
        # 2. LOGO ABAIXO: CONSOLIDADO POR ATIVO
        # ==========================================
        writer.writerow(["=== CONSOLIDADO POR ATIVO ==="])
        colunas_ativo = [
            "Ativo",
            "Data",
            "Tipo",
            "Qtd",
            "Preço Médio",
            "Modalidade",
            "Custos",
            "Operação",
        ]
        writer.writerow(colunas_ativo)

        for res in resultados:
            for atv in res.consolidados_ativos:
                data_ativo_str = atv.data.strftime("%d/%m/%Y") if atv.data else ""
                writer.writerow([
                    atv.ativo,
                    data_ativo_str,
                    atv.tipo,
                    atv.qtd,
                    f"{atv.preco_medio:.4f}".replace(".", ","),
                    atv.modalidade,
                    f"{atv.custos:.2f}".replace(".", ","),
                    atv.operacao,
                ])
