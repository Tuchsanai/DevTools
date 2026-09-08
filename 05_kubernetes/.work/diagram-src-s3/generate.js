const fs = require('fs');
const path = require('path');

const OUT = __dirname;
const W = 1480, H = 820;
const C = {
  acc: '#1c5cab', accw: '#eaf2fd', ok: '#116b11', okw: '#e7f6e7',
  warn: '#86590a', warnw: '#fdf3dd', crit: '#a32222', critw: '#fbeaea',
  ink: '#18181b', muted: '#52525b', rule: '#d4d4d8', white: '#ffffff'
};

let seq = 0;
function id(prefix) { return `${prefix}-${++seq}`; }
function base(title, subtitle = '') {
  seq = 0;
  const e = [
    { id: id('bg'), type: 'rectangle', x: 0, y: 0, width: W, height: H,
      strokeColor: C.white, backgroundColor: C.white, fillStyle: 'solid', roughness: 0, strokeWidth: 1 },
    txt(42, 24, title, 32, C.ink, 1390, 'left', true)
  ];
  if (subtitle) e.push(txt(44, 68, subtitle, 20, C.muted, 1390));
  e.push({ id: id('rule'), type: 'line', x: 42, y: 102, points: [[0,0],[1396,0]],
    strokeColor: C.rule, strokeWidth: 2, roughness: 0 });
  return e;
}
function txt(x, y, text, fontSize = 20, color = C.ink, width = 400, align = 'left', bold = false) {
  const anchorX = align === 'center' ? x + width / 2 : x;
  return { id: id('text'), type: 'text', x: anchorX, y, width, height: Math.ceil(fontSize * 1.35 * String(text).split('\n').length),
    text, fontSize, fontFamily: 'helvetica', textAlign: align, verticalAlign: 'middle',
    strokeColor: color, backgroundColor: 'transparent', fillStyle: 'solid', roughness: 0,
    strokeWidth: bold ? 2 : 1 };
}
function rect(x, y, w, h, stroke = C.rule, fill = C.white, dashed = false, sw = 2) {
  return { id: id('rect'), type: 'rectangle', x, y, width: w, height: h,
    strokeColor: stroke, backgroundColor: fill, fillStyle: 'solid', roughness: 0,
    strokeWidth: sw, strokeStyle: dashed ? 'dashed' : 'solid', roundness: { type: 3 } };
}
function ellipse(x, y, w, h, stroke = C.acc, fill = C.accw, sw = 2) {
  return { id: id('ellipse'), type: 'ellipse', x, y, width: w, height: h,
    strokeColor: stroke, backgroundColor: fill, fillStyle: 'solid', roughness: 0, strokeWidth: sw };
}
function style(kind) {
  if (kind === 'service' || kind === 'ok') return [C.ok, C.okw, 2];
  if (['ingress','config','secret','warn'].includes(kind)) return [C.warn, C.warnw, 2];
  if (kind === 'pvc') return [C.warn, C.warnw, 4];
  if (kind === 'bad' || kind === 'crit') return [C.crit, C.critw, 2];
  if (kind === 'neutral') return [C.ink, C.white, 2];
  return [C.acc, C.accw, 2];
}
function card(x, y, w, h, text, kind = 'pod', fs = 20, dashed = false) {
  const [stroke, fill, sw] = style(kind);
  return { id: id(kind), type: 'rectangle', x, y, width: w, height: h, text,
    fontSize: fs, fontFamily: 'helvetica', textAlign: 'center', verticalAlign: 'middle',
    strokeColor: stroke, backgroundColor: fill, fillStyle: 'solid', roughness: 0,
    strokeWidth: sw, strokeStyle: dashed ? 'dashed' : 'solid', roundness: { type: 3 } };
}
function zone(e, x, y, w, h, label, sub = '') {
  e.push(rect(x, y, w, h, C.rule, C.white, true, 2));
  e.push(txt(x + 18, y + 10, label, 22, C.ink, w - 36, 'left', true));
  if (sub) e.push(txt(x + 18, y + 40, sub, 20, C.muted, w - 36));
}
function arrow(x1, y1, x2, y2, color = C.ink, points = null, dashed = false, sw = 2) {
  const p = points || [[0,0],[x2-x1,y2-y1]];
  return { id: id('arrow'), type: 'arrow', x: x1, y: y1, points: p,
    strokeColor: color, backgroundColor: 'transparent', fillStyle: 'solid', roughness: 0,
    strokeWidth: sw, strokeStyle: dashed ? 'dashed' : 'solid', endArrowhead: 'arrow',
    startArrowhead: null, roundness: p.length > 2 ? { type: 2 } : null };
}
function line(x1, y1, x2, y2, color = C.rule, sw = 2, dashed = false) {
  return { id: id('line'), type: 'line', x: x1, y: y1, points: [[0,0],[x2-x1,y2-y1]],
    strokeColor: color, strokeWidth: sw, strokeStyle: dashed ? 'dashed' : 'solid', roughness: 0 };
}
function browser(e, x, y, w = 190, h = 112, url = 'localhost:8080') {
  e.push(rect(x, y, w, h, C.rule, C.white, false, 2));
  e.push({ id: id('bar'), type: 'rectangle', x: x, y: y, width: w, height: 30,
    strokeColor: C.rule, backgroundColor: C.accw, fillStyle: 'solid', roughness: 0, strokeWidth: 2 });
  e.push(ellipse(x+10,y+10,10,10,C.crit,C.critw,1), ellipse(x+26,y+10,10,10,C.warn,C.warnw,1), ellipse(x+42,y+10,10,10,C.ok,C.okw,1));
  e.push(txt(x+12, y+43, 'Browser', 22, C.ink, w-24, 'center', true));
  e.push(txt(x+12, y+74, url, 20, C.acc, w-24, 'center'));
}
function footer(e, text) {
  e.push(txt(44, 784, text, 20, C.muted, 1390, 'center'));
}

