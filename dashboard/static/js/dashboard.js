async function fetchJSON(url) {
  const res = await fetch(url);
  return res.json();
}

async function refreshDashboard() {
  const stats = await fetchJSON('/api/stats');
  document.getElementById('k-total').textContent = stats.total_attempts;
  document.getElementById('k-failed').textContent = stats.failed_attempts;
  document.getElementById('k-success').textContent = stats.successful_logins;
  document.getElementById('k-blocked').textContent = stats.blocked_count;

  const attempts = await fetchJSON('/api/attempts');
  const tbody = document.getElementById('attempts-tbody');
  if (attempts.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="empty-state">No login attempts yet</td></tr>';
  } else {
    tbody.innerHTML = attempts.map(a => `
      <tr>
        <td>${a.timestamp}</td>
        <td>${a.ip}</td>
        <td>${a.username}</td>
        <td><span class="badge ${a.result === 'FAIL' ? 'fail' : 'success'}">${a.result}</span></td>
      </tr>
    `).join('');
  }

  const blocked = await fetchJSON('/api/blocked');
  const blockedList = document.getElementById('blocked-list');
  if (blocked.length === 0) {
    blockedList.innerHTML = '<div class="empty-state">No IPs blocked</div>';
  } else {
    blockedList.innerHTML = blocked.map(ip => `
      <div class="blocked-row">🚫 ${ip}</div>
    `).join('');
  }
}

refreshDashboard();
setInterval(refreshDashboard, 3000); // auto-refresh every 3 seconds