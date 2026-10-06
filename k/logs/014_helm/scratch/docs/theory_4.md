## 19. คำถามทบทวน

**1. ร้านที่ติดตั้งด้วย `kubectl apply -f` หลายไฟล์มีปัญหาอะไรบ้างเมื่ออยากเปิดสาขาที่ 2 และ Helm แก้ปัญหาใดได้ ปัญหาใดแก้ไม่ได้**

<details>
<summary>แนวคำตอบ</summary>

ปัญหา: ค่าเดียวกันซ้ำหลายไฟล์ (ชื่อ, label, image tag, host) ต้อง copy โฟลเดอร์แล้วแก้ทำให้เกิด drift ระหว่างสาขา ไม่มีรุ่นของทั้งชุด (rollout history มีแค่ Deployment) ต้องจำลำดับการ apply และจำว่ามีอะไรต้องลบ ไม่รู้ว่าใครติดตั้งอะไรไว้ Helm แก้ด้วย template + values (chart เดียวหลายใบสั่ง), release + revision (ย้อนทั้งร้าน), install/uninstall เป็นชุด, `helm list -A` ส่วนที่ Helm ไม่แก้: ไม่ดูแลแอปหลังติดตั้ง (backup, ซ่อม db — งานของ operator), ไม่แก้ drift ที่เกิดจากคนแก้ด้วยมือเอง (งานของ GitOps) และไม่ทำให้ความลับปลอดภัยขึ้นเอง (รหัสยังอยู่ใน release Secret)
</details>

**2. อธิบายความต่างของ chart, values, release และ revision โดยใช้ตัวอย่าง `som-shop` ในบทนี้**

<details>
<summary>แนวคำตอบ</summary>

chart = โฟลเดอร์ `charts/som-shop` (template + `values.yaml` + `Chart.yaml`) values = ใบสั่ง เช่น `values-dev.yaml` และ `--set db.password=...` release = chart + values ที่ติดตั้งแล้ว ระบุด้วยชื่อ + namespace เช่น release `som` ใน `som-dev` และ release `som` ใน `som-shop` (ชื่อซ้ำได้เพราะคนละ namespace) revision = เลขรุ่นของ release เช่น prod rev 1 failed → rev 2 deployed (รับร้าน) → rev 4 (1.8) → rev 5 `Rollback to 2`
</details>

**3. ทำไม Helm 2 (Tiller) จึงถูกมองว่าไม่ปลอดภัย และ Helm 3/4 ใช้สิทธิ์ของใครในการสร้าง object**

<details>
<summary>แนวคำตอบ</summary>

Tiller เป็น Pod ในคลัสเตอร์ที่รับคำสั่งจาก helm แล้วสร้าง object แทน มักได้สิทธิ์ cluster-admin ใครที่คุยกับ Tiller ได้ก็ทำได้ทุกอย่าง ข้ามระบบ RBAC ของผู้ใช้ Helm 3/4 ไม่มี Tiller helm คุยกับ kube-apiserver ด้วย kubeconfig ของผู้ใช้เอง สิทธิ์จึงเป็นไปตาม RBAC ของผู้ใช้ (บทที่ 11) และ release เก็บใน namespace ของ release
</details>

**4. `version` กับ `appVersion` ใน `Chart.yaml` ต่างกันอย่างไร ทำไมใน LAB 12 คอลัมน์ APP VERSION ของ `helm history` ยังเป็น 1.7 ทั้งที่หน้าร้านเป็น 1.8 แล้ว**

<details>
<summary>แนวคำตอบ</summary>

`version` คือรุ่นของ chart (ต้องเพิ่มเมื่อแก้ template/values) `appVersion` คือรุ่นของแอปข้างใน ใช้แสดงผลและเป็น image tag เริ่มต้นใน template ของเรา คอลัมน์ APP VERSION อ่านจาก `appVersion` ของ chart ที่ใช้ใน revision นั้น เราเปลี่ยนแค่ `--set web.image.tag=1.8` โดยใช้ chart 0.1.0 (appVersion 1.7) เดิม คอลัมน์จึงยังเป็น 1.7 ถ้าอยากให้ตรงต้องออก chart รุ่นใหม่ที่ `appVersion: "1.8"`
</details>

