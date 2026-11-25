from flask import Flask, Response, jsonify
import psutil
import requests
import socket
import platform
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

EQUIPE = "Grupo 3"
AMBIENTE = "Painel de Infraestrutura — Grupo 3 • Azure!"
INTEGRANTES = [
    "BRUNO ANTONIO DE SOUSA COSTA",
    "CAIO CESAR LIMA DINIZ",
    "GABRIEL MICHALSKI PAIVA"
]

def obter_conselho_devops():
    try:
        # 1. Busca o conselho original em inglês
        resposta = requests.get("https://api.adviceslip.com/advice", timeout=1.5)
        conselho_en = resposta.json()['slip']['advice']

        # 2. Traduz automaticamente para Português (Brasil)
        conselho_pt = conselho_en
        try:
            traducao = requests.get(
                "https://api.mymemory.translated.net/get",
                params={"q": conselho_en, "langpair": "en|pt-BR"},
                timeout=2.0
            )
            texto_pt = traducao.json()['responseData']['translatedText']
            if texto_pt:
                conselho_pt = texto_pt
        except Exception:
            pass

        return {"pt": conselho_pt, "en": conselho_en}
    except Exception:
        return {
            "pt": "Automatize tudo: se precisar fazer algo duas vezes, escreva um script.",
            "en": "Automate everything: if you have to do it twice, write a script."
        }

def coletar_metricas():
    memoria = psutil.virtual_memory()
    disco = psutil.disk_usage('/')

    cpu_cores_logicos = psutil.cpu_count(logical=True) or 1
    cpu_cores_fisicos = psutil.cpu_count(logical=False) or cpu_cores_logicos

    cpu_percent = psutil.cpu_percent(interval=0.15)
    try:
        load_1, load_5, load_15 = [round(x, 2) for x in psutil.getloadavg()]
        if cpu_percent == 0.0:
            cpu_percent = max(round((load_1 / cpu_cores_logicos) * 100, 1), 0.5)
    except Exception:
        load_1, load_5, load_15 = 0.0, 0.0, 0.0
        if cpu_percent == 0.0:
            cpu_percent = 0.5

    boot_ts = psutil.boot_time()
    uptime_sec = int(datetime.now().timestamp() - boot_ts)
    uptime_horas = uptime_sec // 3600
    uptime_min = (uptime_sec % 3600) // 60
    uptime_s = uptime_sec % 60

    fuso_br = timezone(timedelta(hours=-3))
    horario_atual = datetime.now(fuso_br).strftime("%d/%m/%Y %H:%M:%S (BRT / UTC-3)")

    return {
        "hostname": socket.gethostname(),
        "arquitetura": platform.machine(),
        "kernel": platform.release(),
        "sistema_op_azure": f"Ubuntu 24.04.5 LTS (Kernel {platform.release()})",
        "python_ver": platform.python_version(),
        "cpu_percent": round(cpu_percent, 1),
        "cpu_cores_logicos": cpu_cores_logicos,
        "cpu_cores_fisicos": cpu_cores_fisicos,
        "load_avg": f"{load_1} / {load_5} / {load_15}",
        "ram_percent": round(memoria.percent, 1),
        "ram_usada_gb": round(memoria.used / (1024 ** 3), 2),
        "ram_total_gb": round(memoria.total / (1024 ** 3), 2),
        "ram_disp_gb": round(memoria.available / (1024 ** 3), 2),
        "disco_percent": round(disco.percent, 1),
        "disco_usado_gb": round(disco.used / (1024 ** 3), 2),
        "disco_total_gb": round(disco.total / (1024 ** 3), 2),
        "disco_livre_gb": round(disco.free / (1024 ** 3), 2),
        "uptime": f"{uptime_horas}h {uptime_min}m {uptime_s}s",
        "horario_atual": horario_atual
    }

@app.route('/favicon.ico')
def favicon():
    return Response(status=204)

@app.route('/api/metrics')
def api_metrics():
    return jsonify(coletar_metricas())

@app.route('/api/advice')
def api_advice():
    return jsonify(obter_conselho_devops())

