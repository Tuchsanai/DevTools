set -v
# ออเดอร์ของนักศึกษาในบท 012 (ใช้ key product_id)
for i in 1 2 3; do curl -sk -XPOST -H "content-type: application/json" -d '{"product_id":4,"qty":1}' https://shop.localhost:30081/api/orders; echo; done
curl -sk https://shop.localhost:30081/api/stats; echo
