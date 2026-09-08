import fs from 'node:fs';
import path from 'node:path';

const OUT = path.dirname(new URL(import.meta.url).pathname);
const C = {
  acc: '#1c5cab', ok: '#116b11', warn: '#86590a', crit: '#a32222', ink: '#18181b',
  accw: '#eaf2fd', okw: '#e7f6e7', warnw: '#fdf3dd', critw: '#fbeaea',
  rule: '#d4d4d8', white: '#ffffff', wash: '#f4f4f5', ink2: '#52525b'
};

function scene(name, title, subtitle = '') {
  let seq = 0;
  const e = [];
  const id = p => `${name}-${p}-${++seq}`;
  const rect = (x, y, w, h, stroke = C.rule, fill = C.white, opt = {}) => {
    const el = { id: opt.id || id('rect'), type: 'rectangle', x, y, width: w, height: h,
      strokeColor: stroke, backgroundColor: fill, fillStyle: 'solid', strokeWidth: opt.strokeWidth ?? 2,
      strokeStyle: opt.strokeStyle || 'solid', roughness: 0, opacity: opt.opacity ?? 100,
      roundness: opt.square ? null : { type: 3 } };
    e.push(el); return el.id;
  };
  const ellipse = (x, y, w, h, stroke = C.acc, fill = C.accw, opt = {}) => {
    const el = { id: opt.id || id('ellipse'), type: 'ellipse', x, y, width: w, height: h,
      strokeColor: stroke, backgroundColor: fill, fillStyle: 'solid', strokeWidth: opt.strokeWidth ?? 2,
      strokeStyle: opt.strokeStyle || 'solid', roughness: 0, opacity: opt.opacity ?? 100 };
    e.push(el); return el.id;
  };
  const text = (x, y, value, size = 20, color = C.ink, opt = {}) => {
    // Excalidraw reinterprets width on unbound centered text.  Compute the
    // visual centre ourselves so labels stay inside cards after SVG export.
    if (opt.align === 'center' && opt.width) {
      const maxChars = Math.max(4, Math.floor(opt.width / (size * 0.52)));
      const wrapped = [];
      for (const original of value.split('\n')) {
        const words = original.split(/\s+/).filter(Boolean);
        if (!words.length) { wrapped.push(''); continue; }
        let line = '';
        for (const word of words) {
          if (!line) line = word;
          else if ([...`${line} ${word}`].length <= maxChars) line += ` ${word}`;
          else { wrapped.push(line); line = word; }
        }
        wrapped.push(line);
      }
      value = wrapped.join('\n');
      const lines = value.split('\n');
      const visualWidth = Math.min(opt.width, Math.max(...lines.map(v => [...v].length)) * size * 0.52);
      x += (opt.width - visualWidth) / 2;
      if (opt.height) y += Math.max(0, (opt.height - lines.length * size * 1.25) / 2);
    }
    const el = { id: opt.id || id('text'), type: 'text', x, y, text: value,
      fontSize: size, fontFamily: '2', strokeColor: color, roughness: 0,
      textAlign: 'left', verticalAlign: 'top', lineHeight: 1.25 };
    e.push(el); return el.id;
  };
  const arrow = (pts, color = C.ink2, opt = {}) => {
    const [x0, y0] = pts[0];
    const el = { id: opt.id || id('arrow'), type: 'arrow', x: x0, y: y0,
      points: pts.map(([x, y]) => [x - x0, y - y0]), strokeColor: color,
      strokeWidth: opt.strokeWidth ?? 3, strokeStyle: opt.dashed ? 'dashed' : 'solid',
      roughness: 0, endArrowhead: opt.endArrowhead === false ? null : 'arrow',
      startArrowhead: opt.startArrowhead || null };
    if (pts.length > 2) el.elbowed = opt.elbowed ?? true;
    e.push(el); return el.id;
  };
  const line = (pts, color = C.rule, opt = {}) => arrow(pts, color, { ...opt, endArrowhead: false });
  const label = (x, y, w, h, value, color = C.ink, size = 20) =>
    text(x, y, value, size, color, { width: w, height: h, align: 'center' });
  const card = (x, y, w, h, value, kind = 'pod', opt = {}) => {
    const style = {
      pod: [C.acc, C.accw, 2], service: [C.ok, C.okw, 3], ingress: [C.warn, C.warnw, 3],
      deployment: [C.acc, C.accw, 4], rs: [C.acc, C.white, 2],
      warn: [C.warn, C.warnw, 2], crit: [C.crit, C.critw, 2], ok: [C.ok, C.okw, 2],
      neutral: [C.rule, C.white, 2], dark: [C.ink, C.wash, 2]
    }[kind];
    rect(x, y, w, h, style[0], style[1], { strokeWidth: style[2], strokeStyle: opt.dashed ? 'dashed' : 'solid' });
    label(x + 8, y + 6, w - 16, h - 12, value, opt.color || C.ink, opt.size || 20);
  };
  const zone = (x, y, w, h, titleText, opt = {}) => {
    rect(x, y, w, h, opt.stroke || C.rule, opt.fill || C.white,
      { strokeWidth: opt.strokeWidth || 2, strokeStyle: 'dashed', square: false });
    text(x + 20, y + 12, titleText, opt.size || 22, opt.titleColor || C.ink);
  };
  const browser = (x, y, w, h, url) => {
    rect(x, y, w, h, C.ink, C.white, { strokeWidth: 2 });
    rect(x, y, w, 34, C.ink, C.wash, { strokeWidth: 2, square: true });
    ellipse(x + 12, y + 10, 12, 12, C.crit, C.critw, { strokeWidth: 2 });
    ellipse(x + 32, y + 10, 12, 12, C.warn, C.warnw, { strokeWidth: 2 });
    ellipse(x + 52, y + 10, 12, 12, C.ok, C.okw, { strokeWidth: 2 });
    label(x + 10, y + 40, w - 20, h - 46, `Browser\n${url}`, C.ink, 20);
  };
  const pod = (x, y, nameText, meta = '') => {
    rect(x, y, 180, 130, C.acc, C.accw, { strokeWidth: 2 });
    text(x + 14, y + 10, 'Pod', 20, C.acc);
    label(x + 8, y + 36, 164, meta ? 84 : 78, meta ? `${nameText}\n${meta}` : nameText, C.ink, 20);
  };
  const service = (x, y, nameText, meta = '') => card(x, y, 200, 88, `Service · ${nameText}${meta ? `\n${meta}` : ''}`, 'service');
  const ingress = (x, y, nameText = 'Ingress · /') => card(x, y, 210, 88, nameText, 'ingress');
  const deployment = (x, y, nameText, meta = '') => card(x, y, 240, 94, `Deployment · ${nameText}${meta ? `\n${meta}` : ''}`, 'deployment');
  const rs = (x, y, nameText, meta = '') => card(x, y, 210, 88, `ReplicaSet · ${nameText}${meta ? `\n${meta}` : ''}`, 'rs', { dashed: true });

  rect(0, 0, 1400, 800, C.white, C.white, { square: true, strokeWidth: 1 });
  text(50, 28, title, 32, C.ink);
  line([[50, 82], [1350, 82]], C.rule, { strokeWidth: 2 });
  if (subtitle) text(50, 92, subtitle, 20, C.ink2);

  return { name, e, rect, ellipse, text, arrow, line, label, card, zone, browser, pod, service, ingress, deployment, rs };
}

