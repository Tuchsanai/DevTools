import sys
import time
from kafka import KafkaConsumer

def main():
    # ตั้งชื่อ worker ผ่าน argument เช่น `python worker.py A` (ไว้ดูว่าใครได้งานไหน)
    name = sys.argv[1] if len(sys.argv) > 1 else 'worker'

    # 1) จุดเปลี่ยนสำคัญของแล็บนี้ : ใส่ group_id='workers'
    #    ทุก worker ที่ใช้ group_id เดียวกัน = ทีมเดียวกัน → Kafka "แบ่ง partition" ให้ช่วยกันอ่าน
    #    และจดไว้ด้วยว่าทีมนี้อ่านถึง offset ไหนแล้ว (รันใหม่จะไม่อ่านซ้ำ)
    consumer = KafkaConsumer('tasks',
                             bootstrap_servers='localhost:9092',
                             group_id='workers',
                             auto_offset_reset='earliest')

    print(f' [*] Worker {name} waiting for tasks. To exit press CTRL+C')

    assignment = None
    while True:
        # 2) poll ดึงงานชุดถัดไป (รอไม่เกิน 1 วินาทีต่อรอบ)
        batch = consumer.poll(timeout_ms=1000)

        # 3) เช็กว่าโดน "แบ่ง partition" ใหม่หรือยัง — พิมพ์ทุกครั้งที่มีการเปลี่ยน (rebalance)
        current = sorted(tp.partition for tp in consumer.assignment())
        if current and current != assignment:
            print(f' [*] Worker {name} ได้รับมอบหมาย partitions: {current}')
            assignment = current

        # 4) ทำงานทีละข้อความ — sleep 1 วินาที = แกล้งทำเป็นงานที่ใช้เวลา
        for tp, messages in batch.items():
            for message in messages:
                print(f' [x] Worker {name} got p{message.partition} '
                      f'offset={message.offset} {message.value.decode()}')
                time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
