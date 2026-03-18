from flask import Flask, request
import requests

app = Flask(__name__)

API_KEY = "把你的 Gemini API Key 贴这里"

def ask_ai(message):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

    data = {
        "contents": [{"parts": [{"text": message}]}]
    }

    res = requests.post(url, json=data)
    result = res.json()

    try:
        return result['candidates'][0]['content']['parts'][0]['text']
    except:
        return "AI 出错"

# 定义聊天接口
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    # GET方式从url参数获取 message
    message = request.args.get("message", "你好")
    answer = ask_ai(message)
    return answer

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
