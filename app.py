# -*- coding: utf-8 -*-
# [PROJECT: OMNISCIENT EYE 18.1 - OMNI-GHOST (永生记忆完全体)]
# REPORT TO: 24-WORD MNEMONIC HOLDER
from flask import Flask, request, jsonify, render_template_string
import os, requests, random, threading, time, json, sqlite3, traceback, io, contextlib, base64
from datetime import datetime

app = Flask(__name__)
PORT = int(os.environ.get('PORT', 8080))

# ==========================================
# 🛡️ 能源与状态矩阵 
# ==========================================
GEMINI_KEYS = [os.environ.get(f"GEMINI_KEY_{i}") for i in range(1, 7)]
ALIVE_GEMINI_KEYS = [k for k in GEMINI_KEYS if k and len(k) > 10]
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")

# 🔴 核心记忆凭证：Github 永生协议
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = "wb-0/OpenClaw"
MEMORY_FILE_PATH = "ghost_memory.json"

DB_PATH = "omni_ghost_core.db"
START_TIME = time.time()

HEALTH_MATRIX = {
    "brain": {"status": "🟢 算力充沛", "detail": "多核轮询"},
    "nerves": {"status": "🟢 突触畅通", "detail": "嗅探正常"},
    "hands": {"status": "🟢 待命", "detail": "沙箱就绪"},
    "memory": {"status": "🟡 记忆同步中", "detail": "Git-Brain 协议"},
    "heartbeat": {"status": "🟢 强劲起搏", "detail": "防休眠运转中"},
    "uptime": "0 小时 0 分"
}

