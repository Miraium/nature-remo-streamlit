import streamlit as st
import pandas as pd
import sqlite3
import time
import yaml

# データを読み込む関数
def load_data(db_file):
    conn = sqlite3.connect(db_file)
    data = pd.read_sql_query("SELECT * FROM energy_usage", conn)
    conn.close()
    data['time'] = pd.to_datetime(data['time'])
    return data

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

    placeholder = st.empty()
    while True:
        # データを読み込む
        data = load_data(db_file)
        if not data.empty:
            # グラフを更新
            with placeholder.container():
                plot_graph(data)
        # 10秒待機
        time.sleep(10)

if __name__ == "__main__":
    main()