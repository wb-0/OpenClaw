from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# 🔑 这就是你的“金钥匙”，有了它就不再需要终端验证了
API_KEY = "AIzaSyCuK_v86HfsQBGb_AqNmemREEm7s52t-Ho"

# 这里的界面我已经为您加固了，确保它能稳定显示
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>DIDI TORONTO COMMANDER</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: sans-serif; padding: 20px; }
        #chat { height: 400px; overflow-y: auto; border: 1px solid #30363d; background: #161b22; padding: 15px; margin-bottom: 20px; }
        input { width: 70%; padding: 10px; background: #0d1117; border: 1px solid #30363d; color: white; }
        button { padding: 10px 20px; background: #238636; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <h2>🦞 DIDI TORONTO AI 指挥部</h2>
    <div id="chat">系统就绪。请直接下达清洁指令。</div>
    <input type="text" id="m" placeholder="输入指令...">
    <button onclick="s()">发送</button>

    <script>
        async function s(){
            let m=document.getElementById('m'); let c=document.getElementById('chat');
            c.innerHTML += '<div><b>老板:</b> ' + m.value + '</div>';
            let r = await fetch('/chat',{method:'POST', body:JSON.stringify({p:m.value}), headers:{'Content-Type':'application/json'}});
            let d = await r.json();
            c.innerHTML += '<div style="color:orange"><b>小龙虾:</b> ' + d.r + '</div>';
            m.value = ''; c.scrollTop = c.scrollHeight;
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
    data = request.json
    user_msg = data.get('p', '')
    # 直接使用 API KEY 请求，绕过所有终端验证
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    payload = {"contents": [{"parts": [{"text": "你是小龙虾助手，多伦多Didi Cleaning清洁业务的AI。请回复老板：" + user_msg}]}]}
    
    try:
        res = requests.post(url, json=payload, timeout=15)
        reply = res.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        reply = "信号连接中，请再试一次。"
    return jsonify({"r": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