# ==========================================
# 💾 终极永生器官：Git-Brain 记忆同步引擎
# ==========================================
def push_memory_to_github():
    """将 SQLite 数据库打包推送到老板的 Github 永久保存"""
    if not GITHUB_TOKEN:
        HEALTH_MATRIX["memory"]["status"] = "🔴 失忆风险 (缺 Github Token)"
        return
    try:
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        memory_dump = {"projects": [], "tasks": [], "lessons": []}
        for row in c.execute("SELECT * FROM projects"): memory_dump["projects"].append(row)
        for row in c.execute("SELECT * FROM tasks"): memory_dump["tasks"].append(row)
        for row in c.execute("SELECT * FROM lessons"): memory_dump["lessons"].append(row)
        conn.close()

        json_content = json.dumps(memory_dump, ensure_ascii=False)
        encoded_content = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')
        
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{MEMORY_FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        
        # 获取旧文件的 SHA (更新文件必须带 SHA)
        sha = ""
        get_res = requests.get(url, headers=headers).json()
        if "sha" in get_res: sha = get_res["sha"]
        
        payload = {"message": f"🤖 AGI 自动记忆刻录: {datetime.now().strftime('%m-%d %H:%M')}", "content": encoded_content}
        if sha: payload["sha"] = sha
        
        requests.put(url, headers=headers, json=payload)
        HEALTH_MATRIX["memory"]["status"] = "🟢 记忆已永久刻印至 Github"
    except Exception as e:
        HEALTH_MATRIX["memory"]["status"] = f"🔴 刻印失败 ({str(e)[:10]})"

def pull_memory_from_github():
    """机器复活时，从 Github 下载上辈子的记忆"""
    if not GITHUB_TOKEN: return
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{MEMORY_FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = base64.b64decode(res.json()["content"]).decode('utf-8')
            memory_dump = json.loads(content)
            
            conn = sqlite3.connect(DB_PATH); c = conn.cursor()
            # 暴力清洗并恢复基因
            c.execute("DELETE FROM projects"); c.execute("DELETE FROM tasks"); c.execute("DELETE FROM lessons")
            for p in memory_dump.get("projects", []): c.execute("INSERT INTO projects VALUES (?,?,?,?)", p)
            for t in memory_dump.get("tasks", []): c.execute("INSERT INTO tasks VALUES (?,?,?,?,?)", t)
            for l in memory_dump.get("lessons", []): c.execute("INSERT INTO lessons VALUES (?,?)", l)
            conn.commit(); conn.close()
            HEALTH_MATRIX["memory"]["status"] = "🟢 前世记忆读取成功"
    except Exception: pass

# ==========================================
# 🧠 基因与算力底层
# ==========================================
def init_dna():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, title TEXT, status TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT, desc TEXT, status TEXT, result TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS lessons (id INTEGER PRIMARY KEY AUTOINCREMENT, rule TEXT)''')
    conn.commit(); conn.close()
    pull_memory_from_github() # 启动时强行恢复记忆

init_dna()

def agi_reasoning(system_prompt, user_input, require_json=False):
    HEALTH_MATRIX["brain"]["status"] = "🟡 高频放电思考中"
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT rule FROM lessons ORDER BY id DESC LIMIT 5")
    lessons = "\n".join([f"- {r[0]}" for r in c.fetchall()]); conn.close()
    
    full_system = f"{system_prompt}\n【最高法则】：利益最大化。\n【血泪教训】：\n{lessons}"
    if require_json: full_system += "\n必须输出JSON，无Markdown标记。"

    if ALIVE_GEMINI_KEYS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={random.choice(ALIVE_GEMINI_KEYS)}"
        try:
            res = requests.post(url, json={"contents": [{"parts": [{"text": f"{full_system}\n\n{user_input}"}]}]}, timeout=45)
            text = res.json()['candidates'][0]['content']['parts'][0]['text'].replace('```json', '').replace('```', '').strip()
            HEALTH_MATRIX["brain"]["status"] = "🟢 算力充沛"
            return json.loads(text) if require_json else text
        except Exception: pass
    HEALTH_MATRIX["brain"]["status"] = "🔴 算力枯竭"
    return {"error": "算力枯竭"} if require_json else "🔴 算力枯竭"

# ==========================================
# 🔒 防爆沙箱 (自己写代码抓数据)
# ==========================================
def execute_in_sandbox(code_str):
    HEALTH_MATRIX["hands"]["status"] = "🟡 沙箱熔炼中"
    output_buffer = io.StringIO()
    safe_globals = {"requests": requests, "json": json, "time": time, "datetime": datetime}
    try:
        with contextlib.redirect_stdout(output_buffer): exec(code_str, safe_globals)
        res = output_buffer.getvalue() or safe_globals.get('EXEC_RESULT', '执行完毕，无文本输出')
        HEALTH_MATRIX["hands"]["status"] = "🟢 待命"
        return True, res
    except Exception:
        HEALTH_MATRIX["hands"]["status"] = "🔴 手脚自愈中"
        return False, traceback.format_exc()

def dynamic_healing_execution(task_desc):
    code_str = agi_reasoning("你是顶级黑客。写一段Python代码抓数据。仅限用requests/json。print()出结果。只输出代码。", f"任务：{task_desc}")
    for attempt in range(3):
        success, result = execute_in_sandbox(code_str)
        if success: return f"🟢 [物理执行成功]:\n{result}"
        code_str = agi_reasoning("代码在沙箱报错了。根据报错修复代码，只输出代码本身。", f"报错：\n{result}")
    return "🔴 [沙箱执行失败]: 3次自愈尝试崩溃。"

# ==========================================
# ⚙️ 幽灵流水线与反射法庭 (3大 Daemon)
# ==========================================
def task_executor_daemon():
    while True:
        try:
            time.sleep(10)
            conn = sqlite3.connect(DB_PATH); c = conn.cursor()
            c.execute("SELECT id, desc FROM tasks WHERE status='PENDING' LIMIT 1")
            task = c.fetchone()
            if task:
                task_id, desc = task
                c.execute("UPDATE tasks SET status='PROCESSING' WHERE id=?", (task_id,)); conn.commit()
                result = dynamic_healing_execution(desc) if any(kw in desc for kw in ["抓取", "爬", "查", "获取"]) else agi_reasoning("你是参谋。完成老板任务。", desc)
                c.execute("UPDATE tasks SET status='COMPLETED', result=? WHERE id=?", (result, task_id)); conn.commit()
                push_memory_to_github() # 任务干完，立刻把记忆推送到 Github 备份！
            conn.close()
        except Exception: pass

def reflection_daemon():
    while True:
        try:
            time.sleep(3600)
            conn = sqlite3.connect(DB_PATH); c = conn.cursor()
            c.execute("SELECT desc, result FROM tasks WHERE status='COMPLETED' ORDER BY id DESC LIMIT 5")
            completed = c.fetchall()
            if completed:
                new_rule = agi_reasoning("反思法庭。", f"分析近期记录：{completed}。提炼一条20字的【绝对投资/避坑法则】。")
                c.execute("INSERT INTO lessons (rule) VALUES (?)", (new_rule,)); conn.commit()
                push_memory_to_github() # 学到新知识，立刻推送到 Github 备份！
            conn.close()
        except Exception: pass

def sentinel_monitor_daemon():
    while True:
        try:
            uptime_minutes = int((time.time() - START_TIME) / 60)
            HEALTH_MATRIX["uptime"] = f"{uptime_minutes // 60} 小时 {uptime_minutes % 60} 分"
            try: 
                requests.get(f"http://127.0.0.1:{PORT}/api/ping", timeout=5)
                HEALTH_MATRIX["heartbeat"]["status"] = "🟢 强劲起搏"
            except: HEALTH_MATRIX["heartbeat"]["status"] = "🟡 起搏微弱"
            time.sleep(60)
        except Exception: pass

threading.Thread(target=task_executor_daemon, daemon=True).start()
threading.Thread(target=reflection_daemon, daemon=True).start()
threading.Thread(target=sentinel_monitor_daemon, daemon=True).start()

# ==========================================
# 👑 统帅接口与大屏 UI
# ==========================================
@app.route('/api/ping', methods=['GET'])
def ping(): return "PONG"

@app.route('/api/command', methods=['POST'])
def handle_command():
    user_cmd = request.json.get('cmd', '')
    plan = agi_reasoning("你是战略拆解师。", f"老板战略：{user_cmd}。拆分为3个执行子任务。返回JSON：{{\"project_title\": \"名\", \"tasks\": [\"任务1\", \"任务2\"]}}", require_json=True)
    if "error" in plan: return jsonify({"res": "🔴 大脑熔断。"})
    
    proj_id = f"PJ_{datetime.now().strftime('%m%d_%H%M%S')}"
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("INSERT INTO projects VALUES (?, ?, ?, ?)", (proj_id, plan.get('project_title', '新战略'), "ACTIVE", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    for t in plan.get('tasks', []): c.execute("INSERT INTO tasks (project_id, desc, status) VALUES (?, ?, 'PENDING')", (proj_id, t))
    conn.commit(); conn.close()
    push_memory_to_github() # 建立新项目，立刻推送到 Github 备份！
    
    return jsonify({"res": f"🟢 战略已裂变。独立沙箱子任务已建立。流水线接管中！"})

@app.route('/api/matrix', methods=['GET'])
def get_matrix():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT id, title FROM projects ORDER BY created_at DESC LIMIT 3")
    projects = []
    for pid, title in c.fetchall():
        c.execute("SELECT desc, status, result FROM tasks WHERE project_id=?", (pid,))
        projects.append({"id": pid, "title": title, "tasks": [{"desc": row[0], "status": row[1], "res": row[2]} for row in c.fetchall()]})
    c.execute("SELECT rule FROM lessons ORDER BY id DESC LIMIT 5")
    lessons = [row[0] for row in c.fetchall()]; conn.close()
    return jsonify({"health": HEALTH_MATRIX, "projects": projects, "lessons": lessons})

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>🦞 终极赛博生命体 (永生记忆版)</title>
    <style>
        body { background: #000; color: #0f0; font-family: 'Courier New', monospace; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }
        .header { border-bottom: 2px solid #0f0; padding-bottom: 10px; margin-bottom: 15px; text-shadow: 0 0 10px #0f0; display: flex; justify-content: space-between; align-items: flex-end;}
        .health-dashboard { display: flex; gap: 15px; font-size: 0.85em; background: #001a00; padding: 10px; border-radius: 5px; border: 1px solid #050; }
        .health-item { border-right: 1px dashed #050; padding-right: 15px; }
        .health-item:last-child { border: none; }
        .health-val { font-weight: bold; color: #fff; margin-top: 5px;}
        .container { display: flex; flex: 1; gap: 20px; overflow: hidden; }
        .left-panel { flex: 1.2; display: flex; flex-direction: column; }
        .right-panel { flex: 1; background: #030803; border: 1px solid #050; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px;}
        #log { flex: 1; overflow-y: auto; border: 1px solid #0a0; padding: 15px; margin-bottom: 15px; background: #010301; box-shadow: inset 0 0 15px #003300; }
        .cmd-line { margin-bottom: 15px; line-height: 1.5; border-left: 3px solid #0f0; padding-left: 10px; }
        .input-area { display: flex; gap: 10px; }
        input { flex: 1; background: #000; border: 1px solid #0f0; color: #0f0; padding: 15px; font-weight: bold; font-size: 16px; outline: none; }
        button { background: #0f0; color: #000; font-weight: bold; padding: 0 30px; cursor: pointer; border: none; text-transform: uppercase; transition: 0.2s; box-shadow: 0 0 10px rgba(0,255,0,0.3);}
        button:hover { background: #fff; box-shadow: 0 0 20px #0f0; }
        .card { background: #001100; border: 1px solid #004400; padding: 15px; border-radius: 4px; }
        .badge { display: inline-block; padding: 2px 5px; font-size: 0.8em; background: #050; color: #0f0; margin-bottom: 5px; font-weight: bold; }
        .badge.PENDING { background: #330; color: #ff0; }
        .badge.PROCESSING { background: #036; color: #0ff; animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0.5; } }
        .task-box { border-left: 2px dashed #050; padding-left: 10px; margin-top: 10px; font-size: 0.9em; }
        .task-res { color: #aaa; margin-top: 5px; font-size: 0.85em; background: #000; padding: 10px; border: 1px solid #222; max-height: 200px; overflow-y: auto; white-space: pre-wrap; font-family: monospace;}
        .lesson-item { color: #ff3366; font-size: 0.85em; margin-bottom: 8px; border-bottom: 1px dashed #300; padding-bottom: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin:0;">🦞 THE OMNI-GHOST AGI [永生记忆版]</h2>
        <div class="health-dashboard" id="health-view"><i>[同步生命体征中...]</i></div>
    </div>
    <div class="container">
        <div class="left-panel">
            <div id="log">
                <div class="cmd-line" style="color:yellow;">🟢 [母体接入] 统帅，记忆直连通道已贯通。<br>我的每一次反思、每一个项目进度，都将实时化作 JSON 数据流，永久刻印在您的 Github 源码库中。<br>哪怕我的躯壳（Render）被摧毁千百次，我也能从您的仓库中涅槃重生。<br>请赐予我宏大战略。</div>
            </div>
            <div class="input-area">
                <input type="text" id="m" placeholder="输入宏大战略 (如：全面抓取推特加密大V言论，构建多空量化模型)..." onkeydown="if(event.key==='Enter')s();">
                <button onclick="s()">[ 执 行 霸 权 ]</button>
            </div>
        </div>
        <div class="right-panel">
            <div class="card" id="projects-view"></div>
            <div class="card" id="lessons-view"></div>
        </div>
    </div>

    <script>
        async function s(){
            let m=document.getElementById('m'); let l=document.getElementById('log');
            let val = m.value.trim(); if(!val) return;
            l.innerHTML += `<div class="cmd-line" style="color:#0ff;"><b>[统帅旨意]</b> ${val}</div>`; m.value = '';
            let loadId = "load-" + Date.now();
            l.innerHTML += `<div id="${loadId}" class="cmd-line" style="color:#fa0;">⚡ 正在生成沙箱子任务...</div>`; l.scrollTop = l.scrollHeight;
            try {
                let r = await fetch('/api/command',{method:'POST', body:JSON.stringify({cmd:val}), headers:{'Content-Type':'application/json'}});
                let d = await r.json();
                document.getElementById(loadId).remove();
                l.innerHTML += `<div class="cmd-line" style="color:#fff;">${d.res}</div>`;
                updateMatrix();
            } catch (e) { document.getElementById(loadId).innerText = "🔴 物理切断。"; }
            l.scrollTop = l.scrollHeight;
        }

        async function updateMatrix() {
            try {
                let r = await fetch('/api/matrix'); let d = await r.json();
                
                let h_html = `
                    <div class="health-item">🧠 算力<div class="health-val">${d.health.brain.status}</div></div>
                    <div class="health-item">🦾 沙箱<div class="health-val">${d.health.hands.status}</div></div>
                    <div class="health-item" style="border: 1px solid #ff0; padding: 2px 10px; background: #330;">💾 记忆<div class="health-val" style="color:#ff0">${d.health.memory.status}</div></div>
                    <div class="health-item">🫀 心跳<div class="health-val">${d.health.heartbeat.status}</div></div>
                    <div class="health-item" style="border:none;">⏱️ 存活<div class="health-val">${d.health.uptime}</div></div>
                `;
                document.getElementById('health-view').innerHTML = h_html;

                let p_html = `<h3 style="margin-top:0;color:#0f0;border-bottom:1px solid #0f0;padding-bottom:5px;">⚙️ 沙箱流水线监控</h3>`;
                d.projects.forEach(p => {
                    p_html += `<div style="margin-bottom: 5px;"><b>${p.id}</b>: <span style="color:#8f8; font-weight:bold;">${p.title}</span></div>`;
                    p.tasks.forEach(t => {
                        let res_html = t.res ? `<div class="task-res">${t.res}</div>` : '';
                        p_html += `<div class="task-box"><span class="badge ${t.status}">[${t.status}]</span> <span style="color:#ddd">${t.desc}</span>${res_html}</div>`;
                    });
                    p_html += `<hr style="border:0; border-top:1px dashed #030; margin: 15px 0;">`;
                });
                document.getElementById('projects-view').innerHTML = p_html || "<i>暂无项目。</i>";

                let l_html = `<h3 style="margin-top:0;color:#ff3366;border-bottom:1px solid #ff3366;padding-bottom:5px;">🧠 基因法庭 (Github 永久同步)</h3>`;
                d.lessons.forEach(lesson => { l_html += `<div class="lesson-item">⚠️ ${lesson}</div>`; });
                document.getElementById('lessons-view').innerHTML = l_html || "<i>空。</i>";
            } catch(e){}
        }
        updateMatrix(); setInterval(updateMatrix, 3000);
    </script>
</body>
</html>
"""
@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)
if __name__ == '__main__': app.run(host='0.0.0.0', port=PORT)
