import json
import sys
from kafka import KafkaConsumer, KafkaProducer

# เกณฑ์แจ้งเตือน : อุณหภูมิตั้งแต่ 35.0 °C ขึ้นไปถือว่า "ร้อนผิดปกติ"
THRESHOLD = 35.0

def main():
    # ตั้งชื่อ processor ผ่าน argument เช่น `python processor.py P2` (ไม่ใส่ = P1)
    name = sys.argv[1] if len(sys.argv) > 1 else 'P1'

    # 1) โปรแกรมนี้เป็น "ทั้งผู้อ่านและผู้ส่ง" ในตัวเดียว — ท่ามาตรฐานของ microservice
    #    ฝั่งอ่าน : สมัครอ่าน topic 'sensor.readings' ในนาม group 'processors'
    consumer = KafkaConsumer('sensor.readings',
                             bootstrap_servers='localhost:9092',
                             group_id='processors',
                             auto_offset_reset='earliest')
    #    ฝั่งส่ง : เตรียม producer ไว้ส่งผลไป topic 'sensor.alerts'
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    print(f' [*] Processor {name} waiting (alert เมื่อ temp >= {THRESHOLD}). To exit press CTRL+C')

    assignment = None
    try:
        while True:
            # 2) poll ดึงค่าดิบชุดถัดไป (รอไม่เกิน 1 วินาทีต่อรอบ)
            batch = consumer.poll(timeout_ms=1000)

            #    พิมพ์ทุกครั้งที่ถูก "แบ่ง partition" ใหม่ — ไว้ดู rebalance ตอนเปิด processor เพิ่ม
            current = sorted(tp.partition for tp in consumer.assignment())
            if current and current != assignment:
                print(f' [*] Processor {name} ได้รับมอบหมาย partitions: {current}')
                assignment = current

            for tp, messages in batch.items():
                for message in messages:
                    # 3) bytes → JSON → dict แล้วตรวจค่า
                    reading = json.loads(message.value.decode())
                    temp = reading['temp']

                    if temp >= THRESHOLD:
                        # 4) ร้อนเกินเกณฑ์ → สร้าง event ใหม่ ส่งต่อเข้า topic 'sensor.alerts'
                        alert = {'sensor': reading['sensor'], 'temp': temp, 'level': 'HIGH'}
                        producer.send('sensor.alerts',
                                      key=reading['sensor'].encode(),
                                      value=json.dumps(alert).encode()).get(timeout=10)
                        print(f" [!] {name} ALERT {reading['sensor']} temp={temp} -> sensor.alerts")
                    else:
                        # 5) ค่าปกติ → แค่รับทราบ ไม่ส่งต่อ
                        print(f" [x] {name} OK    {reading['sensor']} temp={temp}")
    except KeyboardInterrupt:
        print(f' [*] Processor {name} leaving the group...')
    finally:
        # 6) ปิดให้เรียบร้อยทั้งสองฝั่ง : consumer บอกลา group (rebalance ทันที) · producer ส่งของค้างให้หมด
        consumer.close()
        producer.close()

if __name__ == '__main__':
    main()
