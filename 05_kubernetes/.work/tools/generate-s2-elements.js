const fs = require('fs');
const path = require('path');

const OUT = path.resolve('.work/diagram-elements-s2');
fs.mkdirSync(OUT, { recursive: true });

const C = {
  ink: '#18181b', acc: '#1c5cab', ok: '#116b11', warn: '#86590a', crit: '#a32222',
  blue: '#e7f0fb', green: '#e8f5e9', amber: '#fff4d6', red: '#fdeaea', white: '#ffffff', zone: '#c9cdd3',
};

function rect(id, x, y, width, height, text, role = 'plain', extra = {}) {
  const palette = {
    plain: [C.ink, C.white], pod: [C.acc, C.blue], service: [C.ok, C.green],
    warn: [C.warn, C.amber], danger: [C.crit, C.red], ok: [C.ok, C.green],
  }[role];
  return {
    id, type: 'rectangle', x, y, width, height,
    strokeColor: palette[0], backgroundColor: palette[1], fillStyle: 'solid',
    strokeWidth: 2, strokeStyle: 'solid', roughness: 0, roundness: { type: 3 },
    ...(text ? { text, fontSize: 20, fontFamily: 'helvetica', textAlign: 'center', verticalAlign: 'middle' } : {}),
    ...extra,
  };
}

function frame(id, x, y, width, height, color = C.zone) {
  return rect(id, x, y, width, height, null, 'plain', {
    strokeColor: color, backgroundColor: 'transparent', strokeWidth: 1.5, strokeStyle: 'dashed', roundness: { type: 3 },
  });
}

function text(id, x, y, width, value, size = 20, color = C.ink, align = 'left') {
  return { id, type: 'text', x, y, width, height: 40, text: value, fontSize: size, fontFamily: 'helvetica',
    textAlign: align, verticalAlign: 'middle', strokeColor: color, roughness: 0 };
}

function ellipse(id, x, y, width, height, value, role = 'plain') {
  const e = rect(id, x, y, width, height, value, role);
  e.type = 'ellipse';
  delete e.roundness;
  return e;
}

function arrow(id, startElementId, endElementId, color = C.ink, dashed = false) {
  return { id, type: 'arrow', x: 0, y: 0, startElementId, endElementId,
    strokeColor: color, strokeWidth: 2, strokeStyle: dashed ? 'dashed' : 'solid', roughness: 0,
    startArrowhead: null, endArrowhead: 'arrow' };
}

function elbowArrow(id, startElementId, endElementId, x, y, points, color = C.ink, dashed = false) {
  return { ...arrow(id, startElementId, endElementId, color, dashed), x, y, points, elbowed: true };
}

function base(title, subtitle, height = 880) {
  return [
    rect('background', 0, 0, 1520, height, null, 'plain', { strokeColor: C.white, backgroundColor: C.white, roundness: null }),
    text('title', 40, 40, 1440, title, 32),
    text('subtitle', 40, 80, 1440, subtitle, 20, '#4b5563'),
  ];
}

function zoneLabel(id, x, y, value, color = C.ink) { return text(id, x, y, 560, value, 20, color); }
function write(name, elements) { fs.writeFileSync(path.join(OUT, `${name}.json`), JSON.stringify(elements, null, 2)); }

