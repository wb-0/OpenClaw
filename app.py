# 小龙虾 15.2 - 核心执行引擎 (app.py) - 【赛博游资·实时全自动盯盘版】

import os
import time
import threading
import yfinance as yf
from flask import Flask, request, jsonify, render_template_string
from supabase import create_client, Client
import google.generativeai as genai
from datetime import datetime

# --- 1. 初始化系统 ---
app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
if all([SUPABASE_URL, SUPABASE_KEY]):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. 内存缓存 (用于存放实时警报) ---
# 保留最近的 15 条雷达警报
RADAR_LOGS = [{"time": datetime.now().strftime("%H:%M:%S"), "msg": "系统启动，赛博游资雷达预热中...", "type": "info"}]
IS_RADAR_ON = False # 雷达总开关
# 盯盘股票池 (可以随时扩充，这里精选三大市场代表)
WATCH_LIST = {
    "A股_茅台": "600519.SS", 
    "A股_东方财富": "300059.SZ", # 券商情绪龙头
    "美股_英伟达": "NVDA",
    "美股_特斯拉": "TSLA",
    "港股_腾讯": "0700.HK"
}

def add_log(msg, log_type="info"):
    time_str = datetime.now().strftime("%H:%M:%S")
    RADAR_LOGS.insert(0, {"time": time_str, "msg": msg, "type": log_type})
    if len(RADAR_LOGS) > 15:
        RADAR_LOGS.pop()

