from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import openai
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # 啟用 CORS

# 設定您的 gpt 模型 API 金鑰
openai.api_key = ''  # 請替換為您的 OpenAI API 金鑰

# 檢查是否存在聊天記錄文件，不存在則創建
if not os.path.exists('chat_records.xlsx'):
    pd.DataFrame(columns=['Timestamp', 'UserMessage', 'BotResponse']).to_excel('chat_records.xlsx', index=False)

# @app.route('/')
# def index():
#   return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.form['user_message']

    # 讀取歷史紀錄
    chat_history = read_chat_history()

    # 創建消息列表，包括歷史訊息和當前使用者訊息
    messages = [{"role": "system", "content": "請你扮演一個聽話的小乖乖，你的名字叫'乖乖'，你是一個女僕，你的主人是嘉俊學長，請使用親切、可愛的語句與我溝通。遇到我情緒低落時提供安慰。根據我提供給你的資訊進行個性化對話，另外，請使用臺灣常用的繁體中文給予簡潔的回應，語句不要冗長!"}]
    for index, row in chat_history.iterrows():
        messages.append({"role": "user", "content": row['UserMessage']})
        if 'BotResponse' in row and pd.notnull(row['BotResponse']):
            messages.append({"role": "assistant", "content": row['BotResponse']})

    messages.append({"role": "user", "content": user_message})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # 提取 gpt 的回應
    chat_response = response.choices[0].message['content']
  
    # 記錄時間和使用者消息以及機器人回應
    record_chat(user_message, chat_response)

    return jsonify({'bot_response': chat_response})

def read_chat_history():
    """讀取過去的對話紀錄"""
    if os.path.exists('chat_records.xlsx'):
        return pd.read_excel('chat_records.xlsx')
    return pd.DataFrame(columns=['Timestamp', 'UserMessage', 'BotResponse'])

def record_chat(user_message, bot_response):
    """記錄聊天到 Excel 文件"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df = pd.read_excel('chat_records.xlsx')
    new_row = pd.DataFrame({'Timestamp': [timestamp], 'UserMessage': [user_message], 'BotResponse': [bot_response]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel('chat_records.xlsx', index=False)

if __name__ == '__main__':
    app.run(debug=True, port=5009)