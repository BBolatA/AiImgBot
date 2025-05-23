(async () => {
  const NAV_HEIGHT = 84;
  const SHEET_RADIUS = 12;

  const $ = s => document.querySelector(s);

  const buildSrc = u =>
    /^https?:\/\//.test(u)
      ? u.replace(/^http:\/\//, 'https://')
      : (window.BASE_URL?.replace(/\/$/, '') || location.origin) +
        (u.startsWith('/') ? u : '/' + u);

  const io = new IntersectionObserver(
    (en, o) => en.forEach(e => {
      if (e.isIntersecting) { e.target.src = e.target.dataset.src; o.unobserve(e.target); }
    }),
    { rootMargin: '200px 0px' }
  );

  const loader = $('#loader');
  const grid = $('#grid');
  const fab = $('#filterBtn');
  const sheetWrap = $('#filterSheet');
  const sheet = sheetWrap.querySelector('.sheet');
  const sheetTabs = $('#sheetTabs');
  const sheetList = $('#sheetOptions');
  const sheetClose = $('#sheetClose');
  const sheetReset = $('#sheetReset');
  const chipBar = document.createElement('div');
  chipBar.id = 'filterChips';
  chipBar.className = 'filter-chips';
  grid.parentElement.insertBefore(chipBar, grid);

  const notif = document.createElement('div');
  notif.className = 'copy-notification';
  document.body.appendChild(notif);
  const toast = txt => { notif.textContent = txt; notif.classList.add('show');
                         setTimeout(()=>notif.classList.remove('show'),1500); };

  const tg = window.Telegram?.WebApp;
  if (!tg) return (loader.textContent = '❗️Откройте из Telegram-бота');
  tg.ready(); await new Promise(r => requestAnimationFrame(r));
  if (!tg.initData) return (loader.textContent = '❗️Telegram не передал initData');

  async function getJwt () {
    let t = localStorage.getItem('jwt');
    if (t) return t;
    const r = await fetch('/api/v1/auth/login/', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({ initData: tg.initData })
    });
    if (!r.ok) throw new Error('auth');
    t = (await r.json()).token; localStorage.setItem('jwt', t); return t;
  }

  let JWT; try { JWT = await getJwt(); }
  catch { return (loader.textContent = 'Ошибка авторизации'); }
  const AUTH = { Authorization:`Bearer ${JWT}` };

  const active = { date:null, model:null, style:null, performance:null, aspect:null };
  let allItems = [], lightbox = null;

  fetch('/api/v1/generation/images/', { headers:AUTH })
    .then(r=>r.ok?r.json():Promise.reject())
    .then(data=>{
      if(!data.length) return(loader.textContent='Нет изображений');
      allItems = data;
      loader.remove(); grid.hidden=false;
      initFilterSystem(); renderGrid(allItems); tg.expand?.();
    })
    .catch(()=>loader.textContent='Ошибка загрузки');

  const openSheet = () => {
    sheet.style.maxHeight = `calc(100vh - ${NAV_HEIGHT}px)`;
    sheetWrap.hidden = false; requestAnimationFrame(()=>sheet.classList.add('open'));
  };
  const closeSheet = () => {
    sheet.classList.remove('open');
    setTimeout(()=>sheetWrap.hidden=true,250);
  };

  fab.onclick = openSheet;
  sheetWrap.onclick = e => { if(e.target===sheetWrap) closeSheet(); };
  sheetClose.onclick = closeSheet;
  document.addEventListener('keydown', e=>{ if(e.key==='Escape' && !sheetWrap.hidden) closeSheet(); });

  sheetReset.onclick = () => {
    Object.keys(active).forEach(k=>active[k]=null);
    updateChips(); buildOptions(currentTab); renderGrid(allItems); closeSheet();
  };

  const TAB_CFG = [
    {key:'date',label:'Дата',svg:'M19 4h-1V2h-2v2H8V2H6v2H5a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 15H5V9h14v10z'},
    {key:'model',label:'Модель',svg:'M12 2 2 7l10 5 10-5-10-5zm0 10-10 5 10 5 10-5-10-5z'},
    {key:'style',label:'Стиль',svg:'M4 4h16v2H4zm0 6h16v2H4zm0 6h16v2H4z'},
    {key:'performance',label:'Качество',svg:'M12 3l2.09 6.26L21 9l-5 4.87L17.91 21 12 17.27 6.09 21 8 13.87 3 9l6.91-1.74z'},
    {key:'aspect',label:'Разрешение',svg:'M 5.3783 2 C 5.3905 2 5.40273 2 5.415 2 L 7.62171 2 C 8.01734 1.99998 8.37336 1.99996 8.66942 2.02454 C 8.98657 2.05088 9.32336 2.11052 9.65244 2.28147 C 10.109 2.51866 10.4813 2.89096 10.7185 3.34757 C 10.8895 3.67665 10.9491 4.01343 10.9755 4.33059 C 11 4.62664 11 4.98265 11 5.37828 V 9.62172 C 11 10.0174 11 10.3734 10.9755 10.6694 C 10.9491 10.9866 10.8895 11.3234 10.7185 11.6524 C 10.4813 12.109 10.109 12.4813 9.65244 12.7185 C 9.32336 12.8895 8.98657 12.9491 8.66942 12.9755 C 8.37337 13 8.01735 13 7.62172 13 H 5.37828 C 4.98265 13 4.62664 13 4.33059 12.9755 C 4.01344 12.9491 3.67665 12.8895 3.34757 12.7185 C 2.89096 12.4813 2.51866 12.109 2.28147 11.6524 C 2.11052 11.3234 2.05088 10.9866 2.02454 10.6694 C 1.99996 10.3734 1.99998 10.0173 2 9.62171 L 2 5.415 C 2 5.40273 2 5.3905 2 5.3783 C 1.99998 4.98266 1.99996 4.62664 2.02454 4.33059 C 2.05088 4.01343 2.11052 3.67665 2.28147 3.34757 C 2.51866 2.89096 2.89096 2.51866 3.34757 2.28147 C 3.67665 2.11052 4.01343 2.05088 4.33059 2.02454 C 4.62664 1.99996 4.98266 1.99998 5.3783 2 Z M 4.27752 4.05297 C 4.27226 4.05488 4.27001 4.05604 4.26952 4.0563 C 4.17819 4.10373 4.10373 4.17819 4.0563 4.26952 C 4.05604 4.27001 4.05488 4.27226 4.05297 4.27752 C 4.05098 4.28299 4.04767 4.29312 4.04372 4.30961 C 4.03541 4.34427 4.02554 4.40145 4.01768 4.49611 C 4.00081 4.69932 4 4.9711 4 5.415 V 9.585 C 4 10.0289 4.00081 10.3007 4.01768 10.5039 C 4.02554 10.5986 4.03541 10.6557 4.04372 10.6904 C 4.04767 10.7069 4.05098 10.717 4.05297 10.7225 C 4.05488 10.7277 4.05604 10.73 4.0563 10.7305 C 4.10373 10.8218 4.17819 10.8963 4.26952 10.9437 C 4.27001 10.944 4.27226 10.9451 4.27752 10.947 C 4.28299 10.949 4.29312 10.9523 4.30961 10.9563 C 4.34427 10.9646 4.40145 10.9745 4.49611 10.9823 C 4.69932 10.9992 4.9711 11 5.415 11 H 7.585 C 8.02891 11 8.30068 10.9992 8.5039 10.9823 C 8.59855 10.9745 8.65574 10.9646 8.6904 10.9563 C 8.70688 10.9523 8.71701 10.949 8.72249 10.947 C 8.72775 10.9451 8.72999 10.944 8.73049 10.9437 C 8.82181 10.8963 8.89627 10.8218 8.94371 10.7305 C 8.94397 10.73 8.94513 10.7277 8.94704 10.7225 C 8.94903 10.717 8.95234 10.7069 8.95629 10.6904 C 8.96459 10.6557 8.97446 10.5986 8.98232 10.5039 C 8.9992 10.3007 9 10.0289 9 9.585 V 5.415 C 9 4.9711 8.9992 4.69932 8.98232 4.49611 C 8.97446 4.40145 8.96459 4.34427 8.95629 4.30961 C 8.95234 4.29312 8.94903 4.28299 8.94704 4.27752 C 8.94513 4.27226 8.94397 4.27001 8.94371 4.26952 C 8.89627 4.17819 8.82181 4.10373 8.73049 4.0563 C 8.72999 4.05604 8.72775 4.05488 8.72249 4.05297 C 8.71701 4.05098 8.70688 4.04767 8.6904 4.04372 C 8.65574 4.03541 8.59855 4.02554 8.5039 4.01768 C 8.30068 4.00081 8.02891 4 7.585 4 H 5.415 C 4.9711 4 4.69932 4.00081 4.49611 4.01768 C 4.40145 4.02554 4.34427 4.03541 4.30961 4.04372 C 4.29312 4.04767 4.28299 4.05098 4.27752 4.05297 Z M 16.3783 2 H 18.6217 C 19.0173 1.99998 19.3734 1.99996 19.6694 2.02454 C 19.9866 2.05088 20.3234 2.11052 20.6524 2.28147 C 21.109 2.51866 21.4813 2.89096 21.7185 3.34757 C 21.8895 3.67665 21.9491 4.01343 21.9755 4.33059 C 22 4.62665 22 4.98267 22 5.37832 V 5.62168 C 22 6.01733 22 6.37336 21.9755 6.66942 C 21.9491 6.98657 21.8895 7.32336 21.7185 7.65244 C 21.4813 8.10905 21.109 8.48135 20.6524 8.71854 C 20.3234 8.88948 19.9866 8.94912 19.6694 8.97546 C 19.3734 9.00005 19.0173 9.00003 18.6217 9 H 16.3783 C 15.9827 9.00003 15.6266 9.00005 15.3306 8.97546 C 15.0134 8.94912 14.6766 8.88948 14.3476 8.71854 C 13.891 8.48135 13.5187 8.10905 13.2815 7.65244 C 13.1105 7.32336 13.0509 6.98657 13.0245 6.66942 C 13 6.37337 13 6.01735 13 5.62172 V 5.37828 C 13 4.98265 13 4.62664 13.0245 4.33059 C 13.0509 4.01344 13.1105 3.67665 13.2815 3.34757 C 13.5187 2.89096 13.891 2.51866 14.3476 2.28147 C 14.6766 2.11052 15.0134 2.05088 15.3306 2.02454 C 15.6266 1.99996 15.9827 1.99998 16.3783 2 Z M 15.2775 4.05297 C 15.2723 4.05488 15.27 4.05604 15.2695 4.0563 C 15.1782 4.10373 15.1037 4.17819 15.0563 4.26952 C 15.056 4.27001 15.0549 4.27226 15.053 4.27752 C 15.051 4.28299 15.0477 4.29312 15.0437 4.30961 C 15.0354 4.34427 15.0255 4.40145 15.0177 4.49611 C 15.0008 4.69932 15 4.9711 15 5.415 V 5.585 C 15 6.02891 15.0008 6.30068 15.0177 6.5039 C 15.0255 6.59855 15.0354 6.65574 15.0437 6.6904 C 15.0477 6.70688 15.051 6.71701 15.053 6.72249 C 15.0549 6.72775 15.056 6.72999 15.0563 6.73049 C 15.1037 6.82181 15.1782 6.89627 15.2695 6.94371 C 15.27 6.94397 15.2723 6.94512 15.2775 6.94704 C 15.283 6.94903 15.2931 6.95234 15.3096 6.95629 C 15.3443 6.96459 15.4015 6.97446 15.4961 6.98232 C 15.6993 6.9992 15.9711 7 16.415 7 H 18.585 C 19.0289 7 19.3007 6.9992 19.5039 6.98232 C 19.5986 6.97446 19.6557 6.96459 19.6904 6.95629 C 19.7069 6.95234 19.717 6.94903 19.7225 6.94704 C 19.7277 6.94512 19.73 6.94397 19.7305 6.94371 C 19.8218 6.89627 19.8963 6.82181 19.9437 6.73049 C 19.944 6.72999 19.9451 6.72775 19.947 6.72249 C 19.949 6.71701 19.9523 6.70688 19.9563 6.6904 C 19.9646 6.65573 19.9745 6.59855 19.9823 6.5039 C 19.9992 6.30068 20 6.02891 20 5.585 V 5.415 C 20 4.9711 19.9992 4.69932 19.9823 4.49611 C 19.9745 4.40145 19.9646 4.34427 19.9563 4.30961 C 19.9523 4.29312 19.949 4.28299 19.947 4.27752 C 19.9451 4.27226 19.944 4.27001 19.9437 4.26952 C 19.8963 4.17819 19.8218 4.10373 19.7305 4.0563 C 19.73 4.05604 19.7277 4.05488 19.7225 4.05297 C 19.717 4.05098 19.7069 4.04767 19.6904 4.04372 C 19.6557 4.03541 19.5986 4.02554 19.5039 4.01768 C 19.3007 4.00081 19.0289 4 18.585 4 H 16.415 C 15.9711 4 15.6993 4.00081 15.4961 4.01768 C 15.4015 4.02554 15.3443 4.03541 15.3096 4.04372 C 15.2931 4.04767 15.283 4.05098 15.2775 4.05297 Z M 16.3783 11 H 18.6217 C 19.0173 11 19.3734 11 19.6694 11.0245 C 19.9866 11.0509 20.3234 11.1105 20.6524 11.2815 C 21.109 11.5187 21.4813 11.891 21.7185 12.3476 C 21.8895 12.6766 21.9491 13.0134 21.9755 13.3306 C 22 13.6266 22 13.9827 22 14.3783 V 18.6217 C 22 19.0173 22 19.3734 21.9755 19.6694 C 21.9491 19.9866 21.8895 20.3234 21.7185 20.6524 C 21.4813 21.109 21.109 21.4813 20.6524 21.7185 C 20.3234 21.8895 19.9866 21.9491 19.6694 21.9755 C 19.3734 22 19.0173 22 18.6217 22 H 16.3783 C 15.9827 22 15.6266 22 15.3306 21.9755 C 15.0134 21.9491 14.6766 21.8895 14.3476 21.7185 C 13.891 21.4813 13.5187 21.109 13.2815 20.6524 C 13.1105 20.3234 13.0509 19.9866 13.0245 19.6694 C 13 19.3734 13 19.0174 13 18.6217 V 14.3783 C 13 13.9827 13 13.6266 13.0245 13.3306 C 13.0509 13.0134 13.1105 12.6766 13.2815 12.3476 C 13.5187 11.891 13.891 11.5187 14.3476 11.2815 C 14.6766 11.1105 15.0134 11.0509 15.3306 11.0245 C 15.6266 11 15.9827 11 16.3783 11 Z M 15.2775 13.053 C 15.2723 13.0549 15.27 13.056 15.2695 13.0563 C 15.1782 13.1037 15.1037 13.1782 15.0563 13.2695 C 15.056 13.27 15.0549 13.2723 15.053 13.2775 C 15.051 13.283 15.0477 13.2931 15.0437 13.3096 C 15.0354 13.3443 15.0255 13.4015 15.0177 13.4961 C 15.0008 13.6993 15 13.9711 15 14.415 V 18.585 C 15 19.0289 15.0008 19.3007 15.0177 19.5039 C 15.0255 19.5986 15.0354 19.6557 15.0437 19.6904 C 15.0477 19.7069 15.051 19.717 15.053 19.7225 C 15.0549 19.7277 15.056 19.73 15.0563 19.7305 C 15.1037 19.8218 15.1782 19.8963 15.2695 19.9437 C 15.27 19.944 15.2723 19.9451 15.2775 19.947 C 15.283 19.949 15.2931 19.9523 15.3096 19.9563 C 15.3443 19.9646 15.4015 19.9745 15.4961 19.9823 C 15.6993 19.9992 15.9711 20 16.415 20 H 18.585 C 19.0289 20 19.3007 19.9992 19.5039 19.9823 C 19.5986 19.9745 19.6557 19.9646 19.6904 19.9563 C 19.7069 19.9523 19.717 19.949 19.7225 19.947 C 19.7277 19.9451 19.73 19.944 19.7305 19.9437 C 19.8218 19.8963 19.8963 19.8218 19.9437 19.7305 C 19.944 19.73 19.9451 19.7277 19.947 19.7225 C 19.949 19.717 19.9523 19.7069 19.9563 19.6904 C 19.9646 19.6557 19.9745 19.5986 19.9823 19.5039 C 19.9992 19.3007 20 19.0289 20 18.585 V 14.415 C 20 13.9711 19.9992 13.6993 19.9823 13.4961 C 19.9745 13.4015 19.9646 13.3443 19.9563 13.3096 C 19.9523 13.2931 19.949 13.283 19.947 13.2775 C 19.9451 13.2723 19.944 13.27 19.9437 13.2695 C 19.8963 13.1782 19.8218 13.1037 19.7305 13.0563 C 19.73 13.056 19.7277 13.0549 19.7225 13.053 C 19.717 13.051 19.7069 13.0477 19.6904 13.0437 C 19.6557 13.0354 19.5986 13.0255 19.5039 13.0177 C 19.3007 13.0008 19.0289 13 18.585 13 H 16.415 C 15.9711 13 15.6993 13.0008 15.4961 13.0177 C 15.4015 13.0255 15.3443 13.0354 15.3096 13.0437 C 15.2931 13.0477 15.283 13.051 15.2775 13.053 Z M 5.37828 15 H 7.62172 C 8.01735 15 8.37337 15 8.66942 15.0245 C 8.98657 15.0509 9.32336 15.1105 9.65244 15.2815 C 10.109 15.5187 10.4813 15.891 10.7185 16.3476 C 10.8895 16.6766 10.9491 17.0134 10.9755 17.3306 C 11 17.6266 11 17.9827 11 18.3783 V 18.6217 C 11 19.0174 11 19.3734 10.9755 19.6694 C 10.9491 19.9866 10.8895 20.3234 10.7185 20.6524 C 10.4813 21.109 10.109 21.4813 9.65244 21.7185 C 9.32336 21.8895 8.98657 21.9491 8.66942 21.9755 C 8.37336 22 8.01733 22 7.62168 22 H 5.37832 C 4.98267 22 4.62665 22 4.33059 21.9755 C 4.01343 21.9491 3.67665 21.8895 3.34757 21.7185 C 2.89096 21.4813 2.51866 21.109 2.28147 20.6524 C 2.11052 20.3234 2.05088 19.9866 2.02454 19.6694 C 1.99996 19.3734 1.99998 19.0173 2 18.6217 V 18.3783 C 1.99998 17.9827 1.99996 17.6266 2.02454 17.3306 C 2.05088 17.0134 2.11052 16.6766 2.28147 16.3476 C 2.51866 15.891 2.89096 15.5187 3.34757 15.2815 C 3.67665 15.1105 4.01344 15.0509 4.33059 15.0245 C 4.62664 15 4.98265 15 5.37828 15 Z M 4.27752 17.053 C 4.27226 17.0549 4.27001 17.056 4.26952 17.0563 C 4.17819 17.1037 4.10373 17.1782 4.0563 17.2695 C 4.05604 17.27 4.05488 17.2723 4.05297 17.2775 C 4.05098 17.283 4.04767 17.2931 4.04372 17.3096 C 4.03541 17.3443 4.02554 17.4015 4.01768 17.4961 C 4.00081 17.6993 4 17.9711 4 18.415 V 18.585 C 4 19.0289 4.00081 19.3007 4.01768 19.5039 C 4.02554 19.5986 4.03541 19.6557 4.04372 19.6904 C 4.04767 19.7069 4.05098 19.717 4.05297 19.7225 C 4.05488 19.7277 4.05604 19.73 4.0563 19.7305 C 4.10373 19.8218 4.17819 19.8963 4.26952 19.9437 C 4.27001 19.944 4.27226 19.9451 4.27752 19.947 C 4.28299 19.949 4.29312 19.9523 4.30961 19.9563 C 4.34427 19.9646 4.40145 19.9745 4.49611 19.9823 C 4.69932 19.9992 4.9711 20 5.415 20 H 7.585 C 8.02891 20 8.30068 19.9992 8.5039 19.9823 C 8.59855 19.9745 8.65573 19.9646 8.6904 19.9563 C 8.70688 19.9523 8.71701 19.949 8.72249 19.947 C 8.72775 19.9451 8.72999 19.944 8.73049 19.9437 C 8.82181 19.8963 8.89627 19.8218 8.94371 19.7305 C 8.94397 19.73 8.94513 19.7277 8.94704 19.7225 C 8.94903 19.717 8.95234 19.7069 8.95629 19.6904 C 8.96459 19.6557 8.97446 19.5986 8.98232 19.5039 C 8.9992 19.3007 9 19.0289 9 18.585 V 18.415 C 9 17.9711 8.9992 17.6993 8.98232 17.4961 C 8.97446 17.4015 8.96459 17.3443 8.95629 17.3096 C 8.95234 17.2931 8.94903 17.283 8.94704 17.2775 C 8.94513 17.2723 8.94397 17.27 8.94371 17.2695 C 8.89627 17.1782 8.82181 17.1037 8.73049 17.0563 C 8.72999 17.056 8.72775 17.0549 8.72249 17.053 C 8.71701 17.051 8.70688 17.0477 8.6904 17.0437 C 8.65574 17.0354 8.59855 17.0255 8.5039 17.0177 C 8.30068 17.0008 8.02891 17 7.585 17 H 5.415 C 4.9711 17 4.69932 17.0008 4.49611 17.0177 C 4.40145 17.0255 4.34427 17.0354 4.30961 17.0437 C 4.29312 17.0477 4.28299 17.051 4.27752 17.053 Z'},
  ];
  let currentTab='date';

  function initFilterSystem(){
    sheetTabs.innerHTML='';
    TAB_CFG.forEach((cfg,i)=>{
      const btn=document.createElement('div');
      btn.className='tab-btn'+(i===0?' active':'');
      btn.dataset.key=cfg.key;
      btn.innerHTML=`<svg viewBox="0 0 24 24" fill="currentColor"><path d="${cfg.svg}"/></svg><span>${cfg.label}</span>`;
      btn.onclick=()=>{ [...sheetTabs.children].forEach(x=>x.classList.remove('active'));
                        btn.classList.add('active'); currentTab=cfg.key; buildOptions(cfg.key); };
      sheetTabs.appendChild(btn);
    });
    buildOptions('date');
  }

  function uniqueLists(){
    return{
      date:[
        'Все', ...[...new Set(allItems.map(i=>i.created_at.slice(0,10)))]
          .sort((a,b)=>b.localeCompare(a))
      ],
      model:[...new Set(allItems.map(i=>i.model).filter(Boolean))],
      style:[...new Set(allItems.flatMap(i=>i.style||[]))],
      performance:[...new Set(allItems.map(i=>i.performance).filter(Boolean))],
      aspect:[...new Set(allItems.map(i=>i.aspect).filter(Boolean))],
    };
  }

  function buildOptions(key){
    const lists = uniqueLists();
    sheetList.innerHTML='';
    lists[key].forEach(v=>{
      const li=document.createElement('li');
      li.textContent = (key==='date'&&v==='Все') ? 'Все даты' : v;
      if((active[key]===null&&v==='Все')||active[key]===v) li.classList.add('selected');
      li.onclick=()=>{
        [...sheetList.children].forEach(x=>x.classList.remove('selected'));
        li.classList.add('selected');
        active[key]=(key==='date'&&v==='Все')?null:v;
        updateChips(); applyFilters();
      };
      sheetList.appendChild(li);
    });
  }

  function updateChips(){
    chipBar.innerHTML='';
    Object.entries(active).forEach(([k,val])=>{
      if(!val) return;
      const chip=document.createElement('span');
      chip.className='chip';
      chip.textContent=val;
      chip.title='Снять фильтр';
      chip.onclick=()=>{
        active[k]=null; updateChips(); applyFilters();
      };
      chipBar.appendChild(chip);
    });
    sheetReset.disabled = !chipBar.children.length;
  }

  function applyFilters(){
    let list=allItems;
    if(active.date) list=list.filter(i=>i.created_at.startsWith(active.date));
    if(active.model) list=list.filter(i=>i.model===active.model);
    if(active.style) list=list.filter(i=>(i.style||[]).includes(active.style));
    if(active.performance) list=list.filter(i=>i.performance===active.performance);
    if(active.aspect) list=list.filter(i=>i.aspect===active.aspect);
    renderGrid(list);
  }

  function renderGrid(arr){
    grid.innerHTML='';
    arr.forEach(it=>{
      const a=document.createElement('a');
      a.className='glightbox item'; a.href=buildSrc(it.url); a.dataset.gallery='gen';

      const img=document.createElement('img');
      img.alt=it.prompt; img.dataset.src=buildSrc(it.url); img.loading='lazy';
      img.onerror=()=>img.classList.add('broken'); io.observe(img);

      const lbl=document.createElement('div');
      lbl.className='date-label'; lbl.textContent=it.created_at.slice(0,10);

      a.append(img,lbl); grid.append(a);
    });

    if(lightbox) lightbox.destroy();
    lightbox = GLightbox({ selector:'.glightbox', loop:true, touchNavigation:true,
                           openEffect:'zoom', closeEffect:'fade' });
  }

  document.addEventListener('click',e=>{
    if(e.altKey && e.target.tagName==='IMG'){
      navigator.clipboard.writeText(e.target.alt||'').then(()=>toast('Промпт скопирован'));
    }
  });

})();
