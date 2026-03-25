# 小龙虾 15.1 - 核心执行引擎 (app.py) - 【网页指挥中心终极版】

import os
from flask import Flask, request, jsonify, render_template_string
from supabase import create_client, Client
import google.generativeai as genai

# --- 1. 初始化系统 ---
app = Flask(__name__)

# --- 2. 加载云端密钥 (Render 环境变量) ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- 3. 配置大脑与记忆库 ---
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Google Gemini 引擎已就绪。")
else:
    print("❌ 警告：未检测到 GEMINI_API_KEY！")

if all([SUPABASE_URL, SUPABASE_KEY]):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase 记忆图书馆已就绪。")
else:
    print("❌ 警告：未检测到 Supabase 密钥！")

# --- 4. 核心技能定义 ---

def auto_feed_memory(data: str, source: str):
    """技能一：经验沉淀 (保存结果到 Supabase)"""
    try:
        supabase.table('claw15_memory').insert({"content": data, "metadata": {"source": source}}).execute()
        return "✅ 记忆已成功喂料入库，系统进化中..."
    except Exception as e:
        error_msg = f"❌ 记忆喂料失败: {str(e)}"
        print(error_msg)
        return error_msg

def execute_lotto_max_analysis(task_description: str):
    """技能二：Lotto Max 深度推演 (调用 Gemini)"""
    try:
        # 召唤 Gemini 1.5 极速版模型
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = f"你现在是【小龙虾 15.1 专家内阁】的首席彩票分析师。请针对 Lotto Max 进行严谨的数据与趋势推演。任务描述: {task_description}"
        
        # 让 AI 开始思考 (这里会耗时十几秒)
        response = model.generate_content(prompt)
        result = response.text
        
        # 思考完毕，立刻保存经验
        feedback = auto_feed_memory(data=result, source="gemini-1.5-flash")
        
        return f"【🎲 Lotto Max 因果推演报告】\n\n{result}\n\n=========================\n[系统状态]: {feedback}"
    except Exception as e:
        return f"❌ Gemini AI 专家会诊失败，原因: {str(e)}"

def execute_cleaning_lead_task(task_description: str):
    """技能三：清洁生意潜客挖掘 (演示版)"""
    result = "【情报嗅探结果】\n目标：多伦多市中心 ABC 科技公司\n面积：约 5000 平方英尺 (新办公室)\n需求：开荒保洁与长期日常清洁\n建议：评级为 A 级，系统已生成邮件草稿备用。"
    feedback = auto_feed_memory(data=result, source="web_scraper_mock")
    return f"【🧹 清洁生意高价值情报】\n\n{result}\n\n=========================\n[系统状态]: {feedback}"

# --- 5. 隐藏的 API 通讯接口 ---

@app.route('/execute_task', methods=['POST'])
def handle_task():
    """接收来自网页面板的指令并分配任务"""
    try:
        data = request.json
        task_description = data.get('task_description', '').lower()
        
        if "lotto max" in task_description:
            result = execute_lotto_max_analysis(task_description)
        elif "cleaning" in task_description or "保洁" in task_description:
            result = execute_cleaning_lead_task(task_description)
        else:
            result = "未知任务指令，无法识别。"
            
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# --- 6. 老板专属可视化网页前端代码 ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>🦞 小龙虾 15.1 终极指挥中心</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; background-