function d01() {
  const e = base('จาก compose.yaml สู่ Kubernetes objects', '3 services เดิม กลายเป็น 10 objects ที่แยกหน้าที่ชัดเจน');
  zone(e, 40, 128, 360, 610, 'Docker Compose · เครื่องเดียว');
  e.push(card(90, 205, 260, 90, 'compose.yaml', 'neutral', 24));
  e.push(card(100, 345, 240, 72, 'service: web', 'pod'));
  e.push(card(100, 455, 240, 72, 'service: api', 'pod'));
  e.push(card(100, 565, 240, 72, 'service: db', 'pod'));
  e.push(arrow(220, 295, 220, 340, C.acc));
  e.push(arrow(220, 417, 220, 450, C.acc));
  e.push(arrow(220, 527, 220, 560, C.acc));
  e.push(arrow(425, 435, 520, 435, C.ink));
  e.push(txt(418, 383, 'แปลงหน้าที่\nไม่ใช่แปลง 1:1', 22, C.ink, 115, 'center', true));
  zone(e, 550, 128, 888, 610, 'namespace lab015 · Kubernetes', 'แต่ละ object มีหน้าที่เดียวและซ่อมแยกชิ้นได้');
  const items = [
    [600,220,'ConfigMap\nweb-config','config'], [840,220,'Deployment\nweb','deployment'],
    [1080,220,'Service\nweb','service'], [600,340,'Deployment\napi','deployment'],
    [840,340,'Service\napi','service'], [1080,340,'Ingress\n/ → web','ingress'],
    [600,500,'Secret\ndb-secret','secret'], [840,500,'PVC\ndb-data','pvc'],
    [1080,500,'Deployment\ndb','deployment'], [720,620,'Service\ndb','service']
  ];
  for (const [x,y,t,k] of items) e.push(card(x,y,200,78,t,k,20));
  e.push(card(960,620,250,78,'รวม 10 objects', 'ok', 24));
  footer(e, 'แนวคิดหลัก: แอปจริงคือหลาย object ที่ทำงานร่วมกัน ไม่ใช่ object เดียว');
  return e;
}

function d02() {
  const e = base('Stateless vs Stateful', 'คำถามสำคัญ: ถ้าลบหรือเพิ่ม Pod แล้ว ข้อมูลต้องตามไปด้วยหรือไม่?');
  zone(e, 40, 135, 660, 580, 'Stateless · web / api', 'ไม่มีข้อมูลเฉพาะตัว — สร้างใหม่แทนกันได้');
  e.push(card(95,235,165,72,'Pod web #1','pod'), card(285,235,165,72,'Pod web #2','pod'), card(475,235,165,72,'Pod web #3','pod'));
  e.push(arrow(175,350,560,350,C.acc));
  e.push(txt(210,320,'scale 1 → 3 ได้ทันที',22,C.acc,330,'center',true));
  e.push(card(125,425,220,84,'ลบได้\nDeployment สร้างใหม่','ok'));
  e.push(card(395,425,220,84,'ไม่ต้องผูก\nดิสก์ส่วนตัว','ok'));
  e.push(txt(125,555,'เหมาะกับ: UI · API · worker ที่เก็บ state ไว้ภายนอก',22,C.ink,520,'center'));
  zone(e, 740, 135, 698, 580, 'Stateful · PostgreSQL', 'ข้อมูลและตัวตนต้องคงอยู่ — ต้องควบคุมเจ้าของดิสก์');
  e.push(card(800,235,210,84,'Pod db\nPostgreSQL','pod'));
  e.push(arrow(1015,277,1080,277,C.warn));
  e.push(card(1090,225,190,104,'PVC\ndb-data','pvc',22));
  e.push(arrow(1185,335,1185,390,C.warn));
  e.push(card(1080,400,210,88,'PV\nข้อมูลคงอยู่','pvc'));
  e.push(card(800,420,210,84,'scale เป็น 2\nบน data dir เดียว','bad'));
  e.push(txt(800,530,'เสี่ยง lock / RWO / ข้อมูลเสีย',22,C.crit,500,'center',true));
  e.push(txt(800,600,'หลาย replica จริง: replication + StatefulSet\nและ PVC แยกต่อ instance',20,C.ink,520,'center'));
  footer(e, 'Stateless ทิ้งและสร้างใหม่ได้ · Stateful ต้องวางแผน storage, identity และ backup');
  return e;
}

