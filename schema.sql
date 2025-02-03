-- ベリーウォッチのテーブル定義
-- 起動時に毎回実行する．テーブルが既にあれば何もしない．


-- 棟（ハウス）．全8棟
CREATE TABLE IF NOT EXISTS houses (
  id    INTEGER PRIMARY KEY,
  name  TEXT NOT NULL,   -- 例：1号棟
  crop  TEXT NOT NULL,   -- 栽培しているいちごの品種
  photo TEXT NOT NULL    -- 画面に表示する写真のファイル名
);

-- 測定記録．センサーが棟ごとに1行ずつ追加する
CREATE TABLE IF NOT EXISTS readings (
  id          INTEGER PRIMARY KEY,
  house_id    INTEGER NOT NULL REFERENCES houses (id),  -- 対象の棟（houses の id）
  measured_at TEXT    NOT NULL,  -- 測定日時．例：2026-11-24 06:30
  temperature REAL    NOT NULL,  -- 温度（℃）
  humidity    REAL    NOT NULL   -- 湿度（%）
);


-- 初期データ（棟）
INSERT OR IGNORE INTO houses (id, name, crop, photo) VALUES
  (1, '1号棟', 'いちご（紅ほっぺ）', 'strawberry.jpg'),
  (2, '2号棟', 'いちご（紅ほっぺ）', 'strawberry.jpg'),
  (3, '3号棟', 'いちご（紅ほっぺ）', 'strawberry.jpg'),
  (4, '4号棟', 'いちご（紅ほっぺ）', 'strawberry.jpg'),
  (5, '5号棟', 'いちご（とちおとめ）', 'strawberry.jpg'),
  (6, '6号棟', 'いちご（とちおとめ）', 'strawberry.jpg'),
  (7, '7号棟', 'いちご（とちおとめ）', 'strawberry.jpg'),
  (8, '8号棟', 'いちご（とちおとめ）', 'strawberry.jpg');
