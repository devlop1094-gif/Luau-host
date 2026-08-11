from flask import Flask, request, redirect, Response, render_template_string, abort
import os

app = Flask(__name__)

# 저장될 스크립트 파일 경로
SCRIPT_FILE = "script.luau"
ADMIN_PASSWORD = "exploit111"
DISCORD_URL = "https://discord.gg/7bHSDS5e"

# 기본 스크립트 (파일이 없을 때)
DEFAULT_SCRIPT = """-- Luau Script
print("Hello from Luau Host")
"""

def load_script() -> str:
    if os.path.exists(SCRIPT_FILE):
        with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return DEFAULT_SCRIPT

def save_script(content: str) -> None:
    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def is_browser(user_agent: str) -> bool:
    """브라우저 User-Agent 감지 (간단한 휴리스틱)"""
    if not user_agent:
        return False
    ua = user_agent.lower()
    browser_keywords = [
        "mozilla", "chrome", "safari", "firefox", "edge", "opera",
        "msie", "trident", "gecko", "webkit"
    ]
    # 실행기/봇이 아닌 일반적인 브라우저로 보이면 True
    return any(k in ua for k in browser_keywords)

# ─── 라우트 ───────────────────────────────────────────────

@app.route("/")
def index():
    ua = request.headers.get("User-Agent", "")
    
    # 브라우저로 접속하면 차단
    if is_browser(ua):
        return Response(
            "<html><body style='background:#111;color:#f55;font-family:monospace;"
            "display:flex;justify-content:center;align-items:center;height:100vh;margin:0'>"
            "<div style='text-align:center'>"
            "<h1>⛔ ACCESS DENIED</h1>"
            "<p>This endpoint is not available for browsers.</p>"
            "</div></body></html>",
            status=403,
            mimetype="text/html"
        )
    
    # 그 외(스크립트 로더/실행기 등)는 Luau 코드 반환
    script = load_script()
    return Response(script, mimetype="text/plain; charset=utf-8")


@app.route("/discord")
def discord():
    return redirect(DISCORD_URL, code=302)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    message = ""
    current_script = load_script()

    if request.method == "POST":
        password = request.form.get("password", "")
        script_content = request.form.get("script", "")

        if password != ADMIN_PASSWORD:
            message = "❌ 비밀번호가 틀렸습니다."
        else:
            save_script(script_content)
            current_script = script_content
            message = "✅ 스크립트가 성공적으로 저장되었습니다."

    # 간단한 관리자 페이지 HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin - Luau Script Manager</title>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                background: #0d1117;
                color: #e6edf3;
                font-family: 'Segoe UI', system-ui, sans-serif;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: flex-start;
                padding: 40px 20px;
            }}
            .container {{
                width: 100%;
                max-width: 800px;
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 12px;
                padding: 32px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.4);
            }}
            h1 {{
                font-size: 1.5rem;
                margin-bottom: 8px;
                color: #58a6ff;
            }}
            .subtitle {{
                color: #8b949e;
                font-size: 0.9rem;
                margin-bottom: 24px;
            }}
            label {{
                display: block;
                margin-bottom: 6px;
                font-weight: 600;
                font-size: 0.9rem;
            }}
            input[type="password"], textarea {{
                width: 100%;
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
                color: #e6edf3;
                padding: 12px 14px;
                font-size: 0.95rem;
                margin-bottom: 18px;
                font-family: 'Cascadia Code', 'Fira Code', monospace;
            }}
            input[type="password"]:focus, textarea:focus {{
                outline: none;
                border-color: #58a6ff;
                box-shadow: 0 0 0 3px rgba(88,166,255,0.2);
            }}
            textarea {{
                min-height: 320px;
                resize: vertical;
                line-height: 1.5;
            }}
            button {{
                background: #238636;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.15s;
            }}
            button:hover {{
                background: #2ea043;
            }}
            .msg {{
                margin-bottom: 20px;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 0.95rem;
            }}
            .msg.success {{
                background: rgba(35,134,54,0.2);
                border: 1px solid #238636;
                color: #3fb950;
            }}
            .msg.error {{
                background: rgba(248,81,73,0.15);
                border: 1px solid #f85149;
                color: #f85149;
            }}
            .info {{
                margin-top: 24px;
                padding-top: 20px;
                border-top: 1px solid #30363d;
                font-size: 0.85rem;
                color: #8b949e;
            }}
            .info code {{
                background: #0d1117;
                padding: 2px 6px;
                border-radius: 4px;
                color: #79c0ff;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛠 Luau Script Admin</h1>
            <p class="subtitle">비밀번호를 입력하고 스크립트를 저장하세요.</p>

            {"<div class='msg success'>" + message + "</div>" if message.startswith("✅") else ""}
            {"<div class='msg error'>" + message + "</div>" if message.startswith("❌") else ""}

            <form method="POST">
                <label for="password">비밀번호</label>
                <input type="password" id="password" name="password" placeholder="admin password" required autocomplete="current-password">

                <label for="script">Luau 스크립트</label>
                <textarea id="script" name="script" spellcheck="false">{current_script}</textarea>

                <button type="submit">저장하기</button>
            </form>

            <div class="info">
                <p>• 메인 엔드포인트 <code>/</code> : 브라우저 접속 시 차단 / 그 외에는 저장된 스크립트 반환</p>
                <p>• Discord 리다이렉트 <code>/discord</code></p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