// d01 — two side-by-side approaches. Service points once to a grouped set of Pods.
{
  const e = base('Pod IP เปลี่ยนได้ — Service ให้ชื่อคงที่', 'อย่าผูกแอปกับ IP ของ Pod โดยตรง ให้เรียกผ่าน DNS ของ Service');
  e.push(frame('fragile-zone', 40, 160, 640, 640, C.crit), frame('stable-zone', 760, 160, 720, 640, C.ok));
  e.push(zoneLabel('fragile-label', 80, 200, 'ทางที่เปราะบาง: เรียก Pod IP โดยตรง', C.crit));
  e.push(zoneLabel('stable-label', 800, 200, 'ทางที่ทนทาน: เรียกชื่อ Service', C.ok));
  e.push(rect('fragile-web', 80, 320, 160, 80, 'Pod web', 'pod'));
  e.push(rect('old-api', 400, 320, 160, 80, 'Pod api เก่า\n10.244.1.7', 'danger'));
  e.push(rect('deleted', 400, 520, 160, 80, 'ถูกลบ', 'danger'));
  e.push(rect('new-api', 400, 680, 160, 80, 'Pod api ใหม่\n10.244.2.9', 'pod'));
  e.push(arrow('fragile-call', 'fragile-web', 'old-api', C.crit), arrow('pod-deleted', 'old-api', 'deleted', C.crit));
  e.push(text('fragile-note', 80, 640, 280, 'web ยังจำ IP เก่า จึงหา Pod ใหม่ไม่เจอ', 20, C.crit));
  e.push(rect('stable-web', 800, 360, 160, 80, 'Pod web', 'pod'));
  e.push(rect('api-service', 1040, 360, 160, 80, 'Service api\nDNS: api', 'service'));
  e.push(frame('api-group', 1280, 200, 160, 400, C.ok));
  e.push(zoneLabel('api-group-label', 1320, 240, 'Pods', C.ok));
  e.push(rect('api-1', 1320, 320, 80, 80, 'api 1', 'pod'), rect('api-2', 1320, 480, 80, 80, 'api 2', 'pod'));
  e.push(arrow('web-service', 'stable-web', 'api-service', C.ok), arrow('service-group', 'api-service', 'api-group', C.ok));
  e.push(text('stable-note', 800, 680, 560, 'Service อัปเดต Endpoints ตาม label โดยอัตโนมัติ', 20, C.ok));
  write('d01-pod-ip-changes', e);
}

// d02 — four equal columns and equal vertical spacing.
{
  const e = base('Service Types — ต่างกันที่ใครเข้าถึงได้', 'จากซ้ายไปขวา: ภายใน cluster → พอร์ตบน node → cloud → ประตู HTTP เดียว');
  const xs = [40, 400, 760, 1120];
  const titles = ['ClusterIP', 'NodePort', 'LoadBalancer', 'Ingress'];
  const colors = [C.ok, C.acc, C.warn, C.warn];
  const roles = ['service', 'pod', 'warn', 'warn'];
  const boxes = [
    ['Client ภายใน', 'Service', 'Pod api'],
    ['Client ภายนอก', 'ทุก Node :30080', 'Service → Pod'],
    ['Internet', 'Cloud LB', 'Service → Pod'],
    ['Browser :80/443', 'Ingress rules', 'หลาย Service'],
  ];
  const notes = ['ค่าเริ่มต้น', 'ทดสอบ / ห้องเรียน', 'เมื่อ cloud จัดให้', 'L7: path / host / TLS'];
  xs.forEach((x, i) => {
    e.push(frame(`panel-${i}`, x, 160, 320, 640, colors[i]));
    e.push(text(`panel-title-${i}`, x + 40, 200, 240, titles[i], 28, colors[i]));
    [280, 440, 600].forEach((y, j) => e.push(rect(`type-${i}-${j}`, x + 80, y, 160, 80, boxes[i][j], roles[i])));
    e.push(arrow(`type-arrow-${i}-0`, `type-${i}-0`, `type-${i}-1`, colors[i]));
    e.push(arrow(`type-arrow-${i}-1`, `type-${i}-1`, `type-${i}-2`, colors[i]));
    e.push(text(`type-note-${i}`, x + 40, 720, 240, notes[i], 20, colors[i], 'center'));
  });
  write('d02-service-types', e);
}

// d03 — one image points to a deployment group; each environment injects its own config vertically.
{
  const e = base('Image เดียว — Config อยู่นอก Image', 'build ครั้งเดียว แล้ว inject ConfigMap / Secret ตามสภาพแวดล้อมตอน deploy');
  e.push(rect('image', 640, 160, 240, 80, 'image: k8s-lab-web:v1', 'pod'));
  e.push(frame('deployments-group', 80, 320, 1360, 440, C.acc));
  e.push(zoneLabel('deployments-label', 120, 360, '3 Deployments ใช้ image เดียวกัน', C.acc));
  const xs = [120, 600, 1080];
  const deps = ['Deployment ฝ่ายซ่อม', 'Deployment ห้องสมุด', 'Deployment ห้องปฏิบัติการ'];
  const cfgs = ['SITE_NAME: ศูนย์ซ่อม\nTHEME: amber', 'SITE_NAME: ระบบยืมคืน\nTHEME: blue', 'SITE_NAME: คลังอุปกรณ์\nTHEME: rose'];
  xs.forEach((x, i) => {
    e.push(rect(`dep-${i}`, x, 440, 320, 80, deps[i], 'pod'));
    e.push(rect(`cfg-${i}`, x, 640, 320, 80, `ConfigMap + Secret\n${cfgs[i]}`, 'warn'));
    e.push(arrow(`cfg-arrow-${i}`, `cfg-${i}`, `dep-${i}`, C.warn, true));
  });
  e.push(arrow('image-group', 'image', 'deployments-group', C.acc));
  e.push(text('config-note', 480, 800, 560, 'เปลี่ยน config ได้โดยไม่ต้อง rebuild image', 20, C.ok, 'center'));
  write('d03-config-outside-image', e);
}