const diagrams = {};
const save = s => { diagrams[s.name] = s.e; };

{
  const s = scene('d01-compose-vs-kubernetes', 'จาก Docker Compose สู่ Kubernetes', 'ความต่างสำคัญ: ผู้ดูแลหนึ่งเครื่อง เทียบกับ control plane ที่ดูแลทั้ง cluster');
  const { zone, card, text, arrow, line } = s;
  zone(55, 145, 530, 560, 'Docker Compose · เครื่องเดียว', { fill: C.warnw, stroke: C.warn });
  card(90, 220, 160, 80, 'compose.yaml', 'warn');
  arrow([[250, 260], [310, 260]], C.warn);
  zone(310, 185, 235, 430, 'Server เดียว', { fill: C.white, stroke: C.rule, size: 20 });
  card(340, 250, 175, 78, 'web container 1', 'pod');
  card(340, 355, 175, 78, 'web container 2', 'pod');
  card(340, 460, 175, 78, 'web container 3', 'pod');
  card(105, 585, 420, 82, 'เครื่องดับ → ทุก container หยุด', 'crit');

  arrow([[610, 420], [760, 420]], C.acc, { strokeWidth: 4 });
  text(610, 360, 'สู่หลายเครื่อง', 22, C.acc, { width: 150, align: 'center' });

  zone(785, 145, 560, 560, 'Kubernetes · cluster หลาย node', { fill: C.accw, stroke: C.acc });
  card(830, 195, 470, 82, 'Control plane · เฝ้า desired state', 'deployment');
  arrow([[1065, 277], [1065, 325]], C.acc);
  zone(820, 325, 235, 270, 'Worker node 1', { fill: C.white, stroke: C.rule, size: 20 });
  zone(1075, 325, 235, 270, 'Worker node 2', { fill: C.white, stroke: C.rule, size: 20 });
  card(850, 405, 175, 78, 'Pod · web 1', 'pod');
  card(850, 505, 175, 78, 'Pod · web 2', 'pod');
  card(1105, 405, 175, 78, 'Pod · web 3', 'pod');
  card(835, 610, 460, 75, 'node หาย → control plane\nรับรู้และแก้ส่วนต่าง', 'ok');
  save(s);
}