function d03() {
  const e = base('Ingress vs NodePort', 'Ingress คือ reverse proxy ของ Kubernetes: ประตูเดียว เลือก backend ด้วย path/host');
  zone(e, 40, 135, 650, 565, 'NodePort · เปิดพอร์ตต่อ Service', 'จำนวน Service มากขึ้น → จำนวนพอร์ตที่ผู้ใช้ต้องจำมากขึ้น');
  browser(e, 85, 260, 180, 112, 'host หลาย port');
  e.push(card(380,205,230,78,'NodePort :30080\nService web','service'));
  e.push(card(380,355,230,78,'NodePort :30081\nService api','service'));
  e.push(card(380,505,230,78,'NodePort :30082\nService admin','service'));
  e.push(arrow(270,300,375,244,C.ok), arrow(270,315,375,394,C.ok), arrow(270,335,375,544,C.ok));
  e.push(txt(90,610,'L4 · route ด้วย port',22,C.muted,510,'center'));
  zone(e, 730, 135, 708, 565, 'Ingress · ประตูเดียว', 'Ingress rule บอก controller (nginx/Traefik) ให้ route อัตโนมัติ');
  browser(e, 770, 275, 190, 112, 'localhost:8080');
  e.push(card(1015,270,190,120,'ingress-nginx\ncontroller','ingress',20));
  e.push(card(1245,195,155,72,'/\nService web','service'));
  e.push(card(1245,315,155,72,'/api\nService api','service'));
  e.push(card(1245,435,155,72,'/admin\nService admin','service'));
  e.push(arrow(965,330,1010,330,C.warn));
  e.push(arrow(1210,310,1240,231,C.ok), arrow(1210,330,1240,351,C.ok), arrow(1210,350,1240,471,C.ok));
  e.push(txt(820,600,'L7 · route ด้วย path / host · รองรับ TLS',22,C.muted,560,'center'));
  footer(e, 'Traefik router ↔ Ingress rule · Traefik service ↔ Service backend');
  return e;
}

function d04() {
  const e = base('RollingUpdate แบบไม่สะดุด', 'replicas=3 · maxSurge=1 · maxUnavailable=0 · readiness เป็นประตูก่อนรับ traffic');
  const xs = [60,340,620,900,1180];
  const labels = ['t0 · ก่อนเริ่ม','t1 · สร้างใหม่','t2 · Ready แล้ว','t3 · แทนต่อ','t4 · เสร็จ'];
  for (let i=0;i<5;i++) {
    e.push(txt(xs[i],132,labels[i],22,C.ink,240,'center',true));
    e.push(line(xs[i]+260,165,xs[i]+275,165,C.rule,2));
  }
  const pod = (x,y,t,k='pod') => card(x,y,210,62,t,k,20);
  e.push(pod(75,210,'v1 · Ready'),pod(75,300,'v1 · Ready'),pod(75,390,'v1 · Ready'));
  e.push(pod(355,195,'v2 · Starting','warn'),pod(355,285,'v1 · Ready'),pod(355,375,'v1 · Ready'),pod(355,465,'v1 · Ready'));
  e.push(pod(635,210,'v2 · Ready','ok'),pod(635,300,'v1 · Ready'),pod(635,390,'v1 · Ready'));
  e.push(pod(915,195,'v2 · Ready','ok'),pod(915,285,'v2 · Starting','warn'),pod(915,375,'v1 · Ready'),pod(915,465,'v1 · Ready'));
  e.push(pod(1195,210,'v2 · Ready','ok'),pod(1195,300,'v2 · Ready','ok'),pod(1195,390,'v2 · Ready','ok'));
  for (let i=0;i<4;i++) e.push(arrow(xs[i]+225,540,xs[i+1]-15,540,C.acc));
  e.push(txt(345,565,'Surge = 4 ชั่วคราว',20,C.warn,230,'center'));
  e.push(txt(630,565,'readiness ผ่าน\nจึงลด v1',20,C.ok,230,'center'));
  e.push(txt(900,565,'ทำซ้ำทีละส่วน',20,C.acc,230,'center'));
  e.push(card(310,650,860,70,'Service ส่ง request เฉพาะ Pod ที่ Ready → ไม่เกิด FAIL / 503','service',22));
  footer(e, 'maxUnavailable=0 เก็บตัวเก่าที่พร้อมไว้เสมอ · maxSurge=1 เพิ่มตัวใหม่ได้ครั้งละ 1');
  return e;
}

function d05() {
  const e = base('requests, limits และการตัดสินใจของ Scheduler', 'requests ใช้ตอนวาง Pod · limits บังคับตอน container กำลังรัน');
  zone(e, 40,140,400,555,'Pod specification');
  e.push(card(85,220,310,210,'resources:\n  requests:\n    cpu: 100m\n    memory: 128Mi\n  limits:\n    cpu: 500m\n    memory: 256Mi','neutral',20));
  e.push(txt(92,470,'requests = ทรัพยากรที่ “จอง”',22,C.acc,300,'center',true));
  e.push(txt(92,530,'limits = เพดานตอนรัน',22,C.warn,300,'center',true));
  e.push(arrow(445,340,540,340,C.acc));
  zone(e, 535,140,470,555,'1 · Schedule ด้วย requests','Scheduler เลือก node ที่ยอดจองยังเหลือพอ');
  e.push(card(585,245,170,220,'worker-1\n\nจอง 700m\nเหลือ 300m','deployment',20));
  e.push(card(790,245,170,220,'worker-2\n\nจอง 950m\nเหลือ 50m','bad',20));
  e.push(card(635,520,280,78,'Pod requests 100m\n→ ลง worker-1','ok',22));
  e.push(arrow(775,515,775,475,C.ok));
  e.push(arrow(1010,340,1095,340,C.warn));
  zone(e, 1090,140,348,555,'2 · Run ด้วย limits','kubelet/runtime บังคับเพดาน');
  e.push(card(1140,245,248,82,'CPU > 500m\nถูก throttle','warn',22));
  e.push(card(1140,375,248,82,'Memory > 256Mi\nOOMKilled','bad',22));
  e.push(card(1140,520,248,82,'อยู่ในเพดาน\nทำงานต่อ','ok',22));
  footer(e, 'ถ้า requests ใหญ่เกิน → Pending · ถ้า memory เกิน limits → OOMKilled');
  return e;
}

function d06() {
  const e = base('Troubleshooting ladder', 'ไล่จากอาการกว้าง → หลักฐานเฉพาะ แล้วจับคู่กับชั้นที่พัง');
  zone(e, 40,140,520,565,'ลำดับตรวจ · ทำซ้ำทุกเคส');
  const steps = [
    [95,205,'1 · kubectl get','เห็น STATUS / READY / endpoints','deployment'],
    [95,315,'2 · kubectl describe','เห็น Conditions และ Events รอบ object','warn'],
    [95,425,'3 · kubectl logs --previous','ฟังเสียงแอป โดยเฉพาะตัวที่ crash','pod'],
    [95,535,'4 · kubectl get events','เห็นภาพรวมทั้ง namespace ตามเวลา','neutral']
  ];
  for (const [x,y,t,s,k] of steps) { e.push(card(x,y,410,76,t,k,22)); e.push(txt(x+15,y+80,s,20,C.muted,380,'center')); }
  e.push(arrow(70,245,70,605,C.acc,[[0,0],[0,360]],false,3));
  zone(e, 600,140,838,565,'4 อาการ → จุดที่ควรสงสัย');
  const cases = [
    [650,210,'Pending','Scheduler','describe → Insufficient cpu','warn'],
    [1035,210,'ImagePullBackOff','Image / registry','describe → pull failed','bad'],
    [650,410,'CrashLoopBackOff','Application','logs --previous','bad'],
    [1035,410,'Endpoints <none>','Service selector / readiness','get endpoints + describe svc','warn']
  ];
  for (const [x,y,a,b,c,k] of cases) {
    e.push(card(x,y,340,78,a,k,22));
    e.push(txt(x,y+90,b,22,C.ink,340,'center',true));
    e.push(txt(x,y+125,c,20,C.muted,340,'center'));
  }
  footer(e, 'get บอกว่า “พังแบบไหน” · describe/logs/events บอกว่า “เพราะอะไร”');
  return e;
}