**5. อธิบาย `{{- include "som-shop.labels" . | nindent 4 }}` ทีละส่วน ถ้าเปลี่ยน `nindent 4` เป็น `indent 4` จะเกิดอะไร**

<details>
<summary>แนวคำตอบ</summary>

`{{-` ตัดช่องว่างและการขึ้นบรรทัดก่อนหน้าทิ้ง, `include "som-shop.labels" .` เรียกตรายางที่ define ไว้ใน `_helpers.tpl` โดยส่ง scope ทั้งหมด (`.`) ให้ ได้ข้อความ 5 บรรทัด, `| nindent 4` ขึ้นบรรทัดใหม่แล้วย่อหน้าทุกบรรทัด 4 ช่อง ให้อยู่ใต้ `labels:` ถูกระดับ ถ้าเป็น `indent 4` จะไม่ขึ้นบรรทัดใหม่ บวกกับ `{{-` ที่ตัดบรรทัดก่อนหน้าไปแล้ว บรรทัดแรกของ label จะไปต่อท้าย `labels:` เป็น `labels:    app.kubernetes.io/name: ...` ได้ YAML ผิด (`mapping values are not allowed in this context`) แบบ LAB 6
</details>

**6. ตรายาง `som-shop.dbPassword` เลือกรหัสอย่างไร ทำไม `helm template` ที่ไม่ใส่รหัสจึง error ทั้งที่ในคลัสเตอร์มี Secret อยู่แล้ว**

<details>
<summary>แนวคำตอบ</summary>

ลำดับ: ถ้าส่ง `--set db.password` ใช้ค่านั้น ไม่งั้น `lookup` Secret `<fullname>-db-secret` ใน namespace ของ release ถ้าเจอถอด `POSTGRES_PASSWORD` มาใช้ ถ้าไม่เจอ `required` หยุดด้วยข้อความภาษาไทย `helm template` (และ `lint`) ไม่ต่อคลัสเตอร์ `lookup` จึงคืนค่าว่างเสมอ จึงตกไปที่ `required` ส่วน `helm install/upgrade` ต่อคลัสเตอร์ `lookup` เห็น Secret จริง จึงรับร้านเดิมได้โดยไม่ต้องส่งรหัส
</details>

**7. ทำไมแม่พิมพ์ `web.yaml` จึงใส่ `checksum/config` ใน annotation ของ Pod template และถ้าใส่ไว้ที่ `metadata.annotations` ของ Deployment แทนจะได้ผลเหมือนกันไหม**

<details>
<summary>แนวคำตอบ</summary>

Pod ที่อ่าน ConfigMap ผ่าน envFrom ไม่เห็นค่าใหม่จนกว่าจะเกิดใหม่ checksum ของ ConfigMap ที่ render แล้วจะเปลี่ยนเมื่อค่าใน `shop.*`/announcement เปลี่ยน ทำให้ Pod template เปลี่ยน Deployment จึงทำ rolling update เอง (LAB 9 ได้ Pod ใหม่เอง) ถ้าใส่ที่ annotation ของ Deployment (ไม่ใช่ `spec.template`) Deployment controller ไม่ถือว่า Pod template เปลี่ยน จึงไม่สร้าง Pod ใหม่ ไม่ได้ผล
</details>

**8. ใน LAB 3 rev 3 สั่ง `helm upgrade hello podinfo/podinfo --set replicaCount=1` แล้ว Ingress หายและ curl ได้ 404 อธิบายสาเหตุ และบอก 2 วิธีป้องกัน**

<details>
<summary>แนวคำตอบ</summary>

upgrade ที่ส่ง values มา (แม้แค่ `--set` ตัวเดียว) คำนวณค่าใหม่จากค่าเริ่มต้นของ chart + สิ่งที่ส่งในคำสั่งนี้ ไม่ได้รวมกับค่าของ revision ก่อน ค่า `ingress.enabled: true` ที่มาจากไฟล์ `-f` ใน rev 2 จึงหายกลับเป็นค่าเริ่มต้น (`false`) Ingress ถูกลบ วิธีป้องกัน: ส่ง `-f podinfo-values.yaml` ทุกครั้งที่ upgrade หรือใช้ `--reuse-values` (หรือ `--reset-then-reuse-values` เมื่อเปลี่ยนรุ่น chart) ข้อควรรู้: ถ้า upgrade โดยไม่ส่งค่าอะไรเลย Helm 4.3 ใช้ค่าเดิมต่อ
</details>

