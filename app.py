@echo off
chcp 65001 >nul
title ☕ 小龙虾 18.1 - 游资印钞机 (全自动挂机中...)
color 0A

echo ========================================================
echo   🔥 尊敬的老板，正在为您启动【小龙虾 18.1 全自动游资系统】
echo ========================================================
echo.
echo [1/3] 正在检查并自动安装需要的零件（请稍等几秒钟）...
pip install Flask waitress yfinance pandas openai supabase >nul 2>&1

echo [2/3] 正在注入您的专属 DeepSeek 投资大脑...
:: 【注意】老板，请把下面这行引号里的字，换成您真实的 DeepSeek API 密钥
set DEEPSEEK_API_KEY="在这里填入您的密钥，如果没有就保留这行不动"

echo [3/3] 系统点火！正在为您自动打开【老板专属可视化看板】...
start http://127.0.0.1:8080

echo.
echo ⚠️ 警告：请不要关闭这个黑色的窗口！只要它开着，系统就在为您赚钱。
echo.
:: 运行桌面上的 app.py
python "%USERPROFILE%\Desktop\app.py"

pause