{
  const s = scene('d02-cluster-architecture', 'สถาปัตยกรรม Kubernetes cluster', 'kubectl คุยกับ API server; control plane ตัดสินใจ ส่วน worker รัน Pod');
  const { zone, card, text, arrow } = s;
  card(55, 280, 180, 84, 'kubectl\nคำสั่งของผู้ใช้', 'dark');
  text(250, 284, 'HTTPS', 20, C.acc);
  zone(345, 135, 990, 570, 'kind cluster · devtools (3 nodes)', { fill: C.white, stroke: C.acc });
  zone(385, 190, 910, 200, 'Control plane · สมองของ cluster', { fill: C.accw, stroke: C.acc });
  card(425, 260, 190, 82, 'API server\nประตูของ API', 'deployment');
  card(650, 260, 180, 82, 'scheduler\nเลือก node', 'pod');
  card(865, 260, 180, 82, 'controller\nเทียบสภาพ', 'pod');
  card(1080, 260, 175, 82, 'etcd\nเก็บ state', 'dark');
  arrow([[615, 301], [650, 301]], C.acc);
  arrow([[615, 326], [630, 370], [955, 370], [955, 342]], C.acc, { elbowed: true });
  arrow([[1080, 301], [1045, 301]], C.acc, { startArrowhead: 'arrow' });
  zone(385, 430, 430, 225, 'Worker node 1', { fill: C.white, stroke: C.rule });
  zone(865, 430, 430, 225, 'Worker node 2', { fill: C.white, stroke: C.rule });
  card(420, 490, 155, 70, 'kubelet', 'neutral');
  card(600, 490, 175, 70, 'container runtime', 'neutral');
  card(520, 575, 160, 62, 'Pod · web', 'pod');
  card(900, 490, 155, 70, 'kubelet', 'neutral');
  card(1080, 490, 175, 70, 'container runtime', 'neutral');
  card(1000, 575, 160, 62, 'Pod · web', 'pod');
  arrow([[520, 390], [500, 430]], C.acc);
  arrow([[960, 390], [980, 430]], C.acc);
  arrow([[235,322],[330,322],[330,301],[425,301]], C.acc, { elbowed: true });
  save(s);
}