**9. เครื่องมือตรวจ chart (`lint`, `template`, `--dry-run=server`, `kubectl apply --dry-run=server`) ต่างกันอย่างไร ใน LAB 6 ทำไม `helm install --dry-run=server --set service.type=NodePortt` จึงผ่าน**

<details>
<summary>แนวคำตอบ</summary>

`lint` ตรวจรูปแบบ chart และ YAML (ไม่ต่อคลัสเตอร์), `template` render ออกมาดู (ไม่ต่อคลัสเตอร์ lookup ว่าง), `--dry-run=server` ของ Helm ต่อคลัสเตอร์เพื่อให้ lookup ทำงานและตรวจ ownership/ชื่อชน แต่ไม่ได้ส่ง object ให้ API server ตรวจแบบ server-side dry run จึงไม่รู้ว่า `NodePortt` ไม่ใช่ค่าที่อนุญาต (ได้ `Dry run complete`) ส่วน `helm template | kubectl apply --dry-run=server -f -` ส่ง manifest ให้ API server validate จริง จึงจับได้ `spec.type: Unsupported value: "NodePortt"`
</details>

**10. Helm 4 ไม่ใส่ `--wait` จะเกิดอะไร ต่างจาก `--wait` และ `--rollback-on-failure` อย่างไร เลือกแบบไหนใน CI**

<details>
<summary>แนวคำตอบ</summary>

ไม่ใส่ = กลยุทธ์ `hookOnly` รอแค่ hook ส่ง manifest เสร็จก็ `deployed` (LAB 4: image ผิด 0.2 วินาทีได้ `deployed` แต่ Pod `ErrImagePull`) `--wait` (watcher) รอจน object พร้อมภายใน `--timeout` ถ้าไม่ทันได้ `failed` แต่ไม่ถอย `--rollback-on-failure` รอแบบเดียวกันและถ้าล้มจะ rollback ไปรุ่นที่ใช้อยู่เอง (LAB 4: ~43 วินาที rev 8 failed, rev 9 `Rollback to 7`) ใน CI นิยม `helm upgrade --install --wait --timeout <เวลาที่เหมาะ> --rollback-on-failure` ตามด้วย `helm test`
</details>

**11. ใน LAB 4 หลัง rev 9 (`Rollback to 7`) สั่ง `helm rollback hello` (ไม่ใส่เลข) แล้วร้านกลับไปพัง อธิบายว่าเพราะอะไร และ rollback เลขอะไรจึงถูก**

<details>
<summary>แนวคำตอบ</summary>

rollback ไม่ใส่เลข = ไป revision ก่อนหน้า (ก่อน rev 9 คือ rev 8) แม้ rev 8 จะเป็นรุ่นที่ `failed` (image ผิด) จึงได้ rev 10 `Rollback to 8` และ Pod ใหม่ `ErrImagePull` ที่ถูกคือดู `helm history` แล้วระบุเลขรุ่นที่ดี เช่น `helm rollback hello 9 --wait` (หรือ 7 หรือ 5 ซึ่งมีเนื้อหาเดียวกัน) ได้ rev 11
</details>

**12. field manager และ conflict ของ server-side apply คืออะไร ทำไม upgrade ครั้งแรกหลังรับร้าน (เปลี่ยน image เป็น 1.8) ยัง conflict ทั้งที่ตอนรับร้านใส่ `--force-conflicts` ไปแล้ว**

<details>
<summary>แนวคำตอบ</summary>

SSA จดว่าแต่ละ field เป็นของ manager ใด (`helm`, `kubectl-client-side-apply`, `kubectl`, `kube-controller-manager`) ถ้า manager หนึ่งจะตั้งค่า field ที่อีกคนถือด้วยค่าต่างกัน API server ตอบ conflict ตอนรับร้าน (rev 2) image ใน chart (`som-shop-web:1.7`) **ตรงกับ** ค่าที่ `kubectl-client-side-apply` ตั้งไว้ จึงไม่ conflict และ field image ยังมีเจ้าของร่วม พอ upgrade ตั้งเป็น 1.8 ค่าต่างจากที่ `kubectl-client-side-apply` ถือ จึง conflict (rev 3 failed) ต้อง `--force-conflicts` อีกครั้งเพื่อโอน field ให้ `helm` หลังจากนั้น upgrade/rollback ไม่ต้อง force
</details>

