from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = r"c:\Users\user\Desktop\DIC4\aiotdb.db"

@app.route('/addData', methods=['GET'])
def add_data():
    # 接收從 Arduino 傳來的 temp 與 humid 參數
    temp = request.args.get('temp')
    humid = request.args.get('humid')
    
    if not temp or not humid:
        return jsonify({"status": "error", "message": "Missing temp or humid parameters"}), 400
        
    try:
        temp = float(temp)
        humid = float(humid)
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid parameter types"}), 400
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # 寫入我們今天建立的 sensors 表格，欄位為 temperature, humidity
        cursor.execute("INSERT INTO sensors (temperature, humidity) VALUES (?, ?)", (temp, humid))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Data logged successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # 執行在 port 5000, 允許所有 IP 連線 (Host=0.0.0.0) 以便讓同一網段的 Arduino 可以存取
    app.run(host='0.0.0.0', port=5000, debug=True)
