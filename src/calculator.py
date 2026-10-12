"""Módulo de cálculos e regras de negócio para notas de corretagem.
Implementa a regra oficial da Receita Federal (IN RFB nº 1.585) para Day Trade:
Quando um ativo é comprado e vendido no mesmo dia, a menor quantidade entre compras e vendas
é casada como Day Trade, e a quantidade excedente é classificada como Swing Trade.
"""
from collections import defaultdict
from typing import List, Dict
from src.models import (
    NotaCorretagem,
    ResumoModalidade,
    ResultadoCalculoNota,
    ConsolidadoAtivo,
    ItemOperacao,
)

def classificar_tipo_ativo(ticker: str, especificacao: str) -> str:
    """Classifica se o ativo é Fundo Imobiliário ('F') ou Ação ('A')."""
    esp_upper = especificacao.upper()
    tick_upper = ticker.upper()

    termos_fii = ["FII", "FDO INV IMOB", "IMOBILIARIO", "IMOB"]
    if any(termo in esp_upper for termo in termos_fii):
        return "F"

    if tick_upper.endswith("11"):
        units_acoes = ["TAEE11", "KLBN11", "SAPR11", "SANB11", "BPAC11", "ALUP11", "ENGI11", "SULA11"]
        if tick_upper in units_acoes or "UNT" in esp_upper or "UNIT" in esp_upper:
            return "A"
        if "CI" in esp_upper or "FDO" in esp_upper:
            return "F"

    return "A"