**13. ทำไมรับร้านน้องส้มเข้า Helm ได้ด้วย `--take-ownership --force-conflicts` แต่ Traefik ทำแบบเดียวกันไม่ได้ และทำไมห้าม `helm uninstall` release ที่ adopt ล้ม**

<details>
<summary>แนวคำตอบ</summary>

chart ร้านออกแบบชื่อและ selector (`app: som-web`) ให้ตรงกับของเดิม SSA จึงแค่ยึด field ที่ชน ส่วน Traefik chart ใช้ selector `app.kubernetes.io/name/instance` ต่างจาก static (`app: traefik`) และ `spec.selector` ของ Deployment เปลี่ยนไม่ได้ (`field is immutable`) ต้องลบของเดิมแล้วติดตั้งใหม่ (ประตูปิด ~19 วินาที) release ที่ adopt ล้มได้ติดป้าย Helm ให้บาง object ไปแล้ว (ServiceAccount, Service) `helm uninstall` จึงลบ object เหล่านั้นด้วย ทั้งที่มันคือของจริงที่ใช้งานอยู่ ประตูจะปิดทันที
</details>

**14. release Secret ของ Helm เก็บอะไรไว้ และถอดอย่างไร ใครควรมีสิทธิ์อ่าน และระบบจริงควรเก็บรหัสฐานข้อมูลอย่างไร**

<details>
<summary>แนวคำตอบ</summary>

Secret `sh.helm.release.v1.<release>.v<N>` type `helm.sh/release.v1` เก็บ JSON ของ release (chart, config = values ที่ส่ง, manifest = YAML ทุก object ที่ render แล้ว, hooks, info, version, apply_method) แบบ gzip + base64 (และ base64 อีกชั้นของ Secret) ถอดด้วย `base64 -d | base64 -d | gzip -d` จึงเห็นรหัสฐานข้อมูลและแม้แต่ `tls.key` ที่อยู่ใน manifest ย้อนหลัง 10 revision ควรให้สิทธิ์ `get secrets` เฉพาะผู้ดูแล namespace (RBAC) ระบบจริงไม่ส่งรหัสผ่าน values: ใช้ External Secrets, Sealed Secrets หรือ SOPS และไม่ commit รหัสลง git
</details>

**15. hook seed ของชุดร้านต่างจาก initContainer `db-seed` ของบท 009–013 อย่างไร และทำไมการติดตั้งสาขา dev ใหม่ด้วยรหัสใหม่จึงล้มที่ hook (หรือที่ som-web ถ้าใส่ `--wait`)**

<details>
<summary>แนวคำตอบ</summary>

initContainer รันทุกครั้งที่ Pod หน้าร้านเกิด (ทุกบูธ ทุก restart) hook Job `post-install,post-upgrade` รันครั้งเดียวหลัง install/upgrade และถูกลบเมื่อสำเร็จ (`hook-succeeded`) การติดตั้งใหม่หลัง uninstall ได้ PVC `data-som-db-0` เดิมที่ฐานข้อมูลถูกสร้างด้วยรหัสเก่า (postgres ตั้งรหัสแค่ตอนสร้าง data directory ครั้งแรก) Secret ใหม่มีรหัสใหม่ Job seed จึง login ไม่ได้ → `failed post-install ... Job Failed` ถ้าใส่ `--wait` Helm รอ som-web พร้อมก่อนถึง hook แต่หน้าร้านก็ต่อ db ไม่ได้ readinessProbe ไม่ผ่าน จึงล้มที่ `Deployment/som-dev/som-web not ready` ก่อน แก้ด้วย upgrade release ที่ failed ด้วยรหัสเดิม หรือลบ namespace (รวม PVC) แล้วเริ่มใหม่
</details>

