import fs from 'node:fs';
import path from 'node:path';

const OUT = '/root/workspace/DevTools/05_kubernetes/.work/diagram-src-s2';
fs.mkdirSync(OUT, { recursive: true });

const C = { acc:'#1c5cab', ok:'#116b11', warn:'#86590a', crit:'#a32222', ink:'#18181b', accw:'#eaf2fd', okw:'#e7f6e7', warnw:'#fdf3dd', critw:'#fbeaea', rule:'#d4d4d8', wash:'#f4f4f5', white:'#ffffff' };
const base = { roughness:0, fillStyle:'solid', strokeWidth:2, opacity:100 };
let seq = 0;
const id = (p='e') => `${p}-${++seq}`;
const bg = () => ({ id:id('bg'), type:'rectangle', x:0, y:0, width:1480, height:820, strokeColor:C.white, backgroundColor:C.white, ...base });
const text = (x,y,s,size=20,color=C.ink,w=1200,align='left') => ({ id:id('t'), type:'text', x,y,width:w,height:Math.ceil(size*1.5*(String(s).split('\n').length)), text:s,fontSize:size,fontFamily:'helvetica',textAlign:align,verticalAlign:'middle',strokeColor:color,backgroundColor:'transparent',roughness:0 });
const rect = (x,y,w,h,label='',stroke=C.acc,fill=C.accw,opts={}) => ({ id:opts.id||id('r'), type:'rectangle', x,y,width:w,height:h,text:label,fontSize:opts.fontSize||20,fontFamily:'helvetica',textAlign:'center',verticalAlign:'middle',strokeColor:stroke,backgroundColor:fill,strokeStyle:opts.dashed?'dashed':'solid',roundness:{type:3},...base,strokeWidth:opts.strokeWidth||2 });
const ellipse = (x,y,w,h,label='',stroke=C.acc,fill=C.accw,opts={}) => ({ id:opts.id||id('el'), type:'ellipse',x,y,width:w,height:h,text:label,fontSize:opts.fontSize||20,fontFamily:'helvetica',textAlign:'center',verticalAlign:'middle',strokeColor:stroke,backgroundColor:fill,...base,strokeWidth:opts.strokeWidth||2 });
const arrow = (a,b,color=C.ink,opts={}) => ({ id:opts.id||id('a'), type:'arrow',x:0,y:0,startElementId:a,endElementId:b,strokeColor:color,backgroundColor:'transparent',strokeWidth:opts.strokeWidth||3,roughness:0,endArrowhead:'arrow',startArrowhead:opts.both?'arrow':null,strokeStyle:opts.dashed?'dashed':'solid' });
const freeArrow = (x,y,pts,color=C.ink,opts={}) => ({ id:opts.id||id('a'), type:'arrow',x,y,points:pts,strokeColor:color,backgroundColor:'transparent',strokeWidth:opts.strokeWidth||3,roughness:0,endArrowhead:'arrow',startArrowhead:opts.both?'arrow':null,strokeStyle:opts.dashed?'dashed':'solid',roundness:opts.curve?{type:2}:null,elbowed:!!opts.elbowed });
const title = s => text(44,24,s,32,C.ink,1360);
const subtitle = s => text(46,68,s,20,'#52525b',1360);
const zone = (x,y,w,h,label='namespace',stroke=C.rule) => [
  rect(x,y,w,h,'',stroke,C.white,{dashed:true,id:id('zone')}),
  text(x+18,y+10,label,20,C.ink,w-36)
];
const browser = (x,y,w=210,h=92,label='Browser') => {
  const outer=rect(x,y,w,h,'',C.ink,C.white,{id:id('browser')});
  const bar=rect(x,y,w,26,'',C.ink,C.wash,{id:id('bar')}); bar.roundness={type:3};
  const body=rect(x+8,y+32,w-16,h-40,label,C.ink,C.white,{id:id('browser-label'),fontSize:20}); body.strokeWidth=0;
  return [outer,bar,text(x+14,y+3,'●  ●  ●',20,'#71717a',w-28),body];
};
const pod = (x,y,w,h,label,opts={}) => rect(x,y,w,h,label,opts.crit?C.crit:C.acc,opts.crit?C.critw:C.accw,{id:opts.id||id('pod'),fontSize:opts.fontSize||20,strokeWidth:opts.strokeWidth||2});
const svc = (x,y,w,h,label,opts={}) => rect(x,y,w,h,label,C.ok,C.okw,{id:opts.id||id('svc'),fontSize:opts.fontSize||20});
const ingress = (x,y,w,h,label='Ingress') => rect(x,y,w,h,label,C.warn,C.warnw,{id:id('ing'),fontSize:20});
const config = (x,y,w,h,label='ConfigMap') => rect(x,y,w,h,label,C.warn,C.warnw,{id:id('cfg'),fontSize:20});
const secret = (x,y,w,h,label='Secret') => rect(x,y,w,h,label,C.warn,C.warnw,{id:id('sec'),fontSize:20,strokeWidth:3});
const pvc = (x,y,w,h,label='PVC') => rect(x,y,w,h,label,C.acc,C.white,{id:id('pvc'),fontSize:20,strokeWidth:4});
const deployStack = (x,y,w,h,name,pods=1,opts={}) => {
  const dep=rect(x,y,w,h,'',C.acc,C.white,{id:id('dep')});
  const rs=rect(x+18,y+42,w-36,h-60,'',C.acc,C.accw,{id:id('rs')});
  const els=[dep,text(x+14,y+8,`Deployment ${name}`,20,C.acc,w-28),rs,text(x+34,y+48,`ReplicaSet ${name}`,20,C.acc,w-68)];
  const gap=12, py=y+88, ph=h-112, pw=(w-60-gap*(pods-1))/pods;
  for(let i=0;i<pods;i++) els.push(pod(x+30+i*(pw+gap),py,pw,ph,`Pod ${name}${pods>1?` ${i+1}`:''}`));
  return { els, dep:dep.id, rs:rs.id, pods:els.filter(e=>e.id?.startsWith('pod-')).map(e=>e.id) };
};
const write = (name, els) => fs.writeFileSync(path.join(OUT, `${name}.json`), JSON.stringify(els,null,2)+'\n');

