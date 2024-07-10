import streamlit as st
import pandas as pd
import sqlite3
import time
import yaml

# データを読み込む関数
def load_data(db_file):
    try:
        conn = sqlite3.connect(db_file)
        data = pd.read_sql_query("SELECT * FROM energy_usage", conn)
        conn.close()
        data['time'] = pd.to_datetime(data['time'])
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=["time", "value"])

# グラフ描画関数
def plot_graph(data):
    st.line_chart(data.set_index('time'))

# メインループ
def main():
    # 設定ファイルを読み込む
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    db_file = config['database_file']

    st.title("Real-time Energy Usage Monitoring")
    # サイドバーの設定
    st.sidebar.header("Settings")
    update_interval = st.sidebar.slider("Data Update Interval (seconds)", 1, 60, 10)
    # メトリック表示用のプレースホルダー
    latest_metric = st.sidebar.empty()
    max_metric = st.sidebar.empty()
    min_metric = st.sidebar.empty()
    avg_metric = st.sidebar.empty()

    # 初期データ読み込み
    data = load_data(db_file)

    placeholder = st.empty()
    with placeholder.container():
        plot_graph(data)

    while True:
        # データを読み込む
        data = load_data(db_file)
        if not data.empty:
            # 最新の電力使用量
            latest_value = data.iloc[-1]['value']
            latest_metric.metric(label="Latest Energy Usage", value=f"{latest_value} W")

            # 最大・最小・平均電力使用量
            max_value = data['value'].max()
            min_value = data['value'].min()
            avg_value = data['value'].mean()
            max_metric.metric(label="Max Energy Usage", value=f"{max_value} W")
            min_metric.metric(label="Min Energy Usage", value=f"{min_value} W")
            avg_metric.metric(label="Avg Energy Usage", value=f"{avg_value:.2f} W")

            # グラフを更新
            with placeholder.container():
                plot_graph(data)
        # 更新間隔
        time.sleep(update_interval)

if __name__ == "__main__":
    main()