function d07() {
  const e = base('เส้นทาง request: Browser → PostgreSQL', 'ลูกศรทึบ = request/data · ลูกศรประ = ค่า config ที่ถูก inject เข้า Pod');
  browser(e,30,255,180,112,'localhost:8080');
  zone(e, 235,125,1203,620,'Kubernetes cluster / namespace lab021');
  e.push(card(270,270,170,84,'ingress-nginx\ncontroller','ingress'));
  e.push(card(475,270,150,84,'Ingress\npath /','ingress'));
  e.push(card(660,270,150,84,'Service\nweb','service'));
  e.push(card(845,270,150,84,'Pod\nweb','pod'));
  e.push(card(1050,270,150,84,'Service\napi','service'));
  e.push(card(1240,270,150,84,'Pod\napi','pod'));
  e.push(arrow(215,311,265,311,C.ink),arrow(445,311,470,311,C.warn),arrow(630,311,655,311,C.ok),arrow(815,311,840,311,C.acc),arrow(1000,311,1045,311,C.ok),arrow(1205,311,1235,311,C.acc));
  e.push(txt(210,220,'host:8080 → node:80',20,C.muted,260,'center'));
  e.push(card(845,160,150,62,'ConfigMap','config'));
  e.push(arrow(920,225,920,265,C.warn,null,true));
  e.push(txt(995,165,'API_BASE_URL',20,C.warn,190,'center'));
  e.push(card(1240,410,150,84,'Service\ndb','service'));
  e.push(card(1050,410,150,84,'Pod\ndb','pod'));
  e.push(card(845,410,150,84,'PVC\ndb-data','pvc'));
  e.push(card(660,410,150,84,'PV\nข้อมูลจริง','pvc'));
  e.push(arrow(1315,360,1315,405,C.acc),arrow(1235,452,1205,452,C.ok),arrow(1045,452,1000,452,C.warn),arrow(840,452,815,452,C.warn));
  e.push(card(1240,555,150,62,'Secret','secret'));
  e.push(arrow(1315,550,1315,500,C.warn,null,true));
  e.push(arrow(1240,586,1140,500,C.warn,[[0,0],[-45,0],[-100,-86]],true));
  e.push(txt(1035,570,'DB_PASSWORD',20,C.warn,200,'center'));
  e.push(card(515,575,570,74,'Response เดินย้อนเส้นทางเดิมกลับไปยัง Browser','ok',22));
  e.push(arrow(815,545,445,545,C.ok));
  footer(e, 'ตัด object ใดออก อาการจะปรากฏที่ชั้นถัดไปของเส้นทาง');
  return e;
}

function d08() {
  const e = base('วงจรการเรียนรู้แบบลงมือจริง', 'ทุกแล็บเริ่มจากการคาดการณ์ แล้วใช้หลักฐานอธิบายสิ่งที่เกิดขึ้น');
  const nodes = [
    [150,190,'1 · ทายผล','warn'],[615,190,'2 · รัน','pod'],[1080,190,'3 · สังเกต','ok'],
    [1080,500,'4 · อธิบาย','pod'],[615,500,'5 · ทำให้พัง','bad'],[150,500,'6 · แก้กลับ','ok']
  ];
  for (const [x,y,t,k] of nodes) e.push(card(x,y,250,78,t,k,24));
  e.push(arrow(405,229,610,229,C.acc),arrow(870,229,1075,229,C.acc));
  e.push(arrow(1205,273,1205,495,C.acc));
  e.push(arrow(1075,539,875,539,C.acc),arrow(610,539,405,539,C.acc));
  e.push(arrow(145,539,145,229,C.acc,[[0,0],[-55,0],[-55,-310],[0,-310]]));
  e.push(card(480,330,520,100,'หลักฐาน 3 มุม\nkubectl · หน้าเว็บ · logs / events','neutral',24));
  e.push(txt(405,285,'ตั้งสมมติฐาน',20,C.muted,205,'center'));
  e.push(txt(870,285,'เก็บหลักฐาน',20,C.muted,205,'center'));
  e.push(txt(875,590,'เชื่อมเหตุและผล',20,C.muted,200,'center'));
  e.push(txt(405,590,'ทดลองขอบเขต',20,C.muted,205,'center'));
  footer(e, 'ทาย → รัน → สังเกต → อธิบาย → ทำให้พัง → แก้กลับ → ทายใหม่');
  return e;
}

function managers(e, x, name, y=165) {
  e.push(card(x,y,170,64,`Deployment\n${name}`,'deployment',20));
  e.push(card(x,y+95,170,64,`ReplicaSet\n${name}`,'deployment',20));
  e.push(card(x,y+190,170,64,`Pod\n${name}`,'pod',20));
  e.push(arrow(x+85,y+68,x+85,y+90,C.acc),arrow(x+85,y+163,x+85,y+185,C.acc));
}
function archFrame(title, subtitle, ns='lab') {
  const e=base(title,subtitle); zone(e,220,125,1218,620,`namespace ${ns}`); return e;
}

