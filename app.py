# 小龙虾 15.1 - 核心执行引擎 (app.py)

import os
import random
from flask import Flask, request, jsonify
from supabase import create_client, Client
import openai

# --- 初始化 ---
app = Flask(__name__)

# 从 GitHub Secrets (环境变量) 加载密钥
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY") # 注意这里用 anon key
OPENAI_API_KEY_POOL_STR = os.environ.get("OPENAI_API_KEY_POOL")

# --- 检查密钥是否存在 ---
if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY_POOL_STR]):
    print("❌ 错误：核心密钥环境变量未完全设置！")
    # 这里可以在未来增加更详细的错误处理

# 创建 Supabase 客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 核心功能模块 ---

def auto_feed_memory(data: str, source: str):
    """核心逻辑：将成功的结果向量化存入 Supabase"""
    try:
        supabase.table('claw15_memory').insert({"content": data, "metadata": {"source": source}}).execute()
        return "✅ 记忆已喂料，系统进化中..."
    except Exception as e:
        error_message = f"❌ 记忆喂料失败: {e}"
        print(error_message)
        return error_message

def execute_lotto_max_analysis(task_description: str):
    """执行 Lotto Max 分析任务"""
    # 随机选择一个 OpenAI API Key
    api_keys = OPENAI_API_KEY_POOL_STR.split(',')
    selected_key = random.choice(api_keys).strip()
    
    client = openai.OpenAI(api_key=selected_key)

    # 实际的分析逻辑会更复杂，这里用一个 AI 调用作为示例
    response = client.chat.completions.create(
      model="gpt-4o", # 可以换成更强大的模型
      messages=[
        {"role": "system", "content": "你是一个顶级的彩票数据分析师，专门分析 Lotto Max。"},
        {"role": "user", "content": f"基于历史数据和当前趋势，请分析下一个 Lotto Max 的号码。任务描述: {task_description}"}
      ]
    )
    result = response.choices[0].message.content
    
    # 任务成功后，将结果喂给记忆库
    feedback = auto_feed_memory(data=result, source="gpt-4o_analysis")
    
    return f"【Lotto Max 分析报告】\n{result}\n\n---\n{feedback}"


def execute_cleaning_lead_task(task_description: str):
    """执行清洁生意潜客挖掘任务"""
    # 伪代码：实际会在这里执行网络抓取
    result = "发现新的高价值清洁订单：多伦多市中心 ABC 公司，5000平米办公室开荒保洁。联系人：John Doe。"
    
    feedback = auto_feed_memory(data=result, source="web_scraper")
    
    return f"【清洁生意情报】\n{result}\n\n---\n{feedback}"


# --- API 入口 ---
# 这是给 Dify 或其他大脑中枢调用的接口
@app.route('/execute_task', methods=['POST'])
def handle_task():
    data = request.json
    task_description = data.get('task_description', '').lower()
    
    if not task_description:
        return jsonify({"error": "缺少任务描述 (task_description)"}), 400

    try:
        # 根据任务描述，自动分配给不同的执行模块
        if "lotto max" in task_description:
            result = execute_lotto_max_analysis(task_description)
        elif "cleaning" in task_description or "保洁" in task_description:
            result = execute_cleaning_lead_task(task_description)
        else:
            result = "未知任务类型，无法执行。"
            
        return jsonify({"status": "success", "result": result})

    except Exception as e:
        error_msg = f"任务执行失败: {str(e)}"
        print(f"❌ {error_msg}")
        # 未来可以在这里触发自愈进化逻辑
        return jsonify({"status": "error", "message": error_msg}), 500

# 心跳检测接口，确保服务在线
@app.route('/', methods=['GET'])
def health_check():
    return "小龙虾 15.1 执行引擎在线，待命中。"

if __name__ == '__main__':
    # 使用 0.0.0.0 使服务在网络上可见
    # 端口可以根据部署平台的要求更改
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
