-- webhook_logs.sql — ดูประวัติการส่ง webhook ล่าสุดจากฐานข้อมูลของ Plane
-- ใช้: pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -f - < webhook_logs.sql
select to_char(l.created_at, 'HH24:MI:SS') as at, l.event_type, l.response_status, l.retry_count,
       left(coalesce(l.response_body, ''), 60) as response_body, w.url
  from webhook_logs l join webhooks w on w.id = l.webhook
 order by l.created_at desc limit 8;
