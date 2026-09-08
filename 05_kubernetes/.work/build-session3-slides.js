#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const root = '/root/workspace/DevTools/05_kubernetes';
const session = path.join(root, '03_Session3_Application_Deployment');
const template = '/root/workspace/DevTools/02_Docker/03_Fullstack_App_Example/Fullstack_Slides.html';
const target = path.join(session, 'Kubernetes_Session3_Slides.html');

const source = fs.readFileSync(template, 'utf8');
const css = source.match(/<style>([\s\S]*?)<\/style>/)[1];

const assetFiles = {
  cover_s3: 'slides_assets/photos/cover-s3.jpg',
  lab015_scene: 'slides_assets/photos/lab015-scene.jpg',
  lab016_scene: 'slides_assets/photos/lab016-scene.jpg',
  lab017_scene: 'slides_assets/photos/lab017-scene.jpg',
  lab018_scene: 'slides_assets/photos/lab018-scene.jpg',
  lab019_scene: 'slides_assets/photos/lab019-scene.jpg',
  lab020_scene: 'slides_assets/photos/lab020-scene.jpg',
  lab021_scene: 'slides_assets/photos/lab021-scene.jpg',
  concept_s3_1: 'slides_assets/photos/concept-s3-1.jpg',
  concept_s3_2: 'slides_assets/photos/concept-s3-2.jpg',
  concept_s3_3: 'slides_assets/photos/concept-s3-3.jpg',
  concept_s3_4: 'slides_assets/photos/concept-s3-4.jpg',
  concept_s3_5: 'slides_assets/photos/concept-s3-5.jpg',
  concept_s3_6: 'slides_assets/photos/concept-s3-6.jpg',
  concept_s3_7: 'slides_assets/photos/concept-s3-7.jpg',
  d01: 'slides_assets/d01-compose-to-objects.svg',
  d02: 'slides_assets/d02-stateless-vs-stateful.svg',
  d03: 'slides_assets/d03-ingress-vs-nodeport.svg',
  d04: 'slides_assets/d04-rolling-update-timeline.svg',
  d05: 'slides_assets/d05-requests-limits-scheduling.svg',
  d06: 'slides_assets/d06-troubleshooting-ladder.svg',
  d07: 'slides_assets/d07-request-path-browser-to-postgres.svg',
  d08: 'slides_assets/d08-learning-loop.svg',
  lab015_arch: 'slides_assets/lab015-architecture.svg',
  lab016_arch: 'slides_assets/lab016-architecture.svg',
  lab017_arch: 'slides_assets/lab017-architecture.svg',
  lab018_arch: 'slides_assets/lab018-architecture.svg',
  lab019_arch: 'slides_assets/lab019-architecture.svg',
  lab020_arch: 'slides_assets/lab020-architecture.svg',
  lab021_arch: 'slides_assets/lab021-architecture.svg',
  s015_1: '015-assembling-a-real-application/images/03-web-api-assembled-no-db.png',
  s015_2: '015-assembling-a-real-application/images/04-api-service-deleted.png',
  s016_1: '016-adding-a-database/images/02-full-stack-with-data.png',
  s016_2: '016-adding-a-database/images/03-data-survives.png',
  s017_1: '017-ingress-the-front-door/images/03-root-via-ingress.png',
  s017_2: '017-ingress-the-front-door/images/03-api-dashboard-json-via-ingress.png',
  s018_1: '018-updating-without-downtime/images/04-rollout-in-progress-mixed.png',
  s018_2: '018-updating-without-downtime/images/04-rollout-done-v2.png',
  s018_3: '018-updating-without-downtime/images/06-after-undo-v1.png',
  s019_1: '019-telling-kubernetes-what-you-need/images/02-web-with-resources.png',
  s020_1: '020-reading-the-symptoms/images/05-service-fixed.png',
  s021_1: '021-the-big-picture/images/01-complete-system.png',
  s021_2: '021-the-big-picture/images/02-ticket-created-trace.png',
  s021_3: '021-the-big-picture/images/04-db-service-cut.png'
};

function mime(name) {
  if (name.endsWith('.svg')) return 'image/svg+xml';
  if (name.endsWith('.png')) return 'image/png';
  return 'image/jpeg';
}

const assets = {};
for (const [key, rel] of Object.entries(assetFiles)) {
  const buf = fs.readFileSync(path.join(session, rel));
  assets[key] = `data:${mime(rel)};base64,${buf.toString('base64')}`;
}

