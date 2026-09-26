docker ps -a --filter label=devtools.lab=lab3 --format '{{.Names}}' | xargs -r docker rm -f    # catfood-web และ catfood-test-N ที่มี label ของ LAB 3 เท่านั้น
docker image ls -aq --filter label=devtools.lab=lab3 | sort -u | xargs -r docker image rm -f    # image ที่ build/pull จาก Jenkinsfile นี้ (มี label devtools.lab=lab3) เท่านั้น image อื่นแม้ชื่อ catfood-shop จะไม่ถูกลบ
rm -rf /root/lab3-work /tmp/lab3-docker-*        # ซอร์สที่ clone และ login ชั่วคราวที่อาจค้างเมื่อ build ถูกยกเลิกกลางทาง
docker ps -a --format '{{.Names}}'; docker network ls --filter name=cicd-net --format '{{.Name}}'; docker volume ls -q --filter name=jenkins_home
