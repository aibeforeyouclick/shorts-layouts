// Tier board S to F. Copied into <video>/vendor/ by tools/ranking_list.py; do not edit the copy.
// Reads window.RANKING (ranking.js): {phase, title, items: [{name, tier, anchor, n}]}.
// Fills the section #<phase>: its own content is hidden, the board takes its place.
(function () {
  const R = window.RANKING;
  const tl = (window.__timelines || {}).main;
  const W = window.WORDS;
  const ph = (window.PHASES || {})[R && R.phase];
  if (!R || !tl || !W || !ph) throw new Error("ranking-list: missing RANKING, main timeline, WORDS or PHASES[" + (R && R.phase) + "]");
  const section = document.getElementById(R.phase);
  if (!section) throw new Error("ranking-list: no section #" + R.phase + " in index.html");

  // n counts inside this phase only (same as the check in tools/ranking_list.py).
  function at(word, n) {
    let seen = 0;
    for (const w of W) {
      if (w[1] < ph.start || w[1] >= ph.end) continue;
      if (w[0].toLowerCase().replace(/[^a-z0-9']/g, "") === word && ++seen === n) return w[1];
    }
    throw new Error("ranking-list: word not in transcript: " + word + " #" + n);
  }

  const TIERS = [["S", "#ff5a5f"], ["A", "#ff9f43"], ["B", "#ffd43b"], ["C", "#69db7c"], ["D", "#4dabf7"], ["F", "#b197fc"]];
  const css = `
    #rank { width: 960px; font-family: Inter, "Segoe UI", ui-sans-serif, system-ui, sans-serif; }
    #rank .title { font-size: 76px; font-weight: 900; letter-spacing: 0.02em; text-align: center; margin-bottom: 34px; color: #fff; }
    #rank .row { display: flex; height: 150px; margin: 10px 0; background: #1b1d22; border-radius: 18px; overflow: hidden; }
    #rank .lab { flex: none; width: 150px; display: flex; align-items: center; justify-content: center; font-size: 84px; font-weight: 900; color: #111; }
    #rank .slot { flex: 1; display: flex; align-items: center; gap: 14px; padding: 0 18px; }
    #rank .card { background: #fff; color: #111; border-radius: 14px; padding: 18px 24px; font-size: 38px; font-weight: 800; line-height: 1.1; max-width: 360px; text-align: left; box-shadow: 0 10px 30px rgba(0,0,0,0.45); }
  `;
  const style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  for (const child of Array.from(section.children)) child.style.display = "none";
  const board = document.createElement("div");
  board.id = "rank";
  board.innerHTML = '<div class="title"></div>' + TIERS.map(([t, c]) =>
    '<div class="row"><div class="lab" style="background:' + c + '">' + t + '</div><div class="slot" id="tier-' + t + '"></div></div>').join("");
  board.querySelector(".title").textContent = R.title;
  section.appendChild(board);

  tl.from("#rank .title", { y: -40, opacity: 0, duration: 0.4 }, ph.start);
  tl.from("#rank .row", { x: -80, opacity: 0, duration: 0.3, stagger: 0.06 }, ph.start + 0.15);
  R.items.forEach((it, i) => {
    const card = document.createElement("div");
    card.className = "card";
    card.id = "rank-card-" + i;
    card.textContent = it.name;
    document.getElementById("tier-" + it.tier).appendChild(card);
    // Drop from above the board into its row on the spoken word.
    tl.from(card, { y: -700, opacity: 0, rotation: -8, duration: 0.5, ease: "bounce.out" }, at(it.anchor, it.n || 1) - 0.1);
  });
  tl.seek(0);
})();