{
  const s = scene('d03-pod-vs-container', 'Pod ไม่ใช่ container', 'Pod คือ “ซอง” ที่ scheduler ย้ายทั้งชุด และมี container ได้ตั้งแต่หนึ่งตัวขึ้นไป');
  const { zone, card, text, arrow, rect, label } = s;
  zone(60, 150, 450, 520, 'มองแยกเป็น container', { fill: C.critw, stroke: C.crit });
  card(120, 245, 330, 90, 'web container', 'crit');
  card(120, 400, 330, 90, 'sidecar container', 'crit');
  text(110, 550, 'ไม่ใช่หน่วยที่ Kubernetes schedule', 22, C.crit);
  arrow([[530, 405], [650, 405]], C.acc, { strokeWidth: 4 });
  text(530, 345, 'รวมเป็น 1 Pod', 22, C.acc, { width: 120, align: 'center' });
  zone(675, 150, 665, 520, 'Pod · หน่วยเล็กที่สุดที่ Kubernetes ดูแล', { fill: C.accw, stroke: C.acc });
  rect(735, 235, 545, 280, C.acc, C.white, { strokeWidth: 3 });
  text(755, 250, 'Pod web2 · IP 10.244.1.8', 22, C.acc);
  card(770, 315, 210, 100, 'web\n:3000', 'pod');
  card(1035, 315, 210, 100, 'sidecar\nเรียก localhost', 'pod');
  arrow([[1035, 365], [980, 365]], C.ok);
  card(825, 445, 365, 54, 'shared volume', 'neutral');
  arrow([[875, 415], [875, 445]], C.ink2);
  arrow([[1140, 415], [1140, 445]], C.ink2);
  card(790, 555, 435, 70, 'แชร์ IP · localhost · volume · lifecycle', 'ok');
  save(s);
}

{
  const s = scene('d04-declarative-loop', 'Declarative reconciliation loop', 'บอกปลายทางที่ต้องการ แล้ว Kubernetes วนตรวจและแก้ส่วนต่างให้เอง');
  const { card, ellipse, text, arrow } = s;
  card(80, 290, 230, 110, 'YAML\ndesired state = 3', 'warn');
  card(405, 155, 240, 110, 'API server\nรับและเก็บ spec', 'deployment');
  card(755, 155, 250, 110, 'controller\nเปรียบเทียบ', 'deployment');
  card(1090, 290, 230, 110, 'แก้ส่วนต่าง\nสร้าง / ลบ / อัปเดต', 'ok');
  card(755, 520, 250, 110, 'actual state\nPod ที่รันจริง', 'pod');
  ellipse(470, 445, 220, 110, C.acc, C.accw, { strokeWidth: 3 });
  text(490, 475, 'desired = actual ?', 22, C.acc, { width: 180, align: 'center' });
  arrow([[310, 345], [405, 210]], C.warn);
  arrow([[645, 210], [755, 210]], C.acc);
  arrow([[1005, 210], [1160, 290]], C.acc);
  arrow([[1205, 400], [1005, 575]], C.ok);
  arrow([[755, 575], [690, 500]], C.acc);
  arrow([[470, 500], [310, 400], [195, 400]], C.acc, { elbowed: true });
  text(470, 650, 'ลูปนี้ทำงานตลอดเวลา ไม่ต้องมีคนนั่งเฝ้า', 24, C.ok, { width: 520, align: 'center' });
  save(s);
}

{
  const s = scene('d05-labels-and-selectors', 'Labels และ selectors คือกาวของ Kubernetes', 'อ้างคุณสมบัติ ไม่อ้างชื่อหรือ IP — สมาชิกเปลี่ยนได้ทันที');
  const { zone, pod, card, text, arrow, rect } = s;
  zone(55, 140, 1290, 570, 'namespace · lab005', { fill: C.white, stroke: C.rule });
  card(90, 210, 300, 88, 'selector\napp=web, version=v2', 'warn');
  arrow([[390, 254], [475, 254]], C.warn);
  rect(470, 175, 420, 455, C.warn, C.warnw, { strokeWidth: 3, strokeStyle: 'dashed', opacity: 45 });
  text(500, 190, 'กลุ่มที่ selector จับได้', 22, C.warn);
  pod(510, 270, 'web-b', 'app=web · version=v2');
  pod(700, 440, 'web-c', 'app=web · version=v2');
  pod(940, 270, 'web-a', 'app=web · version=v1');
  pod(1130, 440, 'worker-x', 'app=worker · version=v2');
  card(930, 585, 350, 70, 'ชื่อ/IP เปลี่ยนได้\nlabel ยังบอกบทบาทเดิม', 'ok');
  save(s);
}