// d01 — ephemeral Pod IP versus stable Service DNS.
{
  const els=[bg(),title('Pod IP เปลี่ยนได้ — Service ให้ชื่อคงที่'),subtitle('อย่าผูกแอปกับ IP ของ Pod โดยตรง ให้เรียกผ่าน DNS ของ Service')];
  els.push(...zone(42,112,660,640,'ทางที่เปราะบาง: เรียก Pod IP โดยตรง',C.crit));
  const w=pod(90,246,190,100,'Pod web'); const old=pod(458,194,190,100,'Pod api\n10.244.1.7',{crit:true}); const dead=rect(508,320,90,48,'ถูกลบ',C.crit,C.critw,{fontSize:20}); const neu=pod(458,436,190,100,'Pod api ใหม่\n10.244.2.9');
  els.push(w,old,dead,neu,arrow(w.id,old.id,C.crit),freeArrow(552,296,[[0,0],[0,22]],C.crit),text(316,172,'web จำ IP เก่า',20,C.crit,220),text(316,540,'IP ใหม่ — web ไม่รู้จัก',20,C.crit,300));
  els.push(...zone(742,112,696,640,'ทางที่ทนทาน: เรียกชื่อ Service',C.ok));
  const w2=pod(790,300,190,100,'Pod web'); const s=svc(1050,300,190,100,'Service api\nDNS: api'); const p1=pod(1255,198,150,92,'Pod api 1'), p2=pod(1255,422,150,92,'Pod api 2');
  els.push(w2,s,p1,p2,arrow(w2.id,s.id,C.ok),arrow(s.id,p1.id,C.ok),arrow(s.id,p2.id,C.ok),text(812,448,'เรียก http://api:8000',20,C.ok,300),text(1055,552,'Service อัปเดต Endpoints ตาม label',20,C.ok,340));
  write('d01-pod-ip-changes',els);
}

