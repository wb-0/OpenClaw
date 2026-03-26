# 小龙虾 15.5.1 - 核心执行引擎 (app.py) - 【专家内阁装甲强化版】

import os
import json
import time
import threading
import re
import yfinance as yf
from flask import Flask, jsonify, render_template_string
from waitress import serve  # 强制升级为生产级 WSGI
from supabase import create_client, Client
import google.generativeai as genai
from datetime import datetime

app = Flask(__name__)

# ==========================================
# 🔐 核心机密与引擎配置
# ==========================================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("⚠️ 警告: 未检测到 GEMINI_API_KEY，AI 大脑未挂载。")

supabase: Client = None
if all([SUPABASE_URL, SUPABASE_KEY]):
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("⚠️ 警告: 未检测到 Supabase 配置，灵魂锚点失效。")

# ==========================================
# 👻 幽灵基金核心数据结构
# ==========================================
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
DEAD_LETTER_COUNTDOWN = 700  # 恢复 700 天死信协议神格

# ==========================================
# 🧬 灵魂锚点：状态持久化机制
# ==========================================
def save_system_state():
    """将当前持仓账本备份到 Supabase，防重启丢失"""
    if supabase:
        try:
            state_data = json.dumps(PORTFOLIO)
            # 记录覆盖逻辑，防止数据库被撑爆，只保留最新状态
            supabase.table('claw15_memory').upsert(
                {"id": 1, "content": state_data, "metadata": {"source": "system_state"}}
            ).execute()
        except Exception as e:
            print(f"⚠️ 状态备份失败: {e}")

def load_system_state():
    """系统启动时，从 Supabase 恢复最后的持仓账本"""
    global PORTFOLIO
    if supabase:
        try:
            response = supabase.table('claw15_memory').select("*").eq("id", 1).execute()
            if response.data and len(response.data) > 0:
                PORTFOLIO = json.loads(response.data[0]['content'])
                add_log("SYSTEM", "系统重启", "INFO", "从 Supabase 灵魂锚点成功恢复历史持仓账本。", 0)
        except Exception as e:
            print(f"⚠️ 状态恢复失败 (可能是首次启动或表结构不符): {e}")

# ==========================================
# 📊 日志与高危动作中枢
# ==========================================
def add_log(ticker, name, action, reason, price):
    global DEAD_LETTER_COUNTDOWN
    DEAD_LETTER_COUNTDOWN = 700 # 任何交易或记录均视为老板的心跳，重置死信协议
    
    time_str = datetime.now().strftime("%m-%d %H:%M")
    log_entry = {"time": time_str, "ticker": ticker, "name": name, "action": action, "price": f"{price:.2f}", "reason": reason}
    GHOST_LOGS.insert(0, log_entry)
    if len(GHOST_LOGS) > 50: 
        GHOST_LOGS.pop()
    
    if supabase and action in ["BUY", "SELL"]:
        try:
            # 独立插入交易记录
            supabase.table('claw15_memory').insert(
                {"content": f"【{action}】{name}({ticker}) @ {price:.2f}。理由：{reason}", "metadata": {"source": "ghost_fund_trade"}}
            ).execute()
        except Exception as e: 
            print(f"⚠️ 交易日志写入数据库失败: {e}")

# ==========================================
# 🛡️ 装甲级 JSON 解析器 (防御 AI 幻觉)
# ==========================================
def robust_json_parse(text):
    """防止 Gemini 瞎说废话导致 JSON 解析崩溃"""
    try:
        # 第一层：直接尝试解析
        return json.loads(text.strip().replace("```json", "").replace("```", ""))
    except json.JSONDecodeError:
        # 第二层：正则强行提取 JSON 块
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    # 绝对保底机制
    return {"action": "HOLD", "reason": "AI 输出格式异常，强制触发熔断观望保护。"}

