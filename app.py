# 小龙虾 15.3 - 核心执行引擎 (app.py) - 【量化圣杯 · 百年规律推演版】

import os
import json
import threading
import yfinance as yf
from flask import Flask, request, jsonify, render_template_string
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

# 标的池
WATCH_LIST = [
    {"market": "A股", "name": "贵州茅台", "ticker": "600519.SS", "logic": "A股价值标杆/周期缩影"},
    {"market": "A股", "name": "东方财富", "ticker": "300059.SZ", "logic": "A股牛熊风向标/券商情绪"},
    {"market": "美股", "name": "英伟达", "ticker": "NVDA", "logic": "全球算力核心/纳指引擎"},
    {"market": "港股", "name": "腾讯控股", "ticker": "0700.HK", "logic": "中国互联网Beta/外资蓄水池"}
]

# 存储深度推演报告的缓存
REPORTS_CACHE = {}

def get_market_laws(market):
    """注入各市场成立以来的底层规律 (宏观左脑)"""
    if market == "A股":
        return "【A股历史规律法则】：1. 典型的‘牛短熊长’与‘均值回归’，情绪极度悲观时往往是政策底。2. 受宏观信贷周期和监管政策绝对主导。3. 资金喜欢在题材间轮动（炒新炒小炒差），但核心资产在长周期具备避险属性。4. T+1限制了日内纠错，买入必须考虑次日流动性溢价。"
    elif market == "美股":
        return "【美股历史规律法则】：1. 长期趋势向上（‘长牛’），受盈利增长、科技创新和回购驱动。2. 绝对受美联储货币政策（利率/流动性）支配。3. 财报季存在巨大的‘戴维斯双击/双杀’效应。4. T+0且无涨跌幅，趋势形成后极具连贯性，顺势交易是利益最大化的核心。"
    elif market == "港股":
        return "【港股历史规律法则】：1. 典型的‘离岸市场’，基本面看中国内地，流动性看美联储。2. 极度看重估值，容易出现‘估值陷阱’。3. 机构投资者主导，缺乏散户情绪溢价，趋势一旦破位极难修复。"
    return ""

def deep_quantum_analysis(ticker, name, market, logic):
    """结合历史规律与实时数据的深度量化推演"""
    global REPORTS_CACHE
    try:
        # 1. 抓取多维度数据：半年日线（看大周期） + 最近3天分时（看微观异动）
        stock = yf.Ticker(ticker)
        hist_daily = stock.history(period="6mo") # 半年数据
        hist_intra = stock.history(period="3d", interval="30m") # 3天30分钟线
        
        if hist_daily.empty:
            REPORTS_CACHE[ticker] = {"status": "error", "msg": "数据源获取失败"}
            return

        current_price = hist_daily['Close'].iloc[-1]
        ma_20 = hist_daily['Close'].rolling(window=20).mean().iloc[-1]
        ma_60 = hist_daily['Close'].rolling(window=60).mean().iloc[-1]

        macro_laws = get_market_laws(market)

        # 2. 召唤顶配大模型进行深度逻辑推演
        model = genai.GenerativeModel('gemini-1.5-pro-latest') # 必须用 Pro 版本进行复杂推理
        prompt = f"""
        你现在是管理着千亿资金的全球宏观对冲基金主理人。
        你的唯一目标是：在严格遵守各市场规则的前提下，实现利益绝对最大化。
        
        【目标标的】：{market} - {name} ({ticker})，代表属性：{logic}。
        【当前微观数据】：最新价 {current_price:.2f}。20日均线 {ma_20:.2f}，60日均线 {ma_60:.2f}。
        【宏观历史法则注入】：{macro_laws}
        
        请结合上述【宏观历史法则】与当前的【均线趋势位置】，穿透表面的连板或涨跌，给我一份严谨的决策。
        请严格按以下 JSON 格式输出，不要有其他废话：
        {{
            "score": "0-100之间的整数 (低于60分坚决不买，90分以上砸锅卖铁)",
            "trend_judgment": "用一句话总结当前所处的大周期阶段(如：处于长期底部的初期反弹 / 处于泡沫化高点)",
            "action": "强烈买入 / 逢低建仓 / 持币观望 / 立即清仓",
            "logic_reasoning": "结合市场历史规律，详细说明为什么做出这个决策？(控制在100字内)",
            "risk_control": "止损价设在多少？止盈预期在哪？"
        }}
        """
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        # 清理可能的 markdown 标记，提取 JSON
        if result_text.startswith("```json"):
             result_text = result_text[7:-3]
        elif result_text.startswith("```"):
             result_text = result_text[3:-3]
             
        ai_decision = json.loads(result_text)
        
        # 3. 记忆沉淀：如果评分超过 80 分，存入 Supabase 记忆库作为经典战役记录
        if int(ai_decision.get("score", 0)) >= 80 and supabase:
             supabase.table('claw15_memory').insert({"content": f"{name}评级{ai_decision['score']}:{ai_decision['logic_reasoning']}", "metadata": {"source": "holy_grail"}}).execute()

        REPORTS_CACHE[ticker] = {"status": "success", "data": ai_decision, "time": datetime.now().strftime("%m-%d %H:%M")}

    except Exception as e:
        REPORTS_CACHE[ticker] = {"status": "error", "msg": f"AI 逻辑推演异常: {str(e)}"}

