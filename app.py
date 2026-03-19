from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)
# 🔑 老板，这是咱们指挥部的核心密钥
API_KEY = "AIzaSyCuK_v86HfsQBGb_AqNmemREEm7s52t-Ho"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>DIDI TORONTO COMMANDER</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: sans-serif; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 95vh; }
        #chat { flex: 1; overflow-y: auto; border: 1px solid #30363d; padding: 15px; border-radius: 6px; background: #161b22; margin-bottom: 20px; }
        .msg { margin-bottom: 12px; padding: 10px; border-radius: 8px; max-width: 85%; font-size: 15px; }
        .user { background: #1f6feb; color: white; align-self: flex-end; margin-left: auto; text-align: right; }
        .bot { background: #21262d; border: 1px solid #30363d; color: #ffa500; }
        .input-area { display: flex; gap: 10px; background: #161b22; padding: 15px; border-top: 1px solid #30363d; }
        input[type="text"] { flex: 1; background: #0d1117; border: 1px solid #30363d; color: white; padding: 12px; border-radius: 6px; outline: none; }
        button { background: #2ea44f; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <h2 style="color:#58a6ff; font-size: 18px;">🦞 DIDI TORONTO - 终极指挥部</h2>
    <div id="chat"><div class="msg bot">指挥部已强制重置！老板，请按回车发送“你好”测试。</div></div>
    <div class="input-area">
        <input type="text" id="m" placeholder="输入指令..." onkeydown="if(event.key==='Enter'){s();event.preventDefault();}">
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
            } catch (err) { c.innerHTML += `<div class="msg bot" style="color:red">连接失败，请检查网络。</div>`; }
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
    # 🚨 换成全球最稳的 v1 接口和 gemini-1.5-flash 模型
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    payload = {"contents": [{"parts": [{"text": f"你是小龙虾，多伦多Didi Cleaning清洁业务助手。请回复老板：{user_msg}"}]}]}
    
    try:
        res = requests.post(url, json=payload, timeout=15)
        data = res.json()
        
        if 'candidates' in data:
            reply = data['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in data:
            # 🛡️ 报错诊断：如果是 API 问题，直接告诉老板原因
            reply = f"【系统提示】Google AI 说：{data['error'].get('message', '未知错误')}"
        else:
            reply = "小龙虾没听清，请老板再试一次。"
    except Exception as e:
        reply = f"【系统提示】网络连接异常：{str(e)}"
        
    return jsonify({"r": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