function lab015() {
  const e=archFrame('Lab 015 · ประกอบ web + api','ยังไม่มี database — ทุก object มาจาก manifests/01..06','lab015');
  browser(e,25,450,175,112,'localhost:8080');
  e.push(card(255,465,175,82,'Ingress\n/ → web','ingress'));
  managers(e,700,'web',165); managers(e,1100,'api',165);
  e.push(card(500,495,170,70,'Service\nweb','service'));
  e.push(card(900,495,170,70,'Service\napi','service'));
  e.push(card(500,650,170,62,'ConfigMap\nweb-config','config'));
  e.push(arrow(205,505,250,505,C.ink),arrow(435,505,495,530,C.warn),arrow(675,530,785,425,C.ok,[[0,0],[55,0],[110,-105]]));
  e.push(arrow(870,385,895,530,C.acc,[[0,0],[12,70],[25,145]]),arrow(1075,530,1185,425,C.ok,[[0,0],[55,0],[110,-105]]));
  e.push(arrow(675,681,700,397,C.warn,[[0,0],[15,0],[15,-284],[25,-284]],true));
  e.push(card(935,650,380,62,'db: ยังไม่มีในแล็บนี้','bad',22));
  footer(e,'ลบ Service / Ingress / ConfigMap แล้ว apply ทั้งโฟลเดอร์เพื่อซ่อม object ที่หาย');
  return e;
}

function lab016() {
  const e=archFrame('Lab 016 · เพิ่ม database และ persistent data','ครบ 3 ชั้น: web + api + PostgreSQL + Secret + PVC','lab016');
  browser(e,20,470,180,112,'localhost:8080');
  e.push(card(245,485,160,80,'Ingress\n/ → web','ingress'));
  managers(e,455,'web',160); managers(e,785,'api',160); managers(e,1115,'db',160);
  e.push(card(455,500,170,65,'Service\nweb','service'),card(785,500,170,65,'Service\napi','service'),card(1115,500,170,65,'Service\ndb','service'));
  e.push(arrow(205,525,240,525),arrow(410,525,450,532,C.warn),arrow(540,495,540,425,C.ok));
  e.push(arrow(630,532,780,532,C.acc),arrow(870,495,870,425,C.ok),arrow(960,532,1110,532,C.acc),arrow(1200,495,1200,425,C.ok));
  e.push(card(455,640,170,62,'ConfigMap','config'),card(785,640,170,62,'Secret','secret'),card(1115,630,170,82,'PVC\ndb-data','pvc'));
  e.push(arrow(635,671,625,385,C.warn,[[0,0],[25,0],[25,-286],[-10,-286]],true));
  e.push(arrow(785,671,785,385,C.warn,[[0,0],[-25,0],[-25,-286],[0,-286]],true));
  e.push(arrow(955,671,1115,385,C.warn,[[0,0],[85,0],[85,-286],[160,-286]],true));
  e.push(arrow(1290,671,1295,385,C.warn,[[0,0],[30,0],[30,-286],[5,-286]]));
  e.push(txt(970,610,'DB_PASSWORD',20,C.warn,170,'center'));
  footer(e,'ลบ Pod db แล้ว Deployment สร้างใหม่ · ข้อมูลยังอยู่ใน PVC');
  return e;
}

function lab017() {
  const e=base('Lab 017 · Ingress คือประตูหน้าบ้าน','host:8080 → node:80 → ingress-nginx → Ingress rules → Services → Pods');
  browser(e,25,330,180,112,'localhost:8080');
  e.push(card(245,320,190,130,'ingress-nginx\ncontroller\n(node :80)','ingress',20));
  zone(e,475,125,963,620,'namespace lab017');
  e.push(card(520,255,190,125,'Ingress rules\n/ → web:3000\n/api → api:8000','ingress',20));
  e.push(card(770,210,180,70,'Service web','service'),card(770,430,180,70,'Service api','service'));
  managers(e,1100,'web',140); managers(e,1100,'api',430);
  e.push(arrow(210,385,240,385,C.ink),arrow(440,385,515,320,C.warn));
  e.push(arrow(715,295,765,245,C.ok),arrow(715,340,765,465,C.ok));
  e.push(arrow(955,245,1095,362,C.ok,[[0,0],[70,0],[140,117]]),arrow(955,465,1095,652,C.ok,[[0,0],[70,0],[140,187]]));
  e.push(txt(710,180,'path /',20,C.warn,120,'center'),txt(710,505,'path /api',20,C.warn,150,'center'));
  e.push(txt(510,535,'object จาก Lab 016 ยังอยู่ครบ; แล็บนี้เปลี่ยนเฉพาะ “ประตู”',20,C.muted,520,'center'));
  e.push(card(510,580,115,58,'ConfigMap','config',20),card(640,580,115,58,'Secret','secret',20));
  e.push(card(770,580,135,58,'Deployment\ndb','deployment',20),card(920,580,135,58,'ReplicaSet\ndb','deployment',20));
  e.push(card(620,675,135,58,'Service\ndb','service',20),card(770,675,135,58,'Pod\ndb','pod',20),card(920,665,135,78,'PVC','pvc',20));
  e.push(arrow(910,609,915,609,C.acc));
  e.push(arrow(988,643,838,670,C.acc,[[0,0],[0,18],[-150,27]]));
  e.push(arrow(760,704,765,704,C.ok),arrow(915,704,910,704,C.warn));
  e.push(arrow(698,643,800,670,C.warn,[[0,0],[45,0],[102,27]],true));
  footer(e,'ประตูเดียวแยก backend ด้วย path; ไม่ต้องเปิด NodePort ใหม่ทุก Service');
  return e;
}