// d04 — straight left-to-right conversion chain with labels offset above the arrows.
{
  const e = base('Secret: base64 คือการแปลงรูป ไม่ใช่การเข้ารหัส', 'Kubernetes รับ stringData แล้วเก็บเป็น data แบบ base64; เมื่อ inject เข้า Pod จะเห็นค่าจริง');
  e.push(rect('secret-yaml', 80, 320, 320, 160, 'Secret YAML\nstringData:\nPOSTGRES_PASSWORD: labpass', 'warn'));
  e.push(rect('api-store', 600, 320, 320, 160, 'API server เก็บเป็น data\nPOSTGRES_PASSWORD:\nbGFi cGFzcw==', 'warn'));
  e.push(rect('pod-process', 1120, 320, 320, 160, 'Pod api / db\nenv: POSTGRES_PASSWORD\nค่าจริง = labpass', 'pod'));
  e.push(arrow('encode-arrow', 'secret-yaml', 'api-store', C.warn), arrow('decode-arrow', 'api-store', 'pod-process', C.acc));
  e.push(text('encode-label', 440, 360, 120, 'encode base64', 20, C.warn, 'center'));
  e.push(text('decode-label', 960, 360, 120, 'inject / decode', 20, C.acc, 'center'));
  e.push(rect('decode-demo', 400, 640, 720, 80, 'echo bGFi cGFzcw== | base64 -d   →   labpass', 'danger'));
  e.push(text('security-note', 400, 760, 720, 'ถอดกลับได้ในคำสั่งเดียว — ใช้ RBAC + encryption at rest', 20, C.crit, 'left'));
  write('d04-secret-base64', e);
}

// d05 — three equal panels with equal boxes and 80px connector gaps.
{
  const e = base('ข้อมูลอยู่รอดแค่ไหน? Container FS → emptyDir → PVC', 'อายุของข้อมูลขึ้นกับชั้นที่เราเลือกเก็บ');
  const xs = [40, 520, 1000];
  const titles = ['Container filesystem', 'emptyDir', 'PVC → PV'];
  const colors = [C.crit, C.warn, C.ok];
  const roles = ['danger', 'warn', 'ok'];
  const rows = [
    ['image layers (read-only)', 'writable layer', 'Pod ใหม่ → หาย'],
    ['Pod มี volume ชั่วคราว', 'container restart → ยังอยู่', 'Pod ใหม่ → หาย'],
    ['Pod mount PVC', 'PVC ผูกกับ PV ภายนอก', 'Pod ใหม่ → ยังอยู่'],
  ];
  const notes = ['รอด: container เดิมเท่านั้น', 'รอด: ภายใน Pod เดิม', 'รอด: ข้ามการเกิดใหม่ของ Pod'];
  xs.forEach((x, i) => {
    e.push(frame(`fs-panel-${i}`, x, 160, 440, 640, colors[i]));
    e.push(text(`fs-title-${i}`, x + 40, 200, 360, titles[i], 28, colors[i]));
    [280, 440, 600].forEach((y, j) => e.push(rect(`fs-${i}-${j}`, x + 80, y, 280, 80, rows[i][j], roles[i])));
    e.push(arrow(`fs-arrow-${i}-0`, `fs-${i}-0`, `fs-${i}-1`, colors[i]));
    e.push(arrow(`fs-arrow-${i}-1`, `fs-${i}-1`, `fs-${i}-2`, colors[i]));
    e.push(text(`fs-note-${i}`, x + 80, 720, 280, notes[i], 20, colors[i], 'left'));
  });
  write('d05-container-fs-vs-volume', e);
}