// d02 — Service exposure types.
{
  const els=[bg(),title('Service Types — ต่างกันที่ใครเข้าถึงได้'),subtitle('จากซ้ายไปขวา: ภายใน cluster → เปิดพอร์ตบน node → cloud → ประตู HTTP เดียว')];
  const cols=[
    {x:40,n:'ClusterIP',c:C.ok,f:C.okw,who:'เฉพาะ Pod ใน cluster',flow:['Pod client','Service','Pod api']},
    {x:395,n:'NodePort',c:C.acc,f:C.accw,who:'คนนอกผ่าน <NodeIP>:30080',flow:['Client','ทุก Node :30080','Service → Pod']},
    {x:750,n:'LoadBalancer',c:C.warn,f:C.warnw,who:'ผู้ใช้ผ่าน External IP',flow:['Internet','Cloud LB','Service → Pod']},
    {x:1105,n:'Ingress',c:C.warn,f:C.warnw,who:'ผู้ใช้ผ่าน host/path',flow:['Browser :80/443','Ingress rules','หลาย Service']}
  ];
  for(const q of cols){ els.push(rect(q.x,134,320,570,'',q.c,C.white,{id:id('col')}),text(q.x+24,154,q.n,28,q.c,270),text(q.x+24,202,q.who,20,C.ink,270)); let prev=null; q.flow.forEach((v,i)=>{const e=rect(q.x+55,282+i*126,210,78,v,q.c,q.f,{id:id('flow'),fontSize:20});els.push(e);if(prev)els.push(arrow(prev.id,e.id,q.c));prev=e;}); }
  els.push(text(88,734,'ค่าเริ่มต้น',20,C.ok,250),text(438,734,'ทดสอบ/ห้องเรียน',20,C.acc,250),text(790,734,'เมื่อ cloud จัดให้',20,C.warn,250),text(1150,734,'L7: path / host / TLS',20,C.warn,250));
  write('d02-service-types',els);
}

// d03 — one image, external configuration per deployment.
{
  const els=[bg(),title('Image เดียว — Config อยู่นอก Image'),subtitle('build ครั้งเดียว แล้ว inject ConfigMap / Secret ตามสภาพแวดล้อมตอน deploy')];
  const img=rect(555,118,370,92,'image: k8s-lab-web:v1',C.acc,C.accw,{id:id('image'),fontSize:24}); els.push(img);
  const envs=[{x:70,name:'ฝ่ายซ่อม',theme:'SITE_NAME=ศูนย์ซ่อม\nTHEME=amber'},{x:530,name:'ห้องสมุด',theme:'SITE_NAME=ระบบยืมคืน\nTHEME=blue'},{x:990,name:'ห้องปฏิบัติการ',theme:'SITE_NAME=คลังอุปกรณ์\nTHEME=rose'}];
  const deps=[];
  for(const e of envs){ const cm=config(e.x,300,280,100,`ConfigMap\n${e.theme}`), sec=secret(e.x,428,280,82,'Secret\nค่าลับของ environment'), dep=rect(e.x,570,280,110,`Deployment ${e.name}\nใช้ image เดิม`,C.acc,C.accw,{id:id('dep'),fontSize:20}); deps.push(dep); els.push(cm,sec,dep,arrow(cm.id,dep.id,C.warn),arrow(sec.id,dep.id,C.warn)); }
  els.push(freeArrow(700,216,[[0,0],[-650,0],[-650,409],[-630,409]],C.acc,{elbowed:true}),freeArrow(740,216,[[0,0],[-240,0],[-240,409],[-210,409]],C.acc,{elbowed:true}),freeArrow(780,216,[[0,0],[550,0],[550,409],[490,409]],C.acc,{elbowed:true}));
  els.push(text(448,724,'เปลี่ยน config ไม่ต้อง rebuild image',24,C.ok,580,'center'));
  write('d03-config-outside-image',els);
}

// d04 — Secret stringData pipeline.
{
  const els=[bg(),title('Secret: base64 คือการแปลงรูป ไม่ใช่การเข้ารหัส'),subtitle('Kubernetes รับ stringData แล้วเก็บเป็น data แบบ base64 — เมื่อ inject เข้า Pod จะเห็นค่าจริง')];
  const a=rect(70,240,310,210,'Secret YAML\n\nstringData:\n  POSTGRES_PASSWORD:\n  labpass',C.warn,C.warnw,{id:id('step'),fontSize:20});
  const b=rect(585,240,310,210,'API server เก็บเป็น data\n\nPOSTGRES_PASSWORD:\n  bGFicGFzcw==',C.warn,C.white,{id:id('step'),fontSize:20});
  const c=pod(1100,240,310,210,'Pod api / db\n\nenv: POSTGRES_PASSWORD\nค่าใน process = labpass');
  els.push(a,b,c,arrow(a.id,b.id,C.warn),arrow(b.id,c.id,C.acc),text(402,320,'encode base64',20,C.warn,170,'center'),text(918,320,'inject / decode',20,C.acc,170,'center'));
  const cmd=rect(395,548,690,96,'echo bGFicGFzcw== | base64 -d   →   labpass',C.crit,C.critw,{id:id('warn'),fontSize:24});els.push(cmd,text(420,678,'ถอดกลับได้ในคำสั่งเดียว — ความปลอดภัยต้องมาจาก RBAC + encryption at rest',22,C.crit,650,'center'));
  write('d04-secret-base64',els);
}

