import sys
from kafka import KafkaConsumer

def main():
    # 1) สมัครเป็นผู้อ่าน topic 'hello'
    #    - auto_offset_reset='earliest' : เริ่มอ่านจากข้อความ "แรกสุด" ที่อยู่ใน log
    #    - ยังไม่ใส่ group_id : Kafka จะไม่จดว่าเราอ่านถึงไหน → รันใหม่ก็อ่านซ้ำได้ทั้งหมด
    consumer = KafkaConsumer('hello',
                             bootstrap_servers='localhost:9092',
                             auto_offset_reset='earliest')

    print(' [*] Waiting for messages. To exit press CTRL+C')

    # 2) วนรออ่านไปเรื่อย ๆ — มีข้อความใหม่เข้ามาเมื่อไหร่ loop ก็เดินต่อทันที
    for message in consumer:
        # 3) ทุกข้อความมี "ที่อยู่" ติดมาด้วยเสมอ : อยู่ partition ไหน ตำแหน่ง (offset) ที่เท่าไร
        #    ตัวเนื้อข้อความเป็น bytes ต้อง .decode() ก่อนพิมพ์
        print(f" [x] Received partition={message.partition} "
              f"offset={message.offset} value={message.value.decode()}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
