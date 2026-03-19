from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# 🛡️ 安全配置：优先读取系统环境变量中的密钥
API_KEY = os.environ.get("GEMINI_API_KEY", "在这里粘贴你的密钥(如果不设置环境变量)")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>DIDI TORONTO - 小龙虾指挥部</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box;}
        #chat { flex: 1; overflow-y: auto; border: 1px solid #30363d; padding: 15px; border-radius: 8px; background: #161b22; margin-bottom: 20px; }
        .msg { margin-bottom: 15px; padding: 12px; border-radius: 10px; max-width: 85%; line-height: 1.6; word-wrap: break-word; }
        .user { background: #1f6feb; color: white; margin-left: auto; border-bottom-right-radius: 2px; }
        .bot { background: #21262d; border: 1px solid #30363d; color: #ffa500; border-bottom-left-radius: 2px; }
        .input-area { display: flex; gap: 10px; padding-bottom: 10px; }
        input { flex: 1; background: #0d1117; border: 1px solid #30363d; color: white; padding: 14px; border-radius: 6px; outline: none; font-size: 16px; }
        input:focus { border-color: #58a6ff; box-shadow: 0 0 0 2px rgba(88,166,255,0.3); }
        button { background: #2ea44f; color: white; border: none; padding: 0 25px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s; }
        button:hover { background: #2c974b; transform: translateY(-1px); }
        b { color: #58a6ff; }
    </style>
</head>
<body>
    <h2 style="color:#58a6ff; margin: 0 0 15px 0; display: flex; align-items: center; gap: 10px;">
        🦞 DIDI TORONTO - 指挥中心
    </h2>
    <div id="chat">
        <div class="msg bot">老板好！我是多伦多 Didi Cleaning 小龙虾指挥官。系统已就绪，请下达清洁调度指令。</div>
    </div>
    <div class="input-area">
        <input type="text" id="m" placeholder="输入指令..." onkeydown="if(event.key==='Enter')s();" autocomplete="off">
        <button onclick="s()">发送</button>
    </div>
    <script>
        function formatText(text) {
            return text.replace(/\\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
        }

        async function s(){
            let m=document.getElementById('m'); let c=document.getElementById('chat');
            let val = m.value.trim(); if(!val) return;
            
            c.innerHTML += `<div class="msg user">${val}</div>`;
            m.value = '';
            
            let loadingId = "load-" + Date.now();
            c.innerHTML += `<div id="${loadingId}" class="msg bot" style="opacity: 0.6;">⚡ 正在联系多伦多总部...</div>`;
            c.scrollTop = c.scrollHeight;

            try {
                let r = await fetch('/chat',{
                    method:'POST', 
                    body:JSON.stringify({p:val}), 
                    headers:{'Content-Type':'application/json'}
                });
                let d = await r.json();
                document.getElementById(loadingId).remove();
                c.innerHTML += `<div class="msg bot"><b>指挥官回复：</b><br>${formatText(d.r)}</div>`;
            } catch (err) { 
                document.getElementById(loadingId).innerText = "❌ 信号受干扰，请检查 API KEY 或网络。"; 
            }
            c.scrollTop = c.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): 
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('p', '')
    # 使用 1.5-flash 或 1.5-pro 保证稳定性
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    payload = {
        "system_instruction": {
            "parts":[{"text": "你是小龙虾指挥官，负责加拿大城市多伦多(Toronto)的 Didi Cleaning 清洁业务。你对老板非常忠诚且专业。你的回复要高效、干练，语气中带着指挥官的威严与细致。"}]
        },
        "contents": [{"parts": [{"text": user_msg}]}]
    }
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        data = res.json()
        if 'candidates' in data:
            reply = data['candidates'][0]['content']['parts'][0]['text']
        else:
            error_msg = data.get('error', {}).get