**16. chart อยู่ใน OCI registry ได้เหมือน image ทำไมใน LAB 11 จึง install chart จาก `oci://localhost:5000` ได้ แต่ไม่ push image ของร้านเข้า registry เดียวกัน**

<details>
<summary>แนวคำตอบ</summary>

chart ถูกดึงโดย helm ที่รันใน k8s-lab ซึ่งมองเห็น `localhost:5000` (registry รันใน docker ของ k8s-lab) และใช้ credential จาก `helm registry login` ส่วน image ถูกดึงโดย containerd บน Node ของ kind ซึ่ง `localhost` คือตัว Node เอง มองไม่เห็น registry นั้น (ต้องตั้ง mirror ของ containerd) และใช้ `imagePullSecrets` ไม่ใช่ helm login
</details>

**17. จากกรณี Bitnami ปี 2568 ทีมควรมีแนวปฏิบัติอย่างไรในการเลือกและใช้ chart จากภายนอก**

<details>
<summary>แนวคำตอบ</summary>

เลือก chart ของเจ้าของโปรเจกต์/Verified Publisher, pin รุ่น chart และ image (ควรเป็น digest), อ่าน `helm show values` และ `helm template | grep image:` ก่อนติดตั้งเพื่อรู้ว่าดึง image จากไหน, เก็บสำเนา chart และ image ใน registry ขององค์กร, ติดตามประกาศของแหล่งที่ใช้และมีแผนย้าย, ไม่เปิดใช้ plugin/แหล่งที่ไม่ตรวจที่มาโดยไม่จำเป็น
</details>

**18. ถ้าทีมของคุณมีแอปภายในที่ deploy 3 environment (dev, staging, prod) ต่างกันแค่จำนวน replica, host และ resource ควรเลือก Kustomize หรือ Helm เพราะอะไร และ GitOps จะช่วยอะไรเพิ่ม**

<details>
<summary>แนวคำตอบ</summary>

ตอบได้ทั้งสองแบบถ้าให้เหตุผล: Kustomize เหมาะเพราะต่างกันเล็กน้อย YAML อ่านง่าย ไม่ต้องเรียนภาษา template แต่ไม่มี release/rollback ในตัว (พึ่ง git) Helm เหมาะถ้าต้องการ lifecycle (revision, rollback, hook, test), แจกให้ทีมอื่นติดตั้ง หรือมีเงื่อนไขเปิด/ปิดส่วนต่าง ๆ GitOps (Argo CD/Flux) ช่วยให้ Git เป็นแหล่งความจริง ทุกการเปลี่ยนผ่าน Pull Request มีรีวิวและประวัติ controller ทำให้คลัสเตอร์ตรงกับ Git เองและแก้ drift ไม่ต้องให้คนพิมพ์ `helm upgrade` และใช้ได้กับทั้ง Helm chart และ Kustomize
</details>

---

## 20. เอกสารอ้างอิง

