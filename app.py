from flask import Flask, request, jsonify, render_template_string
import os
import requests

app = Flask(__name__)

# 🛡️ 密钥配置：从 Render 环境变量读取
# 请在 Render 设置中添加 GEMINI_API_KEY 或 DEEPSEEK_API_KEY
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>小龙虾 18.1 - 游资印钞机 (云端版)</title>
    <style>
        body { background: #000; color: #0f0; font-family: 'Courier New', monospace; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }
        #log { flex: 1; overflow-y: auto; border: 1px solid #0f0; padding: 15px; background: #010; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 0 15px rgba(0,255,0,0.2); }
        .cmd-line { margin-bottom: 10px; line-height: 1.4; border-left: 3px solid #0f0; padding-left: 10px; }
        .input-area { display: flex; gap: 10px; }
        input { flex: 1; background: #000; border: 1px solid #0f0; color: #0f0; padding: 15px; border-radius: 4px; outline: none; font-size: 16px; }
        button { background: #0f0; color: #000; border: none; padding: 0 30px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .status { color: yellow; font-weight: bold; }
    </style>
</head>
<body>
    <h2 style="text-align: center; text-shadow: 0 0 10px #0f0;">🦞 小龙虾 18.1 - 游资核心执行系统</h2>
    <div id="log">
        <div class="cmd-line">[系统] 云端引擎已点火...</div>
        <div class="cmd-line">[状态] <span class="status">全自动挂机监控中...</span></div>
        <div class="cmd-line">老板好！请下达投资分析指令或输入股票代码。</div>
    </div>
    <div class="input-area">
        <input type="text" id="m" placeholder="输入指令 (例如: 分析美股 NVIDIA 趋势)" onkeydown="if(event.key==='Enter')s();">
        <button onclick="s()">执行</button>
    </div>
    <script>
        async function s(){
            let m=document.getElementById('m'); let l=document.getElementById('log');
            let val = m.value.trim(); if(!val) return;
            l.innerHTML += `<div class="cmd-line">[指令] ${val}</div>`;
            m.value = '';
            let loadingId = "load-" + Date.now();
            l.innerHTML += `<div id="${loadingId}" class="cmd-line" style="color:yellow">⚡ 正在调用 DeepSeek/Gemini 专家大脑分析中...</div>`;
            l.scrollTop = l.scrollHeight;
            try {
                let r = await fetch('/chat',{method:'POST', body:JSON.stringify({p:val}), headers:{'Content-Type':'application/json'}});
                let d = await r.json();
                document.getElementById(loadingId).remove();
                l.innerHTML += `<div class="cmd-line" style="color:#fff"><b>[报告]</b><br>${d.r.replace(/\\n/g, '<br>')}</div>`;
            } catch (err) { document.getElementById(loadingId).innerText = "❌ 信号中断，请检查 API KEY 环境变量。"; }
            l.scrollTop = l.scrollHeight;
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
    # 优先使用 DeepSeek，没有则用 Gemini
    if DEEPSEEK_KEY:
        url = "https://api.deepseek.com" # 假设是标准 OpenAI 格式
        headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}"}
        payload = {"model": "deepseek-chat", "messages": [{"role": "system", "content": "你是一个顶级游资操盘手，擅长技术面和筹码面分析。"}, {"role": "user", "content": user_msg}]}
        res = requests.post(url, json=payload)
        reply = res.json()['choices'][0]['message']['content']
    elif GEMINI_KEY:
        url = f"https://generativelanguage.googleapis.com{GEMINI_KEY}"
        payload = {"contents": [{"parts": [{"text": f"你是一个顶级游资操盘手: {user_msg}"}]}]}
        res = requests.post(url, json=payload)
        reply = res.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        reply = "错误：未检测到任何 AI 大脑密钥 (DEEPSEEK_KEY 或 GEMINI_KEY)。"
    return jsonify({"r": reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
