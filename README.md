# NotaCorreta 📊

Extrator e consolidador portátil em Python para notas de corretagem (padrão B3 / SINACOR - Banco Inter e outras corretoras), com segregação automática de modalidades (**Swing Trade** vs **Day Trade**), cálculo de resultado bruto, rateio exato de taxas e emolumentos da B3, consolidação por ativo com preço médio a 4 casas decimais e exportação para CSV.

---

## 🌟 Funcionalidades

- **100% Offline e Privado:** Suas notas são processadas em memória e nunca saem do seu computador ou são enviadas para a nuvem.
- **Segregação Day Trade vs Swing Trade:**
  - Identifica compras e vendas do mesmo ativo no mesmo dia (Day Trade).
  - Trata sobras parciais e operações puras como Swing Trade.
  - Rateia as taxas da B3 proporcionalmente ao volume financeiro.
- **Resumo Consolidado com Resultado:**
  - Tabela consolidada com `Total Compras`, `Total Vendas`, `Volume Total`, `Resultado Bruto`, `Taxas Rateadas` e `Resultado Líquido` (Day Trade).
- **Consolidado por Ativo:**
  - Tabela com colunas: `Ativo`, `Data`, `Tipo` (`A` para Ações, `F` para FIIs), `Qtd`, `Preço Médio` (4 casas decimais), `Modalidade` (`D` ou `S`), `Custos` e `Operação` (`C` ou `V`).
- **Interface Gráfica Embutida:** Arraste e solte o PDF no navegador sem precisar de dependências visuais complexas.
- **Suporte a CLI:** Modo terminal direto para automações e scripts.

---

## 🚀 Como Usar

### 1. Interface Web Local (Recomendado)
Execute sem argumentos:
```bash
./dist/nota-correta
# ou via código fonte:
python3 src/main.py
```
O aplicativo abrirá automaticamente no seu navegador padrão (`http://127.0.0.1:<porta>`). Arraste suas notas em PDF e clique em **"Baixar Relatório em CSV"**.

### 2. Linha de Comando (CLI)
Para processar arquivos via terminal diretamente:
```bash
./dist/nota-correta caminho/para/nota.pdf -o resultado.csv
# ou via código fonte:
python3 src/main.py caminho/para/nota.pdf -o resultado.csv
```

---

## 📋 Estrutura do CSV Gerado

O arquivo CSV utiliza delimitador `;` e codificação `UTF-8 com BOM` (abertura direta no Excel e LibreOffice Calc sem caracteres quebrados):

```csv
=== RESUMO CONSOLIDADO POR MODALIDADE ===
Modalidade;Qtd Operações;Total Compras (R$);Total Vendas (R$);Volume Total (R$);Resultado Bruto (R$);Taxas Rateadas (R$);Resultado Líquido (R$)

=== CONSOLIDADO POR ATIVO ===
Ativo;Data;Tipo;Qtd;Preço Médio;Modalidade;Custos;Operação
```

---

## 🛠️ Desenvolvimento e Compilação

### Pré-requisitos
- Python 3.10+
- Dependências:
  ```bash
  pip install -r requirements.txt
  ```

### Gerar Executável Portátil (Single Binary)
Para compilar um binário executável único usando PyInstaller:
```bash
./build.sh
```
O binário será gerado na pasta `dist/nota-correta`.
