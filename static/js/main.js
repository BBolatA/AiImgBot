(() => {
  const tg = window.Telegram?.WebApp;
  if (tg && tg.viewportHeight) {
    const safe = Math.max(0, window.innerHeight - tg.viewportHeight);
    document.documentElement.style.setProperty('--safe-bottom', safe + 'px');
  }

  const path = window.location.pathname;
  let page = 'home';
  if (path.includes('/gallery'))   page = 'gallery';
  else if (path.includes('/analytics')) page = 'analytics';

  const nav = document.querySelector('.bottom-nav');
  const activeLink = nav.querySelector(`[data-page="${page}"]`);
  if (activeLink){
    activeLink.classList.add('active');
    nav.classList.add(`active-${page}`);
  }

nav.addEventListener('click', e => {
  const a = e.target.closest('a');
  if (!a) return;
  if (a.dataset.page === 'bot') return;
  if (a.classList.contains('active')) return;
  e.preventDefault();
  window.Telegram?.WebApp?.HapticFeedback?.selectionChanged?.();
  window.location.href = a.href;
});
})();
