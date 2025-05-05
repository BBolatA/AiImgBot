(() => {
  const burger  = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');

  burger.addEventListener('click', () => {
    const opening = sidebar.hidden;
    sidebar.hidden = !opening;
    document.body.classList.toggle('sidebar-open', opening);
    burger.textContent = opening ? '×' : '☰';
  });
})();
