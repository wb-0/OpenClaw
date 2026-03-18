from flask import Flask
import requests

app = Flask(__name__)

API_KEY = "AIzaSyCuK_v86HfsQBGb_AqNmemREEm7s52t-Ho"

def ask_ai():
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

    data = {
        "contents": [{"parts": [{"text": "写一条吸引人的多伦多清洁广告"}]}]
    }

    res = requests.post(url, json=data)
    result = res.json()

    try:
        return result['candidates'][0]['content']['parts'][0]['text']
    except:
        return "AI出错"

@app.route('/')
def run():
    result = ask_ai()
    print(result)
    return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
