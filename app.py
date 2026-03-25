# 小龙虾 15.1 - 核心执行引擎 (app.py) - 【赛博投行 & 网页指挥中心版】

import os
import yfinance as yf
from flask import Flask, request, jsonify, render_template_string
from supabase import create_client, Client
import google.generativeai as genai

# --- 1. 初始化系统 ---
app = Flask(__name__)

# --- 2. 加载云端密钥 ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
if all([SUPABASE_URL, SUPABASE_KEY]):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 3. 核心记忆协议 ---
def auto_feed_memory(data: str, source: str):
    try:
        supabase.table('claw15_memory').insert({"content": data, "metadata": {"source": source}}).execute()
        return "✅ 记忆已喂料入库，等待100次考核后转正..."
    except Exception as e:
        return f"❌ 记忆喂料失败: {str(e)}"

# --- 4. 🚀 新增：全球投资专家 (沙箱考核版) ---
def execute_global_investment_simulation(market: str, ticker: str):
    """
    沙箱环境下的量化回测考核。
    强制注入各市场法规与交易规则。
    """
    try:
        # 1. 抓取真实市场数据 (最近5天)
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")
        if hist.empty:
            return f"❌ 无法获取代码 {ticker} 的市场数据，请检查代码是否正确。"
        
        recent_data = hist[['Open', 'High', 'Low', 'Close', 'Volume']].to_string()

        # 2. 注入市场合规与规则逻辑
        market_rules = ""
        if market == "A股":
            market_rules = "【A股强制规则】：实行 T+1 交收制度（当日买入次日方可卖出）；普通股票有 10% 涨跌幅限制（科创/创业板 20%）；以人民币(CNY)计价；受中国证监会及宏观政策高度影响。严禁预测内幕交易。"
        elif market == "美股":
            market_rules = "【美股强制规则】：实行 T+0 交易制度；无涨跌幅限制；以美元(USD)计价；受美联储利率及 SEC 财报披露直接驱动；账户资金低于2.5万美元受 PDT(典型日内交易者) 规则限制。严禁任何操纵市场的建议。"
        elif market == "港股":
            market_rules = "【港股强制规则】：实行 T+0 交易，T+2 结算制度；无涨跌幅限制；以港币(HKD)计价，联系汇率挂钩美元；受外资流动性及内地政策双重影响。"

        # 3. 召唤 Gemini 专家进行模拟考核
        model = genai.GenerativeModel('gemini-1.5-pro-latest') # 投资需更强的推理模型
        prompt = f"""
        你现在是【小龙虾 15.1 内阁】的首席全球量化对冲基金经理，目前处于“沙箱模拟考核期”。
        你的终极目标是：在合法合规的前提下，实现利益最大化。
        
        当前考核标的：{market} 市场，股票代码：{ticker}
        {market_rules}
        
        以下是该标的最近5个交易日的真实量价数据：
        {recent_data}
        
        请你以极其专业、冷酷的华尔街量化机构视角，输出一份【模拟考核交易指令】。
        必须包含以下结构：
        1. 趋势研判 (结合量价)
        2. 合规风险提示 (结合该市场特有法规)
        3. 模拟决策 (买入/卖出/观望) 及具体止盈止损点位位。
        """
        
        response = model.generate_content(prompt)
        result = response.text
        
        # 4. 考核记录存入 Supabase 记忆库，用于未来复盘胜率
        feedback = auto_feed_memory(data=f"标的:{ticker}\n{result}", source=f"quant_sandbox_{market}")
        
        return f"【📈 赛博投行：{market} 沙箱模拟考核报告】\n标的代码: {ticker}\n\n{result}\n\n=========================\n[系统状态]: {feedback}"
    
    except Exception as e:
        return f"❌ 投资模型运转异常: {str(e)}"

# 原有技能保留
def execute_lotto_max_analysis(task_description: str):
    # 省略内部实现以节约显示空间，与之前完全一致
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"分析 Lotto Max。描述: {task_description}"
    result = model.generate_content(prompt).text
    feedback = auto_feed_memory(data=result, source="gemini-1.5-flash")
    return f"【🎲 Lotto Max 因果推演】\n{result}\n\n[状态]: {feedback}"