{
  const s = scene('d06-deployment-rs-pod', 'สามชั้น: Deployment → ReplicaSet → Pod', 'Deployment ดูแลการเปลี่ยนเวอร์ชัน · ReplicaSet ดูแลจำนวน · Pod รันแอป');
  const { deployment, rs, pod, card, text, arrow } = s;
  deployment(580, 140, 'web', 'replicas: 3');
  arrow([[700, 234], [410, 330]], C.acc);
  arrow([[700, 234], [990, 330]], C.acc);
  rs(290, 330, 'web-a1b2', 'v1 · replicas 0');
  rs(885, 330, 'web-c3d4', 'v2 · replicas 3');
  card(235, 470, 320, 84, 'เก็บไว้เป็น revision\nพร้อม rollback', 'neutral');
  arrow([[990, 418], [770, 525]], C.acc);
  arrow([[990, 418], [990, 525]], C.acc);
  arrow([[990, 418], [1210, 525]], C.acc);
  pod(680, 525, 'web-c3d4-a', 'v2');
  pod(900, 525, 'web-c3d4-b', 'v2');
  pod(1120, 525, 'web-c3d4-c', 'v2');
  text(560, 680, 'rollout: scale RS ใหม่ขึ้น · scale RS เก่าลง', 24, C.ok, { width: 580, align: 'center' });
  save(s);
}

{
  const s = scene('d07-rolling-vs-recreate', 'RollingUpdate เทียบกับ Recreate', 'ดูจำนวน Pod ที่ “พร้อมรับงาน” ในแต่ละช่วงเวลา');
  const { zone, card, text, arrow } = s;
  zone(55, 150, 1290, 245, 'Recreate · ปิดของเก่าก่อนเปิดของใหม่', { fill: C.critw, stroke: C.crit });
  const xs = [105, 395, 685, 975];
  const statesR = ['v1  v1  v1', 'หยุดทั้งหมด', 'v2', 'v2  v2  v2'];
  xs.forEach((x, i) => card(x, 245, 220, 82, statesR[i], i === 1 ? 'crit' : (i < 2 ? 'neutral' : 'pod')));
  for (let i=0;i<3;i++) arrow([[xs[i]+220,286],[xs[i+1]-20,286]], C.crit);
  text(455, 340, 'มีช่วง downtime: พร้อมรับงาน = 0', 22, C.crit, { width: 500, align: 'center' });

  zone(55, 430, 1290, 280, 'RollingUpdate · ค่อย ๆ แทนทีละส่วน', { fill: C.okw, stroke: C.ok });
  const statesG = ['v1  v1  v1', 'v1  v1  v2', 'v1  v2  v2', 'v2  v2  v2'];
  xs.forEach((x, i) => card(x, 525, 220, 82, statesG[i], i === 0 ? 'neutral' : 'ok'));
  for (let i=0;i<3;i++) arrow([[xs[i]+220,566],[xs[i+1]-20,566]], C.ok);
  text(450, 625, 'มี Pod พร้อมรับงานตลอด · ของเก่ายังอยู่จนของใหม่ Ready', 22, C.ok, { width: 620, align: 'center' });
  save(s);
}

{
  const s = scene('d08-learning-loop', 'วงจรเรียนรู้ประจำทุกแล็บ', 'ทุกขั้นต้องอ้างอิงหลักฐานจากระบบจริง');
  const { ellipse, text, arrow } = s;
  const nodes = [
    [600,150,'1 · ทายผล',C.warn,C.warnw], [940,250,'2 · รัน',C.acc,C.accw],
    [940,500,'3 · สังเกต',C.ok,C.okw], [600,610,'4 · อธิบาย',C.acc,C.accw],
    [250,500,'5 · ทำให้พัง',C.crit,C.critw], [250,250,'6 · แก้กลับ',C.ok,C.okw]
  ];
  nodes.forEach(([x,y,v,st,fi]) => { ellipse(x,y,220,90,st,fi,{strokeWidth:3}); text(x+10,y+24,v,22,C.ink,{width:200,align:'center'}); });
  arrow([[790,220],[970,270]], C.acc, { strokeWidth: 3 });
  arrow([[1050,340],[1050,500]], C.acc, { strokeWidth: 3 });
  arrow([[970,570],[790,635]], C.acc, { strokeWidth: 3 });
  arrow([[630,635],[450,570]], C.acc, { strokeWidth: 3 });
  arrow([[360,500],[360,340]], C.ok, { strokeWidth: 3 });
  arrow([[450,270],[630,220]], C.acc, { strokeWidth: 3 });
  ellipse(535,335,330,170,C.ink,C.white,{strokeWidth:3});
  text(565,375,'หลักฐานจริง\nkubectl · หน้าเว็บ · logs/events',22,C.ink,{width:270,align:'center'});
  save(s);
}

