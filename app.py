# 小龙虾 15.1 - 核心执行引擎 (app.py) - 【Google Gemini 动力版】

import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
import google.generativeai as genai

# --- 初始化 ---
app = Flask(__name__)

# --- 从 Render 的环境变量中加载密钥 ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- 检查并配置 Google Gemini ---
if not GEMINI_API_KEY:
    print("❌ 错误：GEMINI_API_KEY 未设置！")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Google Gemini 引擎已配置。")

# --- 检查并创建 Supabase 客户端 ---
if not all([SUPABASE_URL, SUPABASE_KEY]):
    print("❌ 错误：Supabase 密钥未完全设置！")
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase 记忆数据库已连接。")

# --- 核心功能模块 ---

def auto_feed_memory(data: str, source: str):
    """核心逻辑：将成功的结果存入 Supabase"""
    try:
        supabase.table('claw15_memory').insert({"content": data, "metadata": {"source": source}}).execute()
        return "✅ 记忆已喂料，系统进化中..."
    except Exception as e:
        error_message = f"❌ 记忆喂料失败: {e}"
        print(error_message)
        return error_message

def execute_lotto_max_analysis(task_description: str):
    """执行 Lotto Max 分析任务 (由 Gemini 驱动)"""
    try:
        # 选择一个快速且免费的模型
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = f"你是一个顶级的彩票数据分析师，专门分析 Lotto Max。基于历史数据和当前趋势，请分析下一个 Lotto Max 的号码。任务描述: {task_description}"
        
        response = model.generate_content(prompt)
        result = response.text
        
        # 任务成功后，将结果喂给记忆库
        feedback = auto_feed_memory(data=result, source="gemini-1.5-flash")
        
        return f"【Lotto Max 分析报告 (Gemini 版)】\n{result}\n\n---\n{feedback}"
    except Exception as e:
        error_message = f"❌ Gemini AI 分析失败: {e}"
        print(error_message)
        return error_message


def execute_cleaning_lead_task(task_description: str):
    """执行清洁生意潜客挖掘任务"""
    result = "发现新的高价值清洁订单：多伦多市中心 ABC 公司，5000平米办公室开荒保洁。联系人：Jane Doe。"
    feedback = auto_feed_memory(data=result, source="web_scraper_mock")
    return f"【清洁生意情报】\n{result}\n\n---\n{feedback}"


# --- API 入口 ---
@app.route('/execute_task', methods=['POST'])
def handle_task():
    data = request.json
    task_description = data.get('task_description', '').lower()
    
    if not task_description:
        return jsonify({"error": "缺少任务描述 (task_description)"}), 400

    if "lotto max" in task_description:
        result = execute_lotto_max_analysis(task_description)
    elif "cleaning" in task_description or "保洁" in task_description:
        result = execute_cleaning_lead_task(task_description)
    else:
        result = "未知任务类型，无法执行。"
        
    return jsonify({"status": "success", "result": result})

@app.route('/', methods=['GET'])
def health_check():
    return "小龙虾 15.1 执行引擎在线 (Google Gemini 动力版)，待命中。"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
