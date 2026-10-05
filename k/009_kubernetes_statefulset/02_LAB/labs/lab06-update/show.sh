#!/usr/bin/env bash
# LAB 6–7: ดูว่าแต่ละบูธใช้ image รุ่นไหน / revision ไหน และสถานะ rollout ของ StatefulSet web
# ใช้:  ./show.sh          (ครั้งเดียว)
#       watch -n2 ./show.sh  (ดูต่อเนื่องทุก 2 วิ — กด Ctrl+C เพื่อออก)
kubectl get pod -l app=web -o custom-columns=NAME:.metadata.name,IMAGE:.spec.containers[0].image,REVISION:.metadata.labels.controller-revision-hash,READY:.status.containerStatuses[0].ready,CREATED:.metadata.creationTimestamp
kubectl get sts web -o jsonpath='currentRevision={.status.currentRevision}  updateRevision={.status.updateRevision}  updated={.status.updatedReplicas}/{.spec.replicas}{"\n"}'