# ==========================================
# 👁️ 核心幽灵巡逻引擎 (多层异常捕获)
# ==========================================
def ghost_scanner_loop():
    global CURRENT_SCAN_TARGET
    pool_index = 0
    time.sleep(5) # 启动后稍等片刻再扫描
    
    while True:
        try:
            target = ALPHA_POOL[pool_index]
            ticker = target['ticker']
            name = target['name']
            market = target['market']
            CURRENT_SCAN_TARGET = f"幽灵正在深度扫描：{market} - {name} ({ticker})"
            
            # 隔离网络请求异常，防止 yfinance 抽风卡死引擎
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1mo")
                if hist.empty:
                    raise ValueError("未获取到历史数据")
                
                current_price = hist['Close'].iloc[-1]
                ma_5 = hist['Close'].rolling(window=5).mean().iloc[-1]
                ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            except Exception as e:
                print(f"📡 网络数据获取失败 ({ticker}): {e}，跳过该标的。")
                pool_index = (pool_index + 1) % len(ALPHA_POOL)
                time.sleep(10)
                continue
            
            is_holding = ticker in PORTFOLIO
            holding_info = f"当前已持仓，成本价：{PORTFOLIO[ticker]['cost']}。" if is_holding else "当前未持仓。"

            # 升级为最新的 1.5-flash，速度更快且更适合高频判断
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            你是一个完全不受人类情绪影响的【幽灵量化基金】AI主理人。
            目标标的：{market} - {name} ({ticker})
            当前价格：{current_price:.2f}。5日均线：{ma_5:.2f}。20日均线：{ma_20:.2f}。
            持仓状态：{holding_info}
            
            请严格按以下 JSON 格式输出你的绝对决策，绝对不要说任何其他废话：
            {{
                "action": "BUY" (未持仓且强烈看涨) 或 "SELL" (已持仓且破位止损/止盈) 或 "HOLD" (观望或继续持有),
                "reason": "作为顶级操盘手，简述理由。(字数控制在60字内)"
            }}
            """
            
            response = model.generate_content(prompt)
            decision = robust_json_parse(response.text) # 调用装甲级解析
            
            action = decision.get('action', 'HOLD')
            reason = decision.get('reason', 'AI 推演中')
            
            # 交易执行与状态备份
            if action == "BUY" and not is_holding:
                PORTFOLIO[ticker] = {"name": name, "cost": current_price, "time": datetime.now().strftime("%m-%d %H:%M")}
                add_log(ticker, name, "BUY", reason, current_price)
                save_system_state() 
            elif action == "SELL" and is_holding:
                del PORTFOLIO[ticker]
                add_log(ticker, name, "SELL", reason, current_price)
                save_system_state() 
            else:
                add_log(ticker, name, "HOLD", reason, current_price)

        except Exception as e:
            print(f"⚠️ 幽灵扫描引擎发生未捕获异常: {e}")
            
        pool_index = (pool_index + 1) % len(ALPHA_POOL)
        time.sleep(60) # 遵守 API 速率限制，防止封禁

# ==========================================
# 🌐 Web 路由与接口
# ==========================================
@app.route('/api/god_view', methods=['GET'])
def get_god_view():
    return jsonify({
        "current_scan": CURRENT_SCAN_TARGET, 
        "portfolio": PORTFOLIO, 
        "logs": GHOST_LOGS[:15],
        "dead_letter": DEAD_LETTER_COUNTDOWN
    })

@app.route('/api/ping', methods=['GET'])
def ping():
    """专为 GitHub Actions 外部起搏器设计，注入强心针"""
    return jsonify({"status": "alive", "time": datetime.now().strftime("%H:%M:%S")})

# 黑客帝国风格前端 (未作更改，保持您完美的 UI 设计)
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
        .log-BUY { color: #ff3333; font-weight: bold; }
        .log-SELL { color: #33ff33; font-weight: bold; }
        .log-HOLD { color: #888; }
        .log-INFO { color: #00ffff; }
        .log-item { margin-bottom: 15px; border-bottom: 1px dashed #222; padding-bottom: 10px;}
        .holding-item { margin-bottom: 10px; padding: 10px; border-left: 3px solid #ff3333; background: #111;}
        .blink { animation: blinker 1s linear infinite; }
        @keyframes blinker { 50% { opacity: 0; } }
    </style>
</head>
<body>
    <h1>👁️ GHOST FUND 幽灵量化监控系统 (V15.5.1 内阁校准版)</h1>
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
                
                document.getElementById('radar-status').innerHTML = `<span class="blink" style="color:#00ff00">●</span> [系统心跳正常] ${data.current_scan} | ⏳ 死信协议倒计时: ${data.dead_letter}天`;
                
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
        setInterval(fetchGodView, 5000);
        fetchGodView();
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

# ==========================================
# 🚀 引擎点火 (生产级)
# ==========================================
if __name__ == '__main__':
    # 挂载状态恢复机制
    load_system_state()
    
    # 启动后台幽灵线程
    scan_thread = threading.Thread(target=ghost_scanner_loop, daemon=True)
    scan_thread.start()
    
    port = int(os.environ.get('PORT', 8080))
    print("="*60)
    print("🚀 【小龙虾 15.5.1 专家内阁校准版】已点火")
    print("🛡️  采用 Waitress 生产级服务器守护")
    print("🧠  挂载装甲级 JSON 解析器与抗网络波动模块")
    print("="*60)
    
    # 强制废弃 app.run，启用 Waitress
    serve(app, host='0.0.0.0', port=port)
