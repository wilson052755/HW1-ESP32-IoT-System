import sqlite3
import time
import random
import os

DB_PATH = r"c:\Users\user\Desktop\DIC4\aiotdb.db"

def init_db():
    """初始化資料庫與表格"""
    # 建立與 SQLite 資料庫的連線（若檔案不存在會自動建立）
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 建立 sensors 表格
    # id: 自動遞增主鍵
    # timestamp: 記錄時間，預設為當下時間 (UTC)
    # temperature: 溫度 (DHT11 通常範圍 0~50°C)
    # humidity: 濕度 (DHT11 通常範圍 20~90%)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT (datetime('now', 'localtime')),
            temperature REAL,
            humidity REAL
        )
    ''')
    conn.commit()
    conn.close()
    print("資料庫與表格初始化完成。")

def simulate():
    """每隔 2 秒插入一筆模擬資料"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        print("開始模擬 DHT11 訊號寫入資料庫... (按 Ctrl+C 停止)")
        while True:
            # 隨機產生符合 DHT11 規格的溫濕度資料
            temperature = round(random.uniform(20.0, 35.0), 1)
            humidity = round(random.uniform(40.0, 80.0), 1)
            
            cursor.execute('''
                INSERT INTO sensors (temperature, humidity)
                VALUES (?, ?)
            ''', (temperature, humidity))
            conn.commit()
            
            print(f"寫入成功 -> 溫度: {temperature}°C, 濕度: {humidity}%")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n停止模擬程式。")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    simulate()