# --- 3. 核心功能：全自动游资异动嗅探器 ---
def analyze_anomaly_with_ai(ticker, market_name, anomaly_desc, recent_data):
    """当发生异动时，AI 自动介入进行游资战法推演"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest') # 盯盘要快，用 flash
        prompt = f"""
        你现在是 A股/美股 顶级短线游资操盘手。
        标的：{market_name} ({ticker}) 刚刚触发了实时雷达警报！
        警报原因：【{anomaly_desc}】
        
        以下是最近的分钟级量价切片数据：
        {recent_data}
        
        请用极度精炼、冷酷的游资视角（字数控制在150字以内），立刻判断：
        这是主升浪启动/洗盘/还是诱多出货？是否建议打板/追入？止损位设在哪里？
        """
        response = model.generate_content(prompt)
        ai_advice = response.text.replace('\n', ' ') # 压缩成一段
        
        # 记录到记忆库备查
        if supabase:
            supabase.table('claw15_memory').insert({"content": f"标的:{ticker}\n异动:{anomaly_desc}\n研判:{ai_advice}", "metadata": {"source": "auto_radar"}}).execute()
        
        add_log(f"🧠 [AI研判 - {market_name}]：{ai_advice}", "ai")
    except Exception as e:
        add_log(f"❌ AI 研判异常: {str(e)}", "error")

def sweep_market():
    """雷达扫描核心算法 (由前端心跳触发)"""
    global IS_RADAR_ON
    if not IS_RADAR_ON:
        return
        
    for name, ticker in WATCH_LIST.items():
        try:
            # 获取最近 1 天，间隔 5 分钟的真实数据
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d", interval="5m")
            
            if len(hist) < 2:
                continue # 数据不足跳过
                
            last_close = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            last_vol = hist['Volume'].iloc[-1]
            prev_vol = hist['Volume'].iloc[-2]
            
            # 计算异动指标
            price_change_pct = ((last_close - prev_close) / prev_close) * 100
            
            # 游资异动算法滤网 (参数可调，这里为演示设置得较敏感)
            # 1. 价格急速拉升 (5分钟内涨幅大于 1.5%)
            if price_change_pct > 1.5:
                anomaly = f"直线拉升！5分钟急涨 {price_change_pct:.2f}% (现价: {last_close:.2f})"
                add_log(f"🚨 [发现异动 - {name}]：{anomaly}", "alert")
                # 开新线程让 AI 分析，不阻塞雷达继续扫描
                threading.Thread(target=analyze_anomaly_with_ai, args=(ticker, name, anomaly, hist.tail(3).to_string())).start()
                
            # 2. 突然放量 (当前 5分钟量 是 上一个 5分钟量的 3倍以上)
            elif prev_vol > 0 and (last_vol / prev_vol) > 3.0:
                anomaly = f"异常放量！成交量骤增 {(last_vol/prev_vol):.1f} 倍 (现价: {last_close:.2f})"
                add_log(f"⚠️ [量价异动 - {name}]：{anomaly}", "alert")
                threading.Thread(target=analyze_anomaly_with_ai, args=(ticker, name, anomaly, hist.tail(3).to_string())).start()
            
            # 如果没有异动，静默，不发垃圾消息
        except Exception as e:
            # 静默处理单个股票的报错，防止刷屏
            pass 

# --- 4. API 接口 (供前端大屏调用) ---

@app.route('/toggle_radar', methods=['POST'])
def toggle_radar():
    global IS_RADAR_ON
    data = request.json
    IS_RADAR_ON = data.get('status', False)
    status_str = "开启" if IS_RADAR_ON else "关闭"
    add_log(f"⚙️ 指挥官已将雷达系统 {status_str}", "info")
    return jsonify({"status": "success", "is_on": IS_RADAR_ON})

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    """前端起搏器每 15 秒调用一次此接口，驱动雷达扫描并获取最新日志"""
    if IS_RADAR_ON:
        # 在后台线程执行扫描，防止前端请求超时
        threading.Thread(target=sweep_market).start()
    
    return jsonify({"logs": RADAR_LOGS, "is_on": IS_RADAR_ON})

# 原有的手动分析接口保留
@app.route('/execute_task', methods=['POST'])
def handle_task():
    return jsonify({"status": "error", "message": "已升级为自动雷达版，请使用网页雷达面板控制。"})

# --- 5. 游资专属可视化战情大屏 (黑客帝国风) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>🦞 赛博游资 · 全息盯盘中心</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Courier New', Courier, monospace; background-color: #050505; color: #00ff00; margin: 0; padding: 15px; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        h1 { margin: 0 0 10px 0; font-size: 24px; color: #00ff00; text-shadow: 0 0 5px #00ff00; border-bottom: 1px solid #333; padding-bottom: 10px; display: flex; justify-content: space-between; align-items: center;}
        
        .radar-controls { display: flex; gap: 15px; margin-bottom: 15px; background: #111; padding: 15px; border: 1px solid #333; border-radius: 5px;}
        .target-list { flex-grow: 1; font-size: 14px; color: #888; }
        .target-list span { color: #00ff00; margin-right: 10px; }
        
        /* 雷达开关按钮 */
        .switch { position: relative; display: inline-block; width: 60px; height: 34px; }
        .switch input { opacity: 0; width: 0; height: 0; }
        .slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #333; transition: .4s; border-radius: 34px; }
        .slider:before { position: absolute; content: ""; height: 26px; width: 26px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
        input:checked + .slider { background-color: #ff0000; box-shadow: 0 0 10px #ff0000;}
        input:checked + .slider:before { transform: translateX(26px); }
        .radar-label { font-size: 18px; font-weight: bold; margin-left: 10px; line-height: 34px; color: #fff;}
        .radar-on-text { color: #ff0000; text-shadow: 0 0 5px #ff0000; animation: blink 1s infinite; }
        @keyframes blink { 50% { opacity: 0.5; } }

        /* 滚动日志区 */
        #terminal { flex-grow: 1; background: #000; border: 1px solid #333; padding: 10px; overflow-y: auto; display: flex; flex-direction: column-reverse; /* 新消息在下面 */ }
        .log-line { margin-bottom: 8px; font-size: 15px; line-height: 1.4; border-bottom: 1px dashed #222; padding-bottom: 5px;}
        .time { color: #888; font-size: 12px; margin-right: 10px; }
        .type-info { color: #00aa00; }
        .type-alert { color: #ff0000; font-weight: bold; background: rgba(255,0,0,0.1); }
        .type-ai { color: #00ffff; }
        .type-error { color: #ff00ff; }
    </style>
</head>
<body>
    <h1>
        <span>🦞 赛博游资核心 (V15.2)</span>
        <span style="font-size:14px; color:#888;" id="pulse-indicator">● 信号连接中...</span>
    </h1>

    <div class="radar-controls">
        <div>
            <label class="switch">
                <input type="checkbox" id="radar-toggle" onchange="toggleRadar(this.checked)">
                <span class="slider"></span>
            </label>
            <span class="radar-label" id="radar-status-text">全域雷达：休眠中</span>
        </div>
        <div class="target-list">
            <div><strong>[ 锁定目标池 ]</strong></div>
            <span>🇨🇳 贵州茅台</span> <span>🇨🇳 东方财富</span> <span>🇺🇸 英伟达</span> <span>🇺🇸 特斯拉</span> <span>🇭🇰 腾讯控股</span>
        </div>
    </div>

    <div id="terminal">
        <!-- 日志将在这里渲染 -->
    </div>

    <script>
        let isRadarOn = false;

        async function toggleRadar(status) {
            isRadarOn = status;
            const textEl = document.getElementById('radar-status-text');
            if (status) {
                textEl.innerText = "全域雷达：🔥 扫描中 (游资算法已激活)";
                textEl.className = "radar-label radar-on-text";
            } else {
                textEl.innerText = "全域雷达：休眠中";
                textEl.className = "radar-label";
            }
            
            await fetch('/toggle_radar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: status })
            });
            fetchPulse(); // 立即触发一次心跳
        }

        async function fetchPulse() {
            const indicator = document.getElementById('pulse-indicator');
            indicator.style.color = '#00ff00';
            
            try {
                const response = await fetch('/heartbeat');
                const data = await response.json();
                
                // 同步后端雷达状态到前端开关 (防止刷新网页后状态不同步)
                if (data.is_on !== isRadarOn) {
                    isRadarOn = data.is_on;
                    document.getElementById('radar-toggle').checked = isRadarOn;
                    toggleRadar(isRadarOn); // 强制更新UI
                }

                // 渲染日志
                const terminal = document.getElementById('terminal');
                terminal.innerHTML = ''; // 清空
                data.logs.forEach(log => {
                    const div = document.createElement('div');
                    div.className = 'log-line';
                    let typeClass = 'type-info';
                    if(log.type === 'alert') typeClass = 'type-alert';
                    if(log.type === 'ai') typeClass = 'type-ai';
                    if(log.type === 'error') typeClass = 'type-error';
                    
                    div.innerHTML = `<span class="time">[${log.time}]</span> <span class="${typeClass}">${log.msg}</span>`;
                    terminal.appendChild(div);
                });

            } catch (error) {
                indicator.style.color = 'red';
                indicator.innerText = "● 失去心跳连接...";
            }
            
            setTimeout(() => { indicator.style.color = '#888'; }, 500);
        }

        // 心跳起搏器：每 15 秒向后端请求一次最新日志，并驱动后端雷达扫描
        setInterval(fetchPulse, 15000);
        
        // 首次加载拉取一次数据
        fetchPulse();
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
