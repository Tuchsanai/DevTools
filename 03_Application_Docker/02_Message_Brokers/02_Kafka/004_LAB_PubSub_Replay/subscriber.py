import sys
from kafka import KafkaConsumer

def main():
    # 1) ชื่อกลุ่มมาจาก argument เช่น `python subscriber.py dashboard`
    #    นี่คือหัวใจของแล็บนี้ : คนละ group = ต่างคนต่างได้ "ครบทุกข้อความ" (pub/sub)
    #    group เดียวกัน = ช่วยกันแบ่งอ่าน (work queue แบบ LAB 3)
    if len(sys.argv) < 2:
        sys.exit('usage: python subscriber.py <group-name>')
    group = sys.argv[1]

    # 2) group ใหม่ที่ยังไม่เคยอ่านเลย + auto_offset_reset='earliest'
    #    → เริ่มอ่านตั้งแต่ข้อความแรกสุดใน log (มาทีหลังก็อ่านย้อนอดีตได้ทั้งหมด!)
    consumer = KafkaConsumer('logs',
                             bootstrap_servers='localhost:9092',
                             group_id=group,
                             auto_offset_reset='earliest')

    print(f' [*] Subscriber (group={group}) waiting. To exit press CTRL+C')

    # 3) Kafka จดให้เองว่า group นี้อ่านถึง offset ไหนแล้ว (commit อัตโนมัติ)
    #    ปิดโปรแกรมแล้วเปิดใหม่ จะอ่านต่อจากที่ค้างไว้ ไม่เริ่มนับหนึ่งใหม่
    for message in consumer:
        print(f' [x] group={group} got offset={message.offset} '
              f'value={message.value.decode()}')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
