"""
Zero-dependency Web UI for Stanford AI4PB Research Agent.
Uses Python built-in http.server.
Runs instantly in any environment without NumPy/PyArrow compatibility issues.
"""

import http.server
import socketserver
import json
import urllib.parse
from agent import AI4PBResearchAgent
from config import PROJECT_ID, LOCATION, GEMINI_MODEL, LAB_NAME, LAB_URL, LAB_DIRECTOR

PORT = 8080

HTML_PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stanford AI4PB Research Agent</title>
    <style>
        :root {
            --primary: #8C1515; /* Stanford Cardinal Red */
            --primary-dark: #620000;
            --bg: #F9FAFB;
            --card-bg: #FFFFFF;
            --border: #E5E7EB;
            --text: #1F2937;
            --text-muted: #6B7280;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 24px;
            line-height: 1.6;
        }
        .container {
            max-width: 960px;
            margin: 0 auto;
        }
        header {
            background: white;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        h1 {
            color: var(--primary);
            margin: 0 0 8px 0;
            font-size: 26px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .badge {
            background: #FEF2F2;
            color: var(--primary);
            border: 1px solid #FECACA;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
        }
        .sample-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 10px;
            margin: 16px 0;
        }
        .btn-sample {
            background: #F3F4F6;
            border: 1px solid var(--border);
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 13px;
            text-align: left;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .btn-sample:hover {
            background: #E5E7EB;
            border-color: #D1D5DB;
        }
        .input-group {
            display: flex;
            gap: 12px;
            margin-top: 12px;
        }
        textarea {
            flex: 1;
            padding: 12px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 15px;
            resize: vertical;
            height: 70px;
            box-sizing: border-box;
        }
        .btn-run {
            background: var(--primary);
            color: white;
            border: none;
            padding: 0 28px;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.15s;
        }
        .btn-run:hover {
            background: var(--primary-dark);
        }
        .btn-run:disabled {
            background: #9CA3AF;
            cursor: not-allowed;
        }
        .card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            margin-top: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .event-item {
            border-left: 3px solid #D1D5DB;
            padding: 12px 16px;
            margin: 12px 0;
            background: #F9FAFB;
            border-radius: 0 8px 8px 0;
        }
        .event-item.plan { border-color: #3B82F6; background: #EFF6FF; }
        .event-item.tool_call { border-color: #8B5CF6; background: #F5F3FF; }
        .event-item.observation { border-color: #10B981; background: #ECFDF5; }
        .event-item.gap { border-color: #F59E0B; background: #FFFBEB; }
        .event-item.report { border-color: #EF4444; background: #FEF2F2; }
        .event-header {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 6px;
        }
        .event-body {
            font-size: 13px;
            color: #374151;
            white-space: pre-wrap;
            word-break: break-word;
        }
        pre {
            background: #1F2937;
            color: #F9FAFB;
            padding: 12px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 12px;
        }
        #report-content {
            white-space: pre-wrap;
            font-family: inherit;
            line-height: 1.7;
        }
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>
            <span>🎓 Stanford AI4PB Research Agent</span>
            <span class="badge">Google Cloud Hackathon MVP</span>
        </h1>
        <p style="margin: 4px 0 16px 0; color: var(--text-muted); font-size: 14px;">
            Stanford大学 <strong>AI for Public Benefit Lab</strong>（ディレクター: Robb Willer 教授）の研究・論文・再現性ガイドを自律調査します。
        </p>
        <div>
            <div style="font-size: 13px; font-weight: 600; color: var(--text-muted);">💡 クイック質問を選択:</div>
            <div class="sample-buttons">
                <button class="btn-sample" onclick="setQuery('Synthetic Respondents について AI4PB ではどんな研究が行われている？')">
                    🤖 <strong>1. Synthetic Respondents</strong><br>
                    <span style="font-size: 11px; color: var(--text-muted);">シリコンサンプリングと人間シミュレーション</span>
                </button>
                <button class="btn-sample" onclick="setQuery('AI4PB の最近の研究テーマと成果を整理して')">
                    📑 <strong>2. 最新テーマの整理</strong><br>
                    <span style="font-size: 11px; color: var(--text-muted);">2024-2026年の主要研究柱</span>
                </button>
                <button class="btn-sample" onclick="setQuery('自分で再現実験するなら、どの研究が取り組みやすい？')">
                    🧪 <strong>3. 再現実験のしやすさ</strong><br>
                    <span style="font-size: 11px; color: var(--text-muted);">難易度・所要時間・プロンプトガイド</span>
                </button>
            </div>
        </div>
        <div class="input-group">
            <textarea id="query-input" placeholder="調査したい質問を入力してください..."></textarea>
            <button id="run-btn" class="btn-run" onclick="startResearch()">調査開始</button>
        </div>
    </header>

    <div id="progress-card" class="card" style="display:none;">
        <h3 style="margin-top:0;">🔄 Agent の自律調査プロセス (Action / Tool Log)</h3>
        <div id="events-list"></div>
    </div>

    <div id="report-card" class="card" style="display:none;">
        <h2 style="margin-top:0; color: var(--primary);">📑 最終リサーチレポート</h2>
        <div id="report-content"></div>
    </div>
</div>

<script>
function setQuery(text) {
    document.getElementById('query-input').value = text;
}

async function startResearch() {
    const input = document.getElementById('query-input').value.trim();
    if (!input) return;

    const runBtn = document.getElementById('run-btn');
    const progressCard = document.getElementById('progress-card');
    const eventsList = document.getElementById('events-list');
    const reportCard = document.getElementById('report-card');
    const reportContent = document.getElementById('report-content');

    runBtn.disabled = true;
    runBtn.innerText = "調査中...";
    progressCard.style.display = "block";
    reportCard.style.display = "none";
    eventsList.innerHTML = "<p><em>Agent を起動中...</em></p>";

    try {
        const response = await fetch('/api/research', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: input})
        });
        const data = await response.json();
        
        eventsList.innerHTML = "";
        data.events.forEach(e => {
            const div = document.createElement('div');
            div.className = 'event-item ' + e.event_type;
            
            let detailsHtml = "";
            if (typeof e.details === 'object') {
                detailsHtml = "<pre>" + JSON.stringify(e.details, null, 2) + "</pre>";
            } else {
                detailsHtml = "<div class='event-body'>" + e.details + "</div>";
            }
            
            div.innerHTML = "<div class='event-header'>[" + e.step + "] " + e.title + "</div>" + detailsHtml;
            eventsList.appendChild(div);
        });

        reportContent.innerText = data.final_report;
        reportCard.style.display = "block";
    } catch (err) {
        alert("エラーが発生しました: " + err.message);
    } finally {
        runBtn.disabled = false;
        runBtn.innerText = "調査開始";
    }
}
</script>
</body>
</html>
"""


class AgentHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/research":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            params = json.loads(body.decode('utf-8'))
            query = params.get("query", "")

            agent = AI4PBResearchAgent()
            events = []
            final_report = ""

            for event in agent.research(query):
                events.append(event.to_dict())
                if event.event_type == "report":
                    final_report = event.details

            response_data = {
                "query": query,
                "events": events,
                "final_report": final_report
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_error(404)


def run_server():
    server_address = ('', PORT)
    with socketserver.TCPServer(server_address, AgentHandler) as httpd:
        print(f"🚀 AI4PB Research Agent Web Server running at http://localhost:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
