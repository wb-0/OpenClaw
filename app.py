from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)
# 🔑 您的金钥匙
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
    <h2 style="color:#58a6ff;">🦞 DIDI TORONTO 指挥部</h2>
    <div id="chat"><div class="msg bot">老板，回车键和 AI 线路已全部加固！我是 Didi Cleaning 的小龙虾，请下达清洁指令。</div></div>
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
    # 🚨 修复 404 的核心：更新 API 地址格式
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    # 🧠 给 AI 注入多伦多 Didi Cleaning 的“生意经”
    prompt = f"""
    你是小龙虾，多伦多 Didi Cleaning 的专属 AI 指挥官。
    你的老板叫“博伟老板”。
    你的业务范围：多伦多、North York、Scarborough、Markham。
    报价参考：
    1. Move-out 清洁：$250 起。
    2. 地毯清洗：$150 起。
    3. 定期保洁：$100 起。
    请根据以下指令回复老板：{user_msg}
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        res = requests.post(url, json=payload, timeout=20)
        res_data = res.json()
        # 增加容错解析
        if 'candidates' in res_data:
            reply = res_data['candidates'][0]['content']['parts'][0]['text']
        else:
            reply = f"AI 线路抖动，请再试一次。(Code: {res.status_code})"
    except Exception as e:
        reply = f"信号丢失: {str(e)}"
    
    return jsonify({"r": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