// d06 — two symmetric panels.
{
  const e = base('Readiness vs Liveness — สองคำถาม สองผลลัพธ์', 'Probe ต้องตอบให้ตรงเรื่อง: พร้อมรับงานหรือยัง? หรือ process ยังมีชีวิตไหม?');
  e.push(frame('ready-panel', 40, 160, 680, 640, C.ok), frame('live-panel', 800, 160, 680, 640, C.crit));
  e.push(text('ready-title', 80, 200, 560, 'readinessProbe — “ตอนนี้รับงานได้ไหม?”', 28, C.ok));
  e.push(text('live-title', 840, 200, 560, 'livenessProbe — “process ยังมีชีวิตไหม?”', 28, C.crit));
  e.push(rect('ready-pod', 120, 320, 200, 80, 'Pod api\nRunning · 0/1', 'pod'));
  e.push(rect('ready-result', 480, 320, 160, 80, 'Service api\nEndpoints', 'service'));
  e.push(arrow('ready-arrow', 'ready-pod', 'ready-result', C.crit, true));
  e.push(text('ready-fail', 120, 480, 520, 'FAIL → ถอด Pod ออกจาก Service', 20, C.crit));
  e.push(text('ready-pass', 120, 560, 520, 'PASS → ใส่กลับเอง\nไม่ restart container', 20, C.ok));
  e.push(rect('live-pod', 880, 320, 200, 80, 'Pod api\nprocess ค้าง', 'danger'));
  e.push(rect('live-result', 1240, 320, 160, 80, 'kubelet\nrestart container', 'danger'));
  e.push(arrow('live-arrow', 'live-pod', 'live-result', C.crit));
  e.push(text('live-fail', 880, 480, 520, 'FAIL → ฆ่าและเริ่ม container ใหม่', 20, C.crit));
  e.push(text('live-note', 880, 560, 520, 'อย่าเช็ก dependency ภายนอก\nเช่น db ใน liveness', 20, C.warn));
  write('d06-readiness-vs-liveness', e);
}

// d07 — six compact stages fit on one left-to-right row with exact 80px gaps.
{
  const e = base('เส้นทาง Request ภายใน Cluster: web → api → db', 'Service ให้ชื่อคงที่ ส่วน Pod ที่รับงานเปลี่ยนได้ตลอด');
  e.push(frame('request-zone', 40, 160, 1440, 600, C.zone));
  e.push(zoneLabel('request-zone-label', 80, 200, 'namespace: lab0NN'));
  const xs = [80, 320, 560, 800, 1040, 1280];
  const labels = ['Service web\n:3000', 'Pod web', 'Service api\n:8000', 'Pod api', 'Service db\n:5432', 'Pod db'];
  const roles = ['service', 'pod', 'service', 'pod', 'service', 'pod'];
  xs.forEach((x, i) => e.push(rect(`request-${i}`, x, 400, 160, 80, labels[i], roles[i])));
  for (let i = 0; i < 5; i++) e.push(arrow(`request-arrow-${i}`, `request-${i}`, `request-${i + 1}`, i % 2 ? C.acc : C.ok));
  e.push(text('http-label', 520, 320, 320, 'HTTP API', 20, C.acc, 'center'));
  e.push(text('sql-label', 1000, 320, 320, 'PostgreSQL', 20, C.acc, 'center'));
  e.push(text('return-note', 480, 600, 560, 'response ตอบกลับย้อนเส้นทางเดิม', 20, C.ok, 'center'));
  write('d07-request-path-web-api-db', e);
}

// d08 — a deliberate loop; diagonal arrows are allowed by feedback rule 3 for theory loops.
{
  const e = base('วงจรการเรียนรู้: ทาย → ลงมือ → อธิบาย → แก้กลับ', 'ทุกแล็บวนครบหนึ่งรอบ เพื่อเปลี่ยนคำสั่งให้เป็นความเข้าใจ');
  const nodes = [
    ['loop-1', 640, 160, '1  ทายผล', 'warn'], ['loop-2', 1080, 280, '2  รันคำสั่ง', 'pod'],
    ['loop-3', 1080, 600, '3  สังเกต', 'ok'], ['loop-4', 640, 720, '4  อธิบาย', 'pod'],
    ['loop-5', 240, 600, '5  ทำให้พัง', 'danger'], ['loop-6', 240, 280, '6  แก้กลับ', 'ok'],
  ];
  nodes.forEach(n => e.push(ellipse(n[0], n[1], n[2], 200, 80, n[3], n[4])));
  e.push(ellipse('loop-core', 600, 400, 320, 160, 'แนวคิดหลัก\n“เพราะอะไร”', 'plain'));
  const cols = [C.acc, C.ok, C.acc, C.crit, C.ok, C.warn];
  for (let i = 0; i < 6; i++) e.push(arrow(`loop-arrow-${i}`, `loop-${i + 1}`, `loop-${(i + 1) % 6 + 1}`, cols[i]));
  write('d08-learning-loop', e);
}

