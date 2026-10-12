"""Modelos de dados para Notas de Corretagem (Padrão SINACOR / B3).
"""
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

@dataclass
class ItemOperacao:
    """Representa uma linha individual de operação de compra ou venda."""
    ordem: int
    negociacao: str              # ex: 1-BOVESPA
    tipo_operacao: str           # 'C' (Compra) ou 'V' (Venda)
    tipo_mercado: str            # VISTA, FRACIONARIO, OPCAO, etc.
    especificacao_titulo: str    # Descrição completa (ex: PETR4 PN N2)
    ticker: str                  # Código extraído (ex: PETR4)
    observacao: str              # 'D' para Day Trade, vazio para Swing Trade
    quantidade: int              # Quantidade negociada
    preco_unitario: float        # Preço por unidade
    valor_total: float           # Valor da operação (qtd * preco)
    debito_credito: str          # 'D' (Débito) ou 'C' (Crédito)
    is_day_trade: bool = False

@dataclass
class ResumoCustos:
    """Taxas e custos operacionais da nota."""
    taxa_liquidacao: float = 0.0
    taxa_registro: float = 0.0
    emolumentos: float = 0.0
    taxa_termo_opcoes: float = 0.0
    taxa_ana: float = 0.0
    corretagem: float = 0.0
    iss: float = 0.0
    irrf: float = 0.0
    outras_bovespa: float = 0.0
    total_custos: float = 0.0

@dataclass
class ResumoModalidade:
    """Consolidado de operações por modalidade (Swing Trade ou Day Trade)."""
    modalidade: str                          # 'Swing Trade' ou 'Day Trade'
    operacoes: list = field(default_factory=list)
    total_compras: float = 0.0
    total_vendas: float = 0.0
    volume_total: float = 0.0
    resultado_bruto: Optional[float] = None
    taxas_proporcionais: float = 0.0
    resultado_liquido: Optional[float] = None

@dataclass
class ConsolidadoAtivo:
    """Consolidação por ativo e tipo de operação."""
    operacao: str                # 'C' ou 'V'
    ativo: str                   # Ticker (ex: PETR4, MXRF11)
    data: Optional[date]         # Data do pregão
    tipo: str                    # 'F' para FIIs ou 'A' para Ações
    qtd: int                     # Quantidade negociada
    preco_medio: float           # Preço médio ponderado
    modalidade: str              # 'Swing' ou 'Day'
    custos: float                # Rateio proporcional de custos

@dataclass
class ResultadoCalculoNota:
    """Resultado processado e segregado da nota de corretagem."""
    numero_nota: str
    data_pregao: Optional[date]
    corretora: str
    swing_trade: ResumoModalidade = field(default_factory=lambda: ResumoModalidade(modalidade="Swing Trade"))
    day_trade: ResumoModalidade = field(default_factory=lambda: ResumoModalidade(modalidade="Day Trade"))
    consolidados_ativos: List[ConsolidadoAtivo] = field(default_factory=list)
    total_custos_nota: float = 0.0
    valor_liquido_nota: float = 0.0

@dataclass
class NotaCorretagem:
    """Representa uma nota de corretagem completa."""
    numero_nota: str
    folha: str
    data_pregao: Optional[date]
    corretora: str
    nome_cliente: str = ""
    cpf_cnpj: str = ""
    operacoes: List[ItemOperacao] = field(default_factory=list)
    custos: ResumoCustos = field(default_factory=ResumoCustos)
    valor_liquido_operacoes: float = 0.0
    valor_liquido_nota: float = 0.0

