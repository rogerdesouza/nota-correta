"""Interface local portátil (servidor web embutido usando apenas a biblioteca padrão do Python).
Não requer instalação de navegadores especiais, nem bibliotecas gráficas do sistema (como tkinter).
Abre automaticamente no navegador padrão do usuário.
"""
import os
import io
import json
import socket
import tempfile
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

from src.parser import SinacorParser
from src.calculator import CalculadoraNota
from src.exporter import exportar_relatorio_completo_csv

HTML_CONTENT = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nota Correta - Extrator de Notas de Corretagem</title>
  <style>
    :root {
      --primary: #ff7900;
      --primary-hover: #e06b00;
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --success: #10b981;
      --danger: #ef4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text);
      padding: 2rem 1rem;
      min-height: 100vh;
    }
    .container {
      max-width: 1150px;
      margin: 0 auto;
    }
    header {
      text-align: center;
      margin-bottom: 2rem;
    }
    h1 {
      font-size: 2rem;
      font-weight: 700;
      color: var(--text);
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
    }
    h1 span { color: var(--primary); }
    p.subtitle {
      color: var(--text-muted);
      margin-top: 0.5rem;
      font-size: 0.95rem;
    }
    .upload-card {
      background-color: var(--card-bg);
      border: 2px dashed var(--card-border);
      border-radius: 12px;
      padding: 2.5rem 1.5rem;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s ease;
      margin-bottom: 2rem;
    }
    .upload-card:hover, .upload-card.dragover {
      border-color: var(--primary);
      background-color: rgba(255, 121, 0, 0.05);
    }
    .upload-icon {
      font-size: 2.5rem;
      margin-bottom: 0.75rem;
    }
    .btn {
      background-color: var(--primary);
      color: white;
      border: none;
      padding: 0.7rem 1.5rem;
      border-radius: 8px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      transition: background 0.2s;
    }
    .btn:hover { background-color: var(--primary-hover); }
    .btn-secondary {
      background-color: #475569;
    }
    .btn-secondary:hover { background-color: #64748b; }
    .btn-group {
      display: flex;
      gap: 1rem;
      justify-content: center;
      margin-top: 1rem;
    }
    .section-title {
      font-size: 1.25rem;
      font-weight: 600;
      margin: 1.5rem 0 0.75rem 0;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: #e2e8f0;
    }
    .table-container {
      background-color: var(--card-bg);
      border-radius: 10px;
      border: 1px solid var(--card-border);
      overflow-x: auto;
      margin-bottom: 1.5rem;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      text-align: left;
    }
    th {
      background-color: #0f172a;
      color: var(--text-muted);
      padding: 0.65rem 0.6rem;
      font-weight: 600;
      border-bottom: 1px solid var(--card-border);
      white-space: nowrap;
    }
    td {
      padding: 0.65rem 0.6rem;
      border-bottom: 1px solid #293548;
      white-space: nowrap;
    }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background-color: rgba(255, 255, 255, 0.02); }
    .badge {
      display: inline-block;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
    }
    .badge-compra { background-color: rgba(16, 185, 129, 0.2); color: #34d399; }
    .badge-venda { background-color: rgba(239, 68, 68, 0.2); color: #f87171; }
    .badge-fii { background-color: rgba(59, 130, 246, 0.2); color: #60a5fa; }
    .badge-acao { background-color: rgba(168, 85, 247, 0.2); color: #c084fc; }
    .badge-swing { background-color: #334155; color: #cbd5e1; }
    .badge-day { background-color: rgba(245, 158, 11, 0.2); color: #fbbf24; }
    .loading {
      display: none;
      text-align: center;
      margin: 1.5rem 0;
      color: var(--text-muted);
    }
    .spinner {
      border: 3px solid rgba(255,255,255,0.1);
      border-top: 3px solid var(--primary);
      border-radius: 50%;
      width: 24px;
      height: 24px;
      animation: spin 0.8s linear infinite;
      margin: 0 auto 0.5rem auto;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1><span>Nota</span>Correta</h1>
      <p class="subtitle">Extrator portátil de Notas de Corretagem B3 / SINACOR com segregação de Swing & Day Trade</p>
    </header>

    <div class="upload-card" id="drop-zone" onclick="document.getElementById('file-input').click()">
      <div class="upload-icon">📄</div>
      <h3>Clique ou arraste o PDF da sua Nota de Corretagem aqui</h3>
      <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.3rem;">Suporta padrão Banco Inter e corretoras SINACOR</p>
      <input type="file" id="file-input" accept="application/pdf" style="display: none" onchange="handleFileSelect(event)">
    </div>

    <div class="loading" id="loading">
      <div class="spinner"></div>
      Processando nota de corretagem...
    </div>

    <div id="results" style="display: none;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h2 style="font-size: 1.3rem;">Resultado da Extração</h2>
        <button class="btn" onclick="downloadCSV()">⬇ Baixar Relatório em CSV</button>
      </div>

      <div class="section-title">📊 Resumo Consolidado por Modalidade</div>
      <div class="table-container">
        <table id="modalidades-table">
          <thead>
            <tr>
              <th>Modalidade</th>
              <th>Qtd Ops</th>
              <th>Total Compras</th>
              <th>Total Vendas</th>
              <th>Volume Total</th>
              <th>Resultado Bruto</th>
              <th>Taxas Rateadas</th>
              <th>Resultado Líquido</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>

      <div class="section-title">💼 Consolidado por Ativo</div>
      <div class="table-container">
        <table id="ativos-table">
          <thead>
            <tr>
              <th>Ativo</th>
              <th>Data</th>
              <th>Tipo</th>
              <th>Qtd</th>
              <th>Preço Médio</th>
              <th>Modalidade</th>
              <th>Custos</th>
              <th>Operação</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>

      <div class="btn-group">
        <button class="btn" onclick="downloadCSV()">⬇ Baixar CSV Formatado</button>
        <button class="btn btn-secondary" onclick="resetForm()">Novo Arquivo</button>
      </div>
    </div>
  </div>

  <script>
    let currentData = null;

    const dropZone = document.getElementById('drop-zone');
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => { dropZone.classList.remove('dragover'); });
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        processFile(e.dataTransfer.files[0]);
      }
    });

    function handleFileSelect(e) {
      if (e.target.files.length > 0) {
        processFile(e.target.files[0]);
      }
    }

    async function processFile(file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Por favor, selecione um arquivo PDF de nota de corretagem.');
        return;
      }
      document.getElementById('loading').style.display = 'block';
      document.getElementById('results').style.display = 'none';

      const formData = new FormData();
      formData.append('pdf', file);

      try {
        const response = await fetch('/api/process', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        if (data.error) {
          alert('Erro ao processar PDF: ' + data.error);
        } else {
          currentData = data;
          renderTables(data);
          document.getElementById('results').style.display = 'block';
        }
      } catch (err) {
        alert('Falha na comunicação com o servidor local: ' + err.message);
      } finally {
        document.getElementById('loading').style.display = 'none';
      }
    }

    function renderTables(data) {
      // Modalidades
      const modBody = document.querySelector('#modalidades-table tbody');
      modBody.innerHTML = '';
      data.modalidades.forEach(m => {
        const tr = document.createElement('tr');
        const resBruto = m.resultado_bruto ? (m.resultado_bruto.startsWith('-') ? `<span style="color:#ef4444; font-weight:600;">R$ ${m.resultado_bruto}</span>` : `<span style="color:#10b981; font-weight:600;">R$ ${m.resultado_bruto}</span>`) : '-';
        const resLiq = m.resultado_liquido ? (m.resultado_liquido.startsWith('-') ? `<span style="color:#ef4444; font-weight:600;">R$ ${m.resultado_liquido}</span>` : `<span style="color:#10b981; font-weight:600;">R$ ${m.resultado_liquido}</span>`) : '-';
        tr.innerHTML = `
          <td><span class="badge ${m.modalidade === 'Day Trade' ? 'badge-day' : 'badge-swing'}">${m.modalidade}</span></td>
          <td>${m.qtd_ops}</td>
          <td>R$ ${m.total_compras}</td>
          <td>R$ ${m.total_vendas}</td>
          <td>R$ ${m.volume_total}</td>
          <td>${resBruto}</td>
          <td>R$ ${m.taxas_rateadas}</td>
          <td>${resLiq}</td>
        `;
        modBody.appendChild(tr);
      });

      // Ativos
      const atvBody = document.querySelector('#ativos-table tbody');
      atvBody.innerHTML = '';
      data.ativos.forEach(a => {
        const tr = document.createElement('tr');
        const opBadge = a.operacao === 'C' ? 'badge-compra' : 'badge-venda';
        const tipoBadge = a.tipo === 'F' ? 'badge-fii' : 'badge-acao';
        const modBadge = (a.modalidade === 'D' || a.modalidade === 'Day') ? 'badge-day' : 'badge-swing';

        tr.innerHTML = `
          <td><strong>${a.ativo}</strong></td>
          <td>${a.data}</td>
          <td><span class="badge ${tipoBadge}">${a.tipo}</span></td>
          <td>${a.qtd}</td>
          <td>${a.preco_medio}</td>
          <td><span class="badge ${modBadge}">${a.modalidade}</span></td>
          <td>${a.custos}</td>
          <td><span class="badge ${opBadge}">${a.operacao}</span></td>
        `;
        atvBody.appendChild(tr);
      });
    }

    function downloadCSV() {
      window.location.href = '/api/download-csv';
    }

    function resetForm() {
      document.getElementById('file-input').value = '';
      document.getElementById('results').style.display = 'none';
      currentData = null;
    }
  </script>
</body>
</html>
"""

class NotaCorretaHandler(BaseHTTPRequestHandler):
    """Manipulador de requisições HTTP locais."""
    resultados_em_memoria = []

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
        elif self.path == "/api/download-csv":
            if not self.resultados_em_memoria:
                self.send_error(404, "Nenhum dado processado.")
                return

            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
                tmp_path = tmp.name

            try:
                exportar_relatorio_completo_csv(self.resultados_em_memoria, tmp_path)
                with open(tmp_path, "rb") as f:
                    csv_bytes = f.read()

                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="relatorio_notas_corretagem.csv"')
                self.send_header("Content-Length", str(len(csv_bytes)))
                self.end_headers()
                self.wfile.write(csv_bytes)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        else:
            self.send_error(404, "Recurso não encontrado.")

    def do_POST(self):
        if self.path == "/api/process":
            content_type = self.headers.get("Content-Type", "")
            if not content_type.startswith("multipart/form-data"):
                self.send_error(400, "Content-Type deve ser multipart/form-data")
                return

            # Extração simples de multipart
            boundary = content_type.split("boundary=")[1].encode()
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            parts = body.split(b"--" + boundary)
            pdf_bytes = None
            for part in parts:
                if b'filename="' in part:
                    header_part, file_data = part.split(b"\r\n\r\n", 1)
                    # Remover \r\n final
                    if file_data.endswith(b"\r\n"):
                        file_data = file_data[:-2]
                    pdf_bytes = file_data
                    break

            if not pdf_bytes:
                self._send_json({"error": "Nenhum arquivo PDF encontrado no envio."}, 400)
                return

            # Salva PDF temporário para processamento com pdfplumber
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
                tmp_pdf.write(pdf_bytes)
                tmp_pdf_path = tmp_pdf.name

            try:
                parser = SinacorParser()
                calc = CalculadoraNota()
                notas = parser.parse_pdf(tmp_pdf_path)
                resultados = calc.processar_notas(notas)
                NotaCorretaHandler.resultados_em_memoria = resultados

                # Formata resposta JSON para o frontend
                resp_modalidades = []
                resp_ativos = []

                for res in resultados:
                    data_str = res.data_pregao.strftime("%d/%m/%Y") if res.data_pregao else ""

                    if res.swing_trade.volume_total > 0:
                        st = res.swing_trade
                        resp_modalidades.append({
                            "modalidade": "Swing Trade",
                            "qtd_ops": len(st.operacoes) or "-",
                            "total_compras": f"{st.total_compras:.2f}".replace(".", ","),
                            "total_vendas": f"{st.total_vendas:.2f}".replace(".", ","),
                            "volume_total": f"{st.volume_total:.2f}".replace(".", ","),
                            "resultado_bruto": None,
                            "taxas_rateadas": f"{st.taxas_proporcionais:.2f}".replace(".", ","),
                            "resultado_liquido": None
                        })

                    if res.day_trade.volume_total > 0:
                        dt = res.day_trade
                        res_bruto_dt_str = f"{dt.resultado_bruto:.2f}".replace(".", ",") if dt.resultado_bruto is not None else None
                        res_liq_dt_str = f"{dt.resultado_liquido:.2f}".replace(".", ",") if dt.resultado_liquido is not None else None
                        resp_modalidades.append({
                            "modalidade": "Day Trade",
                            "qtd_ops": len(dt.operacoes) or "-",
                            "total_compras": f"{dt.total_compras:.2f}".replace(".", ","),
                            "total_vendas": f"{dt.total_vendas:.2f}".replace(".", ","),
                            "volume_total": f"{dt.volume_total:.2f}".replace(".", ","),
                            "resultado_bruto": res_bruto_dt_str,
                            "taxas_rateadas": f"{dt.taxas_proporcionais:.2f}".replace(".", ","),
                            "resultado_liquido": res_liq_dt_str
                        })

                    for atv in res.consolidados_ativos:
                        data_atv_str = atv.data.strftime("%d/%m/%Y") if atv.data else ""
                        resp_ativos.append({
                            "operacao": atv.operacao,
                            "ativo": atv.ativo,
                            "data": data_atv_str,
                            "tipo": atv.tipo,
                            "qtd": atv.qtd,
                            "preco_medio": f"{atv.preco_medio:.4f}".replace(".", ","),
                            "modalidade": atv.modalidade,
                            "custos": f"{atv.custos:.2f}".replace(".", ",")
                        })

                self._send_json({
                    "modalidades": resp_modalidades,
                    "ativos": resp_ativos
                })
            except Exception as e:
                self._send_json({"error": str(e)}, 500)
            finally:
                if os.path.exists(tmp_pdf_path):
                    os.remove(tmp_pdf_path)
        else:
            self.send_error(404, "Endpoint não encontrado")

    def _send_json(self, data: dict, status_code: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Desativa logs verbosos no terminal
        pass

def find_free_port() -> int:
    """Encontra uma porta TCP livre no sistema."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

def iniciar_servidor_local(open_browser: bool = True):
    """Inicia o servidor web local e abre a interface no navegador padrão."""
    port = find_free_port()
    server = HTTPServer(("127.0.0.1", port), NotaCorretaHandler)
    url = f"http://127.0.0.1:{port}"
    print(f"\n=======================================================")
    print(f"🚀 NotaCorreta App em execução!")
    print(f"🔗 Acesse no seu navegador: {url}")
    print(f"Pressione Ctrl+C no terminal para encerrar.")
    print(f"=======================================================\n")

    if open_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
        server.server_close()

