import json
import sys
from kafka import KafkaConsumer, KafkaProducer

# เกณฑ์แจ้งเตือน : อุณหภูมิตั้งแต่ 35.0 °C ขึ้นไปถือว่า "ร้อนผิดปกติ"
THRESHOLD = 35.0

def main():
    # 1) โปรแกรมนี้เป็น "ทั้งผู้อ่านและผู้ส่ง" ในตัวเดียว — ท่ามาตรฐานของ microservice
    #    ฝั่งอ่าน : สมัครอ่าน topic 'sensor.readings' ในนาม group 'processors'
    consumer = KafkaConsumer('sensor.readings',
                             bootstrap_servers='localhost:9092',
                             group_id='processors',
                             auto_offset_reset='earliest')

    #    ฝั่งส่ง : เตรียม producer ไว้ส่งผลไป topic 'sensor.alerts'
    producer = KafkaProducer(bootstrap_servers='localhost:9092')

    print(f' [*] Processor waiting (alert เมื่อ temp >= {THRESHOLD}). To exit press CTRL+C')

    for message in consumer:
        # 2) bytes → JSON → dict แล้วตรวจค่า
        reading = json.loads(message.value.decode())
        temp = reading['temp']

        if temp >= THRESHOLD:
            # 3) ร้อนเกินเกณฑ์ → สร้าง event แจ้งเตือน ส่งต่อเข้า topic 'sensor.alerts'
            alert = {'sensor': reading['sensor'], 'temp': temp, 'level': 'HIGH'}
            producer.send('sensor.alerts',
                          key=reading['sensor'].encode(),
                          value=json.dumps(alert).encode()).get(timeout=10)
            print(f" [!] ALERT {reading['sensor']} temp={temp} -> ส่งต่อเข้า sensor.alerts")
        else:
            # 4) ค่าปกติ → แค่รับทราบ ไม่ส่งต่อ
            print(f" [x] OK    {reading['sensor']} temp={temp}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