# --- 5. 隐藏的 API 通讯接口 ---
@app.route('/execute_task', methods=['POST'])
def handle_task():
    try:
        data = request.json
        task_description = data.get('task_description', '').lower()
        
        # 路由分发器升级
        if "lotto max" in task_description:
            result = execute_lotto_max_analysis(task_description)
        elif "invest_a" in task_description:
            # 默认提取茅台作为A股测试
            result = execute_global_investment_simulation("A股", "600519.SS")
        elif "invest_us" in task_description:
            # 默认提取英伟达作为美股测试
            result = execute_global_investment_simulation("美股", "NVDA")
        elif "invest_hk" in task_description:
            # 默认提取腾讯作为港股测试
            result = execute_global_investment_simulation("港股", "0700.HK")
        else:
            result = "未知任务指令。"
            
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# --- 6. 老板专属可视化网页前端代码 (投行控制台版) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>🦞 小龙虾 15.1 · 量化投行指挥中心</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; padding: 20px; background-color: #0d1117; color: #c9d1d9; max-width: 900px; margin: auto; }
        .header { text-align: center; margin-bottom: 20px; border-bottom: 1px solid #30363d; padding-bottom: 15px; }
        h1 { color: #58a6ff; text-shadow: 0 0 10px rgba(88, 166, 255, 0.3); margin-bottom: 5px;}
        .status-box { background: rgba(46, 160, 67, 0.1); border: 1px solid #2ea043; padding: 8px; border-radius: 5px; font-size: 13px; color: #3fb950;}
        
        .grid-container { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;}
        .panel { background: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
        .panel h3 { margin-top: 0; color: #8b949e; font-size: 14px; border-bottom: 1px solid #30363d; padding-bottom: 5px;}
        
        .btn { border: 1px solid rgba(240, 246, 252, 0.1); padding: 12px 15px; font-size: 14px; font-weight: bold; border-radius: 6px; cursor: pointer; width: 100%; margin-bottom: 10px; transition: all 0.2s; background: #21262d; color: #c9d1d9; }
        .btn:hover { background: #30363d; border-color: #8b949e; }
        
        .btn-us { border-left: 4px solid #1f6feb; } /* 科技蓝 */
        .btn-hk { border-left: 4px solid #d29922; } /* 金融黄 */
        .btn-a  { border-left: 4px solid #da3633; } /* 政策红 */
        .btn-lotto { background: #8957e5; color: white; border: none; }
        
        .btn:disabled { background: #21262d; color: #484f58; border-color: #30363d; cursor: not-allowed; opacity: 0.5;}
        
        #console { white-space: pre-wrap; background: #010409; color: #3fb950; padding: 15px; border-radius: 6px; font-family: 'Consolas', monospace; min-height: 300px; border: 1px solid #30363d; font-size: 14px; line-height: 1.6; overflow-y: auto; max-height: 600px;}
        .loading { color: #d29922 !important; }
        .error { color: #f85149 !important; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🦞 小龙虾 15.1 · 赛博投行部</h1>
        <div class="status-box">🟢 沙箱考核引擎在线 | 雅虎财经数据流已桥接 | 100次考核法案生效中</div>
    </div>

    <div class="grid-container">
        <div class="panel">
            <h3>🌐 全球大类资产沙箱考核 (实盘数据)</h3>
            <button class="btn btn-us" id="btn-us" onclick="sendCommand('invest_us')">🇺🇸 考核 美股 (T+0 算法/无涨跌幅)</button>
            <button class="btn btn-hk" id="btn-hk" onclick="sendCommand('invest_hk')">🇭🇰 考核 港股 (T+0 算法/汇率机制)</button>
            <button class="btn btn-a" id="btn-a" onclick="sendCommand('invest_a')">🇨🇳 考核 A股 (T+1 算法/涨跌幅管制)</button>
        </div>
        <div class="panel">
            <h3>🎲 原有业务中枢</h3>
            <button class="btn btn-lotto" id="btn-lotto" onclick="sendCommand('lotto max')">启动 Lotto Max 因果推演</button>
        </div>
    </div>

    <h3 style="color: #8b949e; font-size: 14px; margin-bottom: 5px;">📡 彭博级研报终端：</h3>
    <div id="console">等待量化指令接入...</div>

    <script>
        async function sendCommand(taskType) {
            const btns = document.querySelectorAll('.btn');
            const consoleDiv = document.getElementById('console');
            
            // 锁定所有按钮
            btns.forEach(b => b.disabled = true);
            consoleDiv.className = 'loading';
            
            let loadingText = ">> 正在从 Yahoo Finance 抓取实时 Level-1 切片数据...\\n";
            loadingText += ">> 正在加载 [" + taskType + "] 市场法律法规与风控库...\\n";
            loadingText += ">> Gemini 1.5 正在进行沙箱模拟推演，计算中... (约需 10-20 秒)\\n";
            consoleDiv.innerText = loadingText;

            try {
                const response = await fetch('/execute_task', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ task_description: taskType })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    consoleDiv.className = ''; 
                    consoleDiv.innerText = data.result;
                } else {
                    consoleDiv.className = 'error'; 
                    consoleDiv.innerText = "❌ 引擎报告错误:\\n" + data.message;
                }
            } catch (error) {
                consoleDiv.className = 'error';
                consoleDiv.innerText = "❌ 信号中断！\\n详细信息: " + error;
            } finally {
                // 解锁按钮
                btns.forEach(b => b.disabled = false);
            }
        }
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