function labBase(num, title, subtitle, zoneHeight = 680) {
  const e = base(`Lab ${num} — ${title}`, subtitle);
  e.push(frame('namespace', 240, 120, 1240, zoneHeight, C.zone));
  e.push(zoneLabel('namespace-label', 280, 160, `namespace: lab${num}`));
  return e;
}

function addWebEntry(e, y = 240) {
  e.push(rect('browser', 40, y, 160, 80, 'Browser\nlocalhost:8080', 'plain'));
  e.push(rect('ingress', 280, y, 160, 80, 'Ingress\npath /', 'warn'));
  e.push(rect('service-web', 520, y, 160, 80, 'Service web\n:3000', 'service'));
  e.push(rect('pod-web', 760, y, 160, 80, 'Pod web', 'pod'));
  e.push(arrow('browser-ingress', 'browser', 'ingress', C.warn), arrow('ingress-service-web', 'ingress', 'service-web', C.warn), arrow('service-web-pod', 'service-web', 'pod-web', C.ok));
}

// lab008 — Service points once to the grouped api Pods.
{
  const e = labBase('008', 'ทำไมต้องมี Service', 'Pod IP เปลี่ยน แต่ Service DNS “api” และ Endpoints ตาม Pod ให้เอง');
  addWebEntry(e, 360);
  e.push(rect('service-api', 1000, 360, 160, 80, 'Service api\nDNS: api :8000', 'service'));
  e.push(frame('api-pods-group', 1240, 200, 200, 400, C.ok));
  e.push(zoneLabel('api-pods-label', 1280, 240, 'Pods · app=api', C.ok));
  e.push(rect('pod-api-1', 1280, 360, 120, 80, 'api 1', 'pod'), rect('pod-api-2', 1280, 520, 120, 80, 'api 2', 'pod'));
  e.push(arrow('pod-web-service-api', 'pod-web', 'service-api', C.acc), arrow('service-api-group', 'service-api', 'api-pods-group', C.ok));
  e.push(text('lab008-note', 600, 720, 720, 'ไม่มี db ในแล็บนี้ · Service เลือก Pod ด้วย label และอัปเดต Endpoints อัตโนมัติ', 20, C.crit, 'center'));
  write('lab008-architecture', e);
}

// lab009 — access methods are grouped, avoiding a diagonal fan into Service web.
{
  const e = base('Lab 009 — Service Types และการเข้าถึง', 'web เปิดด้วย NodePort; api เป็น ClusterIP และเรียกได้เฉพาะภายใน cluster');
  e.push(frame('namespace', 360, 120, 1120, 680, C.zone));
  e.push(zoneLabel('namespace-label', 400, 160, 'namespace: lab009'));
  e.push(frame('access-group', 40, 200, 240, 400, C.acc));
  e.push(zoneLabel('access-label', 80, 240, 'ทางเข้าจากภายนอก', C.acc));
  e.push(rect('nodeport-client', 80, 320, 160, 80, 'Client\n<NodeIP> :30080', 'pod'));
  e.push(rect('port-forward', 80, 480, 160, 80, 'Browser\nport-forward', 'plain'));
  e.push(rect('service-web', 400, 360, 160, 80, 'Service web\nNodePort 30080', 'service'));
  e.push(frame('web-pods-group', 640, 200, 200, 400, C.ok));
  e.push(zoneLabel('web-pods-label', 680, 240, 'Pods · app=web', C.ok));
  e.push(rect('pod-web-1', 680, 320, 120, 80, 'web 1', 'pod'), rect('pod-web-2', 680, 480, 120, 80, 'web 2', 'pod'));
  e.push(rect('service-api', 960, 360, 160, 80, 'Service api\nClusterIP :8000', 'service'));
  e.push(rect('pod-api', 1280, 360, 160, 80, 'Pod api', 'pod'));
  e.push(arrow('access-service', 'access-group', 'service-web', C.acc), arrow('service-web-group', 'service-web', 'web-pods-group', C.ok));
  e.push(arrow('web-group-api-service', 'web-pods-group', 'service-api', C.acc), arrow('api-service-pod', 'service-api', 'pod-api', C.ok));
  e.push(text('nodeport-note', 400, 720, 400, 'NodePort เปิดพอร์ตเดียวกันบนทุก node', 20, C.acc));
  e.push(text('clusterip-note', 960, 720, 480, 'api ไม่เปิดออกนอก cluster', 20, C.ok));
  write('lab009-architecture', e);
}

