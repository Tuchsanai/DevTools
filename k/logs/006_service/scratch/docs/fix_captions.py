import json
p='/root/workspace/DevTools/k/logs/006_service/images.json'
raw=open(p,encoding='utf-8').read()
data=json.loads(raw)
new={
 'L06':'LAB4: nslookup web.shop.svc.cluster.local ได้ ClusterIP (ชื่อสั้น web ก็หาเจอ แต่ nslookup ของ busybox พิมพ์บรรทัด NXDOMAIN ปนและจบด้วย exit 1), ดู resolv.conf; Pod ที่สร้างก่อน Service ไม่มี WEB_SERVICE_HOST แต่ Pod ใหม่มี',
 'L13':'LAB9 (ต่อ): nslookup web-headless.shop.svc.cluster.local คืน Pod IP ทุกตัว เทียบกับ web.shop.svc.cluster.local ที่คืน ClusterIP เดียว; nslookup supplier.shop.svc.cluster.local (ExternalName) คืน CNAME example.com (ต้องมีเน็ตออก) แต่ wget ได้ 409 Conflict เพราะ Host header ไม่ตรง',
 'L14':'LAB9 (ต่อ): NetworkPolicy ให้ kitchen เข้า web ได้ที่ port 8080 (port ของ Service web-alt) → ยัง timed out; แก้เป็น port 80 (targetPort ของ Pod) → เข้าได้ และ policy นี้ทำให้ Pod อื่นนอก kitchen (client ใน shop) เข้า web ไม่ได้ด้วย',
 'L22':'LAB10: ลบ Pod db → ReplicaSet สร้างใหม่ในราว 5 วินาทีได้ IP ใหม่ แต่ชื่อ som-db/ClusterIP เดิม web ต่อใหม่เองโดยไม่ต้อง restart; emptyDir ว่าง หน้าเว็บ 503 "ร้านกำลังเตรียมสินค้า" → ลบ Pod web 1 ตัวให้ initContainer เติมสินค้าใหม่ → ทุกบูธกลับมาขาย แต่ออเดอร์ = 0',
 'L23':'LAB10: set image rs/som-web เป็น 1.3 → Pod เดิมยังเป็น 1.2; ลบ Pod ทีละตัวเอง (1.2/1.3 ปนกัน err 0–1) หรือลบทีเดียวทั้งหมด → ร้านสะดุดราว 2–4 วินาที hit.sh นับ err 4–7 ครั้ง (Connection reset by peer / Operation timed out)',
}
for it in data:
    if it['id'] in new:
        old=json.dumps(it['caption_th'],ensure_ascii=False)
        assert raw.count(old)==1,(it['id'],raw.count(old))
        raw=raw.replace(old,json.dumps(new[it['id']],ensure_ascii=False))
open(p,'w',encoding='utf-8').write(raw)
d2=json.loads(raw)
for a,b in zip(json.load(open('/root/workspace/DevTools/k/logs/006_service/scratch/docs/images.json.bak',encoding='utf-8')),d2):
    for k in a:
        if a[k]!=b[k]: print(a['id'],k,'changed')
