from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# 🚨 老板，请在这里粘贴您在 AI Studio 领到的最新 API KEY
API_KEY = "AIzaSyDCKySgusqHlvUbB0fRwvBKFUHH6CXa1mg"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>DIDI TORONTO - 3.1 PRO 指挥部</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: sans-serif; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 95vh; }
        #chat { flex: 1; overflow-y: auto; border: 1px solid #30363d; padding: 15px; border-radius: 6px; background: #161b22; margin-bottom: 20px; }
        .msg { margin-bottom: 12px; padding: 10px; border-radius: 8px; max-width: 85%; }
        .user { background: #1f6feb; margin-left: auto; text-align: right; }
        .bot { background: #21262d; border: 1px solid #30363d; color: #ffa500; }
        .input-area { display: flex; gap: 10px; }
        input { flex: 1; background: #0d1117; border: 1px solid #30363d; color: white; padding: 12px; border-radius: 6px; }
        button { background: #2ea44f; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; }
    </style>
</head>
<body>
    <h2 style="color:#58a6ff;">🦞 DIDI TORONTO - Gemini 3.1 Pro 指挥部</h2>
    <div id="chat"><div class="msg bot">老板，系统已升级至 3.1 Pro 顶配大脑！请下达清洁业务指令。</div></div>
    <div class="input-area">
        <input type="text" id="m" placeholder="输入指令后按回车..." onkeydown="if(event.key==='Enter')s();">
        <button onclick="s()">发送</button>
    </div>
    <script>
        async function s(){
            let m=document.getElementById('m'); let c=document.getElementById('chat');
            let val = m.value.trim(); if(!val) return;
            c.innerHTML += `<div class="msg user">${val}</div>`;
            m.value = '';
            try {
                let r = await fetch('/chat',{method:'POST', body:JSON.stringify({p:val}), headers:{'Content-Type':'application/json'}});
                let d = await r.json();
                c.innerHTML += `<div class="msg bot"><b>小龙虾:</b><br>${d.r}</div>`;
            } catch (err) { c.innerHTML += `<div class="msg bot" style="color:red">连接异常。</div>`; }
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
    # 🚨 核心修改：模型名称精准对齐您看到的 gemini-3.1-pro-preview
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": f"你是小龙虾指挥官，负责多伦多Didi Cleaning清洁业务。请回复老板：{user_msg}"}]}]
    }
    
    try:
        res = requests.post(url, json=payload, timeout=20)
        data = res.json()
        if 'candidates' in data:
            reply = data['candidates'][0]['content']['parts'][0]['text']
        else:
            # 这里的报错会告诉我们是不是 API 权限问题
            reply = f"系统反馈：{data.get('error', {}).get('message', '大脑连接中，请稍后')}"
    except:
        reply = "多伦多信号延迟，请老板再试。"
        
    return jsonify({"r": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
