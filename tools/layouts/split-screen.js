// Visuals on top, the host below, captions on the seam. Copied into <video>/vendor/ by tools/split_screen.py; do not edit the copy.
// Reads window.SPLIT (split-screen.data.js): {phases: [...], host: "assets/host.png", top: [{src, anchor, n}]}.
// Covers the listed phases (they must be consecutive); their own content is hidden. Top visuals swap on spoken words.
(function () {
  const S = window.SPLIT;
  const tl = (window.__timelines || {}).main;
  const W = window.WORDS;
  const P = window.PHASES || {};
  if (!S || !tl || !W || !S.phases.every((p) => P[p])) throw new Error("split-screen: missing SPLIT, main timeline, WORDS or a phase");
  // p1 starts after the lead-in; a split that opens the video owns frame 0 too.
  const start = S.phases.includes("p1") ? 0 : Math.min(...S.phases.map((p) => P[p].start));
  const end = Math.max(...S.phases.map((p) => P[p].end));

  // n counts inside the covered phases only (same as the check in tools/layoutlib.py, per item phase).
  function at(word, n, phase) {
    let seen = 0;
    for (const w of W) {
      if (w[1] < P[phase].start || w[1] >= P[phase].end) continue;
      if (w[0].toLowerCase().replace(/[^a-z0-9']/g, "") === word && ++seen === n) return w[1];
    }
    throw new Error("split-screen: word not in transcript: " + word + " #" + n + " in " + phase);
  }

  const css = `
    #split { position: absolute; inset: 0; z-index: 3; background: #0b0d12; visibility: hidden; }
    #split .top { position: absolute; left: 0; right: 0; top: 0; height: 960px; overflow: hidden; }
    #split .top img { position: absolute; left: 0; top: 150px; width: 100%; height: 810px; object-fit: cover; opacity: 0; }
    #split .bot { position: absolute; left: 0; right: 0; bottom: 0; height: 960px; overflow: hidden; }
    #split .bot img { width: 100%; height: 100%; object-fit: cover; display: block; }
    #split .seam { position: absolute; left: 0; right: 0; top: 957px; height: 6px; background: #ffd400; }
    #root[data-split="1"] #cap { bottom: auto; top: 800px; }
    #root[data-split="1"] #cap .line { background: rgba(11, 13, 18, 0.82); border-radius: 22px; padding: 14px 26px; left: 50%; right: auto; transform: translateX(-50%); white-space: nowrap; }
  `;
  const style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  for (const p of S.phases) for (const child of Array.from(document.getElementById(p).children)) child.style.display = "none";
  const el = document.createElement("div");
  el.id = "split";
  el.innerHTML = '<div class="top"></div><div class="bot"><img alt="" /></div><div class="seam"></div>';
  el.querySelector(".bot img").src = S.host;
  S.top.forEach((t, i) => {
    const img = document.createElement("img");
    img.id = "split-top-" + i;
    img.alt = "";
    img.src = t.src;
    el.querySelector(".top").appendChild(img);
  });
  document.getElementById("root").appendChild(el);

  tl.set("#split", { visibility: "visible" }, start);
  tl.set("#root", { attr: { "data-split": "1" } }, start);
  tl.set("#root", { attr: { "data-split": "0" } }, end);
  tl.set("#split", { visibility: "hidden" }, end);
  // The host never sits still: a slow push-in over the whole split.
  tl.fromTo("#split .bot img", { scale: 1 }, { scale: 1.08, duration: end - start, ease: "none" }, start);
  S.top.forEach((t, i) => {
    if (i === 0) { tl.set("#split-top-0", { opacity: 1 }, start); return; }  // readable from the first frame
    const t0 = at(t.anchor, t.n, t.phase) - 0.1;
    tl.fromTo("#split-top-" + i, { opacity: 0, scale: 1.06 }, { opacity: 1, scale: 1, duration: 0.35, ease: "power2.out" }, t0);
    tl.to("#split-top-" + (i - 1), { opacity: 0, duration: 0.2 }, t0 + 0.2);
  });
  tl.seek(0);
})();