// lab010 — traffic stays horizontal; ConfigMap injects vertically into the deployment group.
{
  const e = labBase('010', 'แยก Config ออกจาก Image', 'ConfigMap inject SITE_NAME / THEME ตอนสร้าง Pod; image เดิมใช้ได้หลาย config');
  e.push(rect('browser', 40, 320, 160, 80, 'Browser\nlocalhost:8080', 'plain'));
  e.push(rect('ingress', 280, 320, 160, 80, 'Ingress\npath /', 'warn'));
  e.push(rect('service-web', 520, 320, 160, 80, 'Service web\n:3000', 'service'));
  e.push(frame('deployment-web', 800, 240, 240, 240, C.acc));
  e.push(zoneLabel('deployment-label', 840, 280, 'Deployment web', C.acc));
  e.push(rect('pod-web', 840, 360, 160, 80, 'Pod web', 'pod'));
  e.push(rect('configmap', 800, 600, 240, 80, 'ConfigMap web-config\nSITE_NAME · THEME', 'warn'));
  e.push(rect('image-note-box', 1160, 320, 240, 80, 'image เดิม\nk8s-lab-web:v1', 'pod'));
  e.push(arrow('browser-ingress', 'browser', 'ingress', C.warn), arrow('ingress-service', 'ingress', 'service-web', C.warn));
  e.push(arrow('service-deployment', 'service-web', 'deployment-web', C.ok), arrow('config-deployment', 'configmap', 'deployment-web', C.warn, true));
  e.push(text('restart-note', 600, 760, 720, 'เปลี่ยนค่า env → rollout restart เพื่อสร้าง Pod ใหม่', 20, C.warn, 'center'));
  write('lab010-architecture', e);
}

function addThreeTier(e, topY = 200) {
  addWebEntry(e, topY);
  e.push(rect('service-api', 760, topY + 160, 160, 80, 'Service api\nDNS: api :8000', 'service'));
  e.push(rect('pod-api', 1000, topY + 160, 160, 80, 'Pod api', 'pod'));
  e.push(rect('service-db', 1000, topY + 320, 160, 80, 'Service db\nDNS: db :5432', 'service'));
  e.push(rect('pod-db', 1240, topY + 320, 160, 80, 'Pod db', 'pod'));
  e.push(arrow('pod-web-service-api', 'pod-web', 'service-api', C.acc));
  e.push(arrow('service-api-pod', 'service-api', 'pod-api', C.ok));
  e.push(arrow('pod-api-service-db', 'pod-api', 'service-db', C.acc));
  e.push(arrow('service-db-pod', 'service-db', 'pod-db', C.ok));
}

// lab011 — full three-tier request path, Secret as a concise dependency annotation.
{
  const e = labBase('011', 'Secret และระบบ 3 ชั้น', 'Secret ส่งรหัสผ่านให้ api และ db; ฐานข้อมูลยังเขียนลง container filesystem');
  addThreeTier(e, 200);
  e.push(rect('secret', 640, 680, 240, 80, 'Secret db-secret\ninject → api + db', 'warn'));
  e.push(rect('no-pvc', 960, 680, 400, 80, 'ยังไม่มี PVC · Pod db ใหม่ → ข้อมูลหาย', 'danger'));
  write('lab011-architecture', e);
}

// lab012 — emptyDir is directly below Pod db with an 80px connector gap.
{
  const e = labBase('012', 'ทำไมข้อมูลหาย', 'db Pod ใหม่ = container ใหม่; emptyDir รอดแค่ container restart ใน Pod เดิม', 720);
  addThreeTier(e, 240);
  e.push(rect('secret', 640, 680, 240, 80, 'Secret db-secret\ninject → api + db', 'warn'));
  e.push(rect('emptydir', 1240, 720, 160, 80, 'emptyDir\nPod ใหม่ → หาย', 'danger'));
  e.push(arrow('pod-db-emptydir', 'pod-db', 'emptydir', C.crit));
  write('lab012-architecture', e);
}

