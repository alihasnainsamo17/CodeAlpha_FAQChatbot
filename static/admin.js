async function fetchFaqs() {
  const res = await fetch('/faqs');
  return res.json();
}

function el(tag, cls, txt) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (txt !== undefined) e.textContent = txt;
  return e;
}

async function renderFaqs() {
  const container = document.getElementById('faqs');
  container.innerHTML = '';
  const faqs = await fetchFaqs();
  if (!faqs || faqs.length === 0) {
    container.textContent = 'No FAQs yet.';
    return;
  }

  faqs.forEach(f => {
    const box = el('div', 'faq-item');
    const q = el('div', 'faq-question', f.question);
    const a = el('div', 'faq-answer', f.answer);

    const btnEdit = el('button', '', 'Edit');
    const btnDel = el('button', '', 'Delete');

    btnEdit.addEventListener('click', () => editFaq(f));
    btnDel.addEventListener('click', () => deleteFaq(f.id));

    const controls = el('div', 'faq-controls');
    controls.appendChild(btnEdit);
    controls.appendChild(btnDel);

    box.appendChild(q);
    box.appendChild(a);
    box.appendChild(controls);
    container.appendChild(box);
  });
}

async function addFaq(question, answer) {
  const res = await fetch('/faqs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, answer })
  });
  return res.json();
}

async function editFaq(f) {
  const newQ = prompt('Edit question:', f.question);
  if (newQ === null) return;
  const newA = prompt('Edit answer:', f.answer);
  if (newA === null) return;

  await fetch(`/faqs/${f.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: newQ, answer: newA })
  });
  await renderFaqs();
}

async function deleteFaq(id) {
  if (!confirm('Delete this FAQ?')) return;
  await fetch(`/faqs/${id}`, { method: 'DELETE' });
  await renderFaqs();
}

document.getElementById('add-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const q = document.getElementById('new-question').value.trim();
  const a = document.getElementById('new-answer').value.trim();
  if (!q || !a) return alert('Question and answer are required.');
  await addFaq(q, a);
  document.getElementById('new-question').value = '';
  document.getElementById('new-answer').value = '';
  await renderFaqs();
});

// Initial load
renderFaqs();
