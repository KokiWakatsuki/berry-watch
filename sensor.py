"""
センサーの代わりをするプログラム．

実際のハウスでは，センサー（測定機器）が温度・湿度を測定し，サーバーに送信する．
ここでは8棟分の値を生成し，10分ごとに送信する．終了は Ctrl + C．
"""

import json
import random
import time
import urllib.request


# ============================================================
# 設定
# ============================================================

SERVER_URL = "http://localhost:8000/api/readings"  # 送信先
HOUSE_IDS = [1, 2, 3, 4, 5, 6, 7, 8]               # 測定する棟
INTERVAL_SECONDS = 600                             # 送信間隔（秒）
TIMEOUT_SECONDS = 5                                # 応答の待機時間（秒）


# ============================================================
# 関数
# ============================================================

def next_value(previous, change, lowest, highest):
    """前回値を少し変化させた値を返す（実際の温度・湿度は急変しないため）．"""
    value = previous + random.uniform(-change, change)
    if value < lowest:
        value = lowest
    if value > highest:
        value = highest
    return round(value, 1)


def send(house_id, temperature, humidity):
    """測定値をサーバーに送信する．"""
    body = {"house_id": house_id, "temperature": temperature, "humidity": humidity}
    data = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    request = urllib.request.Request(SERVER_URL, data=data, headers=headers)

    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS):
        pass  # 応答があれば送信成功．応答の中身は使わない


def main():
    """全棟の値を10分ごとに測定・送信し続ける．"""
    # 棟ごとの現在値．初期値は全棟共通
    temperatures = {}
    humidities = {}
    for house_id in HOUSE_IDS:
        temperatures[house_id] = 10.0
        humidities[house_id] = 75.0

    while True:
        for house_id in HOUSE_IDS:
            temperatures[house_id] = next_value(temperatures[house_id], 0.4, -10.0, 40.0)
            humidities[house_id] = next_value(humidities[house_id], 1.0, 30.0, 100.0)

            try:
                send(house_id, temperatures[house_id], humidities[house_id])
                print(f"{house_id}号棟：{temperatures[house_id]}℃，{humidities[house_id]}% を送信")
            except OSError as error:
                print(f"{house_id}号棟：送信失敗（{error}）．サーバーの起動を確認してください")

        time.sleep(INTERVAL_SECONDS)


# ============================================================
# 実行開始（python3 sensor.py で実行したときだけ）
# ============================================================

if __name__ == "__main__":
    main()