// lab013 — PVC is inside namespace; PV is below it and outside, vertically aligned.
{
  const e = labBase('013', 'Persistent Storage ด้วย PVC', 'Pod db mount claim เดิม → PV เดิม → ข้อมูลยังอยู่', 640);
  addWebEntry(e, 200);
  e.push(rect('service-api', 760, 360, 160, 80, 'Service api\nDNS: api :8000', 'service'));
  e.push(rect('pod-api', 1000, 360, 160, 80, 'Pod api', 'pod'));
  e.push(frame('data-group', 720, 520, 720, 200, C.acc));
  e.push(zoneLabel('data-group-label', 760, 560, 'ชั้นข้อมูล', C.acc));
  e.push(rect('service-db', 760, 600, 160, 80, 'Service db\nDNS: db :5432', 'service'));
  e.push(rect('pod-db', 1000, 600, 160, 80, 'Pod db', 'pod'));
  e.push(rect('pvc', 1240, 600, 160, 80, 'PVC db-data\n1Gi · RWO', 'pod'));
  e.push(rect('pv', 1240, 800, 160, 80, 'PV\ncluster-scoped', 'pod'));
  e.push(arrow('pod-web-service-api', 'pod-web', 'service-api', C.acc));
  e.push(arrow('service-api-pod', 'service-api', 'pod-api', C.ok));
  e.push(arrow('pod-api-data-group', 'pod-api', 'data-group', C.acc));
  e.push(arrow('service-db-pod', 'service-db', 'pod-db', C.ok));
  e.push(rect('secret', 400, 800, 240, 80, 'Secret db-secret\ninject → api + db', 'warn'));
  e.push(arrow('pod-db-pvc', 'pod-db', 'pvc', C.acc), arrow('pvc-pv', 'pvc', 'pv', C.ok));
  e.push(text('storage-note', 760, 840, 400, 'PV อยู่นอก namespace', 20, C.ok, 'center'));
  write('lab013-architecture', e);
}

// lab014 — grouped api Pods prevent fan-out; probe outcomes are isolated from request lines.
{
  const e = labBase('014', 'Running ไม่ได้แปลว่า Ready', 'readiness ถอด api จาก Service; liveness ให้ kubelet restart container', 720);
  addWebEntry(e, 240);
  e.push(rect('service-api', 760, 400, 160, 80, 'Service api\nDNS: api :8000', 'service'));
  e.push(frame('api-pods-group', 1040, 240, 240, 400, C.ok));
  e.push(zoneLabel('api-pods-label', 1080, 280, 'Pods · app=api', C.ok));
  e.push(rect('pod-api-1', 1080, 360, 160, 80, 'Pod api 1', 'pod'), rect('pod-api-2', 1080, 520, 160, 80, 'Pod api 2', 'pod'));
  e.push(rect('service-db', 1080, 720, 160, 80, 'Service db\n:5432', 'service'));
  e.push(rect('pod-db', 1320, 720, 160, 80, 'Pod db', 'pod'));
  e.push(arrow('pod-web-service-api', 'pod-web', 'service-api', C.acc));
  e.push(arrow('service-api-group', 'service-api', 'api-pods-group', C.ok));
  e.push(arrow('api-group-service-db', 'api-pods-group', 'service-db', C.acc));
  e.push(arrow('service-db-pod', 'service-db', 'pod-db', C.ok));
  e.push(rect('readiness-result', 40, 520, 280, 120, 'readinessProbe /ready\nFAIL → ถอด Pod\nออกจาก Endpoints', 'ok'));
  e.push(rect('liveness-result', 360, 520, 280, 120, 'livenessProbe /health\nFAIL → kubelet\nrestart container', 'danger'));
  e.push(text('running-note', 40, 720, 880, 'db ล่ม: api ยัง Running แต่ 0/1 Ready และ Endpoints ว่าง', 20, C.crit));
  e.push(text('storage-note', 680, 680, 320, 'storage: PVC db-data → PV\n(จาก Lab 013)', 20, C.acc));
  write('lab014-architecture', e);
}

console.log(`generated ${fs.readdirSync(OUT).filter(f => f.endsWith('.json')).length} element files in ${OUT}`);