function lab018() {
  const e=archFrame('Lab 018 · RollingUpdate โดยไม่หยุดบริการ','web replicas=3 · v1 → v2 · Service รับเฉพาะ Pod ที่ readiness ผ่าน','lab018');
  browser(e,20,360,180,112,'localhost:8080');
  e.push(card(245,375,150,80,'Ingress\n/','ingress'),card(435,375,170,80,'Service\nweb','service'));
  e.push(card(675,155,190,72,'Deployment web\nRollingUpdate','deployment'));
  e.push(card(620,270,180,70,'RS v1\nลด replicas','deployment'),card(865,270,180,70,'RS v2\nเพิ่ม replicas','deployment'));
  e.push(card(610,400,170,66,'Pod v1\nReady','pod'),card(810,400,170,66,'Pod v2\nReady','ok'),card(1010,400,190,66,'Pod v2\nStarting','warn'));
  e.push(arrow(205,415,240,415),arrow(400,415,430,415,C.warn));
  e.push(arrow(770,232,710,265,C.acc),arrow(770,232,955,265,C.acc));
  e.push(arrow(710,345,695,395,C.acc),arrow(955,345,895,395,C.acc),arrow(955,345,1105,395,C.acc));
  e.push(arrow(605,415,610,433,C.ok));
  e.push(arrow(520,460,905,475,C.ok,[[0,0],[0,90],[385,90],[385,15]]));
  e.push(txt(605,500,'readiness ✓',20,C.ok,180,'center'),txt(1005,500,'readiness …\nยังไม่รับ traffic',20,C.warn,210,'center'));
  e.push(card(640,585,560,74,'maxSurge=1 · maxUnavailable=0 · minReadySeconds=5','neutral',22));
  e.push(card(1230,210,170,70,'api + db\nทำงานต่อ','ok',20));
  e.push(card(1230,320,170,62,'ConfigMap','config'),card(1230,410,170,62,'Secret','secret'),card(1230,500,170,74,'PVC','pvc'));
  footer(e,'Pod ใหม่ผ่าน readiness ก่อน จึงค่อยลด Pod เก่า — curl loop ไม่เห็น FAIL');
  return e;
}

function lab019() {
  const e=base('Lab 019 · บอก Kubernetes ว่า Pod ต้องการเท่าไร','Browser ผ่าน Ingress ตามเดิม; จุดทดลองอยู่ที่ requests ตอน schedule และ limits ตอนรัน');
  browser(e,30,330,180,112,'localhost:8080');
  e.push(card(250,345,150,80,'Ingress\n/','ingress'));
  e.push(card(445,345,160,80,'Service\nweb','service'));
  zone(e,650,135,788,585,'namespace lab019 / cluster workers');
  e.push(card(700,200,220,100,'Deployment web\nrequests 100m / 128Mi\nlimits 500m / 256Mi','deployment',20));
  e.push(card(700,345,180,70,'ReplicaSet\nweb','deployment'));
  e.push(card(700,480,180,82,'Pod web\nRunning','pod'));
  e.push(arrow(215,385,245,385),arrow(405,385,440,385,C.warn),arrow(610,385,695,520,C.ok,[[0,0],[42,0],[85,135]]));
  e.push(arrow(810,305,790,340,C.acc),arrow(790,420,790,475,C.acc));
  e.push(card(980,210,380,120,'Scheduler\nนับ requests แล้วเลือก node\nที่ยังมีที่จองเหลือ','ok',22));
  e.push(arrow(925,250,975,250,C.ok));
  e.push(card(980,405,170,82,'worker-1\nรับ Pod ได้','ok'),card(1190,405,170,82,'worker-2\nที่จองไม่พอ','bad'));
  e.push(card(980,555,170,82,'CPU เกิน\n→ throttle','warn'),card(1190,555,170,82,'Memory เกิน\n→ OOMKilled','bad'));
  footer(e,'requests ใหญ่เกิน = Pending · memory เกิน limits = OOMKilled');
  return e;
}

