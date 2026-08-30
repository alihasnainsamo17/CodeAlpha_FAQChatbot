const form = document.getElementById('ask-form');
const input = document.getElementById('question');
const chat = document.getElementById('chat');

function addMessage(sender, text, meta) {
  const msg = document.createElement('div');
  msg.className = 'message ' + sender;
  msg.innerHTML = `<div class="text">${text}</div>`;
  if (meta) {
    const m = document.createElement('div');
    m.className = 'meta';
    m.textContent = meta;
    msg.appendChild(m);
  }
  chat.appendChild(msg);
  chat.scrollTop = chat.scrollHeight;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const q = input.value.trim();
  if (!q) return;
  addMessage('user', q);
  input.value = '';

  addMessage('bot', 'Thinking...');
  try {
    const res = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: q })
    });

    // Remove the last 'Thinking...' message
    const thinking = [...document.querySelectorAll('.message.bot')].pop();
    if (thinking && thinking.textContent.includes('Thinking')) thinking.remove();

    if (!res.ok) {
      const err = await res.json();
      addMessage('bot', err.error || 'Request failed');
      return;
    }

    const data = await res.json();
    addMessage('bot', data.answer, data.matched_question ? `Matched: "${data.matched_question}" (score: ${data.score})` : `score: ${data.score}`);
  } catch (err) {
    addMessage('bot', 'Network error. Please try again.');
  }
});
