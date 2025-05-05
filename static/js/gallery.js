(async () => {
  const notif = document.createElement('div');
  notif.className = 'copy-notification';
  notif.textContent = 'Промпт скопирован';
  document.body.appendChild(notif);
  const showNotif = () => {
    notif.classList.add('show');
    setTimeout(() => notif.classList.remove('show'), 1500);
  };

  const tg = window.Telegram?.WebApp;
  if (!tg) {
    document.getElementById('loader').textContent = '❗️Откройте из Telegram-бота';
    return;
  }
  tg.ready();
  await new Promise(r => requestAnimationFrame(r));

  const initData = tg.initData;
  if (!initData) {
    document.getElementById('loader').textContent = '❗️Telegram не передал initData';
    return;
  }

  async function getJwt() {
    let tok = localStorage.getItem('jwt');
    if (tok) return tok;

    const resp = await fetch('/api/v1/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ initData })
    });
    if (!resp.ok) throw new Error(`auth ${resp.status}`);
    tok = (await resp.json()).token;
    localStorage.setItem('jwt', tok);
    return tok;
  }

  let JWT;
  try {
    JWT = await getJwt();
  } catch (e) {
    document.getElementById('loader').textContent = 'Ошибка авторизации';
    return;
  }
  const AUTH_HEADERS = { Authorization: `Bearer ${JWT}` };
  const loader = document.getElementById('loader');
  const grid   = document.getElementById('grid');
  const datesList = document.getElementById('datesList');

  const buildSrc = url => {
    if (/^https?:\/\//.test(url)) return url.replace(/^http:\/\//, 'https://');
    const base = (window.BASE_URL && typeof window.BASE_URL === 'string')
      ? window.BASE_URL.trim().replace(/\/$/, '')
      : location.origin.replace(/\/$/, '');
    return `${base}${url.startsWith('/') ? url : '/' + url}`;
  };

  const io = new IntersectionObserver((entries, obs) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const img = e.target;
        img.src = img.dataset.src;
        obs.unobserve(img);
      }
    });
  }, { rootMargin: '200px 0px' });

  let allItems = [];
  let pswpItems = [];

  /* загрузка данных */
  fetch('/api/v1/generation/images/', { headers: AUTH_HEADERS })
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(data => {
      if (!data.length) {
        loader.textContent = 'Нет изображений';
        return;
      }

      allItems = data;
      pswpItems = data.map(it => ({
        src: buildSrc(it.url),
        w: it.width  || 800,
        h: it.height || 800,
        prompt: it.prompt,
        title:
          `<strong>Промпт:</strong> ${it.prompt}<br>` +
          `<strong>Время:</strong> ${new Date(it.created_at).toLocaleString()}`
      }));

      loader.remove();
      grid.hidden = false;
      initSidebar();
      renderGrid(allItems);
      tg.expand?.();
    })
    .catch(() => {
      loader.textContent = 'Ошибка загрузки';
    });

  function initSidebar() {
    if (!datesList) return;
    const dates = [...new Set(allItems.map(i => i.created_at.split('T')[0]))]
      .sort((a, b) => b.localeCompare(a));
    dates.unshift('Все');

    dates.forEach(d => {
      const li = document.createElement('li');
      li.textContent = d;
      li.onclick = () => {
        datesList.querySelectorAll('li').forEach(x => x.classList.remove('active'));
        li.classList.add('active');
        const filtered = d === 'Все'
          ? allItems
          : allItems.filter(i => i.created_at.split('T')[0] === d);
        renderGrid(filtered);
      };
      datesList.append(li);
    });
    datesList.firstChild.classList.add('active');
  }

  function renderGrid(items) {
    grid.innerHTML = '';
    items.forEach(item => {
      const div = document.createElement('div');
      div.className = 'item';

      const img = document.createElement('img');
      img.alt = item.prompt;
      img.dataset.src = buildSrc(item.url);
      img.loading = 'lazy';
      img.onerror = () => img.classList.add('broken');
      img.onclick  = () => openPhotoSwipe(allItems.indexOf(item));

      io.observe(img);

      const lbl = document.createElement('div');
      lbl.className = 'date-label';
      lbl.textContent = item.created_at.split('T')[0];

      div.append(img, lbl);
      grid.append(div);
    });
  }

  function openPhotoSwipe(index) {
    const el = document.querySelector('.pswp');
    const gallery = new PhotoSwipe(
      el, PhotoSwipeUI_Default, pswpItems,
      { index, showHideOpacity: true, history: false }
    );
    gallery.listen('initialZoomInEnd', setupShare);
    gallery.listen('afterChange',      setupShare);
    gallery.init();
  }

  function setupShare() {
    const pswpEl  = document.querySelector('.pswp');
    const shareBtn = pswpEl.querySelector('.pswp__button--share');
    if (!shareBtn || shareBtn.dataset.ready) return;
    shareBtn.dataset.ready = '1';

    shareBtn.onclick = e => {
      e.preventDefault();
      if (document.getElementById('share-popup')) return;

      const popup = document.createElement('div');
      popup.id = 'share-popup';
      Object.assign(popup.style, {
        position: 'absolute',
        background: '#333', border: '1px solid #555',
        borderRadius: '6px', padding: '8px',
        boxShadow: '0 2px 6px rgba(0,0,0,.5)', zIndex: 2001
      });
      const r = shareBtn.getBoundingClientRect();
      popup.style.top  = `${r.bottom + 8}px`;
      popup.style.left = `${r.left}px`;

      const makeBtn = (txt, cb) => {
        const d = document.createElement('div');
        d.textContent = txt;
        Object.assign(d.style, { margin: '4px 0', cursor: 'pointer' });
        d.onclick = cb;
        popup.appendChild(d);
      };

      makeBtn('WhatsApp', () => {
        const i = pswpEl.pswp.currItem.index;
        const item = pswpItems[i];
        window.open(
          `https://wa.me/?text=${encodeURIComponent(item.prompt + ' ' + item.src)}`,
          '_blank'
        );
        popup.remove();
      });
      makeBtn('Telegram', () => {
        const i = pswpEl.pswp.currItem.index;
        const item = pswpItems[i];
        window.open(
          `https://t.me/share/url?url=${encodeURIComponent(item.src)}&text=${encodeURIComponent(item.prompt)}`,
          '_blank'
        );
        popup.remove();
      });

      document.body.appendChild(popup);
    };

    document.addEventListener('click', e => {
      const pop = document.getElementById('share-popup');
      if (pop && !pop.contains(e.target) && !e.target.closest('.pswp__button--share')) {
        pop.remove();
      }
    });
  }
})();