// d05 — writable layer, emptyDir, PVC/PV.
{
  const els=[bg(),title('ข้อมูลอยู่รอดแค่ไหน? Container FS → emptyDir → PVC'),subtitle('อายุของข้อมูลขึ้นกับชั้นที่เราเลือกเก็บ')];
  const cards=[{x:40,head:'Container filesystem',stroke:C.crit,fill:C.critw,items:['image layers (read-only)','writable layer','Pod ใหม่ → หาย'],foot:'รอด: container เดิมเท่านั้น'}, {x:510,head:'emptyDir',stroke:C.warn,fill:C.warnw,items:['Pod มี volume ชั่วคราว','container restart → ยังอยู่','Pod ใหม่ → หาย'],foot:'รอด: ภายใน Pod เดิม'}, {x:980,head:'PVC → PV',stroke:C.ok,fill:C.okw,items:['Pod mount PVC','PVC ผูกกับ PV ภายนอก','Pod ใหม่ → ยังอยู่'],foot:'รอด: ข้ามการเกิดใหม่ของ Pod'}];
  for(const c of cards){els.push(rect(c.x,140,420,570,'',c.stroke,C.white,{id:id('card')}),text(c.x+28,164,c.head,28,c.stroke,364,'center')); const i1=rect(c.x+70,250,280,72,c.items[0],C.acc,C.accw,{id:id('layer')}),i2=rect(c.x+70,350,280,72,c.items[1],c.stroke,c.fill,{id:id('layer')}),i3=rect(c.x+70,450,280,72,c.items[2],c.stroke,c.fill,{id:id('layer')});els.push(i1,i2,i3,arrow(i1.id,i2.id,c.stroke),arrow(i2.id,i3.id,c.stroke),text(c.x+50,624,c.foot,22,c.stroke,320,'center'));}
  els.push(text(82,744,'เร็วและชั่วคราว',20,C.crit,330,'center'),text(552,744,'แชร์ใน Pod ได้',20,C.warn,330,'center'),text(1022,744,'เหมาะกับฐานข้อมูล',20,C.ok,330,'center'));
  write('d05-container-fs-vs-volume',els);
}

// d06 — readiness versus liveness.
{
  const els=[bg(),title('Readiness vs Liveness — สองคำถาม สองผลลัพธ์'),subtitle('Probe ต้องตอบให้ตรงเรื่อง: พร้อมรับงานหรือยัง? หรือ process ยังมีชีวิตไหม?')];
  const left=rect(55,134,655,610,'',C.ok,C.white,{id:id('panel')}); const right=rect(770,134,655,610,'',C.crit,C.white,{id:id('panel')}); els.push(left,right);
  els.push(text(105,166,'readinessProbe',30,C.ok,560),text(105,214,'“ตอนนี้รับงานได้ไหม?”',22,C.ink,560));
  const rp=pod(110,300,210,100,'Pod api\nRunning · 0/1'); const ep=svc(445,300,210,100,'Service api\nEndpoints'); els.push(rp,ep,arrow(rp.id,ep.id,C.crit,{dashed:true}),text(110,438,'FAIL: ถอด Pod ออกจาก Service',22,C.crit,540),text(110,506,'PASS: ใส่กลับเอง\nไม่ restart container',20,C.ok,540));
  els.push(text(820,166,'livenessProbe',30,C.crit,560),text(820,214,'“process ยังมีชีวิตไหม?”',22,C.ink,560));
  const lp=pod(830,300,210,100,'Pod api\nprocess ค้าง',{crit:true}); const rst=rect(1165,300,210,100,'kubelet\nrestart container',C.crit,C.critw,{id:id('restart'),fontSize:20}); els.push(lp,rst,arrow(lp.id,rst.id,C.crit),text(830,438,'FAIL: ฆ่าและเริ่ม container ใหม่',22,C.crit,540),text(830,506,'อย่าเช็ก dependency ภายนอก\nเช่น db ใน liveness',20,C.warn,540));
  write('d06-readiness-vs-liveness',els);
}

