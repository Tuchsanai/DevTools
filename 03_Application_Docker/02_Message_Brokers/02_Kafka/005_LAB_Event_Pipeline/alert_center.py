import json
import sys
from kafka import KafkaConsumer

def main():
    # 1) ปลายทางของ pipeline : อ่านเฉพาะ topic 'sensor.alerts'
    #    ไม่ต้องรู้เลยว่าต้นทางมีกี่ sensor หรือ processor คิดยังไง — decoupling เต็มรูปแบบ
    consumer = KafkaConsumer('sensor.alerts',
                             bootstrap_servers='localhost:9092',
                             group_id='alert-center',
                             auto_offset_reset='earliest')

    print(' [*] Alert center waiting. To exit press CTRL+C')

    for message in consumer:
        # 2) แปลง JSON กลับเป็น dict แล้วประกาศเตือน
        alert = json.loads(message.value.decode())
        print(f" [!] 🚨 {alert['sensor']} ร้อนผิดปกติ! temp={alert['temp']} "
              f"(level={alert['level']})")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
