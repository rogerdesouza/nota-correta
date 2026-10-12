"""Módulo de leitura e extração de Notas de Corretagem (Padrão SINACOR / Banco Inter / B3).
"""
import re
from datetime import datetime
from typing import List, Optional
import pdfplumber

from src.models import ItemOperacao, NotaCorretagem, ResumoCustos

def parse_ptbr_float(val_str: str) -> float:
    """Converte string no formato brasileiro (ex: '3.650,00') para float (3650.00)."""
    if not val_str:
        return 0.0
    val_str = val_str.strip()
    clean_val = val_str.replace(".", "").replace(",", ".")
    try:
        return float(clean_val)
    except ValueError:
        return 0.0

MAPA_NOMES_TICKERS = {
    "ENGIE BRASIL": "EGIE3",
    "ENGIE": "EGIE3",
    "AXIA ENERGIA": "AXIA3",
    "AXIA": "AXIA3",
    "VALE": "VALE3",
    "PETROBRAS": "PETR4",
    "ITAU UNIBANCO": "ITUB4",
    "ITAU": "ITUB4",
    "BRADESCO": "BBDC4",
    "BANCO DO BRASIL": "BBAS3",
    "ELETROBRAS": "ELET3",
    "WEG": "WEGE3",
    "SUZANO": "SUZB3",
    "KLABIN": "KLBN11",
    "TAESA": "TAEE11",
    "SANEPAR": "SAPR11",
    "COPEL": "CPLE6",
    "CEMIG": "CMIG4",
    "EQUATORIAL": "EQTL3",
    "RUMO": "RAIL3",
    "COSAN": "CSAN3",
    "AMBEV": "ABEV3",
    "MAGALU": "MGLU3",
    "MAGAZINE LUIZA": "MGLU3",
    "LOJAS RENNER": "LREN3",
    "LOCALIZA": "RENT3",
    "B3": "B3SA3",
    "BB SEGURIDADE": "BBSE3",
    "CSN": "CSNA3",
    "CSN MINERACAO": "CMIN3",
    "GERDAU": "GGBR4",
    "USIMINAS": "USIM5",
    "VIBRA": "VBBR3",
    "PRIO": "PRIO3",
    "PETRORIO": "PRIO3",
    "BRAVA": "BRAV3",
    "RAIZEN": "RAIZ4",
    "ALUPAR": "ALUP11",
    "AUREN": "AURE3",
    "SABESP": "SBSP3",
    "CYRELA": "CYRE3",
    "HAPVIDA": "HAPV3",
    "REDE D OR": "RDOR3",
    "TOTVS": "TOTS3",
    "EMBRAER": "EMBR3",
}

def extrair_ticker(especificacao: str) -> str:
    """Extrai o código do ativo/ticker da descrição da B3."""
    esp = especificacao.strip()
    esp_upper = esp.upper()

    # 1. Se já contém ticker explícito com código numérico (ex: VALE3, PETR4, MXRF11)
    match_direto = re.search(r"\b([A-Z]{4}\d{1,2}[A-Z]?)\b", esp_upper)
    if match_direto:
        return match_direto.group(1)

    # 2. Mapeamento por nome de empresa brasileira da B3 (ex: 'ENGIE BRASIL' -> 'EGIE3')
    for nome_empresa, ticker_oficial in MAPA_NOMES_TICKERS.items():
        if nome_empresa in esp_upper:
            if " PN " in esp_upper and ticker_oficial.endswith("3"):
                return ticker_oficial[:-1] + "4"
            return ticker_oficial

    # 2. Caso invertido do SINACOR (ex: 'ON NM VALE', 'PN N2 PETR', 'ON VALE')
    termos_controle = {
        "ON", "PN", "PNA", "PNB", "PNC", "PND", "NM", "N1", "N2",
        "MA", "M2", "MB", "ED", "EJ", "EB", "EX", "REC", "DIR", "FRA", "VIS", "FII"
    }
    tokens = [t.upper() for t in re.findall(r"[A-Za-z0-9]+", esp)]

    ticker_base = None
    tipo_acao = None

    for t in tokens:
        if t in {"ON", "PN", "PNA", "PNB", "UNT", "UNIT", "CI"}:
            tipo_acao = t
        elif len(t) == 4 and t.isalpha() and t not in termos_controle:
            ticker_base = t

    if ticker_base:
        if tipo_acao == "ON":
            return f"{ticker_base}3"
        elif tipo_acao == "PN":
            return f"{ticker_base}4"
        elif tipo_acao == "PNA":
            return f"{ticker_base}5"
        elif tipo_acao == "PNB":
            return f"{ticker_base}6"
        elif tipo_acao in {"UNT", "UNIT"}:
            return f"{ticker_base}11"
        return f"{ticker_base}3"

    palavras = esp.split()
    return palavras[-1] if palavras else "ATIVO"

