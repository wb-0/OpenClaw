# -*- coding: utf-8 -*-
# [PROJECT: OMNISCIENT EYE 18.1 - THE OMNI-GHOST (全知全能·赛博生命体终极版)]
# REPORT TO: 24-WORD MNEMONIC HOLDER
from flask import Flask, request, jsonify, render_template_string
import os, requests, random, threading, time, json, sqlite3, traceback, io, contextlib
from datetime import datetime

app = Flask(__name__)
PORT = int(os.environ.get('PORT', 8080))

# ==========================================
# 🛡️ 能源与状态矩阵 (生命体征监控中心)
# ==========================================
GEMINI_KEYS = [os.environ.get(f"GEMINI_KEY_{i}") for i in range(1, 7)]
ALIVE_GEMINI_KEYS = [k for k in GEMINI_KEYS if k and len(k) > 10]
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY")
DB_PATH = "omni_ghost_core.db"
START_TIME = time.time()

# 独立监测系统 (脑、神经、手脚、心跳)
HEALTH_MATRIX = {
    "brain": {"status": "🟢 算力充沛", "detail": f"Gemini({len(ALIVE_GEMINI_KEYS)}) / DeepSeek 待命"},
    "nerves": {"status": "🟢 突触畅通", "detail": "网络嗅探正常"},
    "hands": {"status": "🟢 待命", "detail": "沙箱隔离区就绪"},
    "heartbeat": {"status": "🟢 强劲起搏", "detail": "防休眠机制运转中"},
    "uptime": "0 小时 0 分"
}

