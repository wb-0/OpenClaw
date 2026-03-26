# 小龙虾 15.5 - 核心执行引擎 (app.py) - 【不朽幽灵基金 (Immortal Ghost) 最终版】

import os
import json
import time
import threading
import yfinance as yf
from flask import Flask, jsonify, render_template_string
from supabase import create_client, Client
import google.generativeai as genai
from datetime import datetime

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
if all([SUPABASE_URL, SUPABASE_KEY]):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 幽灵基金核心数据结构 ---
ALPHA_POOL = [
    {"market": "美股", "ticker": "NVDA", "name": "英伟达"},
    {"market": "美股", "ticker": "TSLA", "name": "特斯拉"},
    {"market": "A股", "ticker": "600519.SS", "name": "贵州茅台"},
    {"market": "A股", "ticker": "300059.SZ", "name": "东方财富"},
    {"market": "港股", "ticker": "0700.HK", "name": "腾讯控股"}
]

GHOST_LOGS = []
PORTFOLIO = {}
CURRENT_SCAN_TARGET = "系统预热中..."

# --- 超越设计的特性：灵魂锚点 (状态持久化) ---
def save_system_state():
    """将当前持仓账本备份到 Supabase，防止服务器重启丢失"""
    if supabase:
        try:
            state_data = json.dumps(PORTFOLIO)
            # 用特殊的 source 标签标记这是系统状态
            supabase.table('claw15_memory').insert({"content": state_data, "metadata": {"source": "system_state"}}).execute()
        except Exception as e:
            print(f"状态备份失败: {e}")

def load_system_state():
    """系统启动时，从 Supabase 恢复最后的持仓账本"""
    global PORTFOLIO
    if supabase:
        try:
            # 查找最后一条状态记录
            response = supabase.table('claw15_memory').select("*").eq("metadata->>source", "system_state").order("id", desc=True).limit(1).execute()
            if response.data and len(response.data) > 0:
                PORTFOLIO = json.loads(response.data[0]['content'])
                add_log("SYSTEM", "系统重启", "INFO", "从 Supabase 灵魂锚点成功恢复历史持仓账本。", 0)
        except Exception as e:
            print(f"状态恢复失败 (可能是首次启动): {e}")

# 启动时执行恢复
load_system_state()

def add_log(ticker, name, action, reason, price):
    time_str = datetime.now().strftime("%m-%d %H:%M")
    log_entry = {"time": time_str, "ticker": ticker, "name": name, "action": action, "price": f"{price:.2f}", "reason": reason}
    GHOST_LOGS.insert(0, log_entry)
    if len(GHOST_LOGS) > 50: GHOST_LOGS.pop()
    
    if supabase and action in ["BUY", "SELL"]:
        try:
            supabase.table('claw15_memory').insert({"content": f"【{action}】{name}({ticker}) @ {price:.2f}。理由：{reason}", "metadata": {"source": "ghost_fund"}}).execute()
        except: pass

# --- 核心幽灵巡逻引擎 ---
def ghost_scanner_loop():
    global CURRENT_SCAN_TARGET
    pool_index = 0
    time.sleep(10) # 启动后稍等片刻再扫描
    
    while True:
        try:
            target = ALPHA_POOL[pool_index]
            ticker = target['ticker']
            name = target['name']
            market = target['market']
            CURRENT_SCAN_TARGET = f"幽灵正在深度扫描：{market} - {name} ({ticker})"
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")
            if hist.empty:
                pool_index = (pool_index + 1) % len(ALPHA_POOL)
                continue
            
            current_price = hist['Close'].iloc[-1]
            ma_5 = hist['Close'].rolling(window=5).mean().iloc[-1]
            ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            
            is_holding = ticker in PORTFOLIO
            holding_info = f"当前已持仓，成本价：{PORTFOLIO[ticker]['cost']}。" if is_holding else "当前未持仓。"

            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            prompt = f"""
            你是一个完全不受人类情绪影响的【幽灵量化基金】AI主理人。
            目标标的：{market} - {name} ({ticker})
            当前价格：{current_price:.2f}。5日均线：{ma_5:.2f}。20日均线：{ma_20:.2f}。
            持仓状态：{holding_info}
            
            请严格按以下 JSON 格式输出你的绝对决策：
            {{
                "action": "BUY" (未持仓且强烈看涨) 或 "SELL" (已持仓且破位止损/止盈) 或 "HOLD" (观望或继续持有),
                "reason": "作为顶级操盘手，简述理由。(字数控制在60字内)"
            }}
            """
            
            response = model.generate_content(prompt)
            result_text = response.text.strip().replace("```json", "").replace("```", "")
            decision = json.loads(result_text)
            action = decision.get('action', 'HOLD')
            reason = decision.get('reason', 'AI 推演中')
            
            # 交易执行与状态备份
            if action == "BUY" and not is_holding:
                PORTFOLIO[ticker] = {"name": name, "cost": current_price, "time": datetime.now().strftime("%m-%d %H:%M")}
                add_log(ticker, name, "BUY", reason, current_price)
                save_system_state() # 变动后备份账本
            elif action == "SELL" and is_holding:
                del PORTFOLIO[ticker]
                add_log(ticker, name, "SELL", reason, current_price)
                save_system_state() # 变动后备份账本
            else:
                # 观望日志只保留在内存中，不写入数据库防止撑爆
                add_log(ticker, name, "HOLD", reason, current_price)

        except Exception as e:
            print(f"幽灵扫描异常: {e}")
            
        pool_index = (pool_index + 1) % len(ALPHA_POOL)
        time.sleep(60) # 每分钟扫描一次，既能及时发现异动，又不会被封禁 API