function lab020() {
  const e=base('Lab 020 · อ่านอาการเพื่อหาชั้นที่พัง','ชุด broken/ สร้าง 4 อาการ แล้วไล่ get → describe → logs → events');
  browser(e,25,335,175,112,'localhost:8080');
  e.push(card(240,350,150,80,'Ingress\n/','ingress'));
  e.push(card(430,350,175,80,'Service web\nendpoints: none','bad',20));
  e.push(arrow(205,390,235,390),arrow(395,390,425,390,C.warn));
  zone(e,650,130,788,590,'namespace lab020 · broken objects');
  e.push(card(700,210,300,86,'Pod A · Pending\nrequests cpu: 64','warn'));
  e.push(card(1060,210,300,86,'Pod B · ImagePullBackOff\ntag ไม่มีจริง','bad'));
  e.push(card(700,360,300,86,'Pod C · CrashLoopBackOff\nnode missing.js','bad'));
  e.push(card(1060,360,300,86,'Service D · endpoints <none>\nselector app: wep','warn'));
  e.push(card(700,540,660,82,'kubectl get → describe → logs --previous → events','neutral',22));
  e.push(arrow(1000,580,1000,455,C.acc));
  e.push(txt(690,650,'แก้ manifest ใน fixed/ แล้ว apply คืนทีละชั้น',22,C.ok,680,'center',true));
  e.push(txt(250,480,'ผู้ใช้เห็น 503 / เข้าไม่ได้\nแต่อาการต้นเหตุอยู่คนละชั้น',20,C.crit,350,'center'));
  footer(e,'Running ไม่ได้แปลว่าเชื่อมต่อได้ — ตรวจ Service, endpoints และ readiness ต่อ');
  return e;
}

function lab021() {
  const e=base('Lab 021 · ภาพใหญ่ของระบบ SkillSpace','เส้นทางเดียวเชื่อม Ingress, Service, Pod, ConfigMap, Secret และ persistent storage');
  browser(e,20,255,180,112,'localhost:8080');
  zone(e,225,125,1213,620,'namespace lab021');
  e.push(card(255,270,155,82,'ingress-nginx','ingress'),card(445,270,145,82,'Ingress\n/','ingress'));
  e.push(card(625,270,145,82,'Service\nweb','service'),card(805,270,145,82,'Pod\nweb','pod'));
  e.push(card(985,270,145,82,'Service\napi','service'),card(1165,270,145,82,'Pod\napi','pod'));
  e.push(arrow(205,310,250,310),arrow(415,310,440,310,C.warn),arrow(595,310,620,310,C.ok),arrow(775,310,800,310,C.acc),arrow(955,310,980,310,C.ok),arrow(1135,310,1160,310,C.acc));
  e.push(card(805,160,145,62,'ConfigMap','config')); e.push(arrow(878,225,878,265,C.warn,null,true));
  e.push(card(1165,410,145,82,'Service\ndb','service'),card(985,410,145,82,'Pod\ndb','pod'));
  e.push(card(805,410,145,82,'PVC','pvc'),card(625,410,145,82,'PV','pvc'));
  e.push(arrow(1238,357,1238,405,C.acc),arrow(1160,451,1135,451,C.ok),arrow(980,451,955,451,C.warn),arrow(800,451,775,451,C.warn));
  e.push(card(1165,555,145,62,'Secret','secret'));
  e.push(arrow(1238,550,1238,498,C.warn,null,true),arrow(1160,586,1058,498,C.warn,[[0,0],[-45,0],[-102,-88]],true));
  e.push(card(720,570,370,70,'Deployment → ReplicaSet\nดูแล Pod ของ web / api / db','deployment',20));
  e.push(txt(230,680,'ลองตัด: Service db · Service api · Ingress · scale web=0 แล้วสังเกตอาการ',22,C.crit,1130,'center',true));
  footer(e,'ทุก object มีหน้าที่เฉพาะ แต่ request สำเร็จได้เมื่อทุกชิ้นต่อกันครบ');
  return e;
}

const diagrams = {
  'd01-compose-to-objects': d01,
  'd02-stateless-vs-stateful': d02,
  'd03-ingress-vs-nodeport': d03,
  'd04-rolling-update-timeline': d04,
  'd05-requests-limits-scheduling': d05,
  'd06-troubleshooting-ladder': d06,
  'd07-request-path-browser-to-postgres': d07,
  'd08-learning-loop': d08,
  'lab015-architecture': lab015,
  'lab016-architecture': lab016,
  'lab017-architecture': lab017,
  'lab018-architecture': lab018,
  'lab019-architecture': lab019,
  'lab020-architecture': lab020,
  'lab021-architecture': lab021
};

for (const [name, fn] of Object.entries(diagrams)) {
  fs.writeFileSync(path.join(OUT, `${name}.json`), JSON.stringify(fn(), null, 2) + '\n');
}
console.log(`generated ${Object.keys(diagrams).length} element files in ${OUT}`);