1. The Helm Authors. *Helm 4 Overview* (server-side apply, plugin ใหม่, chart v3 ทดลอง, `--atomic` → `--rollback-on-failure`, `--force` → `--force-replace`). https://helm.sh/docs/overview/
2. The Helm Authors. *HIP-0023: Server Side Apply* (`--server-side=true|false|auto`, field manager `helm`, `--force-conflicts`). https://helm.sh/community/hips/hip-0023/
3. The Helm Authors. *Helm 4 Changelog* (4.1, 4.2, 4.3: `--wait` strategy, `helm test --logs`). https://helm.sh/docs/changelog/
4. The Helm Authors. *Release v4.3.0*. https://github.com/helm/helm/releases/tag/v4.3.0
5. The Helm Authors. *Helm v3 End of Life*. https://helm.sh/blog/helm-v3-end-of-life
6. The Helm Authors. *Charts* (Chart.yaml, version/appVersion, `crds/`, dependencies, schema). https://helm.sh/docs/topics/charts/
7. The Helm Authors. *Chart Template Guide* (built-in objects, values, functions and pipelines, flow control, named templates). https://helm.sh/docs/chart_template_guide/
8. The Helm Authors. *Template Function List* (รวม Sprig, `lookup`, `required`, `include`, `tpl`). https://helm.sh/docs/chart_template_guide/function_list/
9. The Helm Authors. *Chart Hooks* (hook 9 ชนิด, weight, delete policy). https://helm.sh/docs/topics/charts_hooks/
10. The Helm Authors. *Chart Tests*. https://helm.sh/docs/topics/chart_tests/
11. The Helm Authors. *Use OCI-based registries*. https://helm.sh/docs/topics/registries/
12. The Helm Authors. *Helm Provenance and Integrity*. https://helm.sh/docs/topics/provenance/
13. The Helm Authors. *Chart Best Practices* (values, labels, templates, dependencies). https://helm.sh/docs/chart_best_practices/
14. The Helm Authors. *Advanced Helm Techniques* (post rendering). https://helm.sh/docs/topics/advanced/
15. The Helm Authors. *helm upgrade* (`--reuse-values`, `--reset-then-reuse-values`, `--take-ownership`). https://helm.sh/docs/helm/helm_upgrade/
16. Masterminds. *Sprig Function Documentation*. https://masterminds.github.io/sprig/
17. The Go Authors. *Package text/template*. https://pkg.go.dev/text/template
18. The Kubernetes Authors. *Server-Side Apply* (field management, conflicts). https://kubernetes.io/docs/reference/using-api/server-side-apply/
19. The Kubernetes Authors. *Declarative Management of Kubernetes Objects Using Kustomize*. https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/
20. The Kubernetes Authors. *Operator pattern*. https://kubernetes.io/docs/concepts/extend-kubernetes/operator/
21. Artifact Hub (CNCF). https://artifacthub.io/
22. Traefik Labs. *Traefik Helm Chart* (Artifact Hub). https://artifacthub.io/packages/helm/traefik/traefik และ source https://github.com/traefik/traefik-helm-chart (repository https://traefik.github.io/charts)
23. Kubernetes SIGs. *metrics-server Helm chart* (Artifact Hub). https://artifacthub.io/packages/helm/metrics-server/metrics-server (repository https://kubernetes-sigs.github.io/metrics-server/)
24. Stefan Prodan. *podinfo*. https://github.com/stefanprodan/podinfo
25. Bitnami. *Upcoming changes to the Bitnami catalog (effective August 28th, 2025)*. https://github.com/bitnami/charts/issues/35164
26. databus23. *helm-diff plugin*. https://github.com/databus23/helm-diff
27. Argo Project. *Argo CD — Helm*. https://argo-cd.readthedocs.io/en/stable/user-guide/helm/
28. Flux Project. *Helm Releases*. https://fluxcd.io/flux/components/helm/helmreleases/
29. External Secrets Operator. https://external-secrets.io/
30. Bitnami Labs. *Sealed Secrets*. https://github.com/bitnami-labs/sealed-secrets
31. SOPS. https://github.com/getsops/sops

---

> **หมายเหตุเกี่ยวกับภาพประกอบ:** ภาพประกอบ 52 ภาพในโฟลเดอร์ [`images/`](images/) และภาพตัวละครน้องส้ม (`00-character-som.png`) สร้างขึ้นด้วยปัญญาประดิษฐ์สำหรับการสร้างภาพเพื่อใช้ประกอบการเรียนการสอน ชุดคำสั่งสร้างภาพอยู่ใน [`images/imagegen-prompts.md`](images/imagegen-prompts.md) ภาพใช้อุปมาเชิงเปรียบเทียบเพื่อช่วยความเข้าใจ ตัวเลขในภาพ (เช่น เลข revision, จำนวนวินาที, ชื่อ Pod) เป็นค่าตัวอย่าง ผู้เรียนควรใช้เนื้อหาในเอกสารนี้และเอกสารอ้างอิงเป็นหลัก ผลลัพธ์คำสั่งทั้งหมดมาจากการทดลองจริง (helm v4.3.0, Kubernetes v1.37.0, kubectl v1.37.1, เครื่องจำกัด 4 CPU) ค่าเวลา เลข revision และชื่อ Pod ในเครื่องผู้เรียนอาจต่างกัน รหัสผ่านทุกตัวในเอกสาร (`passwd`, `meow1234`, `meow-admin-123`, `meow-registry-123`) เป็นค่าตัวอย่างเพื่อการเรียนเท่านั้น
