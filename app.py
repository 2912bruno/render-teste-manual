import os
import json
from flask import Flask
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURAÇÃO ---
# O Flask vai ser nosso servidor web
app = Flask(__name__)

# Função para autenticar no Google Sheets
def autenticar_google_sheets():
    # Define o escopo da API - o que queremos acessar
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    # Pega as credenciais do "cofre" do Render
    creds_json_str = os.environ.get('GOOGLE_CREDENTIALS_JSON' )
    creds_json = json.loads(creds_json_str)

    # Autoriza o acesso usando as credenciais
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    return client

# --- ROTA PRINCIPAL (O que o site vai mostrar) ---
@app.route("/")
def ler_planilha():
    try:
        # 1. Autentica no Google
        client = autenticar_google_sheets()

        # 2. Abre a planilha pelo NOME
        # !!! MUITO IMPORTANTE: Altere "NOME_DA_SUA_PLANILHA" para o nome exato da sua planilha no Google Drive !!!
        sheet = client.open("CONTROLE CENTRAL").sheet1

        # 3. Lê o valor da célula A1
        valor_celula_a1 = sheet.acell('A1').value

        # 4. Exibe o valor na página
        return f"<h1>O valor da célula A1 da minha planilha é: {valor_celula_a1}</h1>"

    except Exception as e:
        # Se der algum erro, mostra o erro na tela para sabermos o que aconteceu
        return f"<h1>Ocorreu um erro:</h1><p>{e}</p>"

# --- INICIA O SERVIDOR (Não precisa mexer aqui) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
