import os
import json
from flask import Flask
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURAÇÃO ---
app = Flask(__name__)

# Função para autenticar (a mesma de antes, sem alterações)
def autenticar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds_json_str = os.environ.get('GOOGLE_CREDENTIALS_JSON' )
    creds_json = json.loads(creds_json_str)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    return client

# --- ROTA: RELATÓRIO DO CLIENTE ---
@app.route("/cliente/<codigo_cliente>")
def relatorio_cliente(codigo_cliente):
    try:
        client = autenticar_google_sheets()
        sheet = client.open("CONTROLE CENTRAL").sheet1
        celula = sheet.find(codigo_cliente, in_column=1)

        if celula is None:
            return f"<h1>Cliente com código {codigo_cliente} não encontrado.</h1>"

        linha_dados = sheet.row_values(celula.row)
        
        razao_social = linha_dados[1]
        status = linha_dados[2]
        cnpj = linha_dados[4]

        html_relatorio = f"""
        <h1>Relatório do Cliente</h1>
        <p><strong>Código:</strong> {codigo_cliente}</p>
        <p><strong>Razão Social:</strong> {razao_social}</p>
        <p><strong>CNPJ:</strong> {cnpj}</p>
        <p><strong>Status:</strong> {status}</p>
        """
        return html_relatorio

    except Exception as e:
        return f"<h1>Ocorreu um erro:</h1><p>{e}</p>"

# Rota principal para dar uma instrução
@app.route("/")
def index():
    return "<h1>Serviço de Relatórios Ativo</h1><p>Para ver um relatório, acesse na URL: /cliente/SEU_CODIGO</p>"

# --- INICIA O SERVIDOR ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
