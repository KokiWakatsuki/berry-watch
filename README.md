# ベリーウォッチ

ひだまり農園の，いちごのビニールハウス8棟の温度・湿度を監視するアプリ．
夜間のハウス内が 8℃ 未満になると，低温の棟を警告表示する．

## 起動

Ubuntu で，このフォルダに移動して実行：

```bash
docker compose up --build
```

`Application startup complete.` と表示されたら起動完了．
ブラウザで http://localhost:8000 を開く．終了は Ctrl + C．

初回は記録がないため，全棟「記録なし」と表示される．

## センサーの代わりを実行

別の Ubuntu の画面で，このフォルダに移動して実行：

```bash
python3 sensor.py
```

8棟の温度・湿度を10分ごとにサーバーへ送信する．終了は Ctrl + C．

## 測定値が画面に表示されるまで

```
センサー（sensor.py）
   │  POST /api/readings     測定値を送信
   ▼
サーバー（app.py）            受信して保存
   ▼
データベース（data/house.db）
   ▲  取得
サーバー（app.py）
   ▲  GET /api/houses など    画面からの要求
画面（static/）
```

## API

| 要求 | 応答 | app.py の関数 |
|---|---|---|
| `POST /api/readings` | 測定値を保存 | `add_reading` |
| `GET /api/settings` | 低温の基準（8℃） | `get_settings` |
| `GET /api/houses` | 棟の一覧 | `list_houses` |
| `GET /api/houses/3/today` | 3号棟の本日の集計（最新値・最高・最低） | `today_summary` |
| `GET /api/houses/3/recent` | 3号棟の直近60件の記録 | `recent_readings` |

http://localhost:8000/docs で，API をブラウザから試せる．

## ファイル構成

```
berry-watch/
├── app.py          サーバー．測定値の保存と，画面への応答
├── schema.sql      テーブル定義
├── sensor.py       センサーの代わり．10分ごとに測定値を送信
├── static/         画面
│   ├── index.html  一覧画面
│   ├── list.js     一覧画面の処理
│   ├── house.html  棟の画面
│   ├── house.js    棟の画面の処理
│   ├── style.css   スタイル
│   └── images/     写真
├── Dockerfile      コンテナの作成手順
└── compose.yml     コンテナの起動設定
```
