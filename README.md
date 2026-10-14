# NotaCorreta 📊

Extrator e consolidador portátil de notas de corretagem (padrão B3 / SINACOR - Banco Inter e outras corretoras), com segregação automática de modalidades (**Swing Trade** vs **Day Trade**), cálculo de resultado bruto, rateio exato de taxas e emolumentos da B3, consolidação por ativo com preço médio a 4 casas decimais e exportação para CSV.

**Zero Instalação • 100% Offline • Funciona em Qualquer Dispositivo (Windows, Mac, Linux, Celular)**

---

## 🌟 Funcionalidades

- **100% Offline e Privado:** Suas notas são lidas e processadas diretamente no seu navegador através do PDF.js (Mozilla). Nenhum dado sai do seu computador ou é enviado para servidores.
- **Portabilidade Total:** Roda em qualquer sistema operacional (Windows, macOS, Linux, iOS, Android) sem precisar instalar Python, dependências ou compiladores.
- **Segregação Day Trade vs Swing Trade (Regra RFB):**
  - Identifica compras e vendas do mesmo ativo no mesmo dia (Day Trade).
  - Trata sobras parciais e operações puras como Swing Trade.
  - Rateia as taxas da B3 proporcionalmente ao volume financeiro.
- **Resumo Consolidado com Resultado:**
  - Tabela com `Total Compras`, `Total Vendas`, `Volume Total`, `Resultado Bruto`, `Taxas Rateadas` e `Resultado Líquido` (Day Trade).
- **Consolidado por Ativo:**
  - Colunas: `Ativo`, `Data`, `Tipo` (`A` para Ações, `F` para FIIs), `Qtd`, `Preço Médio` (4 casas decimais), `Modalidade` (`D` ou `S`), `Custos` e `Operação` (`C` ou `V`).
- **Consolidado Day Trade:**
  - Agrupa os Day Trades de cada ativo no dia com colunas: `Ativo`, `Data`, `Tipo` (`A` ou `F`), `Qtd`, `PM Compra`, `PM Venda`, `Modalidade`, `Resultado Bruto`, `Custos` (soma compra + venda), `Resultado Líquido` e botão `📋 Copiar` para a área de transferência.
- **Exportação para CSV:**
  - Gera arquivo `.csv` formatado com `;` e `UTF-8 com BOM` para abertura imediata no Microsoft Excel e LibreOffice Calc.

---

## 🚀 Como Usar

### Opção 1: Uso Local (Basta dar 2 cliques)
1. Dê um duplo clique no arquivo [`index.html`](file:///home/roger/Documentos/pessoal/dev/nota-correta/index.html).
2. O aplicativo abrirá diretamente no seu navegador padrão (Google Chrome, Microsoft Edge, Firefox, Safari, etc.).
3. Arraste suas notas em PDF ou clique no botão para selecionar os arquivos.
4. Visualize as tabelas consolidadas e clique em **"Baixar CSV Consolidado"**.

---

### Opção 2: Acessar Online via GitHub Pages (Grátis)
Você pode usar o aplicativo de qualquer lugar (inclusive no celular) ativando o GitHub Pages no seu repositório:
1. Acesse o seu repositório no GitHub.
2. Vá em **Settings** > **Pages** (no menu lateral esquerdo).
3. Em **Branch**, selecione `main` e a pasta `/ (root)`.
4. Clique em **Save**.
5. Pronto! Em poucos instantes o seu extrator estará online no endereço:
   `https://seu-usuario.github.io/nota-correta/`

---

## 📋 Estrutura do CSV Exportado

```csv
=== RESUMO CONSOLIDADO POR MODALIDADE ===
Modalidade;Qtd Operações;Total Compras (R$);Total Vendas (R$);Volume Total (R$);Resultado Bruto (R$);Taxas Rateadas (R$);Resultado Líquido (R$)

=== CONSOLIDADO POR ATIVO ===
Ativo;Data;Tipo;Qtd;Preço Médio;Modalidade;Custos;Operação

=== CONSOLIDADO DAY TRADE ===
Ativo;Data;Tipo;Qtd;PM Compra;PM Venda;Modalidade;Resultado Bruto;Custos;Resultado Líquido
```
