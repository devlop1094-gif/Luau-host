from flask import Flask, request, redirect, Response, render_template_string
import os
import requests

app = Flask(__name__)

# ─── 설정 ────────────────────────────────────────────────
SCRIPT_FILE = "script.luau"
ADMIN_PASSWORD = "exploit111"
DISCORD_URL = "https://discord.gg/7bHSDS5e"

# MoonVeil API Key (JWT)
MOONVEIL_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NTg0MDc2Yy0zOTNkLTQwMDYtOGMzZi03M2Y2MTA0MDVhNTciLCJ0eXBlIjoiYXBpIiwibWF4Q3JlZGl0cyI6NTAsImlhdCI6MTc4NjQ4ODM2OH0.XBxj49rOvqWkS1PBwmXPs-CE-P1ylt-hJtT_8eRNps4"
MOONVEIL_OBF_URL = "https://moonveil.cc/api/v2/obf"

DEFAULT_SCRIPT = """-- Luau Script
print("Hello from Luau Host")
"""

# ─── 헬퍼 ────────────────────────────────────────────────

def load_script() -> str:
    if os.path.exists(SCRIPT_FILE):
        with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return DEFAULT_SCRIPT


def save_script(content: str) -> None:
    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def is_browser(user_agent: str) -> bool:
    if not user_agent:
        return False
    ua = user_agent.lower()
    browser_keywords = [
        "mozilla", "chrome", "safari", "firefox", "edge", "opera",
        "msie", "trident", "gecko", "webkit"
    ]
    return any(k in ua for k in browser_keywords)


