'use strict';

const eventsElement = document.querySelector('#events');
const formElement = document.querySelector('#event-form');
const messageElement = document.querySelector('#form-message');
const statusElement = document.querySelector('#api-status');

function escapeHtml(value) {
  const node = document.createElement('div');
  node.textContent = value || '';
  return node.innerHTML;
}

function renderEvents(events) {
  eventsElement.innerHTML = events.map((event) => `
    <article class="event-card" data-event-id="${event.id}">
      <div>
        <p class="event-date">${escapeHtml(event.date || 'ไม่ระบุวันที่')}</p>
        <h3>${escapeHtml(event.title)}</h3>
        <p>${escapeHtml(event.detail || 'ไม่มีรายละเอียด')}</p>
      </div>
      <button class="delete" data-delete-id="${event.id}" type="button">ลบ</button>
    </article>
  `).join('');
}

async function loadEvents() {
  const response = await fetch('/api/events');
  if (!response.ok) throw new Error(`GET /api/events returned ${response.status}`);
  renderEvents(await response.json());
}

async function checkHealth() {
  try {
    const response = await fetch('/health');
    const health = await response.json();
    statusElement.textContent = `API พร้อม · version ${health.version}`;
    statusElement.classList.add('healthy');
  } catch (error) {
    statusElement.textContent = 'API ยังไม่พร้อม';
    statusElement.classList.add('unhealthy');
  }
}

formElement.addEventListener('submit', async (event) => {
  event.preventDefault();
  messageElement.textContent = 'กำลังบันทึก…';

  const payload = Object.fromEntries(new FormData(formElement));
  const response = await fetch('/api/events', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    messageElement.textContent = `บันทึกไม่สำเร็จ (${response.status})`;
    return;
  }

  formElement.reset();
  messageElement.textContent = 'เพิ่มกิจกรรมแล้ว';
  await loadEvents();
});

eventsElement.addEventListener('click', async (event) => {
  const button = event.target.closest('[data-delete-id]');
  if (!button) return;

  const response = await fetch(`/api/events/${button.dataset.deleteId}`, { method: 'DELETE' });
  if (response.status === 204) await loadEvents();
});

document.querySelector('#refresh').addEventListener('click', loadEvents);

Promise.all([checkHealth(), loadEvents()]).catch((error) => {
  eventsElement.innerHTML = `<p class="error">โหลดข้อมูลไม่สำเร็จ: ${escapeHtml(error.message)}</p>`;
});
