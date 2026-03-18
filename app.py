from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 博伟老板的 Key
API_KEY = "AIzaSyCuK_v86HfsQBGb_AqNmemREEm7s52t-Ho"

@app.route('/')
def index():
    # 这样访问根目录就不会报 404 了
    return "<h1>🦞 DIDI TORONTO - 指挥部已上线</h1><p>系统正常运行中，等待老板指令...</p>"

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('p', '你好')
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    data = {"contents": [{"parts": [{"text": "你是小龙虾助手，多伦多Didi Cleaning清洁业务的AI。请回复：" + user_msg}]}]}
    try:
        res = requests.post(url, json=data, timeout=10)
        reply = res.json()['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"r": reply})
    except Exception as e:
        return jsonify({"r": f"信号中断: {str(e)}"})

if __name__ == "__main__":
    # Cloud Run 的核心：必须读取 PORT 环境变量
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
