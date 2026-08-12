import os

import redis
from flask import Flask, jsonify

app = Flask(__name__)

r = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=6379,
    decode_responses=True,
)

PAGE = """<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>Cats vs Dogs — Result</title>
<style>
  body {
    margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #2b1055 0%, #7597de 100%);
    font-family: "Leelawadee UI", "Noto Sans Thai", "Segoe UI", sans-serif;
  }
  .card {
    background: #fff; border-radius: 20px; padding: 42px 56px; width: 520px;
    box-shadow: 0 24px 70px rgba(0,0,0,.45); text-align: center;
  }
  h1 { font-size: 30px; color: #16212f; margin: 0 0 26px; }
  .bar-row { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
  .bar-row .label { width: 92px; font-size: 21px; font-weight: 700; text-align: left; }
  .track { flex: 1; height: 40px; background: #eef2f6; border-radius: 10px; overflow: hidden; }
  .fill { height: 100%; border-radius: 10px; transition: width .6s; min-width: 2%; }
  .fill.cats { background: linear-gradient(90deg, #e8590c, #f76707); }
  .fill.dogs { background: linear-gradient(90deg, #1971c2, #22b8cf); }
  .pct { width: 76px; font-size: 21px; font-weight: 800; text-align: right; color: #16212f; }
  .total { color: #5b6b7f; font-size: 17px; margin-top: 8px; }
  .total b { color: #6741d9; }
</style>
</head>
<body>
  <div class="card">
    <h1>🏆 ผลโหวตสด ๆ จาก Redis</h1>
    <div class="bar-row">
      <span class="label">🐱 CATS</span>
      <div class="track"><div class="fill cats" id="bar-cats" style="width:50%"></div></div>
      <span class="pct" id="pct-cats">–</span>
    </div>
    <div class="bar-row">
      <span class="label">🐶 DOGS</span>
      <div class="track"><div class="fill dogs" id="bar-dogs" style="width:50%"></div></div>
      <span class="pct" id="pct-dogs">–</span>
    </div>
    <p class="total">คะแนนรวม <b id="total">0</b> โหวต · หน้านี้ดึงข้อมูลใหม่ทุก 2 วินาที</p>
  </div>
<script>
async function refresh() {
  const res  = await fetch("/data");
  const data = await res.json();
  const total = data.cats + data.dogs;
  const pctCats = total ? Math.round(data.cats / total * 100) : 50;
  document.getElementById("bar-cats").style.width = pctCats + "%";
  document.getElementById("bar-dogs").style.width = (100 - pctCats) + "%";
  document.getElementById("pct-cats").textContent = total ? pctCats + "%" : "–";
  document.getElementById("pct-dogs").textContent = total ? (100 - pctCats) + "%" : "–";
  document.getElementById("total").textContent = total;
}
refresh();
setInterval(refresh, 2000);
</script>
</body>
</html>"""


@app.route("/")
def result():
    return PAGE


@app.route("/data")
def data():
    return jsonify(
        cats=int(r.get("votes:cats") or 0),
        dogs=int(r.get("votes:dogs") or 0),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