class SinacorParser:
    """Extrator de dados de notas de corretagem padrão SINACOR / Banco Inter."""

    OPERACAO_REGEX = re.compile(
        r"^(?:(?P<ordem>\d+)\s+)?"
        r"(?P<negociacao>(?:\d\s*-\s*)?BOVESPA|Bovespa)\s+"
        r"(?P<tipo_op>[CV])\s+"
        r"(?P<tipo_mercado>VISTA|VIS|FRACIONARIO|FRACION[AÁ]RIO|FRA|OPCAO|OP[CÇ][AÃ]O[^\d]*?|TERMO|LEILAO)\s+"
        r"(?P<resto_linha>.+)$",
        re.IGNORECASE
    )

    VALORES_FINAIS_REGEX = re.compile(
        r"^(?P<especificacao>.*?)\s+"
        r"(?:(?P<obs>[DAH\*#2])\s+)?"
        r"(?P<qtd>\d[\d\.]*)\s+"
        r"(?P<preco>\d[\d\.]*,\d{2,4})\s+"
        r"(?P<valor>\d[\d\.]*,\d{2})\s+"
        r"(?P<dc>[DC])$",
        re.IGNORECASE
    )

    def parse_pdf(self, pdf_path: str) -> List[NotaCorretagem]:
        """Lê um arquivo PDF e extrai uma ou mais notas de corretagem."""
        notas: List[NotaCorretagem] = []

        with pdfplumber.open(pdf_path) as pdf:
            nota_atual: Optional[NotaCorretagem] = None

            for page_idx, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if not text.strip():
                    continue

                # 1. Extração do Cabeçalho
                header_multiline = re.search(
                    r"Nr\.\s*nota\s+Folha\s+Data\s+preg[aã]o\s*\n\s*(\d+)\s+(\d+)\s+(\d{2}/\d{2}/\d{4})",
                    text,
                    re.IGNORECASE
                )

                num_nota_encontrado = None
                folha = "1"
                data_str = None

                if header_multiline:
                    num_nota_encontrado = header_multiline.group(1)
                    folha = header_multiline.group(2)
                    data_str = header_multiline.group(3)
                else:
                    num_match = re.search(r"(?:Nr\.|N[úu]mero|Nº)\s*(?:da)?\s*nota[:\s]*(\d+)", text, re.IGNORECASE)
                    data_match = re.search(r"Data\s*(?:do)?\s*preg[aã]o[:\s]*(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
                    folha_match = re.search(r"Folha[:\s]*(\d+)", text, re.IGNORECASE)

                    if num_match:
                        num_nota_encontrado = num_match.group(1)
                    if data_match:
                        data_str = data_match.group(1)
                    if folha_match:
                        folha = folha_match.group(1)

                data_pregao = datetime.strptime(data_str, "%d/%m/%Y").date() if data_str else None

                # 2. Decisão: É uma nova nota ou continuação da nota atual?
                # Se não encontramos um número explícito de nota, assume-se continuação da página anterior
                # para evitar que páginas com taxas fiquem isoladas em notas separadas.
                is_nova_nota = False
                if nota_atual is None:
                    is_nova_nota = True
                elif num_nota_encontrado is not None and num_nota_encontrado != nota_atual.numero_nota:
                    is_nova_nota = True

                if is_nova_nota:
                    num_nota = num_nota_encontrado or f"nota_{page_idx+1}"
                    corretora = "BANCO INTER DTVM" if "INTER" in text.upper() else "B3 / SINACOR"

                    cli_match = re.search(r"Nome\s*(?:do\s*Cliente)?:\s*([^\n\r]+?)(?=\s*C\.P\.F|\n|$)", text, re.IGNORECASE)
                    nome_cliente = cli_match.group(1).strip() if cli_match else ""

                    cpf_match = re.search(r"(?:C\.P\.F\./C\.N\.P\.J\.|CPF/CNPJ):\s*([\d\.\-\/]+)", text, re.IGNORECASE)
                    cpf_cnpj = cpf_match.group(1).strip() if cpf_match else ""

                    nota_atual = NotaCorretagem(
                        numero_nota=num_nota,
                        folha=folha,
                        data_pregao=data_pregao,
                        corretora=corretora,
                        nome_cliente=nome_cliente,
                        cpf_cnpj=cpf_cnpj
                    )
                    notas.append(nota_atual)
                else:
                    # Se for continuação e faltou a data na folha 2, preserva da página 1
                    if nota_atual.data_pregao is None and data_pregao is not None:
                        nota_atual.data_pregao = data_pregao

                # 3. Extrai operações desta página
                self._extrair_operacoes(text, nota_atual)

                # 4. Extrai taxas e custos desta página
                self._extrair_custos(text, nota_atual)

        return notas

    def _extrair_operacoes(self, text: str, nota: NotaCorretagem):
        """Varre o texto linha por linha para identificar transações."""
        linhas = text.split("\n")
        in_negocios = False

        for linha in linhas:
            linha_strip = linha.strip()

            if re.search(r"neg[oó]cios\s+realizados", linha_strip, re.IGNORECASE) or (
                "negocia" in linha_strip.lower() and "tipo mercado" in linha_strip.lower()
            ):
                in_negocios = True
                continue

            if in_negocios and re.search(r"resumo\s+dos\s+neg[oó]cios|resumo\s+financeiro", linha_strip, re.IGNORECASE):
                in_negocios = False
                break

            if not in_negocios:
                if not re.search(r"bovespa\s+[CV]\s+", linha_strip, re.IGNORECASE):
                    continue

            match_op = self.OPERACAO_REGEX.match(linha_strip)
            if not match_op:
                continue

            negociacao = match_op.group("negociacao")
            tipo_op = match_op.group("tipo_op").upper()
            tipo_mercado = match_op.group("tipo_mercado").upper()
            resto = match_op.group("resto_linha").strip()

            match_val = self.VALORES_FINAIS_REGEX.match(resto)
            if match_val:
                especificacao = match_val.group("especificacao").strip()
                obs = match_val.group("obs") or ""
                qtd_str = match_val.group("qtd").replace(".", "")
                preco_str = match_val.group("preco")
                valor_str = match_val.group("valor")
                dc = match_val.group("dc").upper()

                ticker = extrair_ticker(especificacao)
                is_day_trade = (obs == "D")
                idx_op = len(nota.operacoes) + 1

                op = ItemOperacao(
                    ordem=idx_op,
                    negociacao=negociacao,
                    tipo_operacao=tipo_op,
                    tipo_mercado=tipo_mercado,
                    especificacao_titulo=especificacao,
                    ticker=ticker,
                    observacao=obs,
                    quantidade=int(qtd_str),
                    preco_unitario=parse_ptbr_float(preco_str),
                    valor_total=parse_ptbr_float(valor_str),
                    debito_credito=dc,
                    is_day_trade=is_day_trade
                )
                nota.operacoes.append(op)

    def _extrair_custos(self, text: str, nota: NotaCorretagem):
        """Extrai taxas e valores financeiros da nota com padrões abrangentes."""
        custos = nota.custos

        # Padrões flexíveis (com ou sem R$, dois pontos, acentos ou variações de texto)
        patterns = [
            ("taxa_liquidacao", r"Taxa\s*(?:de)?\s*liquida[cç][aã]o[:\s]*(?:R\$\s*)?([\d\.]+,\d{2})"),
            ("taxa_registro", r"Taxa\s*(?:de)?\s*Registro[:\s]*(?:R\$\s*)?([\d\.]+,\d{2})"),
            ("emolumentos", r"Emolumentos[:\s]*(?:R\$\s*)?([\d\.]+,\d{2})"),
            ("taxa_termo_opcoes", r"Taxa\s*(?:de)?\s*termo/op[cç][oõ]es[:\s]*(?:R\$\s*)?([\d\.]+,\d{2})"),
            ("taxa_ana", r"Taxa\s*A\.?N\.?A\.?[:\s]*(?:R\$\s*)?([\d\.]+,\d{2})"),
            ("corretagem", r"Corretagem(?:\s*/\s*Despesas)?[:\s]*(?:R\$\s*)?([\d\.]+,\d{2})"),
            ("iss", r"ISS(?:\s*/\s*Impostos)?[:\s]*(?:R\$\s*)?([\d\.]+,\d{2})"),
            ("irrf", r"I\.?R\.?R\.?F\.?.*?[:\s]*(?:R\$\s*)?([\d\.]+,\d{2})"),
            ("outras_bovespa", r"Outras\s*(?:Bovespa)?[:\s]*(?:R\$\s*)?([\d\.]+,\d{2})"),
        ]

        for field_name, regex in patterns:
            match = re.search(regex, text, re.IGNORECASE)
            if match:
                valor = parse_ptbr_float(match.group(1))
                if valor > 0:
                    setattr(custos, field_name, valor)

        # Total explícito de custos (se houver linhas como "Total Custos / Despesas" ou "Total CBLC + Bolsa")
        total_match = re.search(r"Total\s*(?:Custos|Despesas|Custos\s*/\s*Despesas)[:\s]*(?:R\$\s*)?([\d\.]+,\d{2})", text, re.IGNORECASE)
        if total_match:
            custos.total_custos = parse_ptbr_float(total_match.group(1))

        # Sempre garante que total_custos seja ao menos a soma das taxas individuais encontradas
        soma_taxas = round(
            custos.taxa_liquidacao + custos.taxa_registro + custos.emolumentos +
            custos.corretagem + custos.iss + custos.outras_bovespa +
            custos.taxa_termo_opcoes + custos.taxa_ana,
            2
        )
        if soma_taxas > custos.total_custos:
            custos.total_custos = soma_taxas

        # Valor líquido das operações
        val_op_match = re.search(r"Valor\s*l[ií]quido\s*das\s*opera[cç][oõ]es[:\s]*(?:R\$\s*)?([\d\.]+,\d{2})", text, re.IGNORECASE)
        if val_op_match:
            nota.valor_liquido_operacoes = parse_ptbr_float(val_op_match.group(1))

        # Líquido final da nota
        liq_match = re.search(r"L[ií]quido\s*para\s+\d{2}/\d{2}/\d{4}[:\s]*(?:R\$\s*)?([\d\.]+,\d{2})", text, re.IGNORECASE)
        if liq_match:
            nota.valor_liquido_nota = parse_ptbr_float(liq_match.group(1))
