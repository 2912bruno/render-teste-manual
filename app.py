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

# --- NOVA ROTA: RELATÓRIO DO CLIENTE ---
# Agora, o endereço vai incluir o código do cliente. Ex: /cliente/4
@app.route("/cliente/<codigo_cliente>")
def relatorio_cliente(codigo_cliente):
    try:
        # 1. Autentica no Google
        client = autenticar_google_sheets()

        # 2. Abre a planilha "CONTROLE CENTRAL"
        sheet = client.open("CONTROLE CENTRAL").sheet1

        # 3. Encontra a linha que corresponde ao código do cliente
        # O 'find' procura na primeira coluna (col=1) pelo código que recebemos
        celula = sheet.find(codigo_cliente, in_column=1)

        if celula is None:
            return f"<h1>Cliente com código {codigo_cliente} não encontrado.</h1>"

        # 4. Pega os dados da linha encontrada
        linha_dados = sheet.row_values(celula.row)
        
        # Pega os dados específicos que queremos (lembre-se que a contagem começa em 0)
        # Coluna A (Código) = linha_dados[0]
        # Coluna B (Razão Social) = linha_dados[1]
        # Coluna C (Status) = linha_dados[2]
        # Coluna E (CNPJ) = linha_dados[4]
        
        razao_social = linha_dados[1]
        status = linha_dados[2]
        cnpj = linha_dados[4]

        # 5. Monta e exibe o relatório em HTML
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

# Rota principal para dar uma instrução ao usuário
@app.route("/")
def index():
    return "<h1>Serviço de Relatórios Ativo</h1><p>Para ver um relatório, acesse na URL: /cliente/SEU_CODIGO</p><p>Exemplo: /cliente/4</p>"

# --- INICIA O SERVIDOR (Não precisa mexer aqui) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
