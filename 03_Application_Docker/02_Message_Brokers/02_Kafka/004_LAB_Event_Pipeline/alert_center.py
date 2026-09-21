import json
from kafka import KafkaConsumer

def main():
    # 1) ปลายทางของ pipeline : อ่านเฉพาะ topic 'sensor.alerts'
    #    ไม่ต้องรู้เลยว่าต้นทางมีกี่ sensor หรือ processor คิดยังไง — decoupling เต็มรูปแบบ
    consumer = KafkaConsumer('sensor.alerts',
                             bootstrap_servers='localhost:9092',
                             group_id='alert-center',
                             auto_offset_reset='earliest')

    print(' [*] Alert center waiting. To exit press CTRL+C')

    try:
        for message in consumer:
            # 2) bytes → JSON → dict แล้วประกาศเตือน
            alert = json.loads(message.value.decode())
            print(f" [!] 🚨 {alert['sensor']} ร้อนผิดปกติ! temp={alert['temp']} "
                  f"(level={alert['level']}) offset={message.offset}")
    except KeyboardInterrupt:
        print(' [*] Alert center leaving the group...')
    finally:
        # 3) commit offset ล่าสุด + บอกลา broker ให้เรียบร้อย
        consumer.close()

if __name__ == '__main__':
    main()
