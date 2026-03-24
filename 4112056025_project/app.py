import sqlite3
import pandas as pd
import streamlit as st
import time
import altair as alt

# 設定網頁標題與排版
st.set_page_config(page_title="DHT11 Sensor Dashboard", layout="wide")

DB_PATH = r"c:\Users\user\Desktop\DIC4\aiotdb.db"

def load_data():
    """從資料庫讀取最新的感測器數據"""
    try:
        conn = sqlite3.connect(DB_PATH)
        # 取出最新的 50 筆資料
        df = pd.read_sql_query("SELECT * FROM sensors ORDER BY timestamp DESC LIMIT 50", conn)
        conn.close()
        # 反轉順序讓時間遞增，有利於畫圖
        if not df.empty:
            df = df.sort_values('timestamp')
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"讀取資料庫失敗: {e}")
        return pd.DataFrame()

def create_hover_chart(df, y_field, y_title, line_color):
    """建立帶有游標追蹤鉛直線的 Altair 互動圖表"""
    # 建立一個感測游標Ｘ軸位置的選擇器 (Selector)
    hover = alt.selection_point(fields=['timestamp'], nearest=True, on='mouseover', empty=False)
    
    # 畫出平滑的折線圖主體
    line = alt.Chart(df).mark_line(interpolate='monotone', color=line_color, strokeWidth=3).encode(
        x=alt.X('timestamp:T', title='時間'),
        y=alt.Y(f'{y_field}:Q', scale=alt.Scale(zero=False), title=y_title)
    )
    
    # 建立透明的點用來捕捉所有的游標停留事件，並掛載提示框 Tooltip
    selectors = alt.Chart(df).mark_point().encode(
        x='timestamp:T',
        opacity=alt.value(0),
        tooltip=[
            alt.Tooltip('timestamp:T', title='紀錄時間', format='%Y-%m-%d %H:%M:%S'), 
            alt.Tooltip(f'{y_field}:Q', title=y_title, format='.1f')
        ]
    ).add_params(hover)
    
    # 畫出當游標停留時才顯示的圓點
    points = line.mark_point(size=90, color=line_color, filled=True).encode(
        opacity=alt.condition(hover, alt.value(1), alt.value(0))
    )
    
    # 畫出跟隨游標的鉛直線 (Rule)，僅在選取時顯示
    rules = alt.Chart(df).mark_rule(color='#c1bdb3', strokeWidth=1, strokeDash=[4, 4]).encode(
        x='timestamp:T'
    ).transform_filter(hover)
    
    # 將所有圖層疊加並允許互動
    return (line + selectors + points + rules).interactive()

st.title("即時溫濕度數據儀表板 (Streamlit)")

st.sidebar.title("📖 網站說明")
st.sidebar.markdown("""
本網站用於即時監控 **DHT11 溫濕度感測器** 的環境數據。

### 🚀 操作方法：
1. **模擬感測器**：
   開啟終端機執行 `python simulate_dht11.py`。
2. **真實硬體感測器**：
   - 先執行 API 接收端：`python flask_api.py`。
   - 將 `DHT11_WiFi.ino` 燒錄至具有 WiFi 功能的 Arduino / ESP 開發板。
3. **資料刷新**：
   以下滑桿可設定網頁自動從 SQLite 資料庫重新撈取數據的時間間隔。

---
""")

# 在側邊欄設定更新頻率
refresh_rate = st.sidebar.slider("自動更新頻率 (秒)", min_value=1, max_value=10, value=2)
st.sidebar.info("💡 請確認您的資料來源程式正在背景執行中。")

# 建立一個佔位符來刷新內容
placeholder = st.empty()

while True:
    df = load_data()
    
    with placeholder.container():
        if df.empty:
            st.warning("目前資料庫中沒有資料，請確認資料庫是否建立，或確認模擬程式是否正在執行中。")
        else:
            # 取得最新一筆資料
            latest_temp = df.iloc[-1]["temperature"]
            latest_hum = df.iloc[-1]["humidity"]
            latest_time = df.iloc[-1]["timestamp"]
            
            # 顯示指標 (Metrics)
            col1, col2, col3 = st.columns(3)
            col1.metric(label="最新溫度 (°C)", value=f"{latest_temp:.1f}")
            col2.metric(label="最新濕度 (%)", value=f"{latest_hum:.1f}")
            col3.metric(label="最後更新時間", value=str(latest_time))
            
            st.markdown("---")
            
            # 使用兩欄來顯示圖表
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.subheader("溫度趨勢 (°C)")
                temp_chart = create_hover_chart(df, "temperature", "溫度 (°C)", "#7f7979")
                st.altair_chart(temp_chart, use_container_width=True)
                
            with chart_col2:
                st.subheader("濕度趨勢 (%)")
                hum_chart = create_hover_chart(df, "humidity", "濕度 (%)", "#5f5b6b")
                st.altair_chart(hum_chart, use_container_width=True)
            
            st.markdown("---")
            st.subheader("最新數據紀錄 (最近 10 筆)")
            st.dataframe(df.sort_values("timestamp", ascending=False).head(10), use_container_width=True)
            
    # 等待設定的秒數後重新執行頁面渲染
    time.sleep(refresh_rate)
    st.rerun()
