from flask import Flask
import psutil
import requests
import socket
import platform

app = Flask(__name__)
# CONFIGURAÇÃO DA EQUIPE (Altere no GitHub para testar o CI/CD!)
EQUIPE = "Grupo 3"
INTEGRANTES = [
    "BRUNO ANTONIO DE SOUSA COSTA",
    "CAIO CESAR LIMA DINIZ",
    "GABRIEL MICHALSKI PAIVA"
]
STATUS_DEPLOY = "Pipeline CI/CD Ativo (Azure Cloud)"

def obter_conselho_devops():
    try:
        resposta = requests.get("https://api.adviceslip.com/advice", timeout=2)
        return resposta.json()['slip']['advice']
    except:
        return "Automatize tudo: se você precisa fazer algo mais de uma vez, escreva um script."

@app.route('/')
def home():
    # Coleta de métricas completas do Hardware via psutil e platform
    memoria = psutil.virtual_memory()
    disco = psutil.disk_usage('/')
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_cores_logicos = psutil.cpu_count(logical=True)
    cpu_cores_fisicos = psutil.cpu_count(logical=False) or cpu_cores_logicos
    
    ram_usada_gb = round(memoria.used / (1024 ** 3), 2)
    ram_total_gb = round(memoria.total / (1024 ** 3), 2)
    disco_usado_gb = round(disco.used / (1024 ** 3), 2)
    disco_total_gb = round(disco.total / (1024 ** 3), 2)

    hostname = socket.gethostname()
    arquitetura = platform.machine()
    sistema_op = f"{platform.system()} {platform.release()}"
    conselho = obter_conselho_devops()

    # Gera os cards dos integrantes dinamicamente
    badges_integrantes = "".join([
        f'<div class="member-badge"><span class="dot"></span>{nome}</div>'
        for nome in INTEGRANTES
    ])

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Infra Monitor - {EQUIPE}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-dark: #090d16;
                --glass-bg: rgba(255, 255, 255, 0.04);
                --glass-border: rgba(255, 255, 255, 0.1);
                --neon-cyan: #00f2fe;
                --neon-blue: #4facfe;
                --neon-green: #00e676;
                --neon-purple: #b537f2;
                --text-main: #f1f5f9;
                --text-muted: #94a3b8;
            }}

            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}

            body {{
                font-family: 'Inter', sans-serif;
                background: radial-gradient(circle at top right, #131c31, var(--bg-dark) 60%);
                color: var(--text-main);
                min-height: 100vh;
                padding: 40px 20px;
                display: flex;
                justify-content: center;
                align-items: center;
            }}

            .container {{
                max-width: 1000px;
                width: 100%;
            }}

            /* Cabeçalho e Card da Equipe */
            .header-card {{
                background: var(--glass-bg);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid var(--glass-border);
                border-radius: 20px;
                padding: 32px;
                margin-bottom: 24px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
                position: relative;
                overflow: hidden;
            }}

            .header-card::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 4px;
                background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple));
            }}

            .header-top {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 16px;
                margin-bottom: 20px;
            }}

            .title-group h1 {{
                font-size: 1.9rem;
                font-weight: 700;
                background: linear-gradient(90deg, #fff, var(--neon-cyan));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -0.5px;
            }}

            .title-group p {{
                color: var(--text-muted);
                font-size: 0.9rem;
                margin-top: 4px;
            }}

            .status-pill {{
                background: rgba(0, 230, 118, 0.1);
                border: 1px solid rgba(0, 230, 118, 0.35);
                color: var(--neon-green);
                padding: 8px 16px;
                border-radius: 999px;
                font-size: 0.8rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 8px;
                box-shadow: 0 0 15px rgba(0, 230, 118, 0.15);
            }}

            .pulse {{
                width: 8px;
                height: 8px;
                background: var(--neon-green);
                border-radius: 50%;
                box-shadow: 0 0 8px var(--neon-green);
            }}

            .team-section {{
                border-top: 1px solid var(--glass-border);
                padding-top: 20px;
            }}

            .team-label {{
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                color: var(--neon-cyan);
                margin-bottom: 12px;
                font-weight: 700;
            }}

            .members-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                gap: 12px;
            }}

            .member-badge {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.08);
                padding: 12px 16px;
                border-radius: 12px;
                font-size: 0.85rem;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 10px;
                letter-spacing: 0.3px;
            }}

            .member-badge .dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--neon-cyan), var(--neon-blue));
                box-shadow: 0 0 8px var(--neon-cyan);
                flex-shrink: 0;
            }}

            /* Grid de Telemetria do Hardware */
            .telemetry-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 20px;
                margin-bottom: 24px;
            }}

            .metric-card {{
                background: var(--glass-bg);
                backdrop-filter: blur(12px);
                border: 1px solid var(--glass-border);
                border-radius: 16px;
                padding: 22px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }}

            .metric-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                color: var(--text-muted);
                font-size: 0.85rem;
                font-weight: 600;
                margin-bottom: 12px;
            }}

            .metric-value {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 1.75rem;
                font-weight: 700;
                color: #fff;
                margin-bottom: 8px;
            }}

            .metric-sub {{
                font-size: 0.78rem;
                color: var(--text-muted);
            }}

            .progress-bar {{
                width: 100%;
                height: 8px;
                background: rgba(255, 255, 255, 0.08);
                border-radius: 999px;
                overflow: hidden;
                margin: 10px 0;
            }}

            .progress-fill {{
                height: 100%;
                border-radius: 999px;
                background: linear-gradient(90deg, var(--neon-cyan), var(--neon-blue));
                box-shadow: 0 0 10px var(--neon-cyan);
            }}

            /* Card de Conselho DevOps */
            .advice-card {{
                background: linear-gradient(135deg, rgba(0, 242, 254, 0.07), rgba(181, 55, 242, 0.07));
                backdrop-filter: blur(12px);
                border: 1px solid rgba(0, 242, 254, 0.25);
                border-radius: 16px;
                padding: 24px 28px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 16px;
            }}

            .advice-content h3 {{
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 1.4px;
                color: var(--neon-cyan);
                margin-bottom: 8px;
            }}

            .advice-content p {{
                font-size: 1.05rem;
                font-style: italic;
                color: #e2e8f0;
            }}

            .refresh-btn {{
                background: linear-gradient(135deg, var(--neon-cyan), var(--neon-blue));
                color: #090d16;
                border: none;
                padding: 10px 18px;
                border-radius: 10px;
                font-weight: 700;
                font-size: 0.85rem;
                cursor: pointer;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Cabeçalho e Identificação do Grupo 3 -->
            <div class="header-card">
                <div class="header-top">
                    <div class="title-group">
                        <h1>🚀 Painel de Infraestrutura — {EQUIPE}</h1>
                        <p>Monitoramento de Telemetria em Tempo Real • UFRPE (Infraestrutura de Software)</p>
                    </div>
                    <div class="status-pill">
                        <span class="pulse"></span>
                        {STATUS_DEPLOY}
                    </div>
                </div>

                <div class="team-section">
                    <div class="team-label">Engenheiros DevOps Responsáveis ({EQUIPE})</div>
                    <div class="members-grid">
                        {badges_integrantes}
                    </div>
                </div>
            </div>

            <!-- Telemetria de Hardware do Servidor / Container -->
            <div class="telemetry-grid">
                <div class="metric-card">
                    <div class="metric-header">
                        <span>🖥️ HOSTNAME (CONTAINER ID)</span>
                    </div>
                    <div class="metric-value" style="font-size: 1.35rem; color: var(--neon-cyan);">{hostname}</div>
                    <div class="metric-sub">SO: {sistema_op}</div>
                </div>

                <div class="metric-card">
                    <div class="metric-header">
                        <span>⚙️ ARQUITETURA & CPU</span>
                    </div>
                    <div class="metric-value">{cpu_percent}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {min(cpu_percent, 100)}%;"></div>
                    </div>
                    <div class="metric-sub">Arch: <b>{arquitetura}</b> • {cpu_cores_logicos} vCPUs ({cpu_cores_fisicos} físicos)</div>
                </div>

                <div class="metric-card">
                    <div class="metric-header">
                        <span>🧠 MEMÓRIA RAM</span>
                    </div>
                    <div class="metric-value">{memoria.percent}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {min(memoria.percent, 100)}%;"></div>
                    </div>
                    <div class="metric-sub">{ram_usada_gb} GB usados de {ram_total_gb} GB</div>
                </div>

                <div class="metric-card">
                    <div class="metric-header">
                        <span>💾 ARMAZENAMENTO (DISCO)</span>
                    </div>
                    <div class="metric-value">{disco.percent}%</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {min(disco.percent, 100)}%;"></div>
                    </div>
                    <div class="metric-sub">{disco_usado_gb} GB usados de {disco_total_gb} GB</div>
                </div>
            </div>

            <!-- Conselho DevOps da API Externa -->
            <div class="advice-card">
                <div class="advice-content">
                    <h3>💡 Conselho DevOps do Dia (Slip Advice API)</h3>
                    <p>"{conselho}"</p>
                </div>
                <a href="/" class="refresh-btn">🔄 Atualizar Telemetria</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