// d07 — in-cluster request path.
{
  const els=[bg(),title('เส้นทาง Request ภายใน Cluster: web → api → db'),subtitle('Service ให้ชื่อคงที่ ส่วน Pod ที่รับงานเปลี่ยนได้ตลอด')];
  els.push(...zone(42,118,1396,620,'namespace: lab0NN'));
  const b=browser(72,332,190,96,'Browser\nlocalhost:8080'); const ing=ingress(310,332,180,96,'Ingress\npath /'); const sw=svc(540,332,180,96,'Service web\n:3000'); const pw=pod(770,332,180,96,'Pod web'); const sa=svc(1000,220,180,96,'Service api\n:8000'); const pa=pod(1230,220,170,96,'Pod api'); const sd=svc(1000,476,180,96,'Service db\n:5432'); const pd=pod(1230,476,170,96,'Pod db');
  els.push(...b,ing,sw,pw,sa,pa,sd,pd,arrow(b[0].id,ing.id,C.warn),arrow(ing.id,sw.id,C.warn),arrow(sw.id,pw.id,C.ok),arrow(pw.id,sa.id,C.acc),arrow(sa.id,pa.id,C.ok),arrow(pa.id,sd.id,C.acc),arrow(sd.id,pd.id,C.ok));
  els.push(text(998,164,'HTTP API',20,C.acc,180,'center'),text(998,590,'PostgreSQL',20,C.acc,180,'center'),text(730,610,'ตอบกลับย้อนเส้นทางเดิม',22,C.ok,360,'center'));
  write('d07-request-path-web-api-db',els);
}

// d08 — learning loop.
{
  const els=[bg(),title('วงจรการเรียนรู้: ทาย → ลงมือ → อธิบาย → แก้กลับ'),subtitle('ทุกแล็บวนครบหนึ่งรอบ เพื่อเปลี่ยนคำสั่งให้เป็นความเข้าใจ')];
  const nodes=[{x:590,y:132,t:'1  ทายผล',c:C.warn,f:C.warnw},{x:980,y:230,t:'2  รันคำสั่ง',c:C.acc,f:C.accw},{x:980,y:500,t:'3  สังเกต',c:C.ok,f:C.okw},{x:590,y:620,t:'4  อธิบาย',c:C.acc,f:C.accw},{x:200,y:500,t:'5  ทำให้พัง',c:C.crit,f:C.critw},{x:200,y:230,t:'6  แก้กลับ',c:C.ok,f:C.okw}];
  nodes.forEach(n=>{n.e=ellipse(n.x,n.y,240,96,n.t,n.c,n.f,{id:id('loop'),fontSize:22});els.push(n.e);}); for(let i=0;i<nodes.length;i++)els.push(arrow(nodes[i].e.id,nodes[(i+1)%nodes.length].e.id,nodes[(i+1)%nodes.length].c));
  els.push(ellipse(540,330,400,180,'แนวคิดหลัก\n“เพราะอะไร”',C.ink,C.white,{id:id('center'),fontSize:28,strokeWidth:3}));
  write('d08-learning-loop',els);
}

function archHeader(n,name,concept){ return [bg(),title(`Lab ${n} — ${name}`),subtitle(concept)]; }
function addThreeTier(els, nsLabel, options={}){
  els.push(...zone(230,122,1200,options.nsHeight||650,nsLabel));
  const br=browser(28,332,180,94,options.url||'localhost:8080'); els.push(...br);
  let entry=br[0];
  if(options.ingress!==false){const ig=ingress(254,332,150,94,'Ingress\npath /');els.push(ig,arrow(entry.id,ig.id,C.warn));entry=ig;}
  const sw=svc(options.ingress===false?260:440,332,150,94,options.webService||'Service web'); els.push(sw,arrow(entry.id,sw.id,C.ok));
  const web=deployStack(options.ingress===false?450:625,270,210,220,'web',options.webPods||1);els.push(...web.els,arrow(sw.id,web.pods[0],C.ok));
  if(options.api!==false){const sa=svc(880,206,150,82,'Service api'), api=deployStack(1070,146,320,210,'api',options.apiPods||1);els.push(sa,...api.els,arrow(web.pods[0],sa.id,C.acc),arrow(sa.id,api.pods[0],C.ok)); if(options.db!==false){const sd=svc(880,522,150,82,'Service db'), db=deployStack(1070,458,320,220,'db',1);els.push(sd,...db.els,arrow(api.pods[0],sd.id,C.acc),arrow(sd.id,db.pods[0],C.ok)); return {br,sw,web,sa,api,sd,db};} return {br,sw,web,sa,api};}
  return {br,sw,web};
}