def call_moonveil(script: str, options: dict | None = None) -> tuple[bool, str]:
    """MoonVeil API 호출. 성공 시 (True, obfuscated_code), 실패 시 (False, error_msg)"""
    payload = {"script": script}
    if options:
        payload["options"] = options

    headers = {
        "Authorization": f"Bearer {MOONVEIL_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(MOONVEIL_OBF_URL, json=payload, headers=headers, timeout=120)
        if resp.status_code == 200:
            return True, resp.text
        try:
            err = resp.json().get("error", resp.text)
        except Exception:
            err = resp.text or f"HTTP {resp.status_code}"
        return False, f"[{resp.status_code}] {err}"
    except requests.Timeout:
        return False, "요청 시간 초과 (120초)"
    except Exception as e:
        return False, str(e)


# ─── 라우트 ───────────────────────────────────────────────

@app.route("/")
def index():
    ua = request.headers.get("User-Agent", "")
    if is_browser(ua):
        return Response(
            "<html><body style='background:#111;color:#f55;font-family:monospace;"
            "display:flex;justify-content:center;align-items:center;height:100vh;margin:0'>"
            "<div style='text-align:center'>"
            "<h1>⛔ ACCESS DENIED</h1>"
            "<p>This endpoint is not available for browsers.</p>"
            "</div></body></html>",
            status=403,
            mimetype="text/html",
        )
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
                background: #0d1117; color: #e6edf3;
                font-family: 'Segoe UI', system-ui, sans-serif;
                min-height: 100vh; display: flex; justify-content: center;
                align-items: flex-start; padding: 40px 20px;
            }}
            .container {{
                width: 100%; max-width: 800px; background: #161b22;
                border: 1px solid #30363d; border-radius: 12px; padding: 32px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.4);
            }}
            h1 {{ font-size: 1.5rem; margin-bottom: 8px; color: #58a6ff; }}
            .subtitle {{ color: #8b949e; font-size: 0.9rem; margin-bottom: 24px; }}
            label {{ display: block; margin-bottom: 6px; font-weight: 600; font-size: 0.9rem; }}
            input[type="password"], textarea {{
                width: 100%; background: #0d1117; border: 1px solid #30363d;
                border-radius: 8px; color: #e6edf3; padding: 12px 14px;
                font-size: 0.95rem; margin-bottom: 18px;
                font-family: 'Cascadia Code', 'Fira Code', monospace;
            }}
            input:focus, textarea:focus {{
                outline: none; border-color: #58a6ff;
                box-shadow: 0 0 0 3px rgba(88,166,255,0.2);
            }}
            textarea {{ min-height: 320px; resize: vertical; line-height: 1.5; }}
            button {{
                background: #238636; color: white; border: none; border-radius: 8px;
                padding: 12px 24px; font-size: 1rem; font-weight: 600; cursor: pointer;
            }}
            button:hover {{ background: #2ea043; }}
            .msg {{ margin-bottom: 20px; padding: 12px 16px; border-radius: 8px; font-size: 0.95rem; }}
            .msg.success {{ background: rgba(35,134,54,0.2); border: 1px solid #238636; color: #3fb950; }}
            .msg.error {{ background: rgba(248,81,73,0.15); border: 1px solid #f85149; color: #f85149; }}
            .info {{ margin-top: 24px; padding-top: 20px; border-top: 1px solid #30363d; font-size: 0.85rem; color: #8b949e; }}
            .info code {{ background: #0d1117; padding: 2px 6px; border-radius: 4px; color: #79c0ff; }}
            a {{ color: #58a6ff; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛠 Luau Script Admin</h1>
            <p class="subtitle">비밀번호를 입력하고 스크립트를 저장하세요. · <a href="/obf">난독화 페이지</a></p>

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
                <p>• 메인 <code>/</code> : 브라우저 접속 시 차단 / 그 외에는 저장된 스크립트 반환</p>
                <p>• Discord <code>/discord</code> · 난독화 <code>/obf</code></p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)


@app.route("/obf", methods=["GET", "POST"])
def obfuscate_page():
    result = ""
    error = ""
    input_script = ""
    selected_compile = "cff"
    selected_vm = "skid"

    if request.method == "POST":
        input_script = request.form.get("script", "").strip()
        selected_compile = request.form.get("compileType", "cff")
        selected_vm = request.form.get("vmType", "skid")

        if not input_script:
            error = "스크립트를 입력해주세요."
        else:
            options = {
                "compileType": selected_compile,
                "vmType": selected_vm,
            }
            # 체크박스 옵션
            if request.form.get("cffDecompose"):
                options["cffDecompose"] = True
            if request.form.get("cffMangleStrings"):
                options["cffMangleStrings"] = True
            if request.form.get("cffMangleGlobals"):
                options["cffMangleGlobals"] = True

            ok, out = call_moonveil(input_script, options)
            if ok:
                result = out
            else:
                error = out

    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Luau Obfuscator (MoonVeil)</title>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                background: #0d1117; color: #e6edf3;
                font-family: 'Segoe UI', system-ui, sans-serif;
                min-height: 100vh; padding: 32px 16px;
            }}
            .wrap {{ max-width: 1100px; margin: 0 auto; }}
            h1 {{ font-size: 1.6rem; color: #a371f7; margin-bottom: 6px; }}
            .sub {{ color: #8b949e; margin-bottom: 28px; font-size: 0.9rem; }}
            .sub a {{ color: #58a6ff; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            @media (max-width: 800px) {{ .grid {{ grid-template-columns: 1fr; }} }}
            .panel {{
                background: #161b22; border: 1px solid #30363d;
                border-radius: 12px; padding: 20px;
            }}
            label {{ display: block; font-weight: 600; font-size: 0.85rem; margin-bottom: 6px; color: #c9d1d9; }}
            textarea {{
                width: 100%; min-height: 340px; background: #0d1117;
                border: 1px solid #30363d; border-radius: 8px; color: #e6edf3;
                padding: 14px; font-family: 'Cascadia Code', 'Fira Code', monospace;
                font-size: 0.9rem; line-height: 1.5; resize: vertical;
            }}
            textarea:focus {{ outline: none; border-color: #a371f7; box-shadow: 0 0 0 3px rgba(163,113,247,0.2); }}
            .opts {{
                display: flex; flex-wrap: wrap; gap: 12px 20px;
                margin: 16px 0; align-items: center;
            }}
            .opts select {{
                background: #0d1117; border: 1px solid #30363d; color: #e6edf3;
                padding: 8px 12px; border-radius: 6px; font-size: 0.9rem;
            }}
            .opts label.chk {{
                display: flex; align-items: center; gap: 6px; font-weight: 500;
                cursor: pointer; margin: 0;
            }}
            button {{
                background: #8957e5; color: white; border: none; border-radius: 8px;
                padding: 12px 28px; font-size: 1rem; font-weight: 600; cursor: pointer;
                transition: background 0.15s;
            }}
            button:hover {{ background: #a371f7; }}
            button:disabled {{ opacity: 0.6; cursor: not-allowed; }}
            .msg {{
                margin-top: 16px; padding: 12px 16px; border-radius: 8px; font-size: 0.9rem;
            }}
            .msg.error {{ background: rgba(248,81,73,0.15); border: 1px solid #f85149; color: #f85149; }}
            .msg.ok {{ background: rgba(35,134,54,0.15); border: 1px solid #238636; color: #3fb950; }}
            .copy-btn {{
                background: #21262d; color: #c9d1d9; border: 1px solid #30363d;
                padding: 6px 12px; border-radius: 6px; font-size: 0.8rem;
                cursor: pointer; margin-top: 10px;
            }}
            .copy-btn:hover {{ background: #30363d; }}
        </style>
    </head>
    <body>
        <div class="wrap">
            <h1>🔒 Luau Obfuscator</h1>
            <p class="sub">Powered by MoonVeil · <a href="/admin">Admin</a> · <a href="/discord">Discord</a></p>

            <form method="POST" id="obfForm">
                <div class="grid">
                    <div class="panel">
                        <label for="script">원본 스크립트</label>
                        <textarea id="script" name="script" spellcheck="false" placeholder="-- 여기에 Luau 코드를 붙여넣으세요">{input_script}</textarea>
                    </div>
                    <div class="panel">
                        <label>난독화 결과</label>
                        <textarea id="result" readonly spellcheck="false" placeholder="결과가 여기에 표시됩니다...">{result}</textarea>
                        {"<button type='button' class='copy-btn' onclick='copyResult()'>복사하기</button>" if result else ""}
                    </div>
                </div>

                <div class="opts">
                    <div>
                        <label style="margin:0 0 4px 0">Compile Type</label>
                        <select name="compileType">
                            <option value="cff" {"selected" if selected_compile == "cff" else ""}>cff</option>
                            <option value="vm" {"selected" if selected_compile == "vm" else ""}>vm</option>
                            <option value="safeEnv" {"selected" if selected_compile == "safeEnv" else ""}>safeEnv</option>
                        </select>
                    </div>
                    <div>
                        <label style="margin:0 0 4px 0">VM Type</label>
                        <select name="vmType">
                            <option value="skid" {"selected" if selected_vm == "skid" else ""}>skid</option>
                            <option value="fox" {"selected" if selected_vm == "fox" else ""}>fox</option>
                        </select>
                    </div>
                    <label class="chk"><input type="checkbox" name="cffDecompose" value="1"> cffDecompose</label>
                    <label class="chk"><input type="checkbox" name="cffMangleStrings" value="1"> Mangle Strings</label>
                    <label class="chk"><input type="checkbox" name="cffMangleGlobals" value="1"> Mangle Globals</label>
                </div>

                <button type="submit" id="btn">난독화 실행</button>
            </form>

            {"<div class='msg error'>" + error + "</div>" if error else ""}
            {"<div class='msg ok'>✅ 난독화 완료</div>" if result else ""}
        </div>

        <script>
            document.getElementById('obfForm').addEventListener('submit', function() {{
                document.getElementById('btn').disabled = true;
                document.getElementById('btn').textContent = '처리 중...';
            }});
            function copyResult() {{
                const t = document.getElementById('result');
                t.select();
                navigator.clipboard.writeText(t.value);
            }}
        </script>
    </body>
    </html>
    """
    return render_template_string(html)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