{
  const s = scene('lab001-architecture', 'Lab 001 · รู้จัก Kubernetes cluster', 'แล็บนี้ยังไม่รัน SkillSpace — ตรวจ cluster, node และ load image เข้า node เท่านั้น');
  const { zone, card, text, arrow } = s;
  card(55, 245, 190, 85, 'kubectl / k9s\nในเครื่องเรียน', 'dark');
  zone(350, 140, 995, 570, 'kind cluster · devtools', { fill: C.white, stroke: C.acc });
  zone(390, 195, 915, 135, 'devtools-control-plane · ingress-nginx', { fill: C.accw, stroke: C.acc });
  card(430, 245, 180, 60, 'API server', 'deployment');
  card(645, 245, 180, 60, 'scheduler', 'pod');
  card(860, 245, 180, 60, 'controller', 'pod');
  card(1075, 245, 180, 60, 'etcd', 'dark');
  zone(390, 365, 430, 275, 'devtools-worker', { fill: C.white, stroke: C.rule });
  zone(875, 365, 430, 275, 'devtools-worker2', { fill: C.white, stroke: C.rule });
  card(430, 430, 350, 72, 'system Pods\nkube-system / metrics-server', 'neutral');
  card(915, 430, 350, 72, 'system Pods\nkube-system', 'neutral');
  card(430, 540, 350, 70, 'image cache\nk8s-lab-* ทั้ง 4 images', 'warn');
  card(915, 540, 350, 70, 'image cache\nk8s-lab-* ทั้ง 4 images', 'warn');
  text(60, 385, 'kind load\ndocker-image', 22, C.warn, { width: 180, align: 'center' });
  arrow([[245,288],[350,288],[430,275]],C.acc,{elbowed:true});
  arrow([[240,430],[350,430],[350,575],[430,575]],C.warn,{elbowed:true});
  save(s);
}

{
  const s = scene('lab002-architecture', 'Lab 002 · kubectl และ namespace', 'ทุกอย่างคือ object; namespace แบ่ง “ห้อง” แต่ Node/Namespace เป็น cluster-scoped');
  const { zone, card, text, arrow, pod } = s;
  card(55, 255, 220, 90, 'kubectl\nget / describe / explain', 'dark');
  arrow([[275,300],[375,300]],C.acc);
  zone(375, 140, 965, 560, 'Kubernetes API', { fill: C.white, stroke: C.acc });
  card(420, 190, 245, 80, 'Cluster-scoped\nNode · Namespace', 'deployment');
  card(710, 190, 245, 80, 'API object\napiVersion · kind', 'neutral');
  card(1000, 190, 295, 80, 'metadata · spec · status', 'neutral');
  zone(420, 330, 260, 300, 'namespace · default', { fill: C.white, stroke: C.rule });
  text(455, 455, 'ไม่มี Pod\nในห้องนี้', 22, C.ink2, { width: 190, align: 'center' });
  zone(720, 330, 260, 300, 'namespace · lab002', { fill: C.accw, stroke: C.acc });
  text(755, 455, 'สร้างห้องแล้ว\nยังไม่มี Pod', 22, C.acc, { width: 190, align: 'center' });
  zone(1020, 330, 275, 300, 'namespace · kube-system', { fill: C.white, stroke: C.rule });
  pod(1065, 420, 'system Pod', 'Running');
  save(s);
}