// lab008 final state: web + api, no db.
{
  const els=archHeader('008','ทำไมต้องมี Service','Pod IP เปลี่ยน แต่ Service DNS “api” และ Endpoints ตาม Pod ให้เอง');
  els.push(...zone(250,122,1180,650,'namespace: lab008'));
  const br=browser(28,326,190,96,'localhost:8080'), ig=ingress(280,326,160,96,'Ingress\npath /'), sw=svc(490,326,160,96,'Service web'), web=deployStack(700,260,220,230,'web',1), sa=svc(980,326,160,96,'Service api\nDNS: api'), api=deployStack(1190,214,210,330,'api',2);
  els.push(...br,ig,sw,...web.els,sa,...api.els,arrow(br[0].id,ig.id,C.warn),arrow(ig.id,sw.id,C.ok),arrow(sw.id,web.pods[0],C.ok),arrow(web.pods[0],sa.id,C.acc),arrow(sa.id,api.pods[0],C.ok),freeArrow(1145,362,[[0,0],[35,-90],[190,-90],[190,-60]],C.ok,{elbowed:true}),text(962,578,'ไม่มี db ในแล็บนี้',20,C.crit,210,'center'));
  write('lab008-architecture',els);
}

// lab009 NodePort and ClusterIP.
{
  const els=archHeader('009','Service Types และการเข้าถึง','web เปิดด้วย NodePort; api เป็น ClusterIP และเรียกได้เฉพาะใน cluster');
  els.push(...zone(250,122,1180,650,'namespace: lab009'));
  const br=browser(28,326,190,96,'localhost:3000'), pf=rect(250,326,170,96,'port-forward\nsvc/web',C.ink,C.wash,{id:id('pf')}), sw=svc(470,300,190,148,'Service web\nNodePort 30080\nport 3000'), web=deployStack(710,230,260,290,'web',2), sa=svc(1020,326,150,96,'Service api\nClusterIP'), api=deployStack(1210,250,190,250,'api',1);
  els.push(...br,pf,sw,...web.els,sa,...api.els,arrow(br[0].id,pf.id,C.ink),arrow(pf.id,sw.id,C.ok),arrow(sw.id,web.pods[0],C.ok),freeArrow(665,440,[[0,0],[25,100],[237,100],[237,66]],C.ok,{elbowed:true}),arrow(web.pods[1],sa.id,C.acc),arrow(sa.id,api.pods[0],C.ok),text(438,550,'NodeIP:30080 เข้าได้ทุก node',20,C.acc,250,'center'),text(1000,650,'api ไม่เปิดออกนอก cluster',20,C.ok,210,'center'));
  write('lab009-architecture',els);
}

// lab010 ConfigMap + single web stack + door.
{
  const els=archHeader('010','แยก Config ออกจาก Image','ConfigMap inject SITE_NAME / THEME เข้า Deployment web ตอนสร้าง Pod');
  els.push(...zone(250,122,1180,650,'namespace: lab010'));
  const br=browser(28,326,190,96,'localhost:8080'), ig=ingress(300,326,180,96,'Ingress\npath /'), sw=svc(540,326,180,96,'Service web'), web=deployStack(820,250,300,260,'web',1), cm=config(850,590,240,110,'ConfigMap web-config\nSITE_NAME · THEME');
  els.push(...br,ig,sw,...web.els,cm,arrow(br[0].id,ig.id,C.warn),arrow(ig.id,sw.id,C.ok),arrow(sw.id,web.pods[0],C.ok),arrow(cm.id,web.pods[0],C.warn,{dashed:true}),text(1160,294,'image เดิม',22,C.acc,190,'center'),text(1148,342,'k8s-lab-web:v1',20,C.ink,220,'center'),text(828,728,'เปลี่ยน env → restart Pod เพื่ออ่านค่าใหม่',20,C.warn,300,'center'));
  write('lab010-architecture',els);
}

