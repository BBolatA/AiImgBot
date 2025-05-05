(function(){
  const getUid = () => {
    const rootUid = document.body.dataset.uid;
    if (rootUid) return rootUid;

    const qUid = new URLSearchParams(location.search).get('uid');
    if (qUid) return qUid;

    const tUid = window.Telegram?.WebApp?.initDataUnsafe?.user?.id;
    if (tUid) return String(tUid);

    const sUid = localStorage.getItem('tg_uid');
    if (sUid) return sUid;

    return '';
  };

  const uid = getUid();
  if (!uid) return;
  localStorage.setItem('tg_uid', uid);
  document.querySelectorAll('a[href^="/"]:not([href*="?uid="])')
    .forEach(a => {
      const url = new URL(a.getAttribute('href'), location.origin);
      url.searchParams.set('uid', uid);
      a.setAttribute('href', url.pathname + url.search);
    });
})();
