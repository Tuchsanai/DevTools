ตัวอย่างจริงจาก build หลัง push (job ทดสอบ `verify-local/upstream-main` #2 ซึ่งอ่าน `Jenkinsfile` จาก GitHub `main` commit `e200b55` · ใน job `docker-build-push` ของคุณ path ของ workspace จะเป็น `/var/jenkins_home/workspace/docker-build-push`):

```text
Obtained 04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile from git https://github.com/Tuchsanai/DevTools.git
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins in /var/jenkins_home/workspace/verify-local/upstream-main
[Pipeline] {
[Pipeline] withEnv
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Connect)
```

[![Console Output หลัง push](./images/lab3_scm_08_console_obtained_crop.png)](./images/lab3_scm_08_console_obtained.png)

*ภาพที่ @C08@ Console Output ของ build ทดสอบหลัง push (`verify-local/upstream-main` #2): บรรทัด `Obtained .../Jenkinsfile from git https://github.com/Tuchsanai/DevTools.git` แล้วเข้า stage `(Connect)` ทันที ไม่มี `Declarative: Checkout SCM`*

[![stage ครบ 8 stage](./images/lab3_scm_09_stages_success_crop.png)](./images/lab3_scm_09_stages_success.png)

*ภาพที่ @C09@ หน้า Stages ของ build เดียวกัน: `SUCCESS` ใช้เวลา 28 วินาที Connect → Clone → Build → Test → Push → Clean → Pull → Deploy เขียวครบ ตามด้วย Post Actions · คลิกดูภาพเต็มซึ่งแสดงข้อความของ Post Actions: `docker.io/tuchsanai/catfood-shop@sha256:a33d7870…` ที่ deploy*

