// 一覧画面の処理
// 棟の一覧を取得し，棟ごとのカードを表示する．


// ============================================================
// 画面の要素
// ============================================================

const cardsArea = document.getElementById("cards");
const cardTemplate = document.getElementById("card-template");
const alertBar = document.getElementById("alert");
const summaryText = document.getElementById("summary");
const elapsedText = document.getElementById("elapsed");
const reloadButton = document.getElementById("reload");


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

// 温度を「12.3℃」の形式にする．記録がなければ「－」
function formatTemperature(value) {
  if (value === undefined) {
    return "－";
  }
  return `${value.toFixed(1)}℃`;
}

// 棟1つ分のカードを作成する
function makeCard(house, today) {
  const card = cardTemplate.content.firstElementChild.cloneNode(true);

  let humidityText = "－";
  let timeText = "本日の記録なし";
  if (today.has_data) {
    humidityText = `${today.humidity}%`;
    timeText = `測定：${today.measured_at}`;
  }

  card.href = `/house?id=${house.id}`;
  card.querySelector(".card-photo").src = `/static/images/${house.photo}`;
  card.querySelector(".card-name").textContent = house.name;
  card.querySelector(".card-crop").textContent = house.crop;
  card.querySelector(".card-temperature").textContent = formatTemperature(today.temperature);
  card.querySelector(".card-humidity").textContent = humidityText;
  card.querySelector(".card-max").textContent = formatTemperature(today.max);
  card.querySelector(".card-min").textContent = formatTemperature(today.min);
  card.querySelector(".card-time").textContent = timeText;

  setBadge(card, today);
  return card;
}

// カード右上の状態表示（正常・低温・記録なし）を設定する
function setBadge(card, today) {
  const badge = card.querySelector(".badge");

  if (!today.has_data) {
    badge.textContent = "記録なし";
    badge.classList.add("badge-none");
  } else if (today.is_cold) {
    badge.textContent = "低温";
    badge.classList.add("badge-cold");
    card.classList.add("card-cold");
  } else {
    badge.textContent = "正常";
    badge.classList.add("badge-ok");
  }
}

// 低温の棟があれば警告を表示する
function showAlert(coldHouseNames, coldLimit) {
  if (coldHouseNames.length === 0) {
    alertBar.hidden = true;
    return;
  }
  alertBar.textContent = `${coldHouseNames.join("・")} が ${coldLimit}℃ を下回っています．暖房と換気窓を確認してください．`;
  alertBar.hidden = false;
}

// 一覧を表示する
async function showList() {
  const startTime = Date.now();
  const settings = await getJson("/api/settings");
  const houses = await getJson("/api/houses");
  const coldHouseNames = [];
  cardsArea.innerHTML = "";

  // 棟ごとに本日の集計を取得し，カードを追加する
  for (const house of houses) {
    const today = await getJson(`/api/houses/${house.id}/today`);
    cardsArea.appendChild(makeCard(house, today));
    if (today.is_cold) {
      coldHouseNames.push(house.name);
    }
  }

  showAlert(coldHouseNames, settings.cold_limit);
  summaryText.textContent = `全${houses.length}棟中，低温 ${coldHouseNames.length}棟`;
  const seconds = (Date.now() - startTime) / 1000;
  elapsedText.textContent = `表示時間：${seconds.toFixed(2)} 秒`;
}

// 「更新」ボタンの処理．読み込み中は再実行を防ぐ
async function reload() {
  reloadButton.disabled = true;
  try {
    await showList();
  } catch (error) {
    summaryText.textContent = `読み込み失敗．サーバーの起動を確認してください（${error.message}）`;
  } finally {
    reloadButton.disabled = false;
  }
}


// ============================================================
// 実行開始
// ============================================================

reloadButton.addEventListener("click", reload);
reload();
