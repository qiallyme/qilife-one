let items = [];

// Navigation
function navigateTo(pageId) {
  document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
  document.getElementById(pageId).classList.add('active');
  logActivity(`Navigated to ${pageId}`);
}

// Quick Receipt logic
function addItem() {
  const name = document.getElementById('item-name').value.trim();
  const qty = parseFloat(document.getElementById('item-qty').value);
  const price = parseFloat(document.getElementById('item-price').value);

  if (!name || isNaN(qty) || isNaN(price)) return;

  items.push({ name, quantity: qty, price });
  document.getElementById('item-name').value = '';
  document.getElementById('item-qty').value = '';
  document.getElementById('item-price').value = '';

  updateReceipt();
  logActivity(`Item added: ${name} x${qty} @ $${price}`);
}

function updateReceipt() {
  const receiptDiv = document.getElementById('receipt-preview');
  let total = 0;

  const rows = items.map(item => {
    const subtotal = item.quantity * item.price;
    total += subtotal;
    return `<tr>
      <td>${item.name}</td>
      <td>${item.quantity}</td>
      <td>$${item.price.toFixed(2)}</td>
      <td>$${subtotal.toFixed(2)}</td>
    </tr>`;
  }).join('');

  receiptDiv.innerHTML = `
    <h2>Receipt</h2>
    <table>
      <thead>
        <tr><th>Item</th><th>Qty</th><th>Price</th><th>Subtotal</th></tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
    <p><strong>Total: $${total.toFixed(2)}</strong></p>
    <p>Signature: ___________________</p>
  `;

  // Save to vault
  window.electronAPI.saveReceipt({ items, total, notes: document.getElementById('item-notes').value });
}

function printReceipt() {
  window.print();
  logActivity("Receipt printed");
}

// Dark mode toggle
function toggleDarkMode() {
  document.body.classList.toggle('dark-mode');
  saveSettings();
  logActivity("Dark mode toggled");
}

// Settings auto-save
async function saveSettings() {
  const settings = {
    openaiKey: document.getElementById('openai-key').value,
    geminiKey: document.getElementById('gemini-key').value,
    twilioKey: document.getElementById('twilio-key').value,
    darkMode: document.body.classList.contains('dark-mode')
  };
  await window.electronAPI.saveSettings(settings);
  showSavedIndicator();
}

// Show saved indicator
function showSavedIndicator() {
  const indicator = document.getElementById('saved-indicator');
  indicator.classList.add('show');
  setTimeout(() => indicator.classList.remove('show'), 2000);
}

// Key visibility toggle
function toggleKeyVisibility(id) {
  const input = document.getElementById(id);
  input.type = input.type === 'password' ? 'text' : 'password';
}

// Activity feed
function logActivity(message) {
  const list = document.getElementById('activity-list');
  const li = document.createElement('li');
  li.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
  list.appendChild(li);
  list.scrollTop = list.scrollHeight;
}

// Hide/show feed
function toggleFeed() {
  const feed = document.getElementById('activity-feed');
  feed.style.display = feed.style.display === 'none' ? 'block' : 'none';
}

// File Flow
async function runFileFlow() {
  const output = await window.electronAPI.runFileFlow();
  document.getElementById('fileflow-output').textContent = output;
  logActivity("FileFlow executed");
}
