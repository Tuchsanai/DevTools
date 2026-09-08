# ผลตรวจความถูกต้อง YAML teaching ครั้งที่ 2 (yolo1 reviewer · kubectl explain/dry-run บน v1.36.4 + runlog)
## YAML_Guide.md — ต้องแก้
- ทั้งไฟล์ WARN: ไม่มีหัวข้อ "ทบทวน" Deployment + Ingress(ประตู) (spec 4b) → เพิ่มก่อน ## Service (10-20 บรรทัดต่อ object ใช้ YAML จากไฟล์จริงของครั้งนี้) และให้ README ชี้ anchor นั้น
- L5 NIT: หัวข้อ "## โครง object 5 บรรทัด" → ตั้งชื่อตามสเปก "## 0. อ่าน YAML ให้เป็น (สรุป)"
- L56 NIT: ประโยคติดกันหลัง cluster.local → ขึ้นประโยคใหม่ · L58 NIT: บอกว่า `kubectl get endpoints` จะมี Warning deprecated (v1.33+) หรือใช้ endpointslice ให้สม่ำเสมอ · L60 NIT: เพิ่มอาการจริง selector ผิด = `"error":"fetch failed"` (lab008 L265)
- L76-96, 125-144, 187-208, 241-257 WARN: บล็อก YAML ไม่มี comment ไทย (สเปก §4) และตัด comment ของไฟล์จริงทิ้ง → ใส่ comment ท้ายบรรทัด field สำคัญทุกบล็อก
- L89-96 NIT: ตัด imagePullPolicy/ports กลางบล็อกโดยไม่มี `# ...` → ใส่เครื่องหมายละ
- L156 WARN: Secret "ผิดบ่อย" มีข้อเดียวและเป็น error ระดับแอป → เพิ่ม secretKeyRef name/key ผิด → CreateContainerConfigError (describe pod) และ `data:` ใส่ข้อความไม่ใช่ base64 → error
- L173-183 WARN: ย่อหน้าถูกทำให้แบน (env/volumeMounts ระดับ container vs volumes ระดับ Pod อยู่คอลัมน์เดียวกัน) → แสดง containers:/- name: db เป็นบริบท หรือแยก 2 บล็อกระบุระดับ
- L216 WARN: accessModes ไม่ใช่ "ไม่มี default/เว้นได้" — บังคับ (`spec.accessModes: Required value: at least 1 access mode is required`) → "ต้องระบุ" · L217 WARN: resources.requests.storage บังคับเช่นกัน
- L224 NIT: ยก Event เต็ม `0/3 nodes are available: persistentvolumeclaim "db-data" not found.` (FailedScheduling)
- L261 NIT: "Pod เป็น NotReady" → "Ready condition = False (READY 0/1) แต่ STATUS ยัง Running"
- L274, 297 WARN: readinessProbe.exec ปรากฏครั้งแรกที่ 013/02-db.yaml L40-43 ไม่ใช่ 014 → แก้ตารางสรุป + ให้ README 013 ชี้ #probes
## README
- 008 L126 FAIL: ข้อความ `"error":"The operation was aborted due to timeout"` มาจากขั้น web ชี้ Pod IP เก่า (lab008 L96/L298) ไม่ใช่ selector ผิด — selector ผิดให้ `"error":"fetch failed"` (L265) → แก้ข้อความ/ระบุขั้นให้ถูก
- 011 L133 NIT: "restart ผู้ใช้ Secret" กำกวม → "rollout restart Deployment ที่อ้าง Secret"
- 012 L97-106 WARN: โครง YAML แบน (- name: PGDATA / volumeMounts / volumes คอลัมน์ 0) apply ไม่ได้และสอน parent ผิด → ใส่ env:/containers:/- name: db หรือแยกบล็อกระบุระดับ · L111 NIT: "PGDATA ต้องอยู่ใต้ mountPath มิฉะนั้นข้อมูลไม่ได้อยู่ใน volume" · L115 NIT: 503 เกิดตอน rollout db ชุด emptyDir (L111-113) ไม่ใช่หลัง delete pod ครั้งแรก
- 013 L96-137 WARN: 02-db.yaml มี readinessProbe.exec (pg_isready) และ strategy Recreate ที่ไม่ถูกกล่าวถึง → เพิ่ม 1 บรรทัด/แถว ชี้ [Probes](../YAML_Guide.md#probes) และ Recreate (เรียนครั้งที่ 1)
- 014 L126 NIT: "NotReady" → "READY 0/1 (Ready condition False)" · L102 NIT: อธิบาย `rollingUpdate: null` ใน 02-api-bad-readiness.yaml ว่าใช้ล้างค่าเดิมตอนสลับเป็น Recreate
- 009, 010: ผ่าน
## ยืนยันถูกต้อง: type default ClusterIP · targetPort default = port · nodePort ช่วง · DNS · ConfigMap string/envFrom/optional · Secret Opaque/stringData ทับ data · emptyDir อายุ Pod · storageClassName เว้น→standard · RWO/ROX/RWX · probe defaults (10/1/3/1/0, path /, liveness successThreshold ต้อง 1) · ข้อความ error ตรง runlog · anchor ครบ