# --- 接口 ---
@app.route('/get_dashboard_data', methods=['GET'])
def get_dashboard_data():
    """为前端提供轻量级的实时行情展示"""
    data_list = []
    for item in WATCH_LIST:
        ticker = item['ticker']
        try:
            stock = yf.Ticker(ticker)
            fast_info = stock.fast_info
            current_price = fast_info.last_price
            prev_close = fast_info.previous_close
            change_pct = ((current_price - prev_close) / prev_close) * 100
            
            data_list.append({
                "ticker": ticker,
                "name": item['name'],
                "market": item['market'],
                "price": f"{current_price:.2f}",
                "change": f"{change_pct:.2f}%",
                "color": "red" if change_pct > 0 else "green" # A股红涨绿跌，美股相反，前端统一处理为红涨绿跌
            })
        except:
             data_list.append({"ticker": ticker, "name": item['name'], "market": item['market'], "price": "加载中", "change": "-", "color": "white"})
             
    return jsonify(data_list)

@app.route('/trigger_deep_analysis', methods=['POST'])
def trigger_deep_analysis():
    """触发深度长周期分析 (后台异步执行)"""
    data = request.json
    ticker = data.get('ticker')
    target_item = next((item for item in WATCH_LIST if item["ticker"] == ticker), None)
    
    if target_item:
        REPORTS_CACHE[ticker] = {"status": "loading"} # 标记正在分析
        # 开新线程去跑复杂的 AI 分析，不卡死服务器
        threading.Thread(target=deep_quantum_analysis, args=(ticker, target_item['name'], target_item['market'], target_item['logic'])).start()
        return jsonify({"status": "started"})
    return jsonify({"status": "error", "msg": "未找到标的"})

@app.route('/get_analysis_report', methods=['GET'])
def get_analysis_report():
    """前端轮询获取分析结果"""
    ticker = request.args.get('ticker')
    report = REPORTS_CACHE.get(ticker, {"status": "none"})
    return jsonify(report)

