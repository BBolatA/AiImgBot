document.addEventListener('DOMContentLoaded', () => {
  if (!window.Chart) {
    alert('Chart.js не загрузился.');
    return;
  }

  const uid =
    document.body.dataset.uid ||
    new URLSearchParams(location.search).get('uid') ||
    window.Telegram?.WebApp?.initDataUnsafe?.user?.id ||
    localStorage.getItem('tg_uid') || '';

  if (!uid) {
    alert('UID не найден');
    return;
  }
  localStorage.setItem('tg_uid', uid);

  const buttons= document.querySelectorAll('.btn, .filter button');
  const ctxDaily= document.getElementById('daily');
  const ctxStyles= document.getElementById('styles');
  const ctxModels= document.getElementById('models');

  let chartDaily, chartStyles, chartModels;

  const apiUrl = days =>
    `/api/v1/generation/full_stats/?user_id=${uid}&period=${days}`;

  async function fetchData(days) {
    try {
      const response = await fetch(apiUrl(days));
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const json = await response.json();
      draw(json);
    } catch (err) {
      alert('Ошибка загрузки данных: ' + err.message);
    }
  }

  function destroyOld() {
    [chartDaily, chartStyles, chartModels].forEach(c => c && c.destroy());
  }

  function draw(data) {
    destroyOld();

    chartDaily = new Chart(ctxDaily, {
      type: 'bar',
      data: {
        labels: data.by_date.map(o => o.date),
        datasets: [{ data: data.by_date.map(o => o.count), label: 'в день' }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#aaa' } },
          y: { ticks: { color: '#aaa' }, beginAtZero: true }
        }
      }
    });

    const makeLegend = (canvas, chart) => {
      const card = canvas.parentElement;
      card.querySelectorAll('.my-legend').forEach(el => el.remove());
      const ul = document.createElement('ul');
      ul.className = 'my-legend';
      ul.style.cssText = 'list-style:none;padding:0;margin:16px 0 0;font-size:13px;line-height:1.4';
      const meta = chart.getDatasetMeta(0);
      chart.data.labels.forEach((lbl, i) => {
        const li = document.createElement('li');
        li.style.cssText = 'display:flex;align-items:center;margin-bottom:4px';
        const sw = document.createElement('span');
        sw.style.cssText =
          `width:12px;height:12px;border-radius:3px;display:inline-block;margin-right:6px;` +
          `background:${meta.controller.getStyle(i).backgroundColor}`;
        const tx = document.createElement('span');
        tx.textContent = String(lbl).substring(0, 40);
        li.append(sw, tx);
        ul.append(li);
      });
      card.append(ul);
    };

    chartStyles = new Chart(ctxStyles, {
      type: 'doughnut',
      data: {
        labels: data.by_style.map(o => o.label),
        datasets: [{ data: data.by_style.map(o => o.count) }]
      },
      options: { responsive: true, plugins: { legend: { display: false } } }
    });
    makeLegend(ctxStyles, chartStyles);

    chartModels = new Chart(ctxModels, {
      type: 'pie',
      data: {
        labels: data.by_model.map(o => o.label),
        datasets: [{ data: data.by_model.map(o => o.count) }]
      },
      options: { responsive: true, plugins: { legend: { display: false } } }
    });
    makeLegend(ctxModels, chartModels);
  }

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('btn--active', 'active'));
      btn.classList.add('btn--active');
      fetchData(+btn.dataset.d || 0);
    });
  });

  fetchData(30);
});