// lab011 full 3-tier, Secret, no PVC.
{
  const els=archHeader('011','Secret และระบบ 3 ชั้น','Secret ส่งรหัสผ่านให้ api และ db; ฐานข้อมูลยังเขียนลง container filesystem');
  const o=addThreeTier(els,'namespace: lab011',{apiPods:1});
  const sec=secret(650,660,230,78,'Secret db-secret');els.push(sec,freeArrow(650,680,[[0,0],[-400,0],[-400,-500],[720,-500],[720,-436]],C.warn,{dashed:true,elbowed:true}),freeArrow(880,705,[[0,0],[170,0],[170,-95],[220,-95]],C.warn,{dashed:true,elbowed:true}),text(900,748,'ยังไม่มี PVC',20,C.crit,300));
  write('lab011-architecture',els);
}

// lab012 full 3-tier with ephemeral/emptyDir storage.
{
  const els=archHeader('012','ทำไมข้อมูลหาย','db Pod ใหม่ = container ใหม่; emptyDir รอดแค่ container restart ใน Pod เดิม');
  const o=addThreeTier(els,'namespace: lab012',{apiPods:1});
  const sec=secret(630,680,210,68,'Secret db-secret'), ed=rect(1050,700,170,54,'emptyDir',C.warn,C.warnw,{id:id('vol'),fontSize:20}), lost=rect(1245,700,160,54,'Pod ถูกลบ → หาย',C.crit,C.critw,{id:id('lost'),fontSize:20}); els.push(sec,freeArrow(630,700,[[0,0],[-380,0],[-380,-520],[740,-520],[740,-456]],C.warn,{dashed:true,elbowed:true}),freeArrow(840,720,[[0,0],[190,0],[190,-105],[260,-105]],C.warn,{dashed:true,elbowed:true}),ed,lost,arrow(o.db.pods[0],ed.id,C.warn),arrow(ed.id,lost.id,C.crit));
  write('lab012-architecture',els);
}

// lab013 full 3-tier plus PVC/PV and Secret.
{
  const els=archHeader('013','Persistent Storage ด้วย PVC','db Pod ใหม่ mount claim เดิม → PV เดิม → ข้อมูลยังอยู่');
  const o=addThreeTier(els,'namespace: lab013',{apiPods:1,nsHeight:628});
  const sec=secret(630,670,210,68,'Secret db-secret'), claim=pvc(1045,680,145,58,'PVC db-data'), pv=pvc(1235,752,145,60,'PV\ncluster-scoped');els.push(sec,freeArrow(630,690,[[0,0],[-380,0],[-380,-510],[740,-510],[740,-446]],C.warn,{dashed:true,elbowed:true}),freeArrow(840,710,[[0,0],[190,0],[190,-95],[260,-95]],C.warn,{dashed:true,elbowed:true}),claim,pv,arrow(o.db.pods[0],claim.id,C.acc),arrow(claim.id,pv.id,C.ok));
  write('lab013-architecture',els);
}

// lab014 full system + PVC + probes on api.
{
  const els=archHeader('014','Running ไม่ได้แปลว่า Ready','readiness ถอด api จาก Service; liveness ให้ kubelet restart container');
  const o=addThreeTier(els,'namespace: lab014',{apiPods:2,nsHeight:628});
  const sec=secret(470,650,210,68,'Secret db-secret'), probes=rect(1060,376,330,64,'api probes: /ready · /health',C.warn,C.warnw,{id:id('probe'),fontSize:20}); const claim=pvc(1080,680,140,56,'PVC db-data'), pv=pvc(1260,752,120,60,'PV\ncluster-scoped'); els.push(sec,freeArrow(470,670,[[0,0],[-220,0],[-220,-490],[900,-490],[900,-426]],C.warn,{dashed:true,elbowed:true}),freeArrow(680,690,[[0,0],[350,0],[350,-75],[420,-75]],C.warn,{dashed:true,elbowed:true}),probes,freeArrow(1035,246,[[0,0],[45,-46],[263,-46],[263,34]],C.ok,{elbowed:true}),claim,pv,arrow(probes.id,o.api.pods[0],C.warn,{dashed:true}),arrow(probes.id,o.api.pods[1],C.warn,{dashed:true}),arrow(o.db.pods[0],claim.id,C.acc),arrow(claim.id,pv.id,C.ok),text(470,748,'readiness FAIL → Service api ไม่มี Endpoints',20,C.crit,560));
  write('lab014-architecture',els);
}

console.log('generated', fs.readdirSync(OUT).filter(f=>f.endsWith('.json')).sort().join('\n'));
