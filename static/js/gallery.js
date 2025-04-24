(() => {
  const rawBaseUrl = (window.BASE_URL && typeof window.BASE_URL === 'string')
    ? window.BASE_URL.trim()
    : '';
  const BASE_URL = (rawBaseUrl && !rawBaseUrl.includes('{{'))
    ? rawBaseUrl.replace(/\/$/, '')
    : window.location.origin.replace(/\/$/, '');

  const params = new URLSearchParams(window.location.search);
  let uid = params.get('uid') || '';
  const tg = window.Telegram?.WebApp;
  if (tg) {
    tg.ready();
    if (!uid) uid = String(tg.initDataUnsafe?.user?.id || '');
  }

  // Преобразует item.url в полный HTTPS-URL
  function buildSrc(url) {
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url.replace(/^http:\/\//, 'https://');
    }
    const path = url.startsWith('/') ? url : `/${url}`;
    return `${BASE_URL}${path}`;
  }

  let allItems = [];

  const hamburger     = document.getElementById('hamburger');
  const sidebar       = document.getElementById('sidebar');
  const loader        = document.getElementById('loader');
  const grid          = document.getElementById('grid');
  const datesList     = document.getElementById('datesList');
  const lb            = document.getElementById('lightbox');
  const lbImg         = document.getElementById('lb-img');
  const lbPrompt      = document.getElementById('lb-prompt');
  const lbCreatedAt   = document.getElementById('lb-created-at');
  const btnClose      = document.getElementById('lb-close');
  const btnPrev       = document.getElementById('lb-prev');
  const btnNext       = document.getElementById('lb-next');

  hamburger.addEventListener('click', () => {
    const opening = sidebar.hidden;
    sidebar.hidden = !opening;
    document.body.classList.toggle('sidebar-open', opening);
    hamburger.textContent = opening ? '×' : '☰';
  });

  if (!uid) {
    loader.textContent = '❗️Открывайте из Telegram';
    return;
  }

  fetch(`${BASE_URL}/api/images/?user_id=${encodeURIComponent(uid)}`)
    .then(res => {
      if (!res.ok) throw new Error('network');
      return res.json();
    })
    .then(data => {
      allItems = data;
      loader.remove();
      grid.hidden = false;
      initSidebar();
      renderGrid(allItems);
      tg?.expand();
    })
    .catch(err => {
      console.error('Fetch error:', err);
      loader.textContent = 'Ошибка загрузки';
    });

  function initSidebar() {
    const dates = [...new Set(allItems.map(i => i.created_at.split('T')[0]))]
      .sort((a, b) => b.localeCompare(a));
    dates.unshift('Все');
    dates.forEach(dateStr => {
      const li = document.createElement('li');
      li.textContent = dateStr;
      li.onclick = () => {
        datesList.querySelectorAll('li').forEach(el => el.classList.remove('active'));
        li.classList.add('active');
        filterByDate(dateStr);
      };
      datesList.append(li);
    });
    datesList.querySelector('li').classList.add('active');
  }

  function filterByDate(dateStr) {
    const filtered = dateStr === 'Все'
      ? allItems
      : allItems.filter(i => i.created_at.split('T')[0] === dateStr);
    renderGrid(filtered);
  }

  function renderGrid(items) {
    grid.innerHTML = '';
    items.forEach((item, idx) => {
      const div = document.createElement('div');
      div.className = 'item';

      const img = document.createElement('img');
      img.src = buildSrc(item.url);
      img.alt = item.prompt || '';
      img.onerror = () => { img.classList.add('broken'); };
      img.onclick = () => openLightbox(idx);

      const lbl = document.createElement('div');
      lbl.className = 'date-label';
      lbl.textContent = item.created_at.split('T')[0];

      div.append(img, lbl);
      grid.append(div);
    });
  }

  let currentIndex = 0;

  function openLightbox(idx) {
    currentIndex = idx;
    updateLightbox();
    lb.hidden = false;
  }

  function updateLightbox() {
    const { url, prompt, created_at } = allItems[currentIndex];
    const src = buildSrc(url);

    lbImg.classList.add('hide');
    setTimeout(() => {
      lbImg.src = src;
      void lbImg.offsetWidth;
      lbImg.classList.remove('hide');
      lbPrompt.textContent = prompt;
      lbCreatedAt.textContent = new Date(created_at).toLocaleString();
    }, 300);
  }

  btnClose.onclick = () => lb.hidden = true;
  lb.addEventListener('click', e => { if (e.target === lb) lb.hidden = true; });
  btnPrev.onclick = () => changeIndex(-1);
  btnNext.onclick = () => changeIndex(1);

  document.addEventListener('keydown', e => {
    if (lb.hidden) return;
    if (e.key === 'Escape') lb.hidden = true;
    if (e.key === 'ArrowLeft') changeIndex(-1);
    if (e.key === 'ArrowRight') changeIndex(1);
  });

  function changeIndex(delta) {
    const newIndex = currentIndex + delta;
    if (newIndex < 0 || newIndex >= allItems.length) return;
    currentIndex = newIndex;
    const cls = delta > 0 ? 'slide-in-right' : 'slide-in-left';
    lbImg.classList.add(cls);
    updateLightbox();
    lbImg.addEventListener('animationend', function handler() {
      lbImg.classList.remove('slide-in-right', 'slide-in-left');
      lbImg.removeEventListener('animationend', handler);
    });
  }

  let startX = 0, startY = 0;
  lb.addEventListener('pointerdown', e => { startX = e.clientX; startY = e.clientY; });
  lb.addEventListener('pointerup', e => handleSwipe(e.clientX - startX, e.clientY - startY));
  lb.addEventListener('touchstart', e => { startX = e.touches[0].clientX; startY = e.touches[0].clientY; });
  lb.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - startX;
    const dy = e.changedTouches[0].clientY - startY;
    handleSwipe(dx, dy);
  });

  function handleSwipe(dx, dy) {
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) {
      changeIndex(dx > 0 ? -1 : 1);
    } else if (Math.abs(dy) > 50 && Math.abs(dy) > Math.abs(dx)) {
      lb.hidden = true;
    }
  }
})();