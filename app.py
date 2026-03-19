from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)
# 您的专属 API Key
API_KEY = "AIzaSyCuK_v86HfsQBGb_AqNmemREEm7s52t-Ho"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>DIDI TORONTO COMMANDER</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: sans-serif; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 95vh; }
        #chat { flex: 1; overflow-y: auto; border: 1px solid #30363d; padding: 20px; border-radius: 6px; background: #161b22; margin-bottom: 20px; }
        .msg { margin-bottom: 15px; padding: 12px; border-radius: 8px; max-width: 85%; line-height: 1.5; }
        .user { background: #1f6feb; color: white; align-self: flex-end; margin-left: auto; text-align: right; }
        .bot { background: #21262d; border: 1px solid #30363d; color: orange; }
        .input-area { display: flex; gap: 10px; background: #161b22; padding: 15px; border-top: 1px solid #30363d; }
        input[type="text"] { flex: 1; background: #0d1117; border: 1px solid #30363d; color: white; padding: 12px; border-radius: 6px; outline: none; }
        button { background: #2ea44f; color: white; border: none; padding: 12px 25px; border-radius: 6px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <h2 style="color:#58a6ff;">🦞 DIDI TORONTO - 指挥部已上线</h2>
    <div id="chat"><div class="msg bot">老板，系统已全面加固！我是小龙虾，已准备好处理多伦多清洁业务指令。</div></div>
    <div class="input-area">
        <input type="text" id="m" placeholder="输入指令后按回车..." onkeydown="if(event.key==='Enter'){s();event.preventDefault();}">
        <button onclick="s()">发送</button>
    </div>
    <script>
        async function s(){
            let m=document.getElementById('m'); let c=document.getElementById('chat');
            let val = m.value.trim(); if(!val) return;
            c.innerHTML += `<div class="msg user">${val}</div>`;
            m.value = ''; c.scrollTop = c.scrollHeight;
            try {
                let r = await fetch('/chat',{method:'POST', body:JSON.stringify({p:val}), headers:{'Content-Type':'application/json'}});
                let d = await r.json();
                c.innerHTML += `<div class="msg bot"><b>小龙虾:</b><br>${d.r}</div>`;
            } catch (err) { c.innerHTML += `<div class="msg bot" style="color:red">连接超时，请重试。</div>`; }
            c.scrollTop = c.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('p', '')
    # 🚨 关键修复：使用 v1beta 版本 API 地址
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    # 🧠 为您的清洁业务定制的大脑逻辑
    prompt = f"你是小龙虾助手，多伦多Didi Cleaning清洁业务AI指挥。请回复老板博伟：{user_msg}"
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        res = requests.post(url, json=payload, timeout=20)
        reply = res.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        reply = "AI 信号接收稍有延迟，请再试一次。"
    return jsonify({"r": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