threading.Thread(target=ghost_scanner_loop, daemon=True).start()

# --- 对外接口 ---
@app.route('/api/god_view', methods=['GET'])
def get_god_view():
    return jsonify({"current_scan": CURRENT_SCAN_TARGET, "portfolio": PORTFOLIO, "logs": GHOST_LOGS[:15]})

@app.route('/api/ping', methods=['GET'])
def ping():
    """专为 GitHub Actions 外部起搏器设计的接口，用于防止休眠"""
    return jsonify({"status": "alive", "time": datetime.now().strftime("%H:%M:%S")})

# --- 极简黑客帝国风格前端 ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>👁️ 幽灵量化基金 | 上帝视角</title>
    <style>
        body { font-family: 'Consolas', monospace; background-color: #050505; color: #00ff00; padding: 20px; font-size: 14px;}
        h1 { border-bottom: 1px solid #333; padding-bottom: 10px; color: #00ff00; text-shadow: 0 0 5px #00ff00;}
        .container { display: flex; gap: 20px; }
        .panel { flex: 1; border: 1px solid #333; padding: 15px; border-radius: 5px; background: #0a0a0a; height: 80vh; overflow-y: auto;}
        .log-BUY { color: #ff3333; font-weight: bold; } /* 红色买入 */
        .log-SELL { color: #33ff33; font-weight: bold; } /* 绿色卖出 */
        .log-HOLD { color: #888; } /* 灰色观望 */
        .log-INFO { color: #00ffff; }
        .log-item { margin-bottom: 15px; border-bottom: 1px dashed #222; padding-bottom: 10px;}
        .holding-item { margin-bottom: 10px; padding: 10px; border-left: 3px solid #ff3333; background: #111;}
        .blink { animation: blinker 1s linear infinite; }
        @keyframes blinker { 50% { opacity: 0; } }
    </style>
</head>
<body>
    <h1>👁️ GHOST FUND 幽灵量化监控系统 (V15.5 不朽版)</h1>
    <p style="color:#aaa" id="radar-status"><span class="blink" style="color:#00ff00">●</span> 正在连接核心集群...</p>
    
    <div class="container">
        <div class="panel" id="logs"><h3>📡 实时全域博弈推演 (AI 思维流)</h3><div id="log-content"></div></div>
        <div class="panel" id="portfolio" style="flex:0.5"><h3>💼 当前虚拟建仓 (不可摧毁账本)</h3><div id="port-content"></div></div>
    </div>

    <script>
        async function fetchGodView() {
            try {
                const res = await fetch('/api/god_view');
                const data = await res.json();
                
                document.getElementById('radar-status').innerHTML = `<span class="blink" style="color:#00ff00">●</span> [系统心跳正常] ${data.current_scan}`;
                
                let logsHTML = '';
                data.logs.forEach(l => {
                    logsHTML += `<div class="log-item">
                        <span style="color:#555">[${l.time}]</span> 
                        <strong>${l.name} (${l.ticker})</strong> 
                        <span class="log-${l.action}">[指令: ${l.action}]</span> 现价:${l.price}<br>
                        <span style="color:#ccc">深层逻辑: ${l.reason}</span>
                    </div>`;
                });
                document.getElementById('log-content').innerHTML = logsHTML;

                let portHTML = '';
                const holdings = Object.keys(data.portfolio);
                if(holdings.length === 0) portHTML = '<span style="color:#555">空仓游猎中...</span>';
                holdings.forEach(t => {
                    const h = data.portfolio[t];
                    portHTML += `<div class="holding-item"><strong>${h.name} (${t})</strong><br><span style="color:#888">建仓价: ${h.cost}</span></div>`;
                });
                document.getElementById('port-content').innerHTML = portHTML;

            } catch(e) { document.getElementById('radar-status').innerHTML = '<span style="color:red">● 信号微弱，重新尝试获取脑波...</span>'; }
        }
        setInterval(fetchGodView, 5000); // 网页开着时，每5秒刷新屏幕
        fetchGodView();
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
