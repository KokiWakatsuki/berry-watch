"""
ベリーウォッチのサーバー．

センサーから受信した温度・湿度を保存し，画面からの要求に応答する．
"""

import os
import sqlite3
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


# ============================================================
# 設定
# ============================================================

DB_PATH = "data/house.db"   # データベースのファイル
SCHEMA_PATH = "schema.sql"  # テーブルの作り方
COLD_LIMIT = 8.0            # 低温の基準（℃）．いちごの夜間の最低温度の目安
RECENT_COUNT = 60           # 棟の画面に表示する記録の件数


# ============================================================
# データベース
# ============================================================

def connect():
    """データベースに接続する．"""
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row             # 列名（例：row["temperature"]）で値を取得できるようにする
    db.execute("PRAGMA foreign_keys = ON")  # 存在しない棟への記録を拒否する
    return db


def fetch_all(sql, params=()):
    """SQL を実行し，結果の行を返す．接続は必ず閉じる．"""
    db = connect()
    try:
        return db.execute(sql, params).fetchall()
    finally:
        db.close()


def write(sql, params=()):
    """SQL で書き込む．接続は必ず閉じる．"""
    db = connect()
    try:
        db.execute(sql, params)
        db.commit()
    finally:
        db.close()


def create_tables():
    """テーブルがなければ作成する．"""
    os.makedirs("data", exist_ok=True)
    with open(SCHEMA_PATH, encoding="utf-8") as file:
        schema = file.read()

    db = connect()
    try:
        db.executescript(schema)
        db.commit()
    finally:
        db.close()


def check_house_exists(house_id):
    """棟の存在を確認する．なければ 404（Not Found）を返す．"""
    rows = fetch_all("SELECT id FROM houses WHERE id = ?", (house_id,))
    if len(rows) == 0:
        raise HTTPException(status_code=404, detail=f"{house_id} という棟はありません")


# ============================================================
# API（画面・センサーからの要求に応答する）
# ============================================================

app = FastAPI()


class Reading(BaseModel):
    """センサーから受信する，1回分の記録．"""
    house_id: int
    temperature: float = Field(ge=-30, le=60)  # 範囲外の温度は拒否する
    humidity: float = Field(ge=0, le=100)      # 湿度の範囲は 0〜100%


@app.get("/api/settings")
def get_settings():
    """画面と共通の設定（低温の基準）を返す．"""
    return {"cold_limit": COLD_LIMIT}


@app.post("/api/readings")
def add_reading(reading: Reading):
    """センサーから受信した記録を保存する．"""
    check_house_exists(reading.house_id)

    measured_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    sql = "INSERT INTO readings (house_id, measured_at, temperature, humidity) VALUES (?, ?, ?, ?)"
    params = (reading.house_id, measured_at, reading.temperature, reading.humidity)

    write(sql, params)
    return {"ok": True}


@app.get("/api/houses")
def list_houses():
    """棟の一覧を返す．"""
    sql = "SELECT id, name, crop, photo FROM houses ORDER BY id"
    rows = fetch_all(sql)

    houses = []
    for row in rows:
        houses.append(dict(row))
    return houses


@app.get("/api/houses/{house_id}/today")
def today_summary(house_id: int):
    """棟の本日の集計（最新値・最高・最低）を返す．"""
    check_house_exists(house_id)
    today = datetime.now().strftime("%Y-%m-%d")
    sql = "SELECT measured_at, temperature, humidity FROM readings WHERE house_id = ? ORDER BY id"

    # 1. この棟の全記録を取得する（古い順）
    rows = fetch_all(sql, (house_id,))

    # 2. 本日の記録だけを抽出する
    today_rows = []
    for row in rows:
        if row["measured_at"].startswith(today):
            today_rows.append(row)

    # 3. 本日の記録がなければ「記録なし」を返す
    if len(today_rows) == 0:
        return {"house_id": house_id, "has_data": False}

    # 4. 最新の記録と，本日の最高・最低を求める
    latest = today_rows[-1]
    highest = today_rows[0]["temperature"]
    lowest = today_rows[0]["temperature"]
    for row in today_rows:
        if row["temperature"] > highest:
            highest = row["temperature"]
        if row["temperature"] < lowest:
            lowest = row["temperature"]

    # 5. 集計結果を返す
    return {
        "house_id": house_id,
        "has_data": True,
        "measured_at": latest["measured_at"],
        "temperature": latest["temperature"],
        "humidity": latest["humidity"],
        "max": highest,
        "min": lowest,
        "is_cold": latest["temperature"] < COLD_LIMIT,
    }


@app.get("/api/houses/{house_id}/recent")
def recent_readings(house_id: int):
    """棟の直近の記録を古い順に返す（棟の画面のグラフ用）．"""
    check_house_exists(house_id)
    sql = """
        SELECT measured_at, temperature, humidity FROM readings
        WHERE house_id = ?
        ORDER BY id DESC
        LIMIT ?
    """

    # 新しい順に RECENT_COUNT 件を取得し，古い順に並べ替える
    rows = fetch_all(sql, (house_id, RECENT_COUNT))
    readings = []
    for row in reversed(rows):
        readings.append(dict(row))
    return readings


# ============================================================
# 画面（HTML・CSS・JavaScript・画像を返す）
# ============================================================

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def list_page():
    """一覧画面．"""
    return FileResponse("static/index.html")


@app.get("/house")
def house_page():
    """棟の画面．"""
    return FileResponse("static/house.html")


# ============================================================
# 起動時に1回だけ実行する
# ============================================================

create_tables()
