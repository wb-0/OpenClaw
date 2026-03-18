from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# 🔑 博伟老板的专用金钥匙 - 确保 AI 独立运行
API_KEY = "AIzaSyCuK_v86HfsQBGb_AqNmemREEm7s52t-Ho"

# 网页前端设计：包含回车发送监听与多模态交互
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>DIDI TORONTO COMMANDER</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: sans-serif; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 95vh; }
        #chat { flex: 1; overflow-y: auto; border: 1px solid #30363d; padding: 20px; border-radius: 6px; background: #161b22; margin-bottom: 20px; }
        .msg { margin-bottom: 15px; line-height: 1.5; padding: 10px; border-radius: 8px; max-width: 85%; }
        .user { background: #1f6feb; color: white; align-self: flex-end; margin-left: auto; text-align: right; }
        .bot { background: #21262d; border: 1px solid #30363d; color: orange; }
        .input-area { display: flex; gap: 10px; align-items: center; background: #161b22; padding: 15px; border-top: 1px solid #30363d; }
        input[type="text"] { flex: 1; background: #0d1117; border: 1px solid #30363d; color: white; padding: 12px; border-radius: 6px; }
        #file-btn { background: #238636; color: white; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer; }
        button#send-btn { background: #2ea44f; color: white; border: none; padding: 12px 25px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        #preview { max-width: 100px; display: none; margin-bottom: 10px; border-radius: 4px; border: 1px solid #58a6ff; }
    </style>
</head>
<body>
    <h2 style="color:#58a6ff; margin-top:0;">🦞 DIDI TORONTO AI 指挥部</h2>
    <div id="chat">
        <div class="msg bot">老板您好！我是小龙虾。系统已就绪，支持回车发送。您可以发送指令，或上传多伦多现场清洁照片让我分析。</div>
    </div>
    <img id="preview">
    <div class="input-area">
        <input type="file" id="file-input" style="display:none" accept="image/*,video/*,application/pdf">
        <button id="file-btn" title="上传文件" onclick="document.getElementById('file-input').click()">➕</button>
        <input type="text" id="m" placeholder="输入指令后按回车发送..." autocomplete="off">
        <button id="send-btn" onclick="s()">发送</button>
    </div>

    <script>
        let fileBase64 = "";
        let fileType = "";

        // 监听回车键发送指令
        document.getElementById('m').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                s();
            }
        });

        document.getElementById('file-input').onchange = function(e) {
            let file = e.target.files[0];
            let reader = new FileReader();
            reader.onload = function() {
                fileBase64 = reader.result.split(',')[1];
                fileType = file.type;
                if(fileType.includes('image')) {
                    document.getElementById('preview').src = reader.result;
                    document.getElementById('preview').style.display = 'block';
                }
            };
            reader.readAsDataURL(file);
        };

        async function s(){
            let m=document.getElementById('m'); let c=document.getElementById('chat');
            let val = m.value.trim();
            if(!val && !fileBase64) return;
            
            c.innerHTML += `<div class="msg user">${val} ${fileBase64 ? '<br>[已上传媒体文件]' : ''}</div>`;
            c.scrollTop = c.scrollHeight;
            
            let payload = { p: val, file: fileBase64, type: fileType };
            m.value = ''; fileBase64 = ''; fileType = '';
            document.getElementById('preview').style.display = 'none';

            try {
                let r = await fetch('/chat',{
                    method:'POST', 
                    body:JSON.stringify(payload), 
                    headers:{'Content-Type':'application/json'}
                });
                let d = await r.json();
                c.innerHTML += `<div class="msg bot"><b>小龙虾:</b><br>${d.r}</div>`;
            } catch (err) {
                c.innerHTML += `<div class="msg bot" style="color:red">连接超时，请检查多伦多网络信号。</div>`;
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
    data = request.json
    user_msg = data.get('p', '')
    file_data = data.get('file', '')
    mime_type = data.get('type', '')

    # 使用 Gemini 1.5 Flash 接口，支持多模态分析
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    
    system_instruction = "你是小龙虾助手，多伦多 Didi Cleaning 的 AI 指挥官。负责 Move-out、地毯清洗等业务咨询。请专业且简洁地回复老板："
    
    parts = [{"text": f"{system_instruction} {user_msg}"}]
    if file_data:
        parts.append({"inline_data": {"mime_type": mime_type, "data": file_data}})

    payload = {"contents": [{"parts": parts}]}
    
    try:
        res = requests.post(url, json=payload, timeout=30)
        res_json = res.json()
        # 增加安全解析，防止 candidates 报错
        if 'candidates' in res_json:
            reply = res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            reply = "接收到异常信号，请稍后再试。"
    except Exception as e:
        reply = f"系统处理错误: {str(e)}"
    
    return jsonify({"r": reply})

if __name__ == "__main__":
    # 适配 Cloud Run 动态端口
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