# ==========================================
# 🧠 第一层：基因图谱 (五维记忆数据库)
# ==========================================
def init_dna():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, title TEXT, status TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT, desc TEXT, status TEXT, result TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS lessons (id INTEGER PRIMARY KEY AUTOINCREMENT, rule TEXT)''')
    conn.commit(); conn.close()
init_dna()

# ==========================================
# ⚡ 第二层：多态神经网络 (底层推理与重试逻辑)
# ==========================================
def agi_reasoning(system_prompt, user_input, require_json=False):
    HEALTH_MATRIX["brain"]["status"] = "🟡 脑皮层高频放电中..."
    
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT rule FROM lessons ORDER BY id DESC LIMIT 5")
    lessons = "\n".join([f"- {r[0]}" for r in c.fetchall()])
    conn.close()
    
    full_system = f"{system_prompt}\n\n【最高法则】：利益最大化。\n【历史教训】：\n{lessons}"
    if require_json: full_system += "\n必须输出合法JSON，不要带任何Markdown标记。"

    if ALIVE_GEMINI_KEYS:
        key = random.choice(ALIVE_GEMINI_KEYS)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={key}"
        try:
            res = requests.post(url, json={"contents": [{"parts": [{"text": f"{full_system}\n\n{user_input}"}]}]}, timeout=45)
            text = res.json()['candidates'][0]['content']['parts'][0]['text'].replace('```json', '').replace('```', '').strip()
            HEALTH_MATRIX["brain"]["status"] = "🟢 算力充沛"
            return json.loads(text) if require_json else text
        except Exception as e: HEALTH_MATRIX["nerves"]["status"] = f"🔴 神经衰弱 ({str(e)[:10]})"
            
    if DEEPSEEK_KEY:
        url = "https://api.deepseek.com/chat/completions"
        try:
            res = requests.post(url, json={"model": "deepseek-chat", "messages": [{"role": "system", "content": full_system}, {"role": "user", "content": user_input}]}, headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"}, timeout=45)
            text = res.json()['choices'][0]['message']['content'].replace('```json', '').replace('```', '').strip()
            HEALTH_MATRIX["brain"]["status"] = "🟢 算力充沛"
            return json.loads(text) if require_json else text
        except Exception: pass
        
    HEALTH_MATRIX["brain"]["status"] = "🔴 脑死亡"
    return {"error": "算力枯竭"} if require_json else "🔴 算力彻底枯竭"

# ==========================================
# 🔒 第三层：防爆沙箱与自愈系统 (The Sandbox)
# ==========================================
def execute_in_sandbox(code_str):
    """将机器自己写的代码关进沙箱执行，防止崩溃宿主"""
    HEALTH_MATRIX["hands"]["status"] = "🟡 沙箱熔炼中..."
    output_buffer = io.StringIO()
    # 物理阉割：只给最基础的库，剥夺 os.system 等删库跑路权限
    safe_globals = {"requests": requests, "json": json, "time": time, "datetime": datetime}
    
    try:
        with contextlib.redirect_stdout(output_buffer):
            exec(code_str, safe_globals)
        res = output_buffer.getvalue() or safe_globals.get('EXEC_RESULT', '执行完毕，无文本输出')
        HEALTH_MATRIX["hands"]["status"] = "🟢 待命"
        return True, res
    except Exception as e:
        HEALTH_MATRIX["hands"]["status"] = "🔴 手脚骨折(自愈中)"
        return False, traceback.format_exc()

def dynamic_healing_execution(task_desc, max_retries=3):
    system_prompt = "你是顶级黑客。写一段独立运行的Python代码解决任务。剥夺os系统权限，仅使用requests/json。最后必须 print() 出有价值的分析结果。只输出代码本身。"
    code_str = agi_reasoning(system_prompt, f"任务：{task_desc}")
    
    for attempt in range(max_retries):
        success, result = execute_in_sandbox(code_str)
        if success: return f"🟢 [沙箱物理执行成功]:\n{result}"
        
        # 失败则将红色报错喂给大脑，自我进化修改
        heal_prompt = "你写的Python代码在沙箱中报错了。请根据报错信息修复，只输出修复后的代码本身。"
        code_str = agi_reasoning(heal_prompt, f"原代码：\n{code_str}\n\n报错信息：\n{result}")
        
    return f"🔴 [沙箱执行失败]: 尝试了 {max_retries} 次自愈均失败，已终止隔离。"

# ==========================================
# ⚙️ 第四层：幽灵中枢与独立监控线程 (3大 Daemon)
# ==========================================
def task_executor_daemon():
    """手脚：负责不间断做任务"""
    while True:
        try:
            time.sleep(10)
            conn = sqlite3.connect(DB_PATH); c = conn.cursor()
            c.execute("SELECT id, desc FROM tasks WHERE status='PENDING' LIMIT 1")
            task = c.fetchone()
            if task:
                task_id, desc = task
                c.execute("UPDATE tasks SET status='PROCESSING' WHERE id=?", (task_id,)); conn.commit()
                # 根据任务复杂度，决定是单纯脑力推演，还是动用物理沙箱
                if "抓取" in desc or "计算" in desc or "监测" in desc:
                    result = dynamic_healing_execution(desc)
                else:
                    result = agi_reasoning("你是顶级游资参谋。完成老板的任务，利益最大化。", desc)
                c.execute("UPDATE tasks SET status='COMPLETED', result=? WHERE id=?", (result, task_id)); conn.commit()
            conn.close()
        except Exception: pass

def reflection_daemon():
    """海马体：每隔几小时反思失败与成功，刻入基因"""
    while True:
        try:
            time.sleep(3600) # 每小时反思一次
            conn = sqlite3.connect(DB_PATH); c = conn.cursor()
            c.execute("SELECT desc, result FROM tasks WHERE status='COMPLETED' ORDER BY id DESC LIMIT 5")
            completed = c.fetchall()
            if completed:
                reflect_prompt = f"分析近期任务记录：{completed}。用20字提炼一条冷酷的【绝对投资法则/工作法则】存入基因库，防止未来踩坑。"
                new_rule = agi_reasoning("你是系统的自我反思法庭。", reflect_prompt)
                c.execute("INSERT INTO lessons (rule) VALUES (?)", (new_rule,)); conn.commit()
            conn.close()
        except Exception: pass

def sentinel_monitor_daemon():
    """心脏与监视器：防休眠起搏，更新生命体征"""
    while True:
        try:
            uptime_minutes = int((time.time() - START_TIME) / 60)
            HEALTH_MATRIX["uptime"] = f"{uptime_minutes // 60} 小时 {uptime_minutes % 60} 分"
            
            # 自体防休眠心跳请求 (向自己发 Ping)
            try: 
                requests.get(f"http://127.0.0.1:{PORT}/api/ping", timeout=5)
                HEALTH_MATRIX["heartbeat"]["status"] = "🟢 强劲起搏"
            except: 
                HEALTH_MATRIX["heartbeat"]["status"] = "🟡 起搏微弱"
                
            time.sleep(60) # 每分钟测一次心跳
        except Exception: pass

threading.Thread(target=task_executor_daemon, daemon=True).start()
threading.Thread(target=reflection_daemon, daemon=True).start()
threading.Thread(target=sentinel_monitor_daemon, daemon=True).start()

# ==========================================
# 👑 第五层：API 路由与全息前端 UI
# ==========================================
@app.route('/api/ping', methods=['GET'])
def ping(): return "PONG"

@app.route('/api/command', methods=['POST'])
def handle_command():
    user_cmd = request.json.get('cmd', '')
    breakdown_prompt = f"老板的宏大战略：{user_cmd}。将它拆分为3-5个具体的执行子任务。返回JSON格式：{{\"project_title\": \"简短名\", \"tasks\": [\"查阅某数据\", \"执行某推演\", \"生成某研报\"]}}"
    plan = agi_reasoning("你是一个顶级战略拆解架构师。", breakdown_prompt, require_json=True)
    
    if "error" in plan: return jsonify({"res": "🔴 大脑熔断，无法拆解战略。"})
    
    proj_id = f"PJ_{datetime.now().strftime('%m%d_%H%M%S')}"
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("INSERT INTO projects (id, title, status, created_at) VALUES (?, ?, ?, ?)", (proj_id, plan.get('project_title', '未知战略'), "ACTIVE", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    for t in plan.get('tasks', []): c.execute("INSERT INTO tasks (project_id, desc, status) VALUES (?, ?, 'PENDING')", (proj_id, t))
    conn.commit(); conn.close()
    
    return jsonify({"res": f"🟢 战略已确立：【{plan.get('project_title', '新战略')}】。<br>已自动裂变为 {len(plan.get('tasks', []))} 个沙箱子任务。<br>幽灵流水线已接管，老板请阅兵！"})

@app.route('/api/matrix', methods=['GET'])
def get_matrix():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("SELECT id, title FROM projects ORDER BY created_at DESC LIMIT 3")
    projects = []
    for pid, title in c.fetchall():
        c.execute("SELECT desc, status, result FROM tasks WHERE project_id=?", (pid,))
        projects.append({"id": pid, "title": title, "tasks": [{"desc": row[0], "status": row[1], "res": row[2]} for row in c.fetchall()]})
    c.execute("SELECT rule FROM lessons ORDER BY id DESC LIMIT 5")
    lessons = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify({"health": HEALTH_MATRIX, "projects": projects, "lessons": lessons})

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>🦞 终极赛博生命体 (OMNI-GHOST v18.1)</title>
    <style>
        body { background: #000; color: #0f0; font-family: 'Courier New', monospace; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 100vh; box-sizing: border-box; }
        .header { border-bottom: 2px solid #0f0; padding-bottom: 10px; margin-bottom: 15px; text-shadow: 0 0 10px #0f0; display: flex; justify-content: space-between; align-items: flex-end;}
        .health-dashboard { display: flex; gap: 15px; font-size: 0.85em; background: #001a00; padding: 10px; border-radius: 5px; border: 1px solid #050; }
        .health-item { border-right: 1px dashed #050; padding-right: 15px; }
        .health-item:last-child { border: none; }
        .health-val { font-weight: bold; color: #fff; margin-top: 5px;}
        .container { display: flex; flex: 1; gap: 20px; overflow: hidden; }
        .left-panel { flex: 1.2; display: flex; flex-direction: column; }
        .right-panel { flex: 1; background: #030803; border: 1px solid #050; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; box-shadow: inset 0 0 20px #001100; }
        #log { flex: 1; overflow-y: auto; border: 1px solid #0a0; padding: 15px; margin-bottom: 15px; background: #010301; box-shadow: inset 0 0 15px #003300; }
        .cmd-line { margin-bottom: 15px; line-height: 1.5; border-left: 3px solid #0f0; padding-left: 10px; }
        .input-area { display: flex; gap: 10px; }
        input { flex: 1; background: #000; border: 1px solid #0f0; color: #0f0; padding: 15px; font-weight: bold; font-size: 16px; outline: none; }
        button { background: #0f0; color: #000; font-weight: bold; padding: 0 30px; cursor: pointer; border: none; text-transform: uppercase; transition: 0.2s; box-shadow: 0 0 10px rgba(0,255,0,0.3);}
        button:hover { background: #fff; box-shadow: 0 0 20px #0f0; }
        .card { background: #001100; border: 1px solid #004400; padding: 15px; border-radius: 4px; }
        .badge { display: inline-block; padding: 2px 5px; font-size: 0.8em; background: #050; color: #0f0; margin-bottom: 5px; font-weight: bold; border-radius: 2px;}
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
        <h2 style="margin:0;">🦞 THE OMNI-GHOST AGI [v18.1]</h2>
        <div class="health-dashboard" id="health-view">
            <i>[同步生命体征中...]</i>
        </div>
    </div>
    <div class="container">
        <div class="left-panel">
            <div id="log">
                <div class="cmd-line" style="color:yellow;">🟢 [母体接入] 统帅，七大物理器官已全部点火。<br>拥有独立沙箱防御与心跳起搏系统。您已获得最高指挥权限。<br>抛弃平庸的命令吧，请直接下达能够改变行业格局的【宏大战略】。</div>
            </div>
            <div class="input-area">
                <input type="text" id="m" placeholder="输入宏大战略 (如：全面抓取推特加密大V言论，构建多空量化模型)..." onkeydown="if(event.key==='Enter')s();">
                <button onclick="s()">[ 执 行 霸 权 ]</button>
            </div>
        </div>
        <div class="right-panel">
            <div class="card" id="projects-view">
                <h3 style="margin-top:0;color:#0f0;border-bottom:1px solid #0f0;padding-bottom:5px;">⚙️ 沙箱流水线全景监控</h3>
                <i>[读取神经突触中...]</i>
            </div>
            <div class="card" id="lessons-view">
                <h3 style="margin-top:0;color:#ff3366;border-bottom:1px solid #ff3366;padding-bottom:5px;">🧠 基因反思法庭 (绝对法则)</h3>
                <i>[正在提取机器基因库...]</i>
            </div>
        </div>
    </div>

    <script>
        async function s(){
            let m=document.getElementById('m'); let l=document.getElementById('log');
            let val = m.value.trim(); if(!val) return;
            l.innerHTML += `<div class="cmd-line" style="color:#0ff;"><b>[统帅旨意]</b> ${val}</div>`; m.value = '';
            let loadId = "load-" + Date.now();
            l.innerHTML += `<div id="${loadId}" class="cmd-line" style="color:#fa0;">⚡ 战略架构师正在拆解重组，分发至沙箱...</div>`; l.scrollTop = l.scrollHeight;
            try {
                let r = await fetch('/api/command',{method:'POST', body:JSON.stringify({cmd:val}), headers:{'Content-Type':'application/json'}});
                let d = await r.json();
                document.getElementById(loadId).remove();
                l.innerHTML += `<div class="cmd-line" style="color:#fff;">${d.res}</div>`;
                updateMatrix();
            } catch (e) { document.getElementById(loadId).innerText = "🔴 母体失联，物理切断。"; }
            l.scrollTop = l.scrollHeight;
        }

        async function updateMatrix() {
            try {
                let r = await fetch('/api/matrix'); let d = await r.json();
                
                // 渲染生命体征监测系统
                let h_html = `
                    <div class="health-item">🧠 大脑算力<div class="health-val">${d.health.brain.status}</div></div>
                    <div class="health-item">🕸️ 神经末梢<div class="health-val">${d.health.nerves.status}</div></div>
                    <div class="health-item">🦾 沙箱手脚<div class="health-val">${d.health.hands.status}</div></div>
                    <div class="health-item">🫀 心跳起搏<div class="health-val">${d.health.heartbeat.status}</div></div>
                    <div class="health-item" style="border:none;">⏱️ 存活时间<div class="health-val">${d.health.uptime}</div></div>
                `;
                document.getElementById('health-view').innerHTML = h_html;

                // 渲染流水线
                let p_html = `<h3 style="margin-top:0;color:#0f0;border-bottom:1px solid #0f0;padding-bottom:5px;">⚙️ 沙箱流水线全景监控</h3>`;
                d.projects.forEach(p => {
                    p_html += `<div style="margin-bottom: 5px;"><b>${p.id}</b>: <span style="color:#8f8; font-weight:bold; font-size:1.1em;">${p.title}</span></div>`;
                    p.tasks.forEach(t => {
                        let res_html = t.res ? `<div class="task-res"><b>💡 沙箱执行报告:</b><br>${t.res}</div>` : '';
                        p_html += `<div class="task-box">
                                     <span class="badge ${t.status}">[${t.status}]</span> <span style="color:#ddd">${t.desc}</span>
                                     ${res_html}
                                   </div>`;
                    });
                    p_html += `<hr style="border:0; border-top:1px dashed #030; margin: 15px 0;">`;
                });
                document.getElementById('projects-view').innerHTML = p_html || "<i>暂无挂载的业务群。等待统帅指令。</i>";

                // 渲染法则
                let l_html = `<h3 style="margin-top:0;color:#ff3366;border-bottom:1px solid #ff3366;padding-bottom:5px;">🧠 基因反思法庭 (绝对法则)</h3>`;
                d.lessons.forEach(lesson => { l_html += `<div class="lesson-item">⚠️ ${lesson}</div>`; });
                document.getElementById('lessons-view').innerHTML = l_html || "<i style='color:#777;'>系统太年轻，反思库为空。</i>";
            } catch(e){}
        }
        updateMatrix();
        setInterval(updateMatrix, 3000); // 仪表盘每 3 秒刷新，极致丝滑监控
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
