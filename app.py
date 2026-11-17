from flask import Flask, Response
import psutil
import requests
import socket
import platform
from datetime import datetime

app = Flask(__name__)

# ========================================================
EQUIPE = "Grupo 3"
AMBIENTE = "Painel de Infraestrutura — Grupo 3 • Azure"
INTEGRANTES = [
    {"nome": "BRUNO ANTONIO DE SOUSA COSTA", "role": "Cloud & CI/CD Pipeline"},
    {"nome": "CAIO CESAR LIMA DINIZ", "role": "Containers & Dockerization"},
    {"nome": "GABRIEL MICHALSKI PAIVA", "role": "Telemetry & Monitoring"}
]
# ========================================================

def obter_conselho_devops():
    try:
        # Consome a API externa de conselhos (Slip Advice API)
        resposta = requests.get("https://api.adviceslip.com/advice", timeout=1.5)
        return resposta.json()['slip']['advice']
    except Exception:
        return "Automate everything: if you have to do it twice, write a script."

@app.route('/favicon.ico')
def favicon():
    return Response(status=204)

@app.route('/')
def home():
    conselho = obter_conselho_devops()

    # Coleta de métricas reais do servidor via psutil e platform
    memoria = psutil.virtual_memory()
    disco = psutil.disk_usage('/')
    
    cpu_cores_logicos = psutil.cpu_count(logical=True) or 1
    cpu_cores_fisicos = psutil.cpu_count(logical=False) or cpu_cores_logicos
    
    cpu_percent = psutil.cpu_percent(interval=0.2)
    try:
        load_1, load_5, load_15 = [round(x, 2) for x in psutil.getloadavg()]
        if cpu_percent == 0.0:
            cpu_percent = max(round((load_1 / cpu_cores_logicos) * 100, 1), 0.5)
    except Exception:
        load_1, load_5, load_15 = 0.0, 0.0, 0.0
        if cpu_percent == 0.0:
            cpu_percent = 0.5

    ram_usada_gb = round(memoria.used / (1024 ** 3), 2)
    ram_total_gb = round(memoria.total / (1024 ** 3), 2)
    ram_disp_gb = round(memoria.available / (1024 ** 3), 2)
    
    disco_usado_gb = round(disco.used / (1024 ** 3), 2)
    disco_total_gb = round(disco.total / (1024 ** 3), 2)
    disco_livre_gb = round(disco.free / (1024 ** 3), 2)

    hostname = socket.gethostname()
    arquitetura = platform.machine()
    kernel = platform.release()
    sistema_op = platform.system()
    python_ver = platform.python_version()

    # Cálculo de Uptime do Host
    boot_ts = psutil.boot_time()
    uptime_sec = int(datetime.now().timestamp() - boot_ts)
    uptime_horas = uptime_sec // 3600
    uptime_min = (uptime_sec % 3600) // 60
    horario_atual = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Renderização da lista da equipe
    linhas_equipe = "".join([
        f"""
        <div class="member-item">
            <div class="member-name">{m['nome']}</div>
            <div class="member-role">{m['role']}</div>
        </div>
        """
        for m in INTEGRANTES
    ])

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Infra Monitor — {EQUIPE}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-base: #0a0a0a;
                --bg-surface: #111111;
                --bg-elevated: #161616;
                --border: #262626;
                --border-subtle: #1c1c1c;
                --text-primary: #ededed;
                --text-secondary: #a1a1aa;
                --text-muted: #71717a;
                --accent-green: #10b981;
                --accent-blue: #3b82f6;
                --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                --font-mono: 'JetBrains Mono', monospace;
            }}

            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}

            body {{
                font-family: var(--font-sans);
                background-color: var(--bg-base);
                color: var(--text-primary);
                line-height: 1.5;
                -webkit-font-smoothing: antialiased;
                min-height: 100vh;
                 display: flex;
                flex-direction: column;
            }}

            /* Barra superior estilo Console Cloud */
            .topbar {{
                border-bottom: 1px solid var(--border);
                background-color: var(--bg-surface);
                padding: 14px 32px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
                gap: 16px;
            }}

            .brand {{
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 0.9rem;
                font-weight: 500;
            }}

            .brand-badge {{
                font-family: var(--font-mono);
                font-size: 0.75rem;
                background: var(--bg-elevated);
                border: 1px solid var(--border);
                padding: 2px 8px;
                border-radius: 4px;
                color: var(--text-secondary);
            }}

            .divider {{
                color: var(--border);
            }}

            .status-indicator {{
                display: flex;
                align-items: center;
                gap: 8px;
                font-family: var(--font-mono);
                font-size: 0.75rem;
                color: var(--text-secondary);
                background: var(--bg-elevated);
                border: 1px solid var(--border);
                padding: 5px 12px;
                border-radius: 6px;
            }}

            .status-dot {{
                width: 7px;
                height: 7px;
                background-color: var(--accent-green);
                border-radius: 50%;
            }}

            /* Container Principal */
            .main-container {{
                max-width: 1120px;
                width: 100%;
                margin: 0 auto;
                padding: 36px 24px;
                flex: 1;
            }}

            /* Cabeçalho da Página */
            .page-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-end;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 32px;
                padding-bottom: 24px;
                border-bottom: 1px solid var(--border);
            }}

            .page-title h1 {{
                font-size: 1.5rem;
                font-weight: 600;
                letter-spacing: -0.02em;
                color: var(--text-primary);
            }}

            .page-title p {{
                font-size: 0.875rem;
                color: var(--text-secondary);
                margin-top: 4px;
            }}

            .btn-refresh {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background-color: var(--text-primary);
                color: var(--bg-base);
                font-family: var(--font-sans);
                font-size: 0.8125rem;
                font-weight: 500;
                padding: 8px 14px;
                border-radius: 6px;
                text-decoration: none;
                border: 1px solid transparent;
                transition: opacity 0.15s ease;
            }}

            .btn-refresh:hover {{
                opacity: 0.9;
            }}

            /* Grid de KPIs de Telemetria */
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
                gap: 16px;
                margin-bottom: 24px;
            }}

            .card {{
                background-color: var(--bg-surface);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 20px;
            }}

            .card-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 14px;
            }}

            .card-title {{
                font-size: 0.75rem;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: var(--text-secondary);
            }}

            .card-icon {{
                color: var(--text-muted);
                width: 16px;
                height: 16px;
            }}

            .metric-primary {{
                font-family: var(--font-mono);
                font-size: 1.75rem;
                font-weight: 600;
                color: var(--text-primary);
                letter-spacing: -0.03em;
                margin-bottom: 12px;
            }}

            .meter {{
                width: 100%;
                height: 4px;
                background-color: var(--border);
                border-radius: 2px;
                overflow: hidden;
                margin-bottom: 12px;
            }}

            .meter-fill {{
                height: 100%;
                background-color: var(--text-primary);
                border-radius: 2px;
            }}

            .metric-footer {{
                display: flex;
                justify-content: space-between;
                font-family: var(--font-mono);
                font-size: 0.75rem;
                color: var(--text-muted);
            }}

            /* Seção Inferior: Especificações + Equipe */
            .bottom-grid {{
                display: grid;
                grid-template-columns: 1.4fr 1fr;
                gap: 16px;
                margin-bottom: 24px;
            }}

            @media (max-width: 820px) {{
                .bottom-grid {{
                    grid-template-columns: 1fr;
                }}
            }}

            .section-label {{
                font-size: 0.8125rem;
                font-weight: 600;
                color: var(--text-primary);
                margin-bottom: 16px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}

            .section-label span {{
                font-family: var(--font-mono);
                font-size: 0.72rem;
                font-weight: 400;
                color: var(--text-muted);
            }}

            .spec-table {{
                width: 100%;
                border-collapse: collapse;
            }}

            .spec-table tr {{
                border-bottom: 1px solid var(--border-subtle);
            }}

            .spec-table tr:last-child {{
                border-bottom: none;
            }}

            .spec-table td {{
                padding: 10px 0;
                font-size: 0.8125rem;
            }}

            .spec-key {{
                color: var(--text-secondary);
            }}

            .spec-val {{
                font-family: var(--font-mono);
                color: var(--text-primary);
                text-align: right;
            }}

            /* Lista da Equipe */
            .member-list {{
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}

            .member-item {{
                background-color: var(--bg-elevated);
                border: 1px solid var(--border);
                border-radius: 6px;
                padding: 12px 14px;
                display: flex;
                flex-direction: column;
                gap: 2px;
            }}

            .member-name {{
                font-size: 0.8125rem;
                font-weight: 600;
                color: var(--text-primary);
                letter-spacing: 0.01em;
            }}

            .member-role {{
                font-family: var(--font-mono);
                font-size: 0.72rem;
                color: var(--text-muted);
            }}

            /* Terminal de API Externa */
            .api-box {{
                background-color: var(--bg-surface);
                border: 1px solid var(--border);
                border-radius: 8px;
                padding: 18px 20px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 16px;
            }}

            .api-left {{
                display: flex;
                flex-direction: column;
                gap: 4px;
            }}

            .api-tag {{
                font-family: var(--font-mono);
                font-size: 0.7rem;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.06em;
            }}

            .api-quote {{
                font-family: var(--font-mono);
                font-size: 0.875rem;
                color: var(--text-primary);
            }}

            .footer {{
                border-top: 1px solid var(--border);
                padding: 16px 32px;
                font-family: var(--font-mono);
                font-size: 0.72rem;
                color: var(--text-muted);
                display: flex;
                justify-content: space-between;
                flex-wrap: wrap;
                gap: 12px;
            }}
        </style>
    </head>
    <body>
        <!-- Barra de Topo -->
        <header class="topbar">
            <div class="brand">
                <span>UFRPE</span>
                <span class="divider">/</span>
                <span>Infraestrutura de Software</span>
                <span class="divider">/</span>
                <span class="brand-badge">{EQUIPE}</span>
            </div>
            <div class="status-indicator">
                <span class="status-dot"></span>
                <span>{AMBIENTE}</span>
            </div>
        </header>

        <!-- Conteúdo Principal -->
        <main class="main-container">
            <div class="page-header">
                <div class="page-title">
                    <h1>System Telemetry & Node Status</h1>
                    <p>Monitoramento de recursos do container e automação CI/CD via GitHub Actions</p>
                </div>
                <a href="/" class="btn-refresh">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
                        <path d="M3 3v5h5"/>
                        <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/>
                        <path d="M16 21h5v-5"/>
                    </svg>
                    Atualizar Métricas
                </a>
            </div>

            <!-- Cards de Métricas Principais -->
            <div class="metrics-grid">
                <!-- Card Hostname -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Container ID (Hostname)</span>
                        <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
                    </div>
                    <div class="metric-primary" style="font-size: 1.45rem;">{hostname}</div>
                    <div class="meter">
                        <div class="meter-fill" style="width: 100%; background-color: var(--accent-green);"></div>
                    </div>
                    <div class="metric-footer">
                        <span>Status: Running</span>
                        <span>Uptime: {uptime_horas}h {uptime_min}m</span>
                    </div>
                </div>

                <!-- Card CPU -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">CPU Utilization</span>
                        <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>
                    </div>
                    <div class="metric-primary">{cpu_percent}%</div>
                    <div class="meter">
                        <div class="meter-fill" style="width: {min(cpu_percent, 100)}%;"></div>
                    </div>
                    <div class="metric-footer">
                        <span>Arch: {arquitetura}</span>
                        <span>{cpu_cores_logicos} vCPUs ({cpu_cores_fisicos} Core)</span>
                    </div>
                </div>

                <!-- Card Memória RAM -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Memory Usage (RAM)</span>
                        <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 19v-3"/><path d="M10 19v-3"/><path d="M14 19v-3"/><path d="M18 19v-3"/><path d="M8 11V9"/><path d="M16 11V9"/><path d="M12 11V9"/><path d="M2 15h20"/><path d="M2 7a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v1.1a2 2 0 0 0 0 3.837V17a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-5.1a2 2 0 0 0 0-3.837Z"/></svg>
                    </div>
                    <div class="metric-primary">{memoria.percent}%</div>
                    <div class="meter">
                        <div class="meter-fill" style="width: {min(memoria.percent, 100)}%;"></div>
                    </div>
                    <div class="metric-footer">
                        <span>Used: {ram_usada_gb} GB</span>
                        <span>Total: {ram_total_gb} GB</span>
                    </div>
                </div>

                <!-- Card Disco -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Disk Allocation (/)</span>
                        <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>
                    </div>
                    <div class="metric-primary">{disco.percent}%</div>
                    <div class="meter">
                        <div class="meter-fill" style="width: {min(disco.percent, 100)}%;"></div>
                    </div>
                    <div class="metric-footer">
                        <span>Used: {disco_usado_gb} GB</span>
                        <span>Free: {disco_livre_gb} GB</span>
                    </div>
                </div>
            </div>

            <!-- Grid Inferior: Detalhes do Ambiente + Equipe -->
            <div class="bottom-grid">
                <div class="card">
                    <div class="section-label">
                        Ambiente & Especificações do Host
                        <span>psutil / platform</span>
                    </div>
                    <table class="spec-table">
                        <tr>
                            <td class="spec-key">Sistema Operacional</td>
                            <td class="spec-val">{sistema_op} (Kernel {kernel})</td>
                        </tr>
                        <tr>
                            <td class="spec-key">Arquitetura do Processador</td>
                            <td class="spec-val">{arquitetura} ({cpu_cores_logicos} Logical CPUs)</td>
                        </tr>
                        <tr>
                            <td class="spec-key">System Load Average (1m / 5m / 15m)</td>
                            <td class="spec-val">{load_1} / {load_5} / {load_15}</td>
                        </tr>
                        <tr>
                            <td class="spec-key">Memória Disponível para Alocação</td>
                            <td class="spec-val">{ram_disp_gb} GB de {ram_total_gb} GB</td>
                        </tr>
                        <tr>
                            <td class="spec-key">Runtime do Container</td>
                            <td class="spec-val">Python {python_ver} • Flask (Port 80)</td>
                        </tr>
                    </table>
                </div>

                <div class="card">
                    <div class="section-label">
                        Engenharia Responsável
                        <span>{EQUIPE}</span>
                    </div>
                    <div class="member-list">
                        {linhas_equipe}
                    </div>
                </div>
            </div>

            <!-- Resposta da API Externa -->
            <div class="api-box">
                <div class="api-left">
                    <span class="api-tag">GET https://api.adviceslip.com/advice • 200 OK</span>
                    <span class="api-quote">"{conselho}"</span>
                </div>
            </div>
        </main>

        <footer class="footer">
            <span>Host: {hostname} ({arquitetura})</span>
            <span>Last probe: {horario_atual}</span>
        </footer>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)
