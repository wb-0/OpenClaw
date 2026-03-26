# 小龙虾 15.4 - 核心执行引擎 (app.py) - 【全自动幽灵基金 (Ghost Fund) 版】

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

# --- 幽灵基金核心数据结构 (内存模拟数据库) ---
# 阿尔法狩猎池 (幽灵雷达24小时循环扫描的目标)
ALPHA_POOL = [
    {"market": "美股", "ticker": "NVDA", "name": "英伟达"},
    {"market": "美股", "ticker": "TSLA", "name": "特斯拉"},
    {"market": "美股", "ticker": "AAPL", "name": "苹果"},
    {"market": "A股", "ticker": "600519.SS", "name": "贵州茅台"},
    {"market": "A股", "ticker": "300059.SZ", "name": "东方财富"},
    {"market": "港股", "ticker": "0700.HK", "name": "腾讯控股"}
]

# 幽灵日志库 (保存最近的50条操盘记录和深度理由)
GHOST_LOGS = []
# 当前持仓 (虚拟账本)
PORTFOLIO = {}
# 雷达当前状态 (前端展示用)
CURRENT_SCAN_TARGET = "系统预热中..."

def add_log(ticker, name, action, reason, price):
    """记录操作日志，并同步到 Supabase 永久记忆库"""
    time_str = datetime.now().strftime("%m-%d %H:%M")
    log_entry = {
        "time": time_str,
        "ticker": ticker,
        "name": name,
        "action": action, # BUY, SELL, HOLD
        "price": f"{price:.2f}",
        "reason": reason
    }
    GHOST_LOGS.insert(0, log_entry)
    if len(GHOST_LOGS) > 50:
        GHOST_LOGS.pop()
        
    # 异步写入 Supabase
    if supabase and action in ["BUY", "SELL"]:
        try:
            supabase.table('claw15_memory').insert({"content": f"【{action}】{name}({ticker}) @ {price:.2f}。理由：{reason}", "metadata": {"source": "ghost_fund"}}).execute()
        except:
            pass

# --- 核心幽灵巡逻引擎 (在后台无限循环运行) ---
def ghost_scanner_loop():
    global CURRENT_SCAN_TARGET
    pool_index = 0
    
    while True:
        try:
            # 1. 锁定当前扫描目标
            target = ALPHA_POOL[pool_index]
            ticker = target['ticker']
            name = target['name']
            market = target['market']
            CURRENT_SCAN_TARGET = f"正在深度扫描：{market} - {name} ({ticker})"
            
            # 2. 抓取真实量价切片 (最近1个月日线 + 最近3天分时)
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")
            if hist.empty:
                time.sleep(10)
                continue
            
            current_price = hist['Close'].iloc[-1]
            ma_5 = hist['Close'].rolling(window=5).mean().iloc[-1]
            ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            
            # 3. 判断是否已经持仓
            is_holding = ticker in PORTFOLIO
            holding_info = f"当前已持仓，成本价：{PORTFOLIO[ticker]['cost']}。" if is_holding else "当前未持仓。"

            # 4. 召唤顶配 Gemini 进行全自动上帝视角决策
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            prompt = f"""
            你是一个完全不受人类情绪影响的【幽灵量化基金】AI主理人。
            目标标的：{market} - {name} ({ticker})
            当前价格：{current_price:.2f}。5日均线：{ma_5:.2f}。20日均线：{ma_20:.2f}。
            持仓状态：{holding_info}
            
            请结合{market}的交易规则，分析其近期趋势。
            请严格按以下 JSON 格式输出你的绝对决策（不要输出其他任何字符）：
            {{
                "action": "BUY" (如果未持仓且看大涨) 或 "SELL" (如果已持仓且破位/止盈) 或 "HOLD" (观望或继续持有),
                "reason": "作为顶级操盘手，详细说明为什么做出这个买/卖/观望的决定？结合均线、量价和宏观逻辑。(字数控制在80字左右)"
            }}
            """
            
            response = model.generate_content(prompt)
            result_text = response.text.strip()
            
            if result_text.startswith("```json"):
                 result_text = result_text[7:-3]
            elif result_text.startswith("```"):
                 result_text = result_text[3:-3]
                 
            decision = json.loads(result_text)
            action = decision.get('action', 'HOLD')
            reason = decision.get('reason', 'AI 逻辑分析失败')
            
            # 5. 执行虚拟交易，更新账本
            if action == "BUY" and not is_holding:
                PORTFOLIO[ticker] = {"name": name, "cost": current_price, "time": datetime.now().strftime("%m-%d %H:%M")}
                add_log(ticker, name, "BUY", reason, current_price)
            elif action == "SELL" and is_holding:
                del PORTFOLIO[ticker]
                add_log(ticker, name, "SELL", reason, current_price)
            else:
                # 即使是 HOLD，也记录到后台，但前端可以过滤掉以防刷屏，这里我们记录下来展示 AI 的思考过程
                add_log(ticker, name, "HOLD", reason, current_price)

        except Exception as e:
            print(f"幽灵引擎扫描 {target['name']} 时异常: {e}")
            
        # 6. 轮换下一个标的，休息 45 秒防止被 API 封禁
        pool_index = (pool_index + 1) % len(ALPHA_POOL)
        time.sleep(45)