{
  const s = scene('lab003-architecture', 'Lab 003 · Pod คือหน่วยเล็กที่สุด', 'ไม่มี Service/Deployment — Browser แอบดู Pod เดียวผ่าน port-forward');
  const { zone, browser, pod, card, text, arrow, rect } = s;
  browser(45, 270, 245, 120, 'localhost:3000');
  zone(430, 145, 900, 545, 'namespace · lab003', { fill: C.white, stroke: C.rule });
  zone(470, 205, 820, 405, 'Worker node', { fill: C.white, stroke: C.rule });
  pod(520, 300, 'web', 'container: web');
  rect(760, 260, 330, 190, C.acc, C.accw, { strokeWidth: 3 });
  text(780, 275, 'Pod · web2', 22, C.acc);
  card(790, 335, 125, 80, 'web', 'pod');
  card(935, 335, 125, 80, 'sidecar', 'pod');
  arrow([[935,375],[915,375]],C.ok);
  card(1110, 300, 145, 105, 'web-broken\nImagePullBackOff', 'crit');
  card(585, 520, 580, 60, 'web + sidecar แชร์ localhost ใน Pod เดียวกัน', 'ok');
  arrow([[290,330],[430,330],[520,352]],C.acc,{elbowed:true});
  text(305, 290, 'port-forward', 20, C.acc);
  save(s);
}

{
  const s = scene('lab004-architecture', 'Lab 004 · ประกาศ desired state ด้วย YAML', 'apply ไฟล์เดิมซ้ำได้; Pod เปลี่ยน image v1 → v2 แต่ field บางอย่าง immutable');
  const { zone, browser, pod, card, text, arrow } = s;
  card(50, 215, 240, 100, '01-pod.yaml\napiVersion · kind\nmetadata · spec', 'warn');
  zone(390, 145, 940, 540, 'namespace · lab004', { fill: C.white, stroke: C.rule });
  card(440, 210, 230, 80, 'API server\nเก็บ desired state', 'deployment');
  arrow([[670,250],[790,340]],C.acc);
  pod(790, 300, 'web', 'image: v1 → v2');
  browser(1040, 275, 245, 120, 'localhost:3000');
  arrow([[1040,335],[970,350]],C.acc);
  text(1010, 415, 'port-forward ตรงสู่ Pod', 20, C.acc, { width: 280, align: 'center' });
  card(490, 480, 330, 95, 'desired state\nอยู่ในไฟล์ที่เก็บใน Git ได้', 'warn');
  card(870, 480, 330, 95, 'actual + status\nKubernetes เขียนกลับ', 'ok');
  arrow([[820,528],[870,528]],C.ink2,{startArrowhead:'arrow'});
  arrow([[290,265],[390,265],[440,250]],C.warn,{elbowed:true});
  text(325, 225, 'apply', 20, C.warn);
  save(s);
}

{
  const s = scene('lab005-architecture', 'Lab 005 · Labels จับกลุ่ม Pod', 'สาม Pod ถูกสร้างตรง ๆ — selector ทำงานกับ label โดยไม่อ้างชื่อหรือ IP');
  const { zone, card, pod, arrow, rect, text } = s;
  card(55, 245, 265, 95, 'kubectl -l\napp=web,version=v2', 'dark');
  arrow([[320,292],[420,292]],C.warn);
  zone(420, 145, 910, 540, 'namespace · lab005', { fill: C.white, stroke: C.rule });
  rect(465, 205, 500, 390, C.warn, C.warnw, { strokeWidth: 3, strokeStyle: 'dashed', opacity: 45 });
  text(490, 220, 'selector: version=v2', 22, C.warn);
  pod(510, 310, 'web-b', 'app=web · version=v2');
  pod(735, 430, 'web-c', 'app=web · version=v2');
  pod(1040, 310, 'web-a', 'app=web · version=v1');
  card(1020, 485, 245, 80, 'label เปลี่ยน\nสมาชิกกลุ่มเปลี่ยนทันที', 'ok');
  save(s);
}

