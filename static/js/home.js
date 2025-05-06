(async () => {
  const tg = window.Telegram?.WebApp;
  if (!tg) return;
  tg.ready();
  await new Promise(r => requestAnimationFrame(r));

  const initData = tg.initData;
  if (!initData) return;

  async function login() {
    const r = await fetch("/api/v1/auth/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ initData })
    });
    if (!r.ok) throw new Error("auth " + r.status);
    const t = (await r.json()).token;
    localStorage.setItem("jwt", t);
    return t;
  }

  async function authFetch(url, opts = {}, retry = true) {
    let tok = localStorage.getItem("jwt") || await login();
    const resp = await fetch(url, {
      ...opts,
      headers: { ...(opts.headers || {}), Authorization: `Bearer ${tok}` }
    });
    if ((resp.status === 401 || resp.status === 403) && retry) {
      localStorage.removeItem("jwt");
      tok = await login();
      return authFetch(url, opts, false);
    }
    return resp;
  }

  const buildSrc = url => {
    if (/^https?:\/\//.test(url)) return url.replace(/^http:\/\//, "https://");
    const base = (window.BASE_URL && typeof window.BASE_URL === "string")
      ? window.BASE_URL.trim().replace(/\/$/, "")
      : location.origin.replace(/\/$/, "");
    return `${base}${url.startsWith("/") ? url : "/" + url}`;
  };

  const statResp = await authFetch("/api/v1/generation/full_stats/?period=0");
  if (!statResp.ok) return;
  const stat = await statResp.json();

  document.querySelector("[data-total]").textContent =
    stat.by_date.reduce((s, o) => s + o.count, 0);
  const avg = stat.by_date.length
    ? stat.by_date.reduce((s, o) => s + o.count, 0) / stat.by_date.length
    : 0;
  document.querySelector("[data-avg]").textContent = avg.toFixed(1);
  const cont = document.getElementById("last");
  if (cont) {
    const imgResp = await authFetch("/api/v1/generation/images/?limit=3");
    if (!imgResp.ok) return;
    const imgs = await imgResp.json();

    cont.innerHTML = "";
    imgs.forEach(i => {
      const img = document.createElement("img");
      img.className = "thumb";
      img.loading = "lazy";
      img.src = buildSrc(i.url);
      img.alt = i.prompt;
      img.onclick = () => location.href = "/gallery/";
      cont.append(img);
    });
  }
})();
