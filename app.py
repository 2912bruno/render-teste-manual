import os
import json
from flask import Flask, render_template, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from collections import Counter

# --- CONFIGURAÇÃO ---
app = Flask(__name__, template_folder='templates' )

# Função de autenticação (sem alterações)
def autenticar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds_json_str = os.environ.get('GOOGLE_CREDENTIALS_JSON' )
    creds_json = json.loads(creds_json_str)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    return client

# --- ROTAS DA APLICAÇÃO ---

@app.route("/")
def dashboard():
    return render_template('index.html')

@app.route("/api/dados")
def api_dados():
    try:
        client = autenticar_google_sheets()
        sheet = client.open("CONTROLE CENTRAL").sheet1
        
        # Pega todos os registros, o gspread já transforma os cabeçalhos em chaves
        todos_os_dados_brutos = sheet.get_all_records()

        # --- NOVO: Limpeza e Padronização dos Dados ---
        # Cria uma nova lista de dados com chaves limpas (sem espaços e em maiúsculas)
        todos_os_dados = []
        for linha_bruta in todos_os_dados_brutos:
            linha_limpa = {str(k).strip().upper(): v for k, v in linha_bruta.items()}
            todos_os_dados.append(linha_limpa)
        # -------------------------------------------

        # --- Processa os dados para os KPIs ---
        total_clientes = len(todos_os_dados)
        
        # Agora o código procura pelas chaves padronizadas (sempre em maiúsculas)
        contador_status = Counter(d.get('STATUS', 'N/A') for d in todos_os_dados)
        contador_regime = Counter(d.get('REGIME TRIBUTÁRIO', 'N/A') for d in todos_os_dados)

        # --- Formata os dados para a tabela ---
        clientes_formatados = []
        for linha in todos_os_dados:
            clientes_formatados.append({
                "codigo": linha.get('CÓDIGO', ''),
                "razao_social": linha.get('RAZÃO SOCIAL', ''),
                "status": linha.get('STATUS', ''),
                "regime": linha.get('REGIME TRIBUTÁRIO', ''),
                "segmento": linha.get('SEGMENTO', '')
            })
        
        pacote_final = {
            "kpis": {
                "total_clientes": total_clientes,
                "status": dict(contador_status),
                "regime": dict(contador_regime)
            },
            "clientes": clientes_formatados
        }

        return jsonify(pacote_final)

    except Exception as e:
        # Retorna um erro claro em JSON se algo der errado
        # Isso ajuda a diagnosticar problemas futuros
        return jsonify({"erro": f"Ocorreu uma exceção no servidor: {str(e)}"}), 500

# --- INICIA O SERVIDOR ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
