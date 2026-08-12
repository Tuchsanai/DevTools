'use strict';

const express = require('express');
const morgan = require('morgan');
const path = require('path');

const app = express();
const port = Number.parseInt(process.env.PORT || '8080', 10);
const appVersion = process.env.APP_VERSION || 'development';

let nextId = 4;
const events = [
  { id: 1, title: 'Docker Workshop', detail: 'เรียนรู้การสร้าง image แบบหลาย stage', date: '2026-08-12' },
  { id: 2, title: 'Healthcheck Clinic', detail: 'ตรวจ readiness จาก endpoint จริง', date: '2026-08-13' },
  { id: 3, title: 'Registry Release', detail: 'tag, push และ pull อย่างเป็นระบบ', date: '2026-08-14' }
];

app.use(morgan('combined'));
app.use(express.json({ limit: '32kb' }));
app.use(express.static(__dirname));

app.get('/health', (request, response) => {
  response.status(200).json({
    status: 'ok',
    version: appVersion,
    uptimeSeconds: Math.floor(process.uptime())
  });
});

app.get('/api/events', (request, response) => {
  response.status(200).json(events);
});

app.post('/api/events', (request, response) => {
  const title = typeof request.body.title === 'string' ? request.body.title.trim() : '';
  const detail = typeof request.body.detail === 'string' ? request.body.detail.trim() : '';
  const date = typeof request.body.date === 'string' ? request.body.date : '';

  if (!title) {
    response.status(400).json({ error: 'title is required' });
    return;
  }

  const event = { id: nextId, title, detail, date };
  nextId += 1;
  events.push(event);
  response.status(201).json(event);
});

app.delete('/api/events/:eventId', (request, response) => {
  const eventId = Number.parseInt(request.params.eventId, 10);
  const index = events.findIndex((event) => event.id === eventId);

  if (index === -1) {
    response.status(404).json({ error: 'event not found' });
    return;
  }

  events.splice(index, 1);
  response.status(204).end();
});

app.get('*', (request, response) => {
  response.sendFile(path.join(__dirname, 'index.html'));
});

const server = app.listen(port, '0.0.0.0', () => {
  console.log(`Bulletin Board ${appVersion} listening on port ${port}`);
});

function shutdown(signal) {
  console.log(`${signal} received; shutting down`);
  server.close(() => process.exit(0));
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