{
  const s = scene('lab006-architecture', 'Lab 006 · ReplicaSet และ self-healing', 'ไม่มี Deployment — ReplicaSet ถือ desired replicas = 3 และสร้าง Pod ใหม่เมื่อสมาชิกหาย');
  const { zone, browser, ingress, service, rs, pod, arrow, text, rect } = s;
  browser(35, 300, 235, 120, 'localhost:8080');
  zone(350, 135, 1010, 590, 'namespace · lab006', { fill: C.white, stroke: C.rule });
  ingress(395, 185, 'Ingress · path /');
  arrow([[605,229],[700,229]],C.ok);
  service(700, 185, 'web', 'ClusterIP :3000');
  text(700, 150, 'เขียว = traffic', 20, C.ok);
  rs(1020, 185, 'web', 'desired = 3');
  text(1040, 150, 'น้ำเงิน = owner', 20, C.acc);
  rect(540, 395, 720, 175, C.ok, 'transparent', { strokeWidth: 3, strokeStyle: 'dashed' });
  text(560, 400, 'selector: app=web', 20, C.ok);
  arrow([[1125,273],[660,430]],C.acc);
  arrow([[1125,273],[890,430]],C.acc);
  arrow([[1125,273],[1120,430]],C.acc);
  arrow([[900,229],[900,350],[540,395]],C.ok,{elbowed:true});
  pod(570, 430, 'web-abcde', 'v1');
  pod(800, 430, 'web-fghij', 'v1');
  pod(1030, 430, 'web-klmno', 'v1');
  text(540, 585, 'ลบ 1 Pod', 22, C.crit);
  arrow([[650,610],[800,610]],C.acc);
  text(820, 585, 'ReplicaSet สร้าง Pod ชื่อใหม่ให้ครบ 3', 22, C.ok);
  arrow([[270,360],[320,360],[320,229],[395,229]],C.warn,{elbowed:true});
  save(s);
}

{
  const s = scene('lab007-architecture', 'Lab 007 · Deployment จัดการ rollout และ rollback', 'Browser เข้าผ่านประตูเดิม; Deployment ค่อย ๆ ย้าย replicas จาก RS v1 ไป RS v2');
  const { zone, browser, ingress, service, deployment, rs, pod, arrow, text, rect } = s;
  browser(25, 310, 225, 120, 'localhost:8080');
  zone(325, 125, 1035, 620, 'namespace · lab007', { fill: C.white, stroke: C.rule });
  ingress(370, 180, 'Ingress · path /');
  arrow([[580,224],[645,224]],C.ok);
  service(645, 180, 'web', 'ClusterIP :3000');
  deployment(940, 170, 'web', 'replicas: 3');
  arrow([[1060,264],[815,340]],C.acc);
  arrow([[1060,264],[1105,340]],C.acc);
  rs(700, 340, 'web-old', 'v1 · scale down');
  rs(1000, 340, 'web-new', 'v2 · scale up');
  arrow([[1105,428],[760,545]],C.acc);
  arrow([[1105,428],[995,545]],C.acc);
  arrow([[1105,428],[1230,545]],C.acc);
  rect(640, 510, 700, 170, C.ok, 'transparent', { strokeWidth: 3, strokeStyle: 'dashed' });
  text(655, 480, 'Service selector: app=web', 20, C.ok);
  arrow([[845,268],[620,268],[620,490],[640,510]],C.ok,{elbowed:true});
  pod(670, 545, 'web-v2-a', 'Ready');
  pod(905, 545, 'web-v2-b', 'Ready');
  pod(1140, 545, 'web-v2-c', 'Ready');
  text(420, 700, 'rollback ใช้ RS เก่าที่เก็บไว้ · Service ส่ง traffic เฉพาะ Pod ที่พร้อม', 22, C.ok, { width: 850, align: 'center' });
  arrow([[250,370],[300,370],[300,224],[370,224]],C.warn,{elbowed:true});
  save(s);
}

for (const [name, elements] of Object.entries(diagrams)) {
  fs.writeFileSync(path.join(OUT, `${name}.json`), JSON.stringify(elements, null, 2) + '\n');
}

console.log(`generated ${Object.keys(diagrams).length} element files`);
