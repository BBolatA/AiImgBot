(async () => {
  /* === Telegram WebApp init === */
  const tg = window.Telegram?.WebApp;
  if (!tg) return;
  tg.ready();
  await new Promise(r => requestAnimationFrame(r));

  /* ---------- helper: авторизация через initData ---------- */
  const initData = tg.initData;
  if (!initData) return;

  async function login() {
    const r = await fetch("/api/v1/auth/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ initData })
    });
    if (!r.ok) throw new Error("auth " + r.status);
    const { token } = await r.json();
    localStorage.setItem("jwt", token);
    return token;
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

  /* ---------- 1. ВДОХНОВЕНИЕ ДНЯ ---------- */
  try {
  const p = await (await fetch("/api/v1/generation/prompts/of_day/")).json();

  dailyEmoji.textContent  = p.emoji || "💡";
  dailyPrompt.textContent = p.prompt;

  dailyGen.onclick = () => {
    const cmd  = `/img ${p.prompt}`;
    const text = encodeURIComponent(cmd);

    // универсальная ссылка «открыть диалог с ботом и подставить текст»
    const link = `https://t.me/${window.TELEGRAM_BOT_USERNAME}?text=${text}`;

    if (tg.openTelegramLink) {
      tg.openTelegramLink(link);
    } else if (tg.openLink) {
      tg.openLink(link);
    } else {
      window.open(link, "_blank");
    }
  };
} catch (_) {
  dailyPrompt.textContent = "Не удалось загрузить промпт дня";
  dailyGen.disabled = true;
}

  /* ---------- 2. СТАТИСТИКА (total, avg, streak) ---------- */
  try {
    const statResp = await authFetch("/api/v1/generation/full_stats/?period=0");
    if (statResp.ok) {
      const stat = await statResp.json();
      const total = stat.by_date.reduce((s, o) => s + o.count, 0);
      const avg   = stat.by_date.length ? total / stat.by_date.length : 0;

      document.querySelector("[data-total]").textContent  = total;
      document.querySelector("[data-avg]").textContent    = avg.toFixed(1);
      document.querySelector("[data-streak]").textContent = stat.streak ?? 0;
    }
  } catch (e) {
    console.error(e);
  }

  /* ---------- 3. ПОСЛЕДНИЕ 3 КАРТИНКИ ---------- */
  try {
    const cont = document.getElementById("last");
    const imgResp = await authFetch("/api/v1/generation/images/?limit=3");
    if (imgResp.ok) {
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
  } catch (e) {
    console.error(e);
  }

  /* ---------- 4. ОЧЕРЕДЬ ЗАДАЧ (polling) ---------- */
  async function loadQueue() {
    const list = document.getElementById("queue");
    try {
      const resp = await authFetch("/api/v1/generation/queue/");
      if (!resp.ok) return;
      const tasks = await resp.json();
      list.innerHTML = "";
      if (!tasks.length) {
        list.innerHTML = "<li>Очередь пуста</li>";
        return;
      }
      tasks.forEach(t=>{
        const li = document.createElement("li");
        li.innerHTML =
          `<span class="queue-status ${t.status}">${t.status}</span>` +
          `<span class="queue-dash">—</span>` +
          `<span class="queue-prompt">${t.prompt}</span>`;
        list.append(li);
      });
    } catch (e) {
      console.error(e);
    }
  }
  loadQueue();
  setInterval(loadQueue, 5000);

})();
