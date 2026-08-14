<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark light">
  <title>Container Network Console</title>
  <style>
    :root {
      color-scheme: dark;
      --bg-a: #070b18;
      --bg-b: #111a33;
      --surface: rgba(19, 29, 54, .68);
      --surface-strong: rgba(23, 35, 65, .9);
      --border: rgba(255, 255, 255, .13);
      --text: #f4f7ff;
      --muted: #aebbd7;
      --cyan: #57d9ff;
      --violet: #9d8cff;
      --green: #55e6a5;
      --red: #ff6b7a;
      --shadow: 0 24px 70px rgba(0, 0, 0, .35);
    }

    * { box-sizing: border-box; }

    body {
      min-height: 100vh;
      margin: 0;
      font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at 14% 12%, rgba(87, 217, 255, .18), transparent 28rem),
        radial-gradient(circle at 90% 22%, rgba(157, 140, 255, .2), transparent 30rem),
        linear-gradient(145deg, var(--bg-a), var(--bg-b));
      line-height: 1.6;
    }

    .shell { width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 64px 0 28px; }
    .hero { display: flex; gap: 22px; align-items: flex-end; justify-content: space-between; margin-bottom: 28px; }
    .eyebrow { color: var(--cyan); margin: 0 0 8px; font-size: .82rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
    h1 { margin: 0; max-width: 820px; font-size: clamp(2.35rem, 7vw, 5.4rem); line-height: .98; letter-spacing: -.055em; }
    .badge { flex: 0 0 auto; padding: 9px 14px; border: 1px solid rgba(87, 217, 255, .35); border-radius: 999px; color: var(--cyan); background: rgba(87, 217, 255, .09); font-size: .78rem; font-weight: 750; white-space: nowrap; }

    .glass {
      border: 1px solid var(--border);
      border-radius: 22px;
      background: var(--surface);
      box-shadow: var(--shadow);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
    }

    .stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px; overflow: hidden; padding: 1px; }
    .stat { min-width: 0; padding: 22px; background: rgba(255, 255, 255, .025); }
    .stat-label { display: block; color: var(--muted); font-size: .76rem; font-weight: 750; letter-spacing: .07em; text-transform: uppercase; }
    .stat-value { display: block; margin-top: 7px; overflow-wrap: anywhere; color: var(--text); font-family: ui-monospace, "SFMono-Regular", Consolas, monospace; font-size: .98rem; }

    .dns-note { display: grid; grid-template-columns: auto 1fr; gap: 16px; align-items: start; margin: 24px 0; padding: 22px; }
    .dns-icon { display: grid; width: 46px; height: 46px; place-items: center; border-radius: 14px; color: #061412; background: linear-gradient(135deg, var(--green), var(--cyan)); font-weight: 900; }
    .dns-note h2 { margin: 0 0 5px; font-size: 1.08rem; }
    .dns-note p { margin: 0; color: var(--muted); }
    code { border: 1px solid var(--border); border-radius: 7px; padding: .12em .42em; color: var(--cyan); background: rgba(0, 0, 0, .2); font-family: ui-monospace, "SFMono-Regular", Consolas, monospace; }

    .section-title { margin: 38px 0 14px; font-size: 1.42rem; letter-spacing: -.02em; }
    .modes { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
    .mode { padding: 24px; }
    .mode-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
    .mode h3 { margin: 0; font-size: 1.18rem; }
    .mode-tag { border-radius: 99px; padding: 4px 9px; color: var(--violet); background: rgba(157, 140, 255, .12); font-size: .7rem; font-weight: 800; text-transform: uppercase; }
    .mode p { margin: 14px 0; color: var(--muted); font-size: .92rem; }
    .mode .when { color: var(--text); }
    .command { display: block; overflow-x: auto; border-radius: 10px; padding: 10px 12px; color: var(--green); background: rgba(3, 7, 18, .62); font-size: .78rem; white-space: nowrap; }

    .diagram { overflow: hidden; padding: 16px; }
    svg { display: block; width: 100%; height: auto; }
    footer { padding: 30px 4px 0; color: var(--muted); text-align: center; font-size: .78rem; }

    @media (max-width: 760px) {
      .shell { padding-top: 38px; }
      .hero { align-items: flex-start; flex-direction: column; }
      .stats, .modes { grid-template-columns: 1fr; }
      .stat { padding: 18px; }
      .dns-note { grid-template-columns: 1fr; }
      .diagram { padding: 6px; }
    }

    @media (prefers-color-scheme: light) {
      :root {
        color-scheme: light;
        --bg-a: #eef4ff;
        --bg-b: #dfe8fb;
        --surface: rgba(255, 255, 255, .72);
        --surface-strong: rgba(255, 255, 255, .92);
        --border: rgba(20, 42, 80, .14);
        --text: #12203a;
        --muted: #52627d;
        --cyan: #087da4;
        --violet: #5d4dc1;
        --green: #087f56;
        --red: #bf3045;
        --shadow: 0 20px 60px rgba(40, 65, 110, .14);
      }
      body { background: radial-gradient(circle at 12% 10%, #d5f4ff, transparent 28rem), radial-gradient(circle at 88% 20%, #e7ddff, transparent 30rem), linear-gradient(145deg, var(--bg-a), var(--bg-b)); }
      .stat { background: rgba(255, 255, 255, .36); }
      .command { color: #bfffe2; background: #16243a; }
      code { background: rgba(255, 255, 255, .55); }
    }
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <div>
        <p class="eyebrow">Runtime observability</p>
        <h1>Container Network Console</h1>
      </div>
      <span class="badge">LAB 6 · Docker Network &amp; DNS</span>
    </header>

    <section class="stats glass" aria-label="ข้อมูลจริงของคอนเทนเนอร์">
      <div class="stat"><span class="stat-label">บริการ · Service</span><strong class="stat-value">__SERVICE_NAME__</strong></div>
      <div class="stat"><span class="stat-label">ชื่อโฮสต์ · Hostname</span><strong class="stat-value">__HOSTNAME__</strong></div>
      <div class="stat"><span class="stat-label">ไอพีคอนเทนเนอร์ · Container IP</span><strong class="stat-value">__CONTAINER_IP__</strong></div>
      <div class="stat"><span class="stat-label">ตัวแก้ชื่อ · DNS Resolver</span><strong class="stat-value">__DNS_RESOLVER__</strong></div>
      <div class="stat"><span class="stat-label">อินเทอร์เฟซ · Network Interfaces</span><strong class="stat-value">__NETWORK_IFACES__</strong></div>
      <div class="stat"><span class="stat-label">เวลาที่เรนเดอร์ · Served At</span><strong class="stat-value">__SERVED_AT__</strong></div>
    </section>

    <aside class="dns-note glass">
      <div class="dns-icon">DNS</div>
      <div>
        <h2>อ่านค่า DNS แล้วรู้ชนิดการเชื่อมต่อ</h2>
        <p>ถ้า DNS resolver เป็น <code>127.0.0.11</code> แปลว่าคอนเทนเนอร์อยู่บน user-defined network และเรียกหากันด้วยชื่อคอนเทนเนอร์ได้ ถ้าไม่ใช่ แสดงว่าอยู่บน default bridge ซึ่งไม่มี DNS สำหรับชื่อคอนเทนเนอร์</p>
      </div>
    </aside>

    <h2 class="section-title">Network modes ที่ควรรู้</h2>
    <section class="modes">
      <article class="mode glass">
        <div class="mode-top"><h3>bridge</h3><span class="mode-tag">isolated</span></div>
        <p>เครือข่ายเสมือนบน host ผ่าน NAT; user-defined bridge มี DNS discovery ในตัว</p>
        <p class="when"><strong>ใช้เมื่อไร:</strong> งานเว็บทั่วไปและบริการที่ต้องคุยกันด้วยชื่อ</p>
        <code class="command">docker network create app-net</code>
      </article>
      <article class="mode glass">
        <div class="mode-top"><h3>host</h3><span class="mode-tag">direct</span></div>
        <p>แชร์ network namespace กับ host โดยตรง ไม่มีการแยก IP และไม่ต้อง publish port</p>
        <p class="when"><strong>ใช้เมื่อไร:</strong> ต้องการลด overhead หรือเข้าถึง port ของ host โดยตรง</p>
        <code class="command">docker run --network host nginx</code>
      </article>
      <article class="mode glass">
        <div class="mode-top"><h3>none</h3><span class="mode-tag">offline</span></div>
        <p>ปิด network ทั้งหมด เหลือเพียง loopback interface ภายในคอนเทนเนอร์</p>
        <p class="when"><strong>ใช้เมื่อไร:</strong> งานประมวลผลออฟไลน์หรือทดสอบ isolation สูงสุด</p>
        <code class="command">docker run --network none alpine</code>
      </article>
    </section>

    <h2 class="section-title">Topology at a glance</h2>
    <section class="diagram glass" aria-label="Docker network topology">
      <svg viewBox="0 0 900 380" preserveAspectRatio="xMidYMid meet" role="img">
        <title>Docker host containing app-net, default bridge, and an isolated none network container</title>
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#57d9ff"/></marker>
          <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        <rect x="14" y="14" width="872" height="352" rx="24" fill="#0d1730" stroke="#8394bc" stroke-opacity=".55" stroke-width="2"/>
        <text x="38" y="46" fill="#f4f7ff" font-size="18" font-weight="700">DOCKER HOST</text>

        <rect x="38" y="64" width="532" height="270" rx="20" fill="#152344" stroke="#57d9ff" stroke-opacity=".75" stroke-width="2"/>
        <text x="58" y="94" fill="#57d9ff" font-size="17" font-weight="700">USER-DEFINED BRIDGE: app-net</text>
        <text x="58" y="114" fill="#aebbd7" font-size="12">subnet และ IP แจกโดย Docker — แต่ละเครื่องไม่เหมือนกัน จึงห้าม hardcode</text>
        <rect x="69" y="127" width="145" height="88" rx="14" fill="#21345d" stroke="#9d8cff"/>
        <text x="141" y="163" fill="#f4f7ff" font-size="17" text-anchor="middle" font-weight="700">web</text>
        <text x="141" y="188" fill="#aebbd7" font-size="13" text-anchor="middle">IP อัตโนมัติ</text>
        <rect x="394" y="127" width="145" height="88" rx="14" fill="#21345d" stroke="#9d8cff"/>
        <text x="466" y="163" fill="#f4f7ff" font-size="17" text-anchor="middle" font-weight="700">client</text>
        <text x="466" y="188" fill="#aebbd7" font-size="13" text-anchor="middle">IP อัตโนมัติ</text>
        <circle cx="304" cy="171" r="51" fill="#10394b" stroke="#55e6a5" stroke-width="2" filter="url(#glow)"/>
        <text x="304" y="165" fill="#55e6a5" font-size="15" text-anchor="middle" font-weight="800">DNS</text>
        <text x="304" y="187" fill="#f4f7ff" font-size="12" text-anchor="middle">127.0.0.11</text>
        <path d="M 217 150 L 252 150" stroke="#57d9ff" stroke-width="2" marker-end="url(#arrow)"/>
        <path d="M 356 193 L 391 193" stroke="#57d9ff" stroke-width="2" marker-end="url(#arrow)"/>
        <text x="234" y="137" fill="#aebbd7" font-size="11" text-anchor="middle">name</text>
        <text x="374" y="218" fill="#aebbd7" font-size="11" text-anchor="middle">IP</text>
        <path d="M 466 235 C 430 300, 180 300, 141 235" fill="none" stroke="#55e6a5" stroke-width="2" stroke-dasharray="7 6" marker-end="url(#arrow)"/>
        <text x="304" y="293" fill="#55e6a5" font-size="13" text-anchor="middle">service discovery by container name</text>

        <rect x="596" y="64" width="264" height="156" rx="20" fill="#251d35" stroke="#ff6b7a" stroke-opacity=".7" stroke-width="2"/>
        <text x="616" y="94" fill="#ffb1bb" font-size="16" font-weight="700">DEFAULT BRIDGE</text>
        <rect x="618" y="119" width="79" height="63" rx="11" fill="#34294a" stroke="#9d8cff"/>
        <text x="657" y="157" fill="#f4f7ff" font-size="14" text-anchor="middle">web2</text>
        <rect x="759" y="119" width="79" height="63" rx="11" fill="#34294a" stroke="#9d8cff"/>
        <text x="798" y="157" fill="#f4f7ff" font-size="14" text-anchor="middle">client</text>
        <line x1="702" y1="150" x2="754" y2="150" stroke="#ff6b7a" stroke-width="3"/>
        <line x1="718" y1="132" x2="738" y2="168" stroke="#ff6b7a" stroke-width="5"/>
        <line x1="738" y1="132" x2="718" y2="168" stroke="#ff6b7a" stroke-width="5"/>
        <text x="728" y="203" fill="#ffb1bb" font-size="12" text-anchor="middle">no container-name DNS</text>

        <rect x="596" y="242" width="264" height="92" rx="20" fill="#171d2d" stroke="#8394bc" stroke-dasharray="7 6"/>
        <text x="616" y="270" fill="#aebbd7" font-size="15" font-weight="700">NONE</text>
        <rect x="704" y="258" width="126" height="56" rx="12" fill="#222a3d" stroke="#8394bc"/>
        <text x="767" y="282" fill="#f4f7ff" font-size="14" text-anchor="middle">isolated job</text>
        <text x="767" y="302" fill="#aebbd7" font-size="11" text-anchor="middle">loopback only</text>
      </svg>
    </section>

    <footer>served by nginx:1.27-alpine</footer>
  </main>
</body>
</html>
