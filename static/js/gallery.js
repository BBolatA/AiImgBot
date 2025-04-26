(() => {
  const copyNotif = document.createElement('div');
  copyNotif.className = 'copy-notification';
  copyNotif.textContent = 'Промпт скопирован';
  document.body.appendChild(copyNotif);
  function showNotification() {
    copyNotif.classList.add('show');
    setTimeout(() => copyNotif.classList.remove('show'), 1500);
  }

  const hamburger = document.getElementById('hamburger');
  const sidebar   = document.getElementById('sidebar');
  hamburger.addEventListener('click', () => {
    const opening = sidebar.hidden;
    sidebar.hidden = !opening;
    document.body.classList.toggle('sidebar-open', opening);
    hamburger.textContent = opening ? '×' : '☰';
  });

  const io = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        obs.unobserve(img);
      }
    });
  }, {
    rootMargin: '200px 0px'
  });

  const loader    = document.getElementById('loader');
  const grid      = document.getElementById('grid');
  const datesList = document.getElementById('datesList');
  let allItems    = [];
  let pswpItems   = [];

  const params = new URLSearchParams(window.location.search);
  let uid = params.get('uid') || '';
  const tg = window.Telegram?.WebApp;
  if (tg) {
    tg.ready();
    if (!uid) uid = String(tg.initDataUnsafe?.user?.id || '');
  }
  if (!uid) {
    loader.textContent = '❗️Открывайте из Telegram';
    return;
  }

  function buildSrc(url) {
    if (/^https?:\/\//.test(url)) return url.replace(/^http:\/\//, 'https://');
    const raw = (window.BASE_URL && typeof window.BASE_URL === 'string')
      ? window.BASE_URL.trim().replace(/\/$/, '')
      : window.location.origin.replace(/\/$/, '');
    return `${raw}${url.startsWith('/') ? url : '/' + url}`;
  }

  fetch(`${buildSrc('/api/v1/generation/images/')}?user_id=${encodeURIComponent(uid)}`)
    .then(res => res.ok ? res.json() : Promise.reject('network'))
    .then(data => {
      allItems  = data;
      pswpItems = data.map(item => ({
        src:   buildSrc(item.url),
        w:     item.width  || window.innerWidth,
        h:     item.height || window.innerHeight,
        prompt: item.prompt,
        title: `<strong>Промпт:</strong> ${item.prompt}<br>` +
               `<strong>Время:</strong> ${new Date(item.created_at).toLocaleString()}`
      }));
      loader.remove();
      grid.hidden = false;
      initSidebar();
      renderGrid(allItems);
      tg?.expand();
    })
    .catch(err => {
      console.error(err);
      loader.textContent = 'Ошибка загрузки';
    });

  function initSidebar() {
    const dates = [...new Set(allItems.map(i => i.created_at.split('T')[0]))]
      .sort((a, b) => b.localeCompare(a));
    dates.unshift('Все');
    dates.forEach(d => {
      const li = document.createElement('li');
      li.textContent = d;
      li.onclick = () => {
        datesList.querySelectorAll('li').forEach(x => x.classList.remove('active'));
        li.classList.add('active');
        filterByDate(d);
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
      img.alt = item.prompt;
      img.setAttribute('loading', 'lazy');
      img.dataset.src = buildSrc(item.url);
      img.onerror = () => img.classList.add('broken');
      img.onclick = () => openPhotoSwipe(idx);

      io.observe(img);

      const lbl = document.createElement('div');
      lbl.className = 'date-label';
      lbl.textContent = item.created_at.split('T')[0];

      div.append(img, lbl);
      grid.append(div);
    });
  }

  function openPhotoSwipe(index) {
    const pswpElement = document.querySelector('.pswp');
    const options = { index, showHideOpacity: true, history: false };
    const gallery = new PhotoSwipe(pswpElement, PhotoSwipeUI_Default, pswpItems, options);

    const setupSharePopup = () => {
      const shareBtn = pswpElement.querySelector('.pswp__button--share');
      if (!shareBtn) return;
      shareBtn.onclick = e => {
        e.preventDefault();
        if (document.getElementById('share-popup')) return;
        const popup = document.createElement('div');
        popup.id = 'share-popup';
        popup.style.position = 'absolute';
        const rect = shareBtn.getBoundingClientRect();
        popup.style.top = (rect.bottom + 8) + 'px';
        popup.style.left = rect.left + 'px';
        popup.style.background = '#333';
        popup.style.border = '1px solid #555';
        popup.style.borderRadius = '6px';
        popup.style.padding = '8px';
        popup.style.boxShadow = '0 2px 6px rgba(0,0,0,0.5)';
        popup.style.zIndex = 2001;
        popup.style.pointerEvents = 'auto';

        const wa = document.createElement('div');
        wa.textContent = 'WhatsApp';
        wa.style.margin = '4px 0';
        wa.style.cursor = 'pointer';
        wa.onclick = () => {
          const i = gallery.getCurrentIndex();
          const item = pswpItems[i];
          window.open(`https://wa.me/?text=${encodeURIComponent(item.prompt + ' ' + item.src)}`, '_blank');
          popup.remove();
        };

        const tgShare = document.createElement('div');
        tgShare.textContent = 'Telegram';
        tgShare.style.margin = '4px 0';
        tgShare.style.cursor = 'pointer';
        tgShare.onclick = () => {
          const i = gallery.getCurrentIndex();
          const item = pswpItems[i];
          window.open(`https://t.me/share/url?url=${encodeURIComponent(item.src)}&text=${encodeURIComponent(item.prompt)}`, '_blank');
          popup.remove();
        };

        popup.append(wa, tgShare);
        document.body.append(popup);
      };
      document.addEventListener('click', e => {
        const popup = document.getElementById('share-popup');
        if (popup && !popup.contains(e.target) && !e.target.closest('.pswp__button--share')) {
          popup.remove();
        }
      });
    };

    gallery.listen('initialZoomInEnd', setupSharePopup);
    gallery.listen('afterChange', setupSharePopup);
    gallery.init();
  }
})();
