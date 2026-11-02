// Visuals on top, the host below, captions on the seam. Copied into <video>/vendor/ by tools/split_screen.py; do not edit the copy.
// Reads window.SPLIT (split-screen.data.js): {phases: [...], host: "assets/host.png" or mascot: "lens", top: [{src, anchor, n}]}.
// mascot "lens" = a built-in narrator character, drawn inline and driven by the word timings:
// idle = eye floats and blinks; speaking = the eye becomes 5 bars that jump on every word, with a pulse ring.
// mascot "lens+clicky" = a dialogue: Lens left, Clicky (a cursor character) right. Needs a script
// with "cast" and window.ENVELOPE (tools/tts.py): every frame reads each speaker's loudness, so bars, mouth and
// lean follow the real audio; the listener looks at the speaker and dims a little. Captions take the speaker's colour.
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

  // Lens mascot, 540x480 units = the 1080x960 bottom half. Colours from logo A.
  const LENS = '<svg id="lens" viewBox="0 0 540 480" width="1080" height="960" xmlns="http://www.w3.org/2000/svg">' +
    '<rect width="540" height="480" fill="#110C07"/><ellipse cx="270" cy="420" rx="92" ry="13" fill="#3A2C19"/>' +
    '<g id="lens-body" transform="translate(14 -16)">' +
    '<circle id="lens-pulse" cx="256" cy="246" r="168" fill="none" stroke="#FFB020" stroke-width="7" opacity="0"/>' +
    '<circle cx="256" cy="246" r="128" fill="none" stroke="#FBF5EC" stroke-width="30"/>' +
    '<g id="lens-eye"><circle cx="256" cy="246" r="72" fill="#FFB020"/><g id="lens-pupil"><circle cx="266" cy="238" r="28" fill="#110C07"/><circle cx="279" cy="225" r="9" fill="#FBF5EC"/></g></g>' +
    '<g id="lens-bars" opacity="0">' + [[159, 64], [201, 120], [243, 164], [285, 112], [327, 70]].map(([x, h], j) =>
      '<rect class="lens-bar" x="' + x + '" y="' + (246 - h / 2) + '" width="26" height="' + h + '" rx="13" fill="#FFB020"/>').join("") +
    '</g></g></svg>';

  const DUO = '<svg id="duo" viewBox="0 0 540 480" width="1080" height="960" xmlns="http://www.w3.org/2000/svg">' +
    '<rect width="540" height="480" fill="#110C07"/>' +
    '<ellipse cx="160" cy="372" rx="70" ry="10" fill="#3A2C19"/><ellipse cx="410" cy="372" rx="70" ry="10" fill="#3A2C19"/>' +
    '<g id="duo-lens"><g transform="translate(-32 36) scale(0.75)">' +
    '<circle id="lens-pulse" cx="256" cy="246" r="168" fill="none" stroke="#FFB020" stroke-width="7" opacity="0"/>' +
    '<circle cx="256" cy="246" r="128" fill="none" stroke="#FBF5EC" stroke-width="30"/>' +
    '<g id="lens-eye"><circle cx="256" cy="246" r="72" fill="#FFB020"/><g id="lens-pupil"><circle cx="266" cy="238" r="28" fill="#110C07"/><circle cx="279" cy="225" r="9" fill="#FBF5EC"/></g></g>' +
    '<g id="lens-bars" opacity="0">' + [[159, 64], [201, 120], [243, 164], [285, 112], [327, 70]].map(([x, h]) =>
      '<rect class="lens-bar" x="' + x + '" y="' + (246 - h / 2) + '" width="26" height="' + h + '" rx="13" fill="#FFB020"/>').join("") +
    '</g></g></g>' +
    '<g id="duo-clicky"><g transform="translate(200 36) scale(0.75)">' +
    '<g id="clicky-waves" opacity="0">' + [30, 52].map((d) => '<path d="M' + (176 - d) + ' ' + (200 - d * 0.9) + ' Q' + (176 - d * 1.35) + ' 200 ' + (176 - d) + ' ' + (200 + d * 0.9) +
      '" fill="none" stroke="#FF6B5B" stroke-width="9" stroke-linecap="round"/>').join("") + '</g>' +
    '<polygon points="176,84 176,372 246,306 296,416 336,398 286,290 382,290" fill="#FF6B5B" stroke="#FBF5EC" stroke-width="12" stroke-linejoin="round"/>' +
    '<circle cx="222" cy="222" r="28" fill="#FBF5EC"/><circle cx="276" cy="250" r="20" fill="#FBF5EC"/>' +
    '<g id="clicky-pupils"><circle cx="230" cy="216" r="13" fill="#110C07"/><circle cx="234" cy="211" r="4" fill="#FBF5EC"/>' +
    '<circle cx="272" cy="254" r="10" fill="#110C07"/><circle cx="275" cy="250" r="3" fill="#FBF5EC"/></g>' +
    '<path id="clicky-smile" d="M196 300 Q224 322 252 298" fill="none" stroke="#110C07" stroke-width="8" stroke-linecap="round"/>' +
    '<g id="clicky-mouth" opacity="0"><ellipse cx="222" cy="304" rx="26" ry="20" fill="#110C07"/><ellipse cx="226" cy="315" rx="13" ry="7" fill="#FF9F95"/>' +
    '<rect x="210" y="286" width="12" height="10" rx="2" fill="#FBF5EC"/></g>' +
    '</g></g></svg>';
  const COLORS = { lens: "#FFB020", clicky: "#FF6B5B" };

  const css = `
    #split { position: absolute; inset: 0; z-index: 3; background: #0b0d12; visibility: hidden; }
    #split .top { position: absolute; left: 0; right: 0; top: 0; height: 960px; overflow: hidden; }
    #split .top img { position: absolute; left: 0; top: 150px; width: 100%; height: 810px; object-fit: cover; opacity: 0; }
    #split .bot { position: absolute; left: 0; right: 0; bottom: 0; height: 960px; overflow: hidden; }
    #split .bot img { width: 100%; height: 100%; object-fit: cover; display: block; }
    #split .seam { position: absolute; left: 0; right: 0; top: 957px; height: 6px; background: #ffd400; }
    #root[data-split="1"] #cap { bottom: auto; top: 800px; }
    #duo .lens-bar, #clicky-mouth, #lens-eye { transform-box: fill-box; transform-origin: 50% 50%; }
    #duo-lens, #duo-clicky { transform-box: fill-box; transform-origin: 50% 100%; }
    #root[data-split="1"] #cap .line { background: rgba(11, 13, 18, 0.82); border-radius: 22px; padding: 14px 26px; left: 50%; right: auto; transform: translateX(-50%); width: max-content; max-width: 940px; font-size: 54px; }
  `;
  const style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  for (const p of S.phases) for (const child of Array.from(document.getElementById(p).children)) child.style.display = "none";
  const el = document.createElement("div");
  el.id = "split";
  el.innerHTML = '<div class="top"></div><div class="bot"></div><div class="seam"></div>';
  if (S.mascot === "lens") el.querySelector(".bot").innerHTML = LENS;
  else if (S.mascot === "lens+clicky") el.querySelector(".bot").innerHTML = DUO;
  else el.querySelector(".bot").innerHTML = '<img alt="" />', el.querySelector(".bot img").src = S.host;
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
  if (S.mascot === "lens") animateLens();
  else if (S.mascot === "lens+clicky") animateDuo();
  // An image host never sits still: a slow push-in over the whole split.
  else tl.fromTo("#split .bot img", { scale: 1 }, { scale: 1.08, duration: end - start, ease: "none" }, start);
  S.top.forEach((t, i) => {
    if (i === 0) { tl.set("#split-top-0", { opacity: 1 }, start); return; }  // readable from the first frame
    const t0 = at(t.anchor, t.n, t.phase) - 0.1;
    tl.fromTo("#split-top-" + i, { opacity: 0, scale: 1.06 }, { opacity: 1, scale: 1, duration: 0.35, ease: "power2.out" }, t0);
    tl.to("#split-top-" + (i - 1), { opacity: 0, duration: 0.2 }, t0 + 0.2);
  });
  tl.seek(0);

  // Dialogue: one tween over the whole split whose onUpdate redraws both characters for the current time,
  // so every rendered frame is a pure function of t (seek-safe, no randomness).
  function animateDuo() {
    const E = window.ENVELOPE;
    if (!E || !E.lens || !E.clicky) throw new Error("split-screen: lens+clicky needs window.ENVELOPE with lens and clicky (run tools/tts.py with a cast)");
    window.CAPTIONS.forEach((c, ci) => {
      const line = document.getElementById("cap").children[ci];
      if (line && COLORS[c.who]) line.style.color = COLORS[c.who];
    });
    // Talking runs per speaker: whole line spans when tts.py wrote them (a laugh after the last word still counts),
    // else the words; pieces closer than 0.35 s join.
    const runs = { lens: [], clicky: [] };
    const spans = window.LINES ? window.LINES.map((l) => [l.who, l.start, l.end]) : W.map((w) => [w[3], w[1], w[2]]);
    for (const [who, s, e] of spans) {
      const r = runs[who];
      if (!r || s < start || s >= end) continue;
      const last = r[r.length - 1];
      if (last && s - last.end < 0.35) last.end = e; else r.push({ start: s, end: e });
    }
    // 0..1: how much `who` is inside a speaking run at t, with 0.15 s ramps at both edges.
    const active = (who, t) => Math.max(0, ...runs[who].map((r) => Math.min(1, (t - r.start + 0.15) / 0.15, (r.end + 0.15 - t) / 0.15)));
    const level = (who, t) => E[who][Math.floor(t * E.fps)] || 0;
    const $ = (id) => document.getElementById(id);
    const bars = Array.from(document.querySelectorAll("#duo .lens-bar"));
    const draw = (t) => {
      const la = active("lens", t), ca = active("clicky", t), lv = level("lens", t), cv = level("clicky", t);
      const f = Math.floor(t * E.fps);
      // Lens: eye <-> bars; the bars follow loudness with a fixed per-bar wobble; the pupil looks at Clicky.
      $("lens-eye").style.opacity = 1 - la;
      $("lens-bars").style.opacity = la;
      $("lens-pulse").style.opacity = 0.55 * la * (0.5 + 0.5 * lv);
      bars.forEach((b, j) => {
        b.style.transform = "scaleY(" + (0.3 + 0.75 * lv * (0.65 + 0.35 * Math.abs(Math.sin(f * 0.9 + j * 1.7)))).toFixed(3) + ")";
      });
      $("lens-pupil").style.transform = "translate(" + (18 * ca).toFixed(1) + "px, 0px)";
      const blink = la + ca < 0.01 && t % 2.6 < 0.14;
      $("lens-eye").style.transform = blink ? "scaleY(0.12)" : "none";
      // Clicky: the mouth opens with loudness, waves while talking; the pupils look at Lens while it talks.
      $("clicky-smile").style.opacity = 1 - ca;
      $("clicky-mouth").style.opacity = ca;
      $("clicky-mouth").style.transform = "scaleY(" + (0.35 + 0.85 * cv).toFixed(3) + ")";
      $("clicky-waves").style.opacity = 0.9 * ca * Math.min(1, cv * 1.5);
      $("clicky-pupils").style.transform = "translate(" + (-10 * la).toFixed(1) + "px, " + (-3 * la).toFixed(1) + "px)";
      // Both float (different periods); the speaker leans in, the listener dims a little.
      const bobL = -6 * (1 - Math.cos((2 * Math.PI * t) / 2.8));
      const bobC = -8 * (1 - Math.cos((2 * Math.PI * t) / 1.9)) - 10 * cv * ca;
      $("duo-lens").style.transform = "translateY(" + bobL.toFixed(1) + "px) scale(" + (1 + 0.04 * la).toFixed(3) + ")";
      $("duo-clicky").style.transform = "translateY(" + bobC.toFixed(1) + "px) rotate(" + (-5 * ca * cv).toFixed(2) + "deg) scale(" + (1 + 0.04 * ca).toFixed(3) + ")";
      $("duo-lens").style.opacity = 1 - 0.2 * ca * (1 - la);
      $("duo-clicky").style.opacity = 1 - 0.2 * la * (1 - ca);
    };
    tl.to({ p: 0 }, { p: 1, duration: end - start, ease: "none", onUpdate() { draw(start + this.time()); } }, start);
    draw(start);
  }

  function animateLens() {
    const span = end - start;
    tl.fromTo("#lens-body", { y: -16 }, { y: -30, duration: 1.4, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.floor(span / 1.4)) }, start);
    // Speaking runs: words closer than 0.35 s belong to one run.
    const words = W.filter((w) => w[1] >= start && w[1] < end);
    const runs = [];
    for (const w of words) {
      const last = runs[runs.length - 1];
      if (last && w[1] - last.end < 0.35) last.end = w[2]; else runs.push({ start: w[1], end: w[2] });
    }
    for (const r of runs) {
      tl.to("#lens-eye", { opacity: 0, duration: 0.12 }, r.start - 0.08);
      tl.to("#lens-bars", { opacity: 1, duration: 0.12 }, r.start - 0.08);
      tl.to("#lens-pulse", { opacity: 0.55, duration: 0.2 }, r.start - 0.08);
      tl.to("#lens-eye", { opacity: 1, duration: 0.2 }, r.end + 0.1);
      tl.to("#lens-bars", { opacity: 0, duration: 0.2 }, r.end + 0.1);
      tl.to("#lens-pulse", { opacity: 0, duration: 0.3 }, r.end + 0.1);
    }
    // Bars jump on every word (deterministic heights, no randomness: renders must be repeatable).
    const bars = Array.from(document.querySelectorAll("#lens .lens-bar"));
    words.forEach((w, i) => {
      bars.forEach((b, j) => {
        const peak = 0.6 + 0.4 * (((i * 7 + j * 3) % 5) / 4);
        tl.to(b, { scaleY: peak, transformOrigin: "50% 50%", duration: 0.08, ease: "power2.out" }, w[1]);
        tl.to(b, { scaleY: 0.4, transformOrigin: "50% 50%", duration: Math.max(0.1, (w[2] - w[1]) * 0.7), ease: "power1.in" }, w[1] + 0.08);
      });
    });
    // Idle: the pupil glances and the eye blinks every ~2.6 s, only outside speaking runs.
    const quiet = (t) => !runs.some((r) => t > r.start - 0.3 && t < r.end + 0.4);
    for (let t = start + 0.8, k = 0; t < end - 0.3; t += 2.6, k++) {
      if (!quiet(t)) continue;
      tl.to("#lens-eye", { scaleY: 0.12, transformOrigin: "50% 50%", duration: 0.07, yoyo: true, repeat: 1 }, t);
      tl.to("#lens-pupil", { x: k % 2 ? -14 : 10, duration: 0.3, ease: "power2.out" }, t + 0.3);
    }
  }
})();