class CalculadoraNota:
    """Responsável por processar, segregar e calcular métricas financeiras das notas."""

    def processar_nota(self, nota: NotaCorretagem) -> ResultadoCalculoNota:
        """Segrega as operações em Swing Trade e Day Trade respeitando o casamento de quantidades."""
        resultado = ResultadoCalculoNota(
            numero_nota=nota.numero_nota,
            data_pregao=nota.data_pregao,
            corretora=nota.corretora,
            total_custos_nota=nota.custos.total_custos,
            valor_liquido_nota=nota.valor_liquido_nota,
        )

        # 1. Agrupar operações da nota por ativo e por tipo (C ou V)
        ops_por_ticker: Dict[str, Dict[str, List[ItemOperacao]]] = defaultdict(lambda: {"C": [], "V": []})
        for op in nota.operacoes:
            ops_por_ticker[op.ticker][op.tipo_operacao].append(op)

        # Estruturas para consolidação por modalidade e ativo
        # Cada item: {"ticker": str, "operacao": str, "modalidade": str, "qtd": int, "valor": float, "espec": str}
        itens_consolidados = []

        # Totais para os resumos de topo
        dt_compras_val = 0.0
        dt_vendas_val = 0.0
        dt_ops_count = 0

        st_compras_val = 0.0
        st_vendas_val = 0.0
        st_ops_count = 0

        for ticker, dic in ops_por_ticker.items():
            compras = dic["C"]
            vendas = dic["V"]

            qtd_c = sum(c.quantidade for c in compras)
            val_c = sum(c.valor_total for c in compras)

            qtd_v = sum(v.quantidade for v in vendas)
            val_v = sum(v.valor_total for v in vendas)

            pm_c = round(val_c / qtd_c, 4) if qtd_c > 0 else 0.0
            pm_v = round(val_v / qtd_v, 4) if qtd_v > 0 else 0.0

            espec_exemplo = (compras[0].especificacao_titulo if compras else vendas[0].especificacao_titulo)

            # Caso 1: Houve tanto Compra quanto Venda no mesmo pregão -> Casamento de Day Trade
            if qtd_c > 0 and qtd_v > 0:
                qtd_casada_dt = min(qtd_c, qtd_v)

                # Parcela de Compra no Day Trade
                val_c_dt = round(pm_c * qtd_casada_dt, 2)
                itens_consolidados.append({
                    "ticker": ticker,
                    "operacao": "C",
                    "modalidade": "D",
                    "qtd": qtd_casada_dt,
                    "preco_medio": round(pm_c, 4),
                    "valor_total": val_c_dt,
                    "espec": espec_exemplo
                })
                dt_compras_val += val_c_dt

                # Parcela de Venda no Day Trade
                val_v_dt = round(pm_v * qtd_casada_dt, 2)
                itens_consolidados.append({
                    "ticker": ticker,
                    "operacao": "V",
                    "modalidade": "D",
                    "qtd": qtd_casada_dt,
                    "preco_medio": round(pm_v, 4),
                    "valor_total": val_v_dt,
                    "espec": espec_exemplo
                })
                dt_vendas_val += val_v_dt
                dt_ops_count += len(compras) + len(vendas)

                # Sobra de Compra para Swing Trade (se comprou mais do que vendeu)
                if qtd_c > qtd_casada_dt:
                    sobra_c = qtd_c - qtd_casada_dt
                    val_c_st = round(val_c - val_c_dt, 2)
                    itens_consolidados.append({
                        "ticker": ticker,
                        "operacao": "C",
                        "modalidade": "S",
                        "qtd": sobra_c,
                        "preco_medio": round(pm_c, 4),
                        "valor_total": val_c_st,
                        "espec": espec_exemplo
                    })
                    st_compras_val += val_c_st
                    st_ops_count += 1

                # Sobra de Venda para Swing Trade (se vendeu mais do que comprou)
                if qtd_v > qtd_casada_dt:
                    sobra_v = qtd_v - qtd_casada_dt
                    val_v_st = round(val_v - val_v_dt, 2)
                    itens_consolidados.append({
                        "ticker": ticker,
                        "operacao": "V",
                        "modalidade": "S",
                        "qtd": sobra_v,
                        "preco_medio": round(pm_v, 4),
                        "valor_total": val_v_st,
                        "espec": espec_exemplo
                    })
                    st_vendas_val += val_v_st
                    st_ops_count += 1

            # Caso 2: Apenas Compras -> 100% Swing Trade
            elif qtd_c > 0:
                itens_consolidados.append({
                    "ticker": ticker,
                    "operacao": "C",
                    "modalidade": "S",
                    "qtd": qtd_c,
                    "preco_medio": round(pm_c, 4),
                    "valor_total": round(val_c, 2),
                    "espec": espec_exemplo
                })
                st_compras_val += val_c
                st_ops_count += len(compras)

            # Caso 3: Apenas Vendas -> 100% Swing Trade
            elif qtd_v > 0:
                itens_consolidados.append({
                    "ticker": ticker,
                    "operacao": "V",
                    "modalidade": "S",
                    "qtd": qtd_v,
                    "preco_medio": round(pm_v, 4),
                    "valor_total": round(val_v, 2),
                    "espec": espec_exemplo
                })
                st_vendas_val += val_v
                st_ops_count += len(vendas)

        # 2. Resumos de Topo
        resultado.day_trade = ResumoModalidade(
            modalidade="Day Trade",
            operacoes=[None] * dt_ops_count,
            total_compras=round(dt_compras_val, 2),
            total_vendas=round(dt_vendas_val, 2),
            volume_total=round(dt_compras_val + dt_vendas_val, 2),
        )

        resultado.swing_trade = ResumoModalidade(
            modalidade="Swing Trade",
            operacoes=[None] * st_ops_count,
            total_compras=round(st_compras_val, 2),
            total_vendas=round(st_vendas_val, 2),
            volume_total=round(st_compras_val + st_vendas_val, 2),
        )

        # Rateio proporcional de custos entre Day Trade e Swing Trade
        vol_total = resultado.day_trade.volume_total + resultado.swing_trade.volume_total
        total_custos_nota = nota.custos.total_custos

        if vol_total > 0 and total_custos_nota > 0:
            resultado.day_trade.taxas_proporcionais = round(
                total_custos_nota * (resultado.day_trade.volume_total / vol_total), 2
            )
            resultado.swing_trade.taxas_proporcionais = round(
                total_custos_nota - resultado.day_trade.taxas_proporcionais, 2
            )

        # Resultados para Day Trade: Bruto e Líquido
        if resultado.day_trade.volume_total > 0:
            res_bruto_dt = round(resultado.day_trade.total_vendas - resultado.day_trade.total_compras, 2)
            resultado.day_trade.resultado_bruto = res_bruto_dt
            resultado.day_trade.resultado_liquido = round(
                res_bruto_dt - resultado.day_trade.taxas_proporcionais,
                2
            )

        # 3. Consolidado por Ativo (com rateio exato de custos de cada linha)
        # Ordenação: Swing Trade primeiro (C depois V), Day Trade depois (C depois V)
        itens_consolidados.sort(key=lambda x: (0 if x["modalidade"] == "S" else 1, x["operacao"], x["ticker"]))

        consolidados: List[ConsolidadoAtivo] = []
        custos_acumulados = 0.0

        for idx, item in enumerate(itens_consolidados):
            tipo_ativo = classificar_tipo_ativo(item["ticker"], item["espec"])

            if vol_total > 0 and total_custos_nota > 0:
                if idx == len(itens_consolidados) - 1:
                    custo_item = round(total_custos_nota - custos_acumulados, 2)
                else:
                    custo_item = round(total_custos_nota * (item["valor_total"] / vol_total), 2)
                    custos_acumulados += custo_item
            else:
                custo_item = 0.0

            consolidados.append(ConsolidadoAtivo(
                operacao=item["operacao"],
                ativo=item["ticker"],
                data=nota.data_pregao,
                tipo=tipo_ativo,
                qtd=item["qtd"],
                preco_medio=item["preco_medio"],
                modalidade=item["modalidade"],
                custos=custo_item,
            ))

        resultado.consolidados_ativos = consolidados
        return resultado

    def processar_notas(self, notas: List[NotaCorretagem]) -> List[ResultadoCalculoNota]:
        """Processa uma lista de notas de corretagem."""
        return [self.processar_nota(nota) for nota in notas]