@app.route('/')
def home():
    conselho = obter_conselho_devops()
    m = coletar_metricas()

    linhas_equipe = "".join([
        f"""
        <div class="member-item">
            <span class="member-indicator"></span>
            <span class="member-name">{nome}</span>
        </div>
        """
        for nome in INTEGRANTES
    ])

    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Painel de Infraestrutura — {EQUIPE}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-base: #0f172a;
                --bg-surface: #111111;
                --bg-elevated: #161616;
                --border: #262626;
                --border-subtle: #1c1c1c;
                --text-primary: #ededed;
                --text-secondary: #a1a1aa;
                --text-muted: #71717a;
                --accent-green: #10b981;
                --accent-amber: #f59e0b;
                --accent-red: #ef4444;
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
                color: var(--text-primary);
            }}

            .divider {{
                color: var(--border);
            }}

            .status-indicator {{
                display: flex;
                align-items: center;
                gap: 10px;
                font-family: var(--font-mono);
                font-size: 0.75rem;
                color: var(--text-secondary);
                background: var(--bg-elevated);
                border: 1px solid var(--border);
                padding: 5px 12px;
                border-radius: 6px;
            }}

            .live-dot-wrapper {{
                position: relative;
                width: 8px;
                height: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            .status-dot {{
                width: 7px;
                height: 7px;
                background-color: var(--accent-green);
                border-radius: 50%;
                position: relative;
                z-index: 2;
            }}

            .status-dot-ping {{
                position: absolute;
                width: 100%;
                height: 100%;
                border-radius: 50%;
                background-color: var(--accent-green);
                opacity: 0.7;
                animation: pulse-ring 1.8s cubic-bezier(0, 0, 0.2, 1) infinite;
            }}

            @keyframes pulse-ring {{
                0% {{ transform: scale(1); opacity: 0.75; }}
                75%, 100% {{ transform: scale(2.6); opacity: 0; }}
            }}

            .live-tag {{
                color: var(--accent-green);
                font-weight: 600;
                letter-spacing: 0.04em;
            }}

            .main-container {{
                max-width: 1120px;
                width: 100%;
                margin: 0 auto;
                padding: 36px 24px;
                flex: 1;
            }}

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
                border: 1px solid transparent;
                cursor: pointer;
                transition: opacity 0.15s ease, transform 0.1s ease;
            }}

            .btn-refresh:hover {{
                opacity: 0.9;
            }}

            .btn-refresh:active {{
                transform: scale(0.98);
            }}

            .spin {{
                animation: spin-icon 0.6s linear infinite;
            }}

            @keyframes spin-icon {{
                from {{ transform: rotate(0deg); }}
                to {{ transform: rotate(360deg); }}
            }}

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
                transition: border-color 0.25s ease;
            }}

            .card:hover {{
                border-color: #363636;
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

            .metric-row {{
                display: flex;
                align-items: flex-end;
                justify-content: space-between;
                gap: 12px;
                margin-bottom: 12px;
            }}

            .metric-primary {{
                font-family: var(--font-mono);
                font-size: 1.75rem;
                font-weight: 600;
                color: var(--text-primary);
                letter-spacing: -0.03em;
                font-variant-numeric: tabular-nums;
                transition: color 0.35s ease;
            }}

            .value-updated {{
                color: var(--accent-green) !important;
            }}

            .sparkline {{
                width: 72px;
                height: 26px;
                overflow: visible;
            }}

            .sparkline polyline {{
                fill: none;
                stroke: var(--text-secondary);
                stroke-width: 1.75;
                stroke-linecap: round;
                stroke-linejoin: round;
                transition: all 0.4s ease;
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
                transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1), background-color 0.4s ease;
            }}

            .metric-footer {{
                display: flex;
                justify-content: space-between;
                font-family: var(--font-mono);
                font-size: 0.75rem;
                color: var(--text-muted);
                font-variant-numeric: tabular-nums;
            }}

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
                font-variant-numeric: tabular-nums;
                transition: color 0.35s ease;
            }}

            .member-list {{
                display: flex;
                flex-direction: column;
                gap: 10px;
            }}

            .member-item {{
                background-color: var(--bg-elevated);
                border: 1px solid var(--border);
                border-radius: 6px;
                padding: 14px 16px;
                display: flex;
                align-items: center;
                gap: 12px;
            }}

            .member-indicator {{
                width: 6px;
                height: 6px;
                background-color: var(--text-secondary);
                border-radius: 50%;
                flex-shrink: 0;
            }}

            .member-name {{
                font-size: 0.8125rem;
                font-weight: 500;
                color: var(--text-primary);
                letter-spacing: 0.02em;
            }}

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
                gap: 6px;
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
                transition: opacity 0.25s ease;
            }}

            .api-quote-en {{
                font-family: var(--font-mono);
                font-size: 0.78rem;
                color: var(--text-muted);
                font-style: italic;
                transition: opacity 0.25s ease;
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
        <!-- Barra Superior -->
        <header class="topbar">
            <div class="brand">
                <span>UFRPE</span>
                <span class="divider">/</span>
                <span>Infraestrutura de Software</span>
                <span class="divider">/</span>
                <span class="brand-badge">{EQUIPE}</span>
            </div>
            <div class="status-indicator">
                <span class="live-dot-wrapper">
                    <span class="status-dot-ping"></span>
                    <span class="status-dot"></span>
                </span>
                <span class="live-tag">AO VIVO</span>
                <span class="divider">|</span>
                <span>{AMBIENTE}</span>
            </div>
        </header>

        <!-- Conteúdo Principal -->
        <main class="main-container">
            <div class="page-header">
                <div class="page-title">
                    <h1>Telemetria do Servidor & Status do Container</h1>
                    <p>Monitoramento automático em tempo real (polling 1.5s) e deploy CI/CD via GitHub Actions</p>
                </div>
                <button id="btn-sync" class="btn-refresh" onclick="sincronizarManual()">
                    <svg id="icon-sync" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
                        <path d="M3 3v5h5"/>
                        <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/>
                        <path d="M16 21h5v-5"/>
                    </svg>
                    Sincronizar & Novo Conselho
                </button>
            </div>

            <!-- Cards de Métricas Principais -->
            <div class="metrics-grid">
                <!-- Card Hostname -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Hostname (ID do Container)</span>
                        <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>
                    </div>
                    <div class="metric-row">
                        <div id="val-hostname" class="metric-primary" style="font-size: 1.45rem;">{m['hostname']}</div>
                    </div>
                    <div class="meter">
                        <div class="meter-fill" style="width: 100%; background-color: var(--accent-green);"></div>
                    </div>
                    <div class="metric-footer">
                        <span>Status: Ativo</span>
                        <span id="val-uptime">Atividade: {m['uptime']}</span>
                    </div>
                </div>

                <!-- Card CPU -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Uso de CPU</span>
                        <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>
                    </div>
                    <div class="metric-row">
                        <div id="val-cpu" class="metric-primary">{m['cpu_percent']}%</div>
                        <svg class="sparkline" viewBox="0 0 72 26">
                            <polyline id="spark-cpu" points="0,24 72,24" />
                        </svg>
                    </div>
                    <div class="meter">
                        <div id="bar-cpu" class="meter-fill" style="width: {min(m['cpu_percent'], 100)}%;"></div>
                    </div>
                    <div class="metric-footer">
                        <span>Arq: {m['arquitetura']}</span>
                        <span>{m['cpu_cores_logicos']} vCPUs ({m['cpu_cores_fisicos']} Núcleo)</span>
                    </div>
                </div>

                <!-- Card Memória RAM -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Uso de Memória (RAM)</span>
                        <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 19v-3"/><path d="M10 19v-3"/><path d="M14 19v-3"/><path d="M18 19v-3"/><path d="M8 11V9"/><path d="M16 11V9"/><path d="M12 11V9"/><path d="M2 15h20"/><path d="M2 7a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v1.1a2 2 0 0 0 0 3.837V17a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-5.1a2 2 0 0 0 0-3.837Z"/></svg>
                    </div>
                    <div class="metric-row">
                        <div id="val-ram" class="metric-primary">{m['ram_percent']}%</div>
                        <svg class="sparkline" viewBox="0 0 72 26">
                            <polyline id="spark-ram" points="0,24 72,24" />
                        </svg>
                    </div>
                    <div class="meter">
                        <div id="bar-ram" class="meter-fill" style="width: {min(m['ram_percent'], 100)}%;"></div>
                    </div>
                    <div class="metric-footer">
                        <span id="val-ram-used">Usado: {m['ram_usada_gb']} GB</span>
                        <span>Total: {m['ram_total_gb']} GB</span>
                    </div>
                </div>

                <!-- Card Disco -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Armazenamento em Disco (/)</span>
                        <svg class="card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>
                    </div>
                    <div class="metric-row">
                        <div id="val-disco" class="metric-primary">{m['disco_percent']}%</div>
                    </div>
                    <div class="meter">
                        <div id="bar-disco" class="meter-fill" style="width: {min(m['disco_percent'], 100)}%;"></div>
                    </div>
                    <div class="metric-footer">
                        <span id="val-disco-used">Usado: {m['disco_usado_gb']} GB</span>
                        <span id="val-disco-free">Livre: {m['disco_livre_gb']} GB</span>
                    </div>
                </div>
            </div>

            <!-- Grid Inferior: Especificações do Servidor + Integrantes -->
            <div class="bottom-grid">
                <div class="card">
                    <div class="section-label">
                        Especificações do Servidor (Azure VM)
                        <span>psutil / platform</span>
                    </div>
                    <table class="spec-table">
                        <tr>
                            <td class="spec-key">Sistema Operacional</td>
                            <td class="spec-val">{m['sistema_op_azure']}</td>
                        </tr>
                        <tr>
                            <td class="spec-key">Arquitetura do Processador</td>
                            <td class="spec-val">{m['arquitetura']} ({m['cpu_cores_logicos']} vCPUs)</td>
                        </tr>
                        <tr>
                            <td class="spec-key">Carga Média do Sistema (1m / 5m / 15m)</td>
                            <td id="val-load" class="spec-val">{m['load_avg']}</td>
                        </tr>
                        <tr>
                            <td class="spec-key">Memória Disponível</td>
                            <td id="val-ram-disp" class="spec-val">{m['ram_disp_gb']} GB de {m['ram_total_gb']} GB</td>
                        </tr>
                        <tr>
                            <td class="spec-key">Ambiente de Execução</td>
                            <td class="spec-val">Python {m['python_ver']} • Flask (Porta 80)</td>
                        </tr>
                    </table>
                </div>

                <div class="card">
                    <div class="section-label">
                        Integrantes da Equipe
                        <span>{EQUIPE}</span>
                    </div>
                    <div class="member-list">
                        {linhas_equipe}
                    </div>
                </div>
            </div>

            <!-- Conselho DevOps do Dia -->
            <div class="api-box">
                <div class="api-left">
                    <span class="api-tag">Conselho DevOps do Dia • API Externa (api.adviceslip.com)</span>
                    <span id="val-advice-pt" class="api-quote">"{conselho['pt']}"</span>
                    <span id="val-advice-en" class="api-quote-en">Original (EN): "{conselho['en']}"</span>
                </div>
            </div>
        </main>

        <footer class="footer">
            <span>Servidor: vm-infra-monitor ({m['hostname']} • {m['arquitetura']})</span>
            <span id="val-horario">Última leitura: {m['horario_atual']}</span>
        </footer>

        <script>
            const cpuHistory = [{m['cpu_percent']}];
            const ramHistory = [{m['ram_percent']}];
            const MAX_POINTS = 20;

            function corPorNivel(valor) {{
                if (valor >= 85) return 'var(--accent-red)';
                if (valor >= 70) return 'var(--accent-amber)';
                return 'var(--text-primary)';
            }}

            function atualizarTextoComAnimacao(id, novoTexto) {{
                const el = document.getElementById(id);
                if (!el || el.textContent === novoTexto) return;
                el.textContent = novoTexto;
                el.classList.add('value-updated');
                setTimeout(() => el.classList.remove('value-updated'), 450);
            }}

            function atualizarSparkline(id, historico) {{
                const poly = document.getElementById(id);
                if (!poly || historico.length < 2) return;
                const largura = 72;
                const altura = 24;
                const passo = largura / (MAX_POINTS - 1);
                const pontos = historico.map((val, i) => {{
                    const x = (i * passo).toFixed(1);
                    const y = (altura - (Math.min(val, 100) / 100) * (altura - 2)).toFixed(1);
                    return `${{x}},${{y}}`;
                }}).join(' ');
                poly.setAttribute('points', pontos);
            }}

            async function buscarMetricas() {{
                try {{
                    const res = await fetch('/api/metrics', {{ cache: 'no-store' }});
                    if (!res.ok) return;
                    const data = await res.json();

                    atualizarTextoComAnimacao('val-cpu', `${{data.cpu_percent}}%`);
                    atualizarTextoComAnimacao('val-ram', `${{data.ram_percent}}%`);
                    atualizarTextoComAnimacao('val-disco', `${{data.disco_percent}}%`);
                    atualizarTextoComAnimacao('val-load', data.load_avg);
                    atualizarTextoComAnimacao('val-ram-disp', `${{data.ram_disp_gb}} GB de ${{data.ram_total_gb}} GB`);

                    document.getElementById('val-uptime').textContent = `Atividade: ${{data.uptime}}`;
                    document.getElementById('val-ram-used').textContent = `Usado: ${{data.ram_usada_gb}} GB`;
                    document.getElementById('val-disco-used').textContent = `Usado: ${{data.disco_usado_gb}} GB`;
                    document.getElementById('val-disco-free').textContent = `Livre: ${{data.disco_livre_gb}} GB`;
                    document.getElementById('val-horario').textContent = `Última leitura: ${{data.horario_atual}}`;

                    const barCpu = document.getElementById('bar-cpu');
                    barCpu.style.width = `${{Math.min(data.cpu_percent, 100)}}%`;
                    barCpu.style.backgroundColor = corPorNivel(data.cpu_percent);

                    const barRam = document.getElementById('bar-ram');
                    barRam.style.width = `${{Math.min(data.ram_percent, 100)}}%`;
                    barRam.style.backgroundColor = corPorNivel(data.ram_percent);

                    const barDisco = document.getElementById('bar-disco');
                    barDisco.style.width = `${{Math.min(data.disco_percent, 100)}}%`;
                    barDisco.style.backgroundColor = corPorNivel(data.disco_percent);

                    cpuHistory.push(data.cpu_percent);
                    if (cpuHistory.length > MAX_POINTS) cpuHistory.shift();
                    atualizarSparkline('spark-cpu', cpuHistory);

                    ramHistory.push(data.ram_percent);
                    if (ramHistory.length > MAX_POINTS) ramHistory.shift();
                    atualizarSparkline('spark-ram', ramHistory);
                }} catch (err) {{
                    console.error('Erro ao coletar métricas:', err);
                }}
            }}

            async function sincronizarManual() {{
                const icon = document.getElementById('icon-sync');
                const quotePt = document.getElementById('val-advice-pt');
                const quoteEn = document.getElementById('val-advice-en');
                icon.classList.add('spin');
                quotePt.style.opacity = '0.4';
                quoteEn.style.opacity = '0.4';

                await buscarMetricas();
                try {{
                    const res = await fetch('/api/advice', {{ cache: 'no-store' }});
                    if (res.ok) {{
                        const data = await res.json();
                        quotePt.textContent = `"${{data.pt}}"`;
                        quoteEn.textContent = `Original (EN): "${{data.en}}"`;
                    }}
                }} catch (err) {{
                    console.error('Erro ao atualizar conselho:', err);
                }}

                quotePt.style.opacity = '1';
                quoteEn.style.opacity = '1';
                setTimeout(() => icon.classList.remove('spin'), 400);
            }}
            setInterval(buscarMetricas, 1500);
        </script>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, threaded=True)