# --- 量化圣杯可视化大屏 (黑金华尔街风) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>🏆 量化圣杯系统 (V15.3)</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d0e15; color: #e2e8f0; margin: 0; padding: 20px; }
        h1 { text-align: center; color: #d4af37; text-transform: uppercase; letter-spacing: 2px; border-bottom: 1px solid #d4af37; padding-bottom: 15px; margin-bottom: 30px;}
        .subtitle { text-align: center; font-size: 14px; color: #64748b; margin-top: -20px; margin-bottom: 30px;}
        
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }
        .card { background: #1e293b; border-radius: 10px; padding: 20px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5); border: 1px solid #334155; position: relative;}
        
        .card-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 15px;}
        .card-title { font-size: 20px; font-weight: bold; color: #f8fafc;}
        .market-tag { font-size: 12px; padding: 3px 8px; border-radius: 4px; background: #475569; color: #fff;}
        
        .price-section { display: flex; align-items: baseline; gap: 10px; margin-bottom: 20px;}
        .price { font-size: 28px; font-weight: bold; font-family: monospace;}
        .change { font-size: 16px; font-weight: bold;}
        .red { color: #ef4444; } /* 涨 */
        .green { color: #22c55e; } /* 跌 */
        
        .btn-analyze { background: linear-gradient(135deg, #d4af37, #b8860b); color: #000; border: none; padding: 10px 15px; width: 100%; border-radius: 6px; font-weight: bold; font-size: 15px; cursor: pointer; transition: 0.3s;}
        .btn-analyze:hover { filter: brightness(1.2); }
        .btn-analyze:disabled { background: #475569; color: #94a3b8; cursor: not-allowed; }
        
        /* AI 报告呈现区 */
        .report-box { margin-top: 15px; background: #0f172a; border-radius: 6px; padding: 15px; border-left: 4px solid #d4af37; display: none;}
        .score-circle { width: 50px; height: 50px; border-radius: 50%; background: #000; color: #d4af37; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; border: 2px solid #d4af37; float: right;}
        .report-line { margin-bottom: 10px; font-size: 14px; line-height: 1.5; color: #cbd5e1;}
        .report-label { color: #94a3b8; font-weight: bold; margin-right: 5px;}
        .highlight { color: #d4af37; font-weight: bold;}
        
        .loading-text { text-align: center; color: #d4af37; font-size: 14px; margin-top: 15px; display: none; animation: pulse 1.5s infinite;}
        @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }

    </style>
</head>
<body>
    <h1>🏆 量化圣杯指挥舱</h1>
    <div class="subtitle">历史周期法则注入完成 | 多因子博弈模型在线 | 利益最大化协议生效中</div>

    <div class="grid" id="dashboard">
        <!-- 卡片将由 JS 动态生成 -->
    </div>

    <script>
        // 1. 初始化仪表盘基本数据 (轻量级)
        async function loadDashboard() {
            const res = await fetch('/get_dashboard_data');
            const data = await res.json();
            const grid = document.getElementById('dashboard');
            grid.innerHTML = '';
            
            data.forEach(item => {
                const card = document.createElement('div');
                card.className = 'card';
                card.id = `card-${item.ticker}`;
                card.innerHTML = `
                    <div class="card-header">
                        <div class="card-title">${item.name} (${item.ticker})</div>
                        <div class="market-tag">${item.market}</div>
                    </div>
                    <div class="price-section">
                        <div class="price">${item.price}</div>
                        <div class="change ${item.color}">${item.change}</div>
                    </div>
                    <button class="btn-analyze" id="btn-${item.ticker}" onclick="triggerAnalysis('${item.ticker}')">
                        🧠 发起百年周期规律深度推演
                    </button>
                    <div class="loading-text" id="loading-${item.ticker}">
                        [系统] 正在调取历史周期规律...<br>
                        [AI] 正在进行利益最大化多因子博弈计算...
                    </div>
                    <div class="report-box" id="report-${item.ticker}"></div>
                `;
                grid.appendChild(card);
            });
        }

        // 2. 触发深度分析 (异步)
        async function triggerAnalysis(ticker) {
            const btn = document.getElementById(`btn-${ticker}`);
            const loading = document.getElementById(`loading-${ticker}`);
            const reportBox = document.getElementById(`report-${ticker}`);
            
            btn.style.display = 'none';
            reportBox.style.display = 'none';
            loading.style.display = 'block';

            await fetch('/trigger_deep_analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticker: ticker })
            });

            // 启动轮询检查结果
            checkReport(ticker, btn, loading, reportBox);
        }

        // 3. 轮询获取分析结果
        function checkReport(ticker, btn, loading, reportBox) {
            const interval = setInterval(async () => {
                const res = await fetch(`/get_analysis_report?ticker=${ticker}`);
                const report = await res.json();

                if (report.status === 'success') {
                    clearInterval(interval);
                    loading.style.display = 'none';
                    btn.style.display = 'block';
                    btn.innerText = "🔄 重新推演更新";
                    
                    const ai = report.data;
                    reportBox.style.display = 'block';
                    
                    // 根据分数变换颜色
                    let scoreColor = "#ef4444"; // 红色(低分)
                    if(ai.score >= 60) scoreColor = "#eab308"; // 黄色(及格)
                    if(ai.score >= 80) scoreColor = "#22c55e"; // 绿色(高分买入)
                    
                    reportBox.innerHTML = `
                        <div class="score-circle" style="border-color:${scoreColor}; color:${scoreColor}">${ai.score}</div>
                        <div class="report-line"><span class="report-label">研判时间:</span> ${report.time}</div>
                        <div class="report-line"><span class="report-label">周期定性:</span> <span class="highlight">${ai.trend_judgment}</span></div>
                        <div class="report-line"><span class="report-label">操盘指令:</span> <span style="color:${scoreColor}; font-weight:bold; font-size:16px;">${ai.action}</span></div>
                        <div class="report-line"><span class="report-label">底层逻辑:</span> ${ai.logic_reasoning}</div>
                        <div class="report-line"><span class="report-label">风控纪律:</span> ${ai.risk_control}</div>
                    `;
                } else if (report.status === 'error') {
                    clearInterval(interval);
                    loading.style.display = 'none';
                    btn.style.display = 'block';
                    alert("推演失败: " + report.msg);
                }
                // 如果是 loading，继续等待下一秒
            }, 2000); // 每2秒问一次后台
        }

        // 启动加载
        loadDashboard();
        // 设定每 30 秒刷新一次头部轻量级行情价格
        setInterval(loadDashboard, 30000); 
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
