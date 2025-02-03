// 棟の画面の処理
// URL の「?id=3」で棟を特定し，直近の記録を数値とグラフで表示する．


// ============================================================
// 対象の棟と画面の要素
// ============================================================

const houseId = new URLSearchParams(location.search).get("id");  // URL の ?id=3 の「3」
const nameText = document.getElementById("name");
const cropText = document.getElementById("crop");
const photoImage = document.getElementById("photo");
const temperatureText = document.getElementById("temperature");
const humidityText = document.getElementById("humidity");
const timeText = document.getElementById("time");
const chartArea = document.getElementById("chart");


// ============================================================
// 関数
// ============================================================

// サーバーから JSON を取得する．失敗時は理由つきでエラーにする
async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${url} の取得に失敗（${response.status}）`);
  }
  return await response.json();
}

// 棟の名前・作物・写真を表示する
function showHouse(house) {
  document.title = `${house.name} | ベリーウォッチ`;
  nameText.textContent = house.name;
  cropText.textContent = house.crop;
  photoImage.src = `/static/images/${house.photo}`;
}

// 最新の記録を表示する
function showLatest(latest) {
  temperatureText.textContent = `${latest.temperature.toFixed(1)}℃`;
  humidityText.textContent = `${latest.humidity}%`;
  timeText.textContent = `最終測定：${latest.measured_at}`;
}

// 直近の温度を折れ線グラフで表示する
function drawChart(readings, coldLimit) {
  // グラフ部品（Chart.js）はインターネットから読み込む．失敗時はその旨を表示する
  if (typeof Chart === "undefined") {
    chartArea.replaceWith("グラフ部品の読み込みに失敗．インターネット接続を確認してください．");
    return;
  }
  // グラフの文字をページと同じ書体・サイズにする
  Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
  Chart.defaults.font.size = 13;

  const labels = [];
  const temperatures = [];
  const coldLine = [];
  for (const reading of readings) {
    labels.push(reading.measured_at.slice(5));  // 「11-24 06:30」の部分（年は省略）
    temperatures.push(reading.temperature);
    coldLine.push(coldLimit);
  }

  new Chart(chartArea, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        { label: "温度（℃）", data: temperatures, borderColor: "#03AF7A", tension: 0.3 },
        { label: "低温の基準", data: coldLine, borderColor: "#FF4B00", borderDash: [6, 6], pointRadius: 0 },
      ],
    },
    options: { maintainAspectRatio: false },  // 高さは style.css の .chart-box で指定
  });
}

// 画面を表示する
async function showPage() {
  const settings = await getJson("/api/settings");
  const houses = await getJson("/api/houses");
  const house = houses.find((item) => String(item.id) === houseId);
  if (house === undefined) {
    nameText.textContent = "該当する棟がありません";
    return;
  }
  showHouse(house);

  const readings = await getJson(`/api/houses/${houseId}/recent`);
  if (readings.length === 0) {
    timeText.textContent = "記録なし";
    return;
  }
  showLatest(readings[readings.length - 1]);
  drawChart(readings, settings.cold_limit);
}


// ============================================================
// 実行開始
// ============================================================

showPage().catch((error) => {
  nameText.textContent = "読み込み失敗";
  timeText.textContent = `サーバーの起動を確認してください（${error.message}）`;
});
