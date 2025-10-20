import os
import json
from flask import Flask, render_template, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from collections import Counter

# --- CONFIGURAÇÃO ---
# Adicionamos a pasta 'templates' para o Flask saber onde procurar o index.html
app = Flask(__name__, template_folder='templates')

# Função para autenticar (a mesma de antes)
def autenticar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds_json_str = os.environ.get('GOOGLE_CREDENTIALS_JSON' )
    creds_json = json.loads(creds_json_str)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    return client

# --- ROTAS DA APLICAÇÃO ---

# Rota principal: agora ela vai renderizar nossa página HTML
@app.route("/")
def dashboard():
    # O Flask vai procurar por 'index.html' na pasta 'templates' e exibi-lo
    return render_template('index.html')

# Nova rota de API: ela vai fornecer todos os dados para o nosso frontend
@app.route("/api/dados")
def api_dados():
    try:
        client = autenticar_google_sheets()
        sheet = client.open("CONTROLE CENTRAL").sheet1

        # Pega TODOS os registros da planilha, exceto o cabeçalho
        todos_os_dados = sheet.get_all_records()

        # --- Processa os dados para os KPIs ---
        total_clientes = len(todos_os_dados)
        
        # Conta a frequência de cada item nas colunas de Status e Regime
        contador_status = Counter(d['STATUS'] for d in todos_os_dados)
        contador_regime = Counter(d['REGIME TRIBUTÁRIO'] for d in todos_os_dados)

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
        
        # Monta o pacote de dados final
        pacote_final = {
            "kpis": {
                "total_clientes": total_clientes,
                "status": dict(contador_status),
                "regime": dict(contador_regime)
            },
            "clientes": clientes_formatados
        }

        # Retorna os dados no formato JSON, que o JavaScript entende
        return jsonify(pacote_final)

    except Exception as e:
        # Em caso de erro, retorna um JSON com a mensagem de erro
        return jsonify({"erro": str(e)}), 500

# --- INICIA O SERVIDOR ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