# 启动幽灵引擎 (它会在后台永远运行，不依赖网页请求)
threading.Thread(target=ghost_scanner_loop, daemon=True).start()


# --- API 接口 (供前端大屏无刷新调用) ---
@app.route('/api/god_view', methods=['GET'])
def get_god_view():
    """上帝视角接口：一次性返回雷达状态、操作日志和持仓账本"""
    return jsonify({
        "current_scan": CURRENT_SCAN_TARGET,
        "portfolio": PORTFOLIO,
        "logs": GHOST_LOGS[:15] # 前端只展示最新15条
    })

# --- 老板专属：上帝视角监控中心 (全景全自动版) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>👁️ 小龙虾 15.4 · 幽灵基金上帝视角</title>
    <style>
        body { font-family: 'Helvetica Neue', Arial, sans-serif; background-color: #0a0a0a; color: #d1d5db; margin: 0; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 15px; margin-bottom: 20px;}
        h1 { color: #10b981; margin: 0; font-size: 24px; text-transform: uppercase; letter-spacing: 2px; text-shadow: 0 0 10px rgba(16, 185, 129, 0.4);}
        .radar-status { font-family: monospace; font-size: 16px; color: #f59e0b; background: #1f2937; padding: 8px 15px; border-radius: 4px; border: 1px solid #374151;}
        
        .main-container { display: flex; gap: 20px; height: calc(100vh - 100px); }
        
        /* 左侧：操作记录与 AI 深度理由 */
        .logs-panel { flex: 2; background: #111827; border-radius: 8px; border: 1px solid #1f2937; display: flex; flex-direction: column; overflow: hidden;}
        .panel-title { background: #1f2937; padding: 12px 20px; font-weight: bold; color: #f3f4f6; font-size: 16px; border-bottom: 1px solid #374151; margin: 0;}
        .log-container { flex: 1; overflow-y: auto; padding: 15px; }
        .log-card { background: #1f2937; border-radius: 6px; padding: 15px; margin-bottom: 15px; border-left: 4px solid #4b5563; box-shadow: 0 4px 6px rgba(0,0,0,0.3);}
        .log-header { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px;}
        .log-name { font-weight: bold; font-size: 16px; color: #fff;}
        .action-BUY { color: #ef4444; font-weight: bold; font-size: 18px;} /* A股红涨绿跌习惯 */
        .action-SELL { color: #10b981; font-weight: bold; font-size: 18px;}
        .action-HOLD { color: #6b7280; font-weight: bold; font-size: 16px;}
        .log-reason { color: #9ca3af; font-size: 14px; line-height: 1.6;}
        
        /* 右侧：当前持仓 */
        .portfolio-panel { flex: 1; background: #111827; border-radius: 8px; border: 1px solid #1f2937; display: flex; flex-direction: column; overflow: hidden;}
        .portfolio-container { padding: 15px; overflow-y: auto;}
        .holding-item { display: flex; justify-content: space-between; background: #1f2937; padding: 12px; border-radius: 4px; margin-bottom: 10px; border-left: 2px solid #ef4444;}
        .holding-name { font-weight: bold; color: #fff;}
        .holding-cost { color: #9ca3af; font-size: 13px;}
        
        /* 闪烁光标 */
        .blink { animation: blinker 1s linear infinite; }
        @keyframes blinker { 50% { opacity: 0; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>👁️ 幽灵量化基金 (Ghost Fund)</h1>
        <div class="radar-status" id="radar-status"><span class="blink">●</span> 正在连接核心服务器...</div>
    </div>

    <div class="main-container">
        <!-- 左侧：AI 决策流 -->
        <div class="logs-panel">
            <h3 class="panel-title">🧠 核心决策流 & 深度博弈理由 (实时同步)</h3>
            <div class="log-container" id="log-container">
                <!-- 日志动态加载 -->
                <div style="text-align:center; color:#6b7280; margin-top: 50px;">等待幽灵引擎传回第一条情报...</div>
            </div>
        </div>

        <!-- 右侧：虚拟持仓 -->
        <div class="portfolio-panel">
            <h3 class="panel-title">💼 当前虚拟持仓 (Alpha 阵列)</h3>
            <div class="portfolio-container" id="portfolio-container">
                <!-- 持仓动态加载 -->
            </div>
        </div>
    </div>

    <script>
        async function fetchGodView() {
            try {
                const res = await fetch('/api/god_view');
                const data = await res.json();
                
                // 1. 更新雷达状态
                document.getElementById('radar-status').innerHTML = `<span class="blink" style="color:#10b981">●</span> ${data.current_scan}`;
                
                // 2. 更新操作日志
                const logContainer = document.getElementById('log-container');
                logContainer.innerHTML = '';
                data.logs.forEach(log => {
                    const card = document.createElement('div');
                    card.className = 'log-card';
                    // 根据动作改变边框颜色
                    if(log.action === 'BUY') card.style.borderLeftColor = '#ef4444';
                    if(log.action === 'SELL') card.style.borderLeftColor = '#10b981';
                    
                    let actionText = log.action === 'BUY' ? '建仓买入' : (log.action === 'SELL' ? '止盈/止损卖出' : '持续观望');
                    
                    card.innerHTML = `
                        <div class="log-header">
                            <div><span class="log-name">${log.name} (${log.ticker})</span> <span style="color:#6b7280; font-size:12px; margin-left:10px">${log.time}</span></div>
                            <div class="action-${log.action}">${actionText} @ ${log.price}</div>
                        </div>
                        <div class="log-reason"><strong style="color:#e5e7eb">AI 深度推演：</strong>${log.reason}</div>
                    `;
                    logContainer.appendChild(card);
                });

                // 3. 更新持仓账本
                const portContainer = document.getElementById('portfolio-container');
                portContainer.innerHTML = '';
                const holdings = Object.keys(data.portfolio);
                if(holdings.length === 0) {
                    portContainer.innerHTML = '<div style="color:#6b7280; text-align:center; padding:20px;">空仓中，等待狩猎信号。</div>';
                } else {
                    holdings.forEach(ticker => {
                        const item = data.portfolio[ticker];
                        const div = document.createElement('div');
                        div.className = 'holding-item';
                        div.innerHTML = `
                            <div>
                                <div class="holding-name">${item.name}</div>
                                <div class="holding-cost">${ticker}</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="color:#ef4444; font-weight:bold;">持仓中</div>
                                <div class="holding-cost">建仓价: ${item.cost}</div>
                            </div>
                        `;
                        portContainer.appendChild(div);
                    });
                }

            } catch (error) {
                document.getElementById('radar-status').innerHTML = `<span style="color:red">● 信号中断，正在重连...</span>`;
            }
        }

        // 页面打开后，立刻拉取一次数据
        fetchGodView();
        // 之后每 10 秒自动拉取一次，实现真正的“全自动看盘”
        setInterval(fetchGodView, 10000);
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