const labs = [
  {
    sec:'1', num:'015', slug:'015-assembling-a-real-application', title:'Assembling a Real Application', thai:'ต่อ object ให้กลายเป็นระบบ',
    scene:'lab015_scene', sceneAlt:'ทีมช่างกำลังประกอบเครื่องจักรจากหลายชิ้นส่วนโดยยังมีข้อต่อสำคัญหนึ่งจุดที่ขาดอยู่',
    conceptPhoto:'concept_s3_1', conceptAlt:'ทีมช่างสี่คนร่วมกันประกอบปั๊ม ท่อ มอเตอร์ และตู้ควบคุมเป็นเครื่องจักรหนึ่งระบบ',
    diagram:'d01', diagramAlt:'ไดอะแกรมแปลง Docker Compose เป็น ConfigMap, Deployment, Service และ Ingress ของ Kubernetes',
    arch:'lab015_arch', archAlt:'สถาปัตยกรรมแล็บ 015 แสดง Browser ผ่าน Ingress และ Service ไปยัง web กับ api',
    problem:'compose.yaml ไฟล์เดียวมี 3 service — บน Kubernetes ระบบเดียวกันต้องใช้ object กี่ตัว ตัวไหนทำหน้าที่อะไร และถ้าลืมตัวใดตัวหนึ่งจะรู้ได้อย่างไร?',
    main:'แอปจริงคือหลาย object ที่ทำงานร่วมกัน ไม่ใช่ object เดียว',
    question:'ถ้า api Pod ยัง Running แต่ Service api หาย หน้าเว็บจะหา API เจอจากอะไร?',
    bullets:['Deployment ดูแลจำนวนและเวอร์ชันของ Pod','Service ให้ชื่อคงที่และเลือกปลายทางด้วย label','ConfigMap ส่งค่า ส่วน Ingress เปิดประตูจากภายนอก'],
    tech:[['compose service','Deployment + Service'],['environment','ConfigMap'],['ports','Ingress → Service'],['source of truth','โฟลเดอร์ manifests/']],
    cmd:'kubectl create namespace lab015\nkubectl apply -f manifests/\nkubectl wait -n lab015 --for=condition=available deploy/web deploy/api --timeout=120s',
    explain:'apply ทั้ง directory สร้าง object ตามไฟล์ · wait รอ Deployment พร้อม · namespace แยกห้องทดลอง',
    output:'configmap/web-config created\ndeployment.apps/web created\nservice/web created\ndeployment.apps/api created\nservice/api created\ningress.networking.k8s.io/web created\ndeployment "web" successfully rolled out\ndeployment "api" successfully rolled out',
    proof:[['s015_1','หน้า SkillSpace แสดง web และ api เชื่อมกันได้ แต่ฐานข้อมูลยัง down ตามแผน','web + api ต่อครบ'],['s015_2','หน้า SkillSpace หลังลบ Service api โดย API Pod ยังทำงานแต่ web ติดต่อไม่ได้','Pod อยู่ แต่ทางเชื่อมหาย']],
    breakTitle:'ลบ Service api', breakOutput:'service "api" deleted from lab015 namespace\npod/api-59d8fcb74b-5llqm  1/1  Running\npod/api-59d8fcb74b-v86vp  1/1  Running\n"api": {"configured": true, "reachable": false, "error": "fetch failed"}',
    remember:'Deployment สร้างคนทำงาน, Service ให้เบอร์กลาง, ConfigMap ส่งคู่มือ และ Ingress เปิดประตู'
  },
  {
    sec:'2', num:'016', slug:'016-adding-a-database', title:'Adding a Database', thai:'stateless ไม่เหมือน stateful',
    scene:'lab016_scene', sceneAlt:'โต๊ะทำงานว่างสามชุดที่ใช้แทนกันได้อยู่ข้างตู้เก็บข้อมูลซึ่งมีผู้ใช้ได้ทีละคน',
    conceptPhoto:'concept_s3_2', conceptAlt:'ห้องทำงานเหมือนกันสามห้องอยู่ข้างตู้เอกสารเฉพาะที่เก็บของไม่เหมือนใคร',
    diagram:'d02', diagramAlt:'ไดอะแกรมเปรียบเทียบ stateless web และ api กับ stateful PostgreSQL ที่ผูก PVC',
    arch:'lab016_arch', archAlt:'สถาปัตยกรรมแล็บ 016 แสดง web, api, PostgreSQL, Secret และ PVC',
    problem:'web กับ api สั่ง scale เป็น 3 ได้สบาย — ถ้าสั่ง db เป็น 3 บ้างจะเกิดอะไร? (ทายก่อน) ทำไมชั้นข้อมูลถึงต้องคิดต่างจากชั้นอื่น?',
    main:'ส่วนที่มีข้อมูลต้องการการดูแลต่างจากส่วนที่ไม่มีข้อมูล',
    question:'ถ้า web เพิ่มจาก 1 เป็น 3 ตัวได้ด้วยคำสั่งเดียว เหตุใด PostgreSQL จึงไม่ควรทำแบบเดียวกันบน PVC เดียว?',
    bullets:['stateless ทิ้ง สร้าง และ scale ได้เพราะไม่มีของติดตัว','PostgreSQL ต้องมีเจ้าของ data directory ที่ชัดเจน','PVC ทำให้ข้อมูลอยู่ข้ามอายุ Pod แต่ไม่ได้ทำ replication'],
    tech:[['web / api','scale แนวนอนได้ง่าย'],['db + RWO PVC','มีผู้เขียนหลักหนึ่งชุด'],['StatefulSet','ใช้เมื่อต้องการ identity และ volume ต่อ replica'],['managed DB','ทางเลือกเมื่อไม่อยากดูแล replication เอง']],
    cmd:'kubectl apply -f manifests/\nkubectl wait -n lab016 --for=condition=available deploy/db deploy/api deploy/web --timeout=180s\nkubectl get all,ingress,pvc,secret,configmap -n lab016',
    explain:'สร้าง Secret/PVC/db เพิ่มจากระบบเดิม · wait รอครบสามชั้น · get เปิดหลักฐาน compute, network, storage และ config',
    output:'secret/db-secret created\npersistentvolumeclaim/db-data created\ndeployment.apps/db created\nservice/db created\ndeployment.apps/db condition met\ndeployment.apps/api condition met\ndeployment.apps/web condition met',
    proof:[['s016_1','หน้า SkillSpace ระบบครบสามชั้น แสดงสถานะ web, api และฐานข้อมูลเป็นสีเขียว','สามชั้นพร้อม'],['s016_2','หน้า ticket ของ SkillSpace ยืนยันว่ารายการเลข 9 ยังอยู่หลัง DB Pod ถูกสร้างใหม่','ข้อมูลรอดหลัง Pod เปลี่ยน']],
    breakTitle:'scale db เป็น 2 บน PVC เดียว', breakOutput:'db-7dd8b59fd7-86jqs  1/1  Running  0\ndb-7dd8b59fd7-n6cvl  1/1  Running  0\nLOG: database system was interrupted\nLOG: automatic recovery in progress\ndeployment.apps/db scaled',
    remember:'ส่วน stateless เหมือนโต๊ะว่างที่สลับใช้ได้ ส่วน stateful เหมือนตู้เอกสารที่ต้องรู้ว่าใครเป็นเจ้าของ'
  },
  {
    sec:'3', num:'017', slug:'017-ingress-the-front-door', title:'Ingress — The Front Door', thai:'ประตูเดียว แยกทางด้วย path',
    scene:'lab017_scene', sceneAlt:'เคาน์เตอร์กลางรับผู้มาเยือนจากประตูเดียวแล้วกระจายไปยังทางเดินสองฝั่ง',
    conceptPhoto:'cover_s3', conceptAlt:'โถงมหาวิทยาลัยที่ผู้ใช้ทุกคนผ่านเคาน์เตอร์ต้อนรับและประตูทางเข้าเดียว',
    diagram:'d03', diagramAlt:'ไดอะแกรมเปรียบเทียบหลาย NodePort กับ Ingress ประตูเดียวที่ route ตาม path',
    arch:'lab017_arch', archAlt:'สถาปัตยกรรมแล็บ 017 แสดง localhost 8080 ผ่าน ingress-nginx ไป web และ api',
    problem:'ตอนเรียน Traefik เราเคยเจอ "2 service = 2 port, 20 service = 20 port" แล้วแก้ด้วย reverse proxy — บน Kubernetes NodePort ก็มีปัญหาเดียวกัน แล้วใครจะเป็น proxy ให้ และเราสั่งมันอย่างไร?',
    main:'Ingress คือประตูหน้าบ้านที่ทำหน้าที่เดียวกับ reverse proxy ที่เคยเรียน แต่รับคำสั่งจาก Kubernetes',
    question:'ถ้า web และ api มี Service ของตัวเองอยู่แล้ว เหตุใดผู้ใช้จึงยังควรเข้าผ่าน “ประตู” เดียว?',
    bullets:['Ingress object คือกฎ ไม่ใช่ proxy process','ingress-nginx controller อ่านกฎแล้วปรับ proxy','ภายนอกเข้า localhost:8080 จุดเดียว ส่วน backend ยังเป็น ClusterIP'],
    tech:[['NodePort','หนึ่ง Service ต่อหนึ่งพอร์ต L4'],['Ingress','route ด้วย host/path ที่ L7'],['IngressClass','ระบุ controller ที่ตีความกฎ'],['TLS','รวมการจบ HTTPS ไว้หน้าระบบ']],
    cmd:'kubectl apply -f manifests/\nkubectl describe ingress -n lab017 skillspace\ncurl -s http://localhost:8080/info\ncurl -s http://localhost:8080/api/whoami',
    explain:'describe แปล rule เป็น backend จริง · URL เดียวใช้ path เลือก Service · controller log เป็นหลักฐานว่าผ่าน proxy',
    output:'Rules:\n  Host  Path  Backends\n  *\n        /api  api:8000 (10.244.2.12:8000)\n        /     web:3000 (10.244.1.13:3000)',
    proof:[['s017_1','หน้าแรก SkillSpace ที่เปิดผ่าน Ingress ด้วย localhost พอร์ต 8080','/ → web'],['s017_2','JSON dashboard ของ API ที่เปิดผ่าน Ingress path /api/dashboard','/api → api']],
    breakTitle:'ชี้ backend ไป web-svc ที่ไม่มีจริง', breakOutput:'HTTP/1.1 503 Service Temporarily Unavailable\n/error: services "web-svc" not found/\nแก้กลับ: kubectl apply -f manifests/06-ingress.yaml',
    remember:'Ingress คือแผนผังทางเดิน ส่วน ingress controller คือพนักงานหน้าประตูที่อ่านแผนแล้วส่งคนไปถูกฝั่ง'
  },
  {
    sec:'4', num:'018', slug:'018-updating-without-downtime', title:'Updating without Downtime', thai:'เปลี่ยนทีละส่วนและถอยกลับได้',
    scene:'lab018_scene', sceneAlt:'ช่างเปลี่ยนแผ่นพื้นสะพานทีละแผ่นขณะที่ผู้คนยังเดินผ่านอีกช่องทางได้ต่อเนื่อง',
    conceptPhoto:'concept_s3_3', conceptAlt:'ทีมซ่อมเปลี่ยนพื้นทางเดินยกระดับทีละแผ่นโดยผู้ใช้ยังเดินผ่านอีกด้านได้',
    diagram:'d04', diagramAlt:'ไดอะแกรม timeline ของ rolling update จาก web v1 ไป v2 โดยไม่มีช่วงที่ endpoint เป็นศูนย์',
    arch:'lab018_arch', archAlt:'สถาปัตยกรรมแล็บ 018 แสดง ReplicaSet v1 และ v2 สลับจำนวนหลัง Service',
    problem:'ต้องปล่อย SkillSpace v2 ตอนที่พนักงานกำลังใช้งาน — ห้ามมีวินาทีที่หน้าเว็บล่ม ทำได้จริงหรือ? แล้วถ้า v2 มีบั๊กจะถอยกลับภายในกี่วินาที?',
    main:'เปลี่ยนเวอร์ชันทีละส่วนทำให้ผู้ใช้ไม่สะดุด',
    question:'ถ้า Pod ใหม่ใช้เวลาสตาร์ต แม้เพียงเสี้ยววินาที Kubernetes ต้องรู้อะไรจึงกล้าหยุด Pod เก่า?',
    bullets:['maxUnavailable: 0 เก็บ capacity เดิมไว้','maxSurge: 1 อนุญาต Pod ใหม่เพิ่มทีละตัว','readiness กัน Pod ใหม่ออกจาก Service จนพร้อมจริง'],
    tech:[['ReplicaSet เก่า','ยังรับ request ระหว่างเปลี่ยน'],['ReplicaSet ใหม่','เพิ่มเมื่อ Pod ผ่าน readiness'],['rollout undo','scale revision ก่อนหน้ากลับ'],['หลักฐาน','request loop ต้องไม่มี FAIL']],
    cmd:'kubectl apply -f manifests/02-web-deployment.yaml\nkubectl rollout status -n lab018 deploy/web --timeout=180s\nkubectl get rs,pods -n lab018 -l app=web',
    explain:'apply เปลี่ยน Pod template เป็น v2 · rollout status รอจนเสร็จ · ReplicaSet เก่าเก็บ revision สำหรับ undo',
    output:'Waiting for deployment "web" rollout to finish: 1 out of 3 new replicas have been updated...\nWaiting for deployment "web" rollout to finish: 2 out of 3 new replicas have been updated...\ndeployment "web" successfully rolled out\nweb-678694c6b8   3   3   3\nweb-74cb858c9    0   0   0',
    proof:[['s018_1','ภาพจริงระหว่าง rolling update ที่คลัสเตอร์มี web v1 และ v2 พร้อมกัน','mixed v1 + v2'],['s018_2','หน้า SkillSpace ธีม emerald หลัง rolling update จบเป็น v2','rollout จบ v2'],['s018_3','หน้า SkillSpace กลับเป็นธีม v1 หลัง kubectl rollout undo','rollback กลับ v1']],
    breakTitle:'เปลี่ยน strategy เป็น Recreate', breakOutput:'FAIL\nFAIL\nFAIL  (รอบจริงติดกัน 17 ครั้ง)\nจากนั้น v2 จึงตอบได้\nแก้กลับ: RollingUpdate + readinessProbe',
    remember:'rolling update คือเปลี่ยนหลอดไฟทีละดวงโดยเปิดดวงเก่าไว้ จนดวงใหม่สว่างและผ่านการตรวจแล้ว'
  },
  {
    sec:'5', num:'019', slug:'019-telling-kubernetes-what-you-need', title:'Requests & Limits', thai:'จองให้พอ จำกัดไม่ให้กินหมด',
    scene:'lab019_scene', sceneAlt:'ช่างจัดตุ้มน้ำหนักลงถาดตามความจุโดยมีขอบป้องกันไม่ให้ถาดหนึ่งรับเกินกำหนด',
    conceptPhoto:'concept_s3_4', conceptAlt:'มือสวมถุงมือจัดทรงกระบอกโลหะลงช่องความจุและเหลือชิ้นใหญ่ที่ใส่ช่องใดไม่ได้',
    diagram:'d05', diagramAlt:'ไดอะแกรมแสดง requests ใช้ตอน scheduling และ limits บังคับ CPU กับ memory ตอนรัน',
    arch:'lab019_arch', archAlt:'สถาปัตยกรรมแล็บ 019 แสดง scheduler เทียบ requests กับ allocatable ของ node',
    problem:'scheduler เลือก node ให้ Pod ได้อย่างไรทั้งที่เราไม่เคยบอกว่าแอปหนักแค่ไหน? ถ้า web ตัวหนึ่ง memory leak จะลาก api/db บน node เดียวกันล้มไปด้วยไหม?',
    main:'Kubernetes ต้องรู้ว่าแอปใช้ทรัพยากรเท่าไร จึงจะเลือก node ให้ถูกและกันไม่ให้ตัวหนึ่งกินหมด',
    question:'ถ้า node ใช้ CPU จริงเพียงเล็กน้อย แต่ Pod ขอ cpu: 64 scheduler ควรยอมวาง Pod หรือไม่?',
    bullets:['requests คือจำนวนที่ scheduler กันไว้ก่อนวาง Pod','limits คือเพดานตอน container กำลังรัน','CPU เกินถูก throttle; memory เกินจบด้วย OOMKilled'],
    tech:[['requests','ตัดสินใจตอน schedule'],['limits','บังคับตอน runtime'],['kubectl top','usage จริง ไม่ใช่ของที่จอง'],['QoS','Guaranteed · Burstable · BestEffort']],
    cmd:'kubectl apply -f 03-web-too-big.yaml\nkubectl get pods -n lab019\nkubectl describe pod -n lab019 -l app=web-too-big',
    explain:'workload จงใจขอ 64 CPU · get เห็น Pending · describe เปิดเหตุผลจาก scheduler',
    output:'deployment.apps/web-too-big created\nweb-too-big-85f7c9db4-w2p7r  0/1  Pending  0  3s\nWarning  FailedScheduling  0/3 nodes are available: 1 node had untolerated taint, 2 Insufficient cpu.',
    proof:[['s019_1','หน้า SkillSpace ของ web ที่ประกาศ requests และ limits พร้อมชื่อ Pod จริง','web ปกติพร้อม resources']],
    breakTitle:'ขอใหญ่เกิน / จำกัด memory ต่ำเกิน', breakOutput:'web-too-big-85f7c9db4-w2p7r  0/1  Pending\nWarning  FailedScheduling  2 Insufficient cpu\nweb-oom-57d64f4844-qnfrp  1/1  Running  2\nOOMKilled\nExit Code: 137',
    remember:'requests คือที่นั่งที่จองก่อนขึ้นรถ ส่วน limits คือรั้วที่ห้ามแผ่เกินพื้นที่ระหว่างเดินทาง'
  },
  {
    sec:'6', num:'020', slug:'020-reading-the-symptoms', title:'Reading the Symptoms', thai:'หา layer ที่พังก่อนรีบแก้',
    scene:'lab020_scene', sceneAlt:'ช่างกำลังตรวจห้องเครื่องสี่ช่องที่แสดงอาการเสียแตกต่างกันด้วยลำดับการวินิจฉัย',
    conceptPhoto:'concept_s3_5', conceptAlt:'แพทย์กำลังมองเส้นคลื่นอาการจากจอหลายจอพร้อมเทียบกับแถบสัญญาณในมือ',
    diagram:'d06', diagramAlt:'ไดอะแกรมบันได troubleshooting เรียง kubectl get, describe, logs และ events',
    arch:'lab020_arch', archAlt:'สถาปัตยกรรมแล็บ 020 แสดงสี่อาการ Pending, ImagePullBackOff, process crash และ Service ไม่มี endpoint',
    problem:'เพื่อนส่งโฟลเดอร์ manifests มาให้ apply แล้วหน้าเว็บไม่ขึ้น — มี Pod 4 ตัวสถานะไม่เหมือนกันเลย จะเริ่มดูจากตรงไหน?',
    main:'อาการที่ Kubernetes แสดง บอกได้ว่าปัญหาอยู่ชั้นไหน',
    question:'Pod สี่ตัวเว็บไม่ขึ้นเหมือนกัน เราควรใช้คำสั่งเดียวแก้ทั้งหมดหรือควรระบุ layer ที่เสียก่อน?',
    bullets:['get อ่านอาการภายนอกและขอบเขต','describe อ่าน config กับ Events รอบ object','logs ฟังเสียง process; events เรียงเรื่องทั้ง namespace'],
    tech:[['Pending','scheduler / resource / PVC'],['ImagePullBackOff','ชื่อ image, registry, credential'],['restart + BackOff','application process'],['endpoint ว่าง','selector, label, readiness']],
    cmd:'kubectl apply -f broken/\nkubectl get pods,service,endpoints -n lab020\nkubectl get events -n lab020 --sort-by=.lastTimestamp',
    explain:'สร้างสี่อาการพร้อมกัน · อ่านภาพรวมก่อน · ใช้ Events เป็น timeline ไม่เดาสุ่มจาก YAML',
    output:'crashloop-web  0/1  Error              2  20s\nendpoint-web   1/1  Running            0  20s\nimagepull-web  0/1  ImagePullBackOff   0  20s\npending-web    0/1  Pending            0  20s\nendpoints/web       &lt;none&gt;',
    proof:[['s020_1','หน้า SkillSpace หลังแก้ Service selector แล้ว endpoint-web ตอบ request ได้จริง','แก้ selector แล้ว UI กลับมา']],
    breakTitle:'สี่อาการ = สี่จุดเริ่มตรวจ', breakOutput:'Pending → describe → Insufficient cpu\nImagePull → describe → tag ไม่มี\nError/BackOff → logs → MODULE_NOT_FOUND\nendpoint ว่าง → เทียบ selector กับ label',
    remember:'สถานะคือป้ายบอกชั้นของตึกที่ควรไปตรวจ ไม่ใช่คำตอบสุดท้ายของปัญหา'
  },
  {
    sec:'7', num:'021', slug:'021-the-big-picture', title:'The Big Picture', thai:'ตาม request จาก Browser ถึง PostgreSQL',
    scene:'lab021_scene', sceneAlt:'บัตรคำขอเดินทางผ่านท่อใสและสถานีหลายจุดไปยังลิ้นชักเก็บข้อมูลก่อนวนกลับ',
    conceptPhoto:'concept_s3_7', conceptAlt:'แบบจำลองอาคารมองจากด้านบนที่มีเชือกสีน้ำเงินลากผ่านห้องและจุดเชื่อมต่อตลอดเส้นทาง',
    diagram:'d07', diagramAlt:'ไดอะแกรมเส้นทาง request จาก Browser ผ่าน Ingress, web, api ไป PostgreSQL และ PVC',
    arch:'lab021_arch', archAlt:'สถาปัตยกรรมแล็บ 021 แสดงระบบ Kubernetes ครบทุก object และเส้น request, config, secret, storage',
    problem:'ผู้ใช้กดปุ่ม "สร้างใบแจ้งซ่อม" ในเบราว์เซอร์ — request นั้นเดินผ่านอะไรบ้างกว่าจะถึง PostgreSQL แล้วกลับมา? ถ้าดึงชิ้นใดออก ผู้ใช้จะเห็นอาการอะไร?',
    main:'ทุกอย่างที่เรียนมาต่อกันเป็นภาพเดียวได้',
    question:'เมื่อผู้ใช้กด “แจ้งซ่อม” หนึ่งครั้ง request ผ่าน object ใดบ้าง และ object ใดมีไว้เก็บ config กับข้อมูลโดยไม่ส่ง packet เอง?',
    bullets:['request: Ingress → Service → Pod ในแต่ละชั้น','config: ConfigMap/Secret ถูก inject ตอนสร้าง Pod ไม่ได้ส่ง packet','storage: db เขียนผ่าน mount ไป PVC/PV ที่ปลายทาง'],
    tech:[['Browser → Ingress','ประตูภายนอก'],['Service → Pod','ชื่อคงที่และ endpoint'],['ConfigMap / Secret','ป้อนค่าให้ container'],['PVC / PV','เก็บข้อมูลนอกอายุ Pod']],
    cmd:'kubectl apply -f manifests/\nkubectl wait -n lab021 --for=condition=available deploy/db deploy/api deploy/web --timeout=180s\ncurl -s http://localhost:8080/info | jq',
    explain:'สร้างระบบครบจาก source of truth · รอทุกชั้นพร้อม · /info ยืนยันชื่อ Pod และ db.status จาก request จริง',
    output:'pod/api-77cd4cf44d-95hgq  1/1  Running  0  24s\npod/api-77cd4cf44d-d4v79  1/1  Running  0  24s\npod/db-59469494cf-nj5qg   1/1  Running  0  24s\npod/web-5587f599bf-8ds22  1/1  Running  0  25s\npod/web-5587f599bf-sbz56  1/1  Running  0  25s\npersistentvolumeclaim/db-data  Bound  pvc-5d77aa76-...  1Gi  RWO  standard',
    proof:[['s021_1','หน้า SkillSpace ระบบครบ แสดงชื่อ Pod และสถานะเขียวทั้งสามชั้น','ระบบครบ 3 ชั้น'],['s021_2','หน้า SkillSpace หลังสร้าง ticket เลข 9 สำหรับตามรอย request','ticket #9 ถึงฐานข้อมูล'],['s021_3','หน้า SkillSpace หลังตัด Service db ซึ่งการ์ดฐานข้อมูลเปลี่ยนเป็นสีแดง','ตัด db Service → เห็นอาการ']],
    breakTitle:'ตัด object ทีละชิ้น', breakOutput:'service "api" deleted from lab021 namespace\n503\ningress.networking.k8s.io "skillspace" deleted\n404\ndeployment.apps/web scaled\n503\ndeployment.apps/web condition met',
    remember:'Browser → Ingress → Service web → Pod web → Service api → Pod api → Service db → Pod db → PVC/PV'
  }
];

function esc(v) {
  return String(v).replace(/&(?!(?:lt|gt|amp|quot|#39);)/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function img(key, alt, cls='', style='') {
  return `<img data-a="${key}" alt="${alt}"${cls ? ` class="${cls}"` : ''}${style ? ` style="${style}"` : ''}>`;
}
function foot(label) { return `<div class="s-foot"><span>${label}</span><span class="pg"></span></div>`; }
function slide(inner, cls='', attrs='') { return `<div class="slot"${attrs}><section class="slide${cls ? ' '+cls : ''}">${inner}</section></div>`; }
function head(eyebrow, title, sub='') { return `<div class="s-head"><div class="eyebrow">${eyebrow}</div><h2>${title}</h2>${sub ? `<div class="sub">${sub}</div>` : ''}</div>`; }

const slides = [];
slides.push(slide(
  `${img('cover_s3','โถงมหาวิทยาลัยที่ทุกคนผ่านเคาน์เตอร์ต้อนรับและประตูทางเข้าเดียว','','position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:saturate(.88) brightness(.48)')}`+
  `<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(9,18,32,.96),rgba(9,18,32,.78) 55%,rgba(9,18,32,.2))"></div>`+
  `<div class="s-body" style="position:relative;z-index:2;padding-right:490px;align-items:flex-start"><div class="k" style="color:#9cc7f4">KUBERNETES · SESSION 03 · 7 HANDS-ON LABS</div><h1 style="font-size:63px;line-height:1.08">Application<br>Deployment</h1><div class="rule"></div><div class="m" style="font-size:22px">ประกอบระบบจริง · เปิดประตู · อัปเดต<br><b style="color:#fff">จัดสรรทรัพยากร · อ่านอาการ · ตาม request</b></div></div>`+
  foot('Kubernetes · ครั้งที่ 3 · Application Deployment'), 'cover'));

slides.push(slide(
  head('ภาพรวมครั้งที่ 3','เส้นทางวันนี้ — <em>7 ปัญหา 7 แล็บ</em>','คลิกการ์ดเพื่อกระโดดไปแล็บนั้นได้ทันที')+
  `<div class="s-body top"><div class="agenda">${labs.map(l=>`<div class="it lab" data-go="${l.sec}"><div class="ix">${l.num}</div><div class="tt">${l.title}<s>${l.thai}</s></div></div>`).join('')}<div class="it"><div class="ix">✓</div><div class="tt">สรุปทั้ง 3 ครั้ง<s>LO1–LO7 → หลักฐานจากแล็บ</s></div></div></div></div>`+
  foot('สารบัญ · LAB 015–021')));

slides.push(slide(
  head('วิธีเรียนของทุกแล็บ','วงจรเรียนรู้ — <em>เห็นหลักฐานก่อนเชื่อ</em>','ทุกแล็บเริ่มด้วยการทาย จบด้วยการทำให้พังและแก้กลับ')+
  `<div class="s-body"><div class="g21 mid"><div class="fig fix" style="height:430px">${img('d08','ไดอะแกรมวงจรทายผล รัน สังเกตหลักฐาน อธิบายเหตุผล ทดลองให้พัง และแก้กลับ')}</div><div class="loop4"><div class="card a"><h4>1 · ทายผล</h4><p>บอกเหตุผลก่อนกด Enter</p></div><div class="card"><h4>2 · รัน</h4><p>ใช้ manifest จริง</p></div><div class="card o"><h4>3 · หลักฐาน</h4><p>kubectl · UI · log</p></div><div class="card"><h4>4 · อธิบาย</h4><p>โยงอาการกับ object</p></div><div class="card c"><h4>5 · ทำให้พัง</h4><p>เปลี่ยนทีละตัวแปร</p></div><div class="card w"><h4>6 · แก้กลับ</h4><p>Clean Re-run ได้</p></div></div></div></div>`+
  foot('วงจรการเรียนรู้ประจำทุกแล็บ')));

for (const l of labs) {
  const readme = `${l.slug}/README.md`;
  slides.push(slide(
    `${img(l.scene,l.sceneAlt,'','position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:saturate(.86) brightness(.44)')}`+
    `<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(9,18,32,.97),rgba(9,18,32,.78) 60%,rgba(9,18,32,.22))"></div>`+
    `<div class="s-body" style="position:relative;z-index:2;padding-right:450px;align-items:flex-start"><div class="num-big" style="color:#86b6ef">${l.num}</div><h1>${l.title}</h1><div class="m"><b style="color:#fca5a5">ปัญหา:</b> ${l.problem}</div><div style="margin-top:18px"><code style="color:#dbeafe;font-size:14px">${readme}</code></div></div>`+
    foot(`LAB ${l.num} · ${readme}`), 'section', ` data-sec="${l.sec}"`));

  slides.push(slide(
    head(`LAB ${l.num} · ทฤษฎี 1/4 · ปัญหา`,'เริ่มจากปัญหา — <em>ยังไม่รีบเลือกเครื่องมือ</em>')+
    `<div class="s-body"><div class="quote big">${l.problem}</div><div class="grid3"><div class="card c"><span class="n">1</span><h4 style="display:inline">มุมผู้ใช้</h4><p>ผู้ใช้เห็นอาการอะไรเมื่อชิ้นนี้หายหรือไม่พร้อม?</p></div><div class="card w"><span class="n">2</span><h4 style="display:inline">มุมระบบ</h4><p>object ใดควรรับผิดชอบเรื่องนี้เพียงเรื่องเดียว?</p></div><div class="card a"><span class="n">3</span><h4 style="display:inline">มุมหลักฐาน</h4><p>kubectl · UI · log ต้องเล่าเรื่องเดียวกัน</p></div></div></div>`+
    foot(`LAB ${l.num} · ปัญหาตั้งต้นจาก outline`)));

  slides.push(slide(
    head(`LAB ${l.num} · ทฤษฎี 2/4`,'ใช้ภาพจริงเป็นอุปมา — <em>ก่อนกลับสู่ object</em>')+
    `<div class="s-body"><div class="g11 mid"><div class="fig shot fix" style="height:430px">${img(l.conceptPhoto,l.conceptAlt)}</div><div><ul class="bul">${l.bullets.map(x=>`<li>${x}</li>`).join('')}</ul><div class="note a" style="margin-top:18px"><b>มองภาพนี้:</b> ${l.remember}</div></div></div></div>`+
    foot(`LAB ${l.num} · แนวคิดผ่านภาพถ่ายสมจริง`)));

  slides.push(slide(
    head(`LAB ${l.num} · ทฤษฎี 3/4`,'โมเดลทางเทคนิค — <em>ติดตามเส้นและขอบเขต</em>')+
    `<div class="s-body"><div class="g21 mid"><div class="fig fix" style="height:430px">${img(l.diagram,l.diagramAlt)}</div><dl class="kv">${l.tech.map(x=>`<dt>${x[0]}</dt><dd>${x[1]}</dd>`).join('')}</dl></div></div>`+
    foot(`LAB ${l.num} · ไดอะแกรมทฤษฎี`)));

  slides.push(slide(
    head(`LAB ${l.num} · ทฤษฎี 4/4 · ปิดหัวข้อ`,'แนวคิดหลัก — <em>หนึ่งประโยคที่ต้องจำ</em>')+
    `<div class="s-body"><div class="quote big" style="font-size:29px;line-height:1.55">${l.main}</div><div class="card a"><h4>ใช้ประโยคนี้ตรวจความเข้าใจ</h4><p>ถ้าอธิบายเหตุและผลของประโยคนี้ด้วยหลักฐานจากแล็บได้ แปลว่าเข้าใจหัวข้อนี้แล้ว</p></div></div>`+
    foot(`LAB ${l.num} · แนวคิดหลักคำต่อคำจาก outline`)));

  slides.push(slide(
    head(`LAB ${l.num} · ก่อนเริ่มลงมือ`,'คำถามก่อนเริ่ม — <em>ทายก่อนกด Enter</em>')+
    `<div class="s-body"><div class="quote big">${l.question}</div><div class="grid3"><div class="card w"><span class="n">1</span><h4>ทาย</h4><p>เขียนผลที่คาดหนึ่งบรรทัด</p></div><div class="card a"><span class="n">2</span><h4>เลือกหลักฐาน</h4><p>จะดู kubectl · UI · log จุดใด?</p></div><div class="card o"><span class="n">3</span><h4>อธิบาย</h4><p>โยงอาการกับ object และ layer</p></div></div><div class="note"><b>อ่านขั้นตอนเต็ม:</b> <code>${readme}</code></div></div>`+
    foot(`LAB ${l.num} · ${readme}`)));

  slides.push(slide(
    head(`LAB ${l.num} · ลงมือ 1/2`,'ประกอบระบบ — <em>อ่าน topology ก่อนรัน</em>',`แหล่งขั้นตอนฉบับเต็ม: <code>${readme}</code>`)+
    `<div class="s-body"><div class="g21 mid"><div class="fig fix" style="height:365px">${img(l.arch,l.archAlt)}</div><div><pre class="code xs">${esc(l.cmd)}</pre><div class="note a" style="font-size:12.5px;padding:8px 11px;margin-top:8px"><b>📝 คำอธิบาย:</b> ${l.explain}</div><pre class="code xs" style="margin-top:9px"><span class="c"># ✅ Expected output จริง — คัดบรรทัดสำคัญจาก README</span>\n${esc(l.output)}</pre></div></div></div>`+
    foot(`LAB ${l.num} · ${readme}`), 'figs'));

  const proofCols = l.proof.length === 1 ? '1fr' : `repeat(${l.proof.length},1fr)`;
  const proofHeight = l.proof.length === 3 ? 224 : 265;
  slides.push(slide(
    head(`LAB ${l.num} · ลงมือ 2/2`,'หลักฐานจริง — <em>ทดลองให้พัง แล้วแก้กลับ</em>',`screenshot และ Expected output จาก <code>${readme}</code>`)+
    `<div class="s-body top"><div class="figrow" style="grid-template-columns:${proofCols}">${l.proof.map(p=>`<div><div class="fig shot fix" style="height:${proofHeight}px">${img(p[0],p[1])}</div><div class="figcap">${p[2]}</div></div>`).join('')}</div><div class="grid2"><div class="card c"><h4>ทดลองให้พัง · ${l.breakTitle}</h4><pre class="code xs">${esc(l.breakOutput)}</pre></div><div class="card o"><h4>ปิดวงจร</h4><p>${l.remember}</p><p style="margin-top:8px"><code>${readme}</code></p></div></div></div>`+
    foot(`LAB ${l.num} · ${readme}`), 'figs'));
}

slides.push(slide(
  head('สรุปครั้งที่ 3','จาก object แยกชิ้น — <em>สู่ระบบที่ดูแลต่อได้</em>')+
  `<div class="s-body"><div class="grid4"><div class="card a"><span class="n">1</span><h4>ประกอบ</h4><p>Deployment · Service · ConfigMap · Ingress</p></div><div class="card o"><span class="n">2</span><h4>เก็บข้อมูล</h4><p>Secret · PVC · PostgreSQL</p></div><div class="card w"><span class="n">3</span><h4>เปลี่ยนอย่างปลอดภัย</h4><p>RollingUpdate · readiness · rollback</p></div><div class="card c"><span class="n">4</span><h4>อ่านอาการ</h4><p>requests/limits · get → describe → logs → events</p></div></div><div class="quote">manifest คือ source of truth — หลักฐานจาก <mark>UI · kubectl · log · database</mark> ต้องสอดคล้องกัน</div></div>`+
  foot('สรุปครั้งที่ 3 · LAB 015–021')));

slides.push(slide(
  head('มีอยู่ แต่ไม่ทำแล็บ','หัวข้อระดับสูง — <em>ใช้เมื่อปัญหาโตถึงจุดไหน</em>','เครื่องมือ CLI ที่ระบุมีอยู่แล้วใน image การเรียน')+
  `<div class="s-body top"><table class="tbl sm"><tr><th>หัวข้อ</th><th>ใช้เมื่อ</th><th>อ่านต่อ / เครื่องมือใน image</th></tr><tr><td><b>HPA</b></td><td>ปรับ replicas ตาม metric</td><td>Kubernetes docs · metrics-server</td></tr><tr><td><b>Job / CronJob</b></td><td>งานจบเป็นครั้ง / งานตามเวลา</td><td>Kubernetes Workloads docs</td></tr><tr><td><b>RBAC</b></td><td>จำกัดว่าใครทำอะไรกับ object ใด</td><td>Authorization docs</td></tr><tr><td><b>StatefulSet</b></td><td>identity/volume ต่อ replica และลำดับชัด</td><td>Stateful Applications docs</td></tr><tr><td><b>Helm · Kustomize</b></td><td>แพ็ก/ปรับ manifest หลาย environment</td><td><code>helm v4.2.4</code> · <code>kustomize v5.8.1</code></td></tr><tr><td><b>GitOps</b></td><td>ให้ Git เป็น desired state และ sync ต่อเนื่อง</td><td><code>argocd</code> · <code>flux</code></td></tr><tr><td><b>Security / lint</b></td><td>สแกน image และจับ manifest เสี่ยงก่อน deploy</td><td><code>trivy</code> · <code>kube-linter</code> · <code>kubeconform</code></td></tr></table><div class="note w"><b>หลักเลือก:</b> อย่าเพิ่มเครื่องมือเพราะ “production ใช้กัน” — เพิ่มเมื่อระบุปัญหาและเจ้าของความรับผิดชอบในภาพใหญ่ได้</div></div>`+
  foot('ต่อยอด · HPA · Job/CronJob · RBAC · StatefulSet · Helm · Kustomize · GitOps · Security')));

slides.push(slide(
  head('ร้อยทั้ง 3 ครั้ง','LO1–LO7 → <em>แล็บที่พิสูจน์ด้วยหลักฐาน</em>','การอ้างข้ามครั้งเป็นข้อความ ไม่ผูก path ไปโฟลเดอร์ครั้งอื่น')+
  `<div class="s-body top"><table class="tbl sm"><tr><th>LO</th><th>อธิบายได้ว่า…</th><th>แล็บที่พิสูจน์</th></tr><tr><td class="req">LO1</td><td>Kubernetes แก้โจทย์ orchestration; control plane/worker ต่างกัน</td><td>แล็บ 001</td></tr><tr><td class="req">LO2</td><td>Pod คือหน่วยเล็กที่สุด ไม่ใช่ container</td><td>แล็บ 003</td></tr><tr><td class="req">LO3</td><td>desired state, self-healing และ Deployment</td><td>แล็บ 006–007</td></tr><tr><td class="req">LO4</td><td>Service ให้ชื่อคงที่; ClusterIP/NodePort ต่างกัน</td><td>แล็บ 008–009</td></tr><tr><td class="req">LO5</td><td>ConfigMap/Secret/PVC แยกค่า ความลับ และข้อมูล</td><td>แล็บ 010–013</td></tr><tr><td class="req">LO6</td><td>ระบบหลายชั้นและ rolling update ทำงานร่วมกัน</td><td>แล็บ 015–018 และ 021</td></tr><tr><td class="req">LO7</td><td>ไล่ Pending · ImagePull · crash · routing เป็นลำดับ</td><td>แล็บ 019–021</td></tr></table></div>`+
  foot('ผลลัพธ์การเรียนรู้ทั้งชุด · LO1–LO7')));

slides.push(slide(
  head('เช็กลิสต์ก่อนจบ','ฉันอธิบายได้หรือยัง — <em>ไม่ใช่แค่พิมพ์ตามได้</em>')+
  `<div class="s-body"><div class="grid2"><div class="card a"><h4>ภาพระบบ</h4><ul class="bul sm"><li>บอกบทบาท Deployment · Service · Ingress</li><li>แยก request, config และ storage path</li><li>อธิบาย stateless เทียบ stateful</li></ul></div><div class="card o"><h4>การเปลี่ยนและการพิสูจน์</h4><ul class="bul sm"><li>อธิบาย readiness กับ zero-downtime</li><li>แยก requests จาก limits</li><li>ใช้ UI · kubectl · log · db ยืนยันเรื่องเดียวกัน</li></ul></div><div class="card w"><h4>เมื่อระบบพัง</h4><ul class="bul sm"><li>เริ่ม get → describe → logs → events</li><li>ชี้ layer จากอาการก่อนแก้</li><li>apply source of truth คืนและ Clean Re-run</li></ul></div><div class="card c"><h4>ห้ามหลงทาง</h4><ul class="bul sm"><li>Running ไม่เท่ากับ Ready</li><li>base64 ไม่เท่ากับ encryption</li><li>PVC ไม่เท่ากับ backup/replication</li></ul></div></div></div>`+
  foot('เช็กลิสต์ปิดครั้งที่ 3')));

slides.push(slide(
  head('จำภาพเดียวให้ได้','ทั้งชุด Kubernetes — <em>request เดิน ชิ้นส่วนรับผิดชอบ</em>')+
  `<div class="s-body"><div class="g21 mid"><div class="fig fix" style="height:450px">${img('d07','ไดอะแกรมสรุปทั้งชุดจาก Browser ผ่าน Ingress, Service และ Pod ไป PostgreSQL กับ PVC')}</div><div><div class="quote" style="font-size:20px"><b>Browser → Ingress → Service web → Pod web → Service api → Pod api → Service db → Pod db → PVC/PV</b></div><div class="note a" style="margin-top:14px"><b>รอบเส้น:</b> Deployment ดูแลจำนวน/เวอร์ชัน · Probe คัดความพร้อม · ConfigMap/Secret ป้อนค่า · Resources ช่วย schedule/จำกัด · Events/logs บอกอาการ</div></div></div></div>`+
  foot('จำภาพเดียวให้ได้ · ภาพรวมทั้ง 3 ครั้ง')));

slides.push(slide(
  `${img('concept_s3_6','เจ้าหน้าที่ห้องควบคุมกำลังมองข้อมูลหลายมิติจากจอที่แสดงเส้น จุด โหนด แถบ แบบอาคาร และตารางสี','','position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:saturate(.82) brightness(.42)')}`+
  `<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(9,18,32,.97),rgba(9,18,32,.78) 56%,rgba(9,18,32,.22))"></div><div class="s-body" style="position:relative;z-index:2;padding-right:475px;align-items:flex-start"><div class="k" style="color:#9cc7f4">NEXT LEARNING STEP · PRODUCTION READINESS</div><h1 style="font-size:56px;line-height:1.1">จาก “รันได้”<br>สู่ “ดูแลได้จริง”</h1><div class="rule"></div><div class="m">ครั้งถัดไปของการเรียนรู้:<br><b style="color:#fff">TLS · RBAC · backup · monitoring · autoscaling · GitOps</b></div><div class="note" style="margin-top:24px;background:rgba(24,24,27,.78);border-color:#86b6ef;color:#d4d4d8"><b style="color:#fff">ก่อนเพิ่มเครื่องมือ:</b> ชี้ให้ได้ว่ามันรับผิดชอบส่วนไหนของภาพเดียว</div></div>`+
  foot('Kubernetes · จบครั้งที่ 3 · เส้นทางต่อยอด'), 'cover'));

const chrome = `
<div id="bar"><i></i></div>
<div id="counter"><span id="cur">1</span> / <span id="tot">0</span></div>
<div id="ctl">
  <button id="bPrev" aria-label="สไลด์ก่อนหน้า" title="ก่อนหน้า (←)">‹</button>
  <button id="bNext" aria-label="สไลด์ถัดไป" title="ถัดไป (→)">›</button>
  <button id="bOv" aria-label="ดูทุกตอน" title="ดูทุกตอน (O)">▦</button>
  <button id="bFs" aria-label="เต็มจอ" title="เต็มจอ (F)">⛶</button>
  <button id="bHelp" aria-label="ปุ่มลัด" title="ปุ่มลัด (?)">?</button>
</div>
<div id="ov" role="dialog" aria-label="ภาพรวมทุกตอน"><h3>Kubernetes Session 3 — ภาพรวมทุกตอน</h3><div class="oh">คลิกการ์ดเพื่อกระโดดไปตอนนั้น · กด <b>Esc</b> เพื่อปิด</div><div class="cards" id="ovCards"></div></div>
<div id="help" role="dialog" aria-modal="true" aria-label="ปุ่มลัด"><div class="box"><h3>ปุ่มลัด</h3><table><tr><td><kbd>→</kbd><kbd>Space</kbd><kbd>PgDn</kbd></td><td>สไลด์ถัดไป</td></tr><tr><td><kbd>←</kbd><kbd>PgUp</kbd></td><td>สไลด์ก่อนหน้า</td></tr><tr><td><kbd>Home</kbd> / <kbd>End</kbd></td><td>สไลด์แรก / สุดท้าย</td></tr><tr><td><kbd>O</kbd></td><td>เปิดหน้ารวมทุกตอน</td></tr><tr><td><kbd>F</kbd></td><td>เต็มจอ</td></tr><tr><td><kbd>Ctrl</kbd>+<kbd>P</kbd></td><td>พิมพ์ / บันทึกเป็น PDF</td></tr><tr><td><kbd>Esc</kbd></td><td>ปิดหน้าช่วยเหลือ / ภาพรวม</td></tr></table></div></div>`;

const meta = Object.fromEntries(labs.map(l=>[l.sec,{t:`LAB ${l.num} — ${l.title}`,d:l.thai}]));
const script = `(function(){
  var A=window.ASSETS||{};
  Array.prototype.forEach.call(document.querySelectorAll('img[data-a]'),function(im){var k=im.getAttribute('data-a');if(A[k])im.src=A[k];});
  var slots=Array.prototype.slice.call(document.querySelectorAll('.slot'));var n=slots.length,i=0;
  document.getElementById('tot').textContent=n;slots.forEach(function(s,k){var pg=s.querySelector('.pg');if(pg)pg.textContent=(k+1)+' / '+n;});
  var META=${JSON.stringify(meta)};var starts=[{sec:'0',at:0}];slots.forEach(function(s,k){var sec=s.getAttribute('data-sec');if(sec)starts.push({sec:sec,at:k});});
  var box=document.getElementById('ovCards');starts.forEach(function(st,x){var end=(x+1<starts.length)?starts[x+1].at-1:n-1;var m=st.sec==='0'?{t:'เปิดเรื่อง',d:'สารบัญ → วงจรเรียนรู้ → ระบบจริง'}:META[st.sec];var el=document.createElement('div');el.className='oc';el.setAttribute('role','button');el.setAttribute('tabindex','0');el.innerHTML='<div class="n">'+(st.sec==='0'?'เริ่มต้น':'ตอนที่ '+st.sec)+'</div><div class="t"></div><div class="d"></div><div class="r">สไลด์ '+(st.at+1)+'–'+(end+1)+' · '+(end-st.at+1)+' แผ่น</div>';el.querySelector('.t').textContent=m.t;el.querySelector('.d').textContent=m.d;el.addEventListener('click',function(){ov(false);show(st.at);});el.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();ov(false);show(st.at);}});box.appendChild(el);});
  Array.prototype.forEach.call(document.querySelectorAll('[data-go]'),function(el){el.addEventListener('click',function(){var want=el.getAttribute('data-go');var hit=starts.filter(function(s){return s.sec===want;})[0];show(hit?hit.at:0);});});
  function fit(){var s=Math.min(window.innerWidth/1280,window.innerHeight/720);document.documentElement.style.setProperty('--s',s);}function show(k){i=Math.max(0,Math.min(n-1,k));slots.forEach(function(s,x){s.classList.toggle('active',x===i);});document.getElementById('cur').textContent=i+1;document.querySelector('#bar i').style.width=((i+1)/n*100)+'%';if(location.hash!=='#'+(i+1))history.replaceState(null,'','#'+(i+1));}function next(){show(i+1);}function prev(){show(i-1);}function ov(on){var el=document.getElementById('ov');if(on===undefined)on=!el.classList.contains('on');el.classList.toggle('on',on);if(on)el.scrollTop=0;}
  window.addEventListener('resize',fit);document.addEventListener('keydown',function(e){var h=document.getElementById('help'),o=document.getElementById('ov');if(e.key==='Escape'){if(h.classList.contains('on')){h.classList.remove('on');return;}if(o.classList.contains('on')){ov(false);return;}}if(h.classList.contains('on'))return;switch(e.key){case 'ArrowRight':case ' ':case 'PageDown':e.preventDefault();if(!o.classList.contains('on'))next();break;case 'ArrowLeft':case 'PageUp':e.preventDefault();if(!o.classList.contains('on'))prev();break;case 'Home':e.preventDefault();ov(false);show(0);break;case 'End':e.preventDefault();ov(false);show(n-1);break;case 'o':case 'O':ov();break;case 'f':case 'F':if(!document.fullscreenElement){if(document.documentElement.requestFullscreen)document.documentElement.requestFullscreen();}else{document.exitFullscreen();}break;case '?':h.classList.add('on');break;}});
  document.getElementById('bNext').onclick=next;document.getElementById('bPrev').onclick=prev;document.getElementById('bOv').onclick=function(){ov();};document.getElementById('bFs').onclick=function(){if(!document.fullscreenElement){if(document.documentElement.requestFullscreen)document.documentElement.requestFullscreen();}else{document.exitFullscreen();}};document.getElementById('bHelp').onclick=function(){document.getElementById('help').classList.add('on');};document.getElementById('help').onclick=function(){this.classList.remove('on');};
  var uiTimer=null;function poke(){document.body.classList.add('ui-on');if(uiTimer)clearTimeout(uiTimer);uiTimer=setTimeout(function(){document.body.classList.remove('ui-on');},2200);}document.addEventListener('mousemove',poke);document.addEventListener('pointerdown',poke);document.addEventListener('touchstart',poke,{passive:true});fit();var start=parseInt((location.hash||'').replace('#',''),10);show(isNaN(start)?0:start-1);
})();`;

const extraCss = `
/* class required by the Kubernetes course specification; follows the template card language */
.loop4{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;align-items:stretch}
.loop4 .card{min-height:96px}.loop4 .card h4{font-size:16px}.loop4 .card p{font-size:13.5px}
`;

const html = `<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Kubernetes Session 3 — Application Deployment</title><style>${css}${extraCss}</style></head><body><div id="stage">${slides.join('\n')}</div>${chrome}<script>window.ASSETS=${JSON.stringify(assets)};<\/script><script>${script}<\/script></body></html>`;
fs.writeFileSync(target, html);
console.log(JSON.stringify({target,slides:slides.length,assets:Object.keys(assets).length,bytes:Buffer.byteLength(html)}));
