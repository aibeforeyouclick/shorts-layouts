// Trial-reel hook screen. Copied into <video>/vendor/ by tools/trial_reels.py; do not edit the copy.
// Picks the version from the render variable "trial" (A|B|C) and window.TRIALS (trials.js).
// "off" (the default declared on <html>) = control: does nothing.
(function () {
  const hf = window.__hyperframes;
  const key = (hf && hf.getVariables ? hf.getVariables().trial : "off") || "off";
  if (key === "off") return;
  const trial = (window.TRIALS || {})[key];
  const tl = (window.__timelines || {}).main;
  const p1 = (window.PHASES || {}).p1;
  if (!trial || !tl || !p1) throw new Error("trial-hook: missing TRIALS[" + key + "], main timeline or PHASES.p1");

  const css = `
    #trial { position: absolute; inset: 0; z-index: 4; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0 70px 360px; text-align: center; font-family: Inter, "Segoe UI", ui-sans-serif, system-ui, sans-serif; }
    #trial.headline { background: #0b0b0b; }
    #trial.headline .t { display: flex; flex-direction: column; align-items: center; gap: 18px; }
    #trial.headline .t span { background: #ffd400; color: #0b0b0b; font-size: 128px; font-weight: 900; line-height: 1; letter-spacing: -0.03em; padding: 14px 28px 18px; text-transform: uppercase; }
    #trial.headline .s { margin-top: 60px; color: #fff; font-size: 52px; font-weight: 800; }
    #trial.post { background: #15181d; }
    #trial.post .card { width: 920px; background: #fff; color: #0f1419; border-radius: 34px; padding: 54px 58px; text-align: left; box-shadow: 0 30px 80px rgba(0,0,0,0.5); }
    #trial.post .who { display: flex; align-items: center; gap: 26px; margin-bottom: 34px; }
    #trial.post .av { width: 104px; height: 104px; border-radius: 50%; background: #0f1419; color: #ffd400; font-size: 44px; font-weight: 900; display: flex; align-items: center; justify-content: center; }
    #trial.post .nm { font-size: 42px; font-weight: 800; }
    #trial.post .hd { font-size: 34px; color: #536471; }
    #trial.post .t { font-size: 62px; font-weight: 700; line-height: 1.25; }
    #trial.post .s { margin-top: 34px; font-size: 38px; color: #536471; }
    #trial.minimal { background: #f3efe7; color: #1d1b18; }
    #trial.minimal .t { font-family: Georgia, "Times New Roman", serif; font-size: 96px; font-weight: 400; line-height: 1.1; text-transform: lowercase; }
    #trial.minimal .rule { width: 0; height: 4px; background: #1d1b18; margin: 50px auto 0; }
    #root[data-light="1"] #cap .line { color: #1d1b18; text-shadow: none; }
    #root[data-light="1"] .badge { color: #5a554d; border-color: #c9c2b5; }
    #trial.minimal .s { margin-top: 40px; font-size: 40px; letter-spacing: 0.12em; color: #6b655c; text-transform: lowercase; }
  `;
  const style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  const el = document.createElement("div");
  el.id = "trial";
  el.className = trial.style;
  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  if (trial.style === "headline") {
    el.innerHTML = '<div class="t">' + trial.text.split(/\s+/).reduce((rows, w) => {
      const last = rows[rows.length - 1];
      if (last && (last + " " + w).length <= 11) rows[rows.length - 1] = last + " " + w; else rows.push(w);
      return rows;
    }, []).map((r) => "<span>" + esc(r) + "</span>").join("") + '</div><div class="s">' + esc(trial.sub) + "</div>";
  } else if (trial.style === "post") {
    el.innerHTML = '<div class="card"><div class="who"><div class="av">' + esc(trial.avatar || "AI") + '</div><div><div class="nm">' +
      esc(trial.name || "AI Before You Click") + '</div><div class="hd">' + esc(trial.handle || "@aibeforeyouclick") + '</div></div></div><div class="t">' + esc(trial.text) + '</div><div class="s">' + esc(trial.sub) + "</div></div>";
  } else {
    el.innerHTML = '<div class="t">' + esc(trial.text) + '</div><div class="rule"></div><div class="s">' + esc(trial.sub) + "</div>";
  }
  document.getElementById("root").appendChild(el);

  // Text is readable at frame 0; the sub line is the second beat halfway through p1; fade out at the end of p1.
  const mid = p1.start + (p1.end - p1.start) * 0.5;
  if (trial.style === "headline") tl.from("#trial .t span", { scaleX: 0.6, duration: 0.35, stagger: 0.08, ease: "back.out(2)" }, 0);
  if (trial.style === "post") tl.from("#trial .card", { y: 40, duration: 0.5, ease: "power3.out" }, 0);
  if (trial.style === "minimal") tl.to("#trial .rule", { width: 420, duration: 0.8, ease: "power2.out" }, 0.2);
  // Light background: dark captions and badge while the hook screen is up.
  if (trial.style === "minimal") {
    tl.set("#root", { attr: { "data-light": "1" } }, 0);
    tl.set("#root", { attr: { "data-light": "0" } }, p1.end);
  }
  tl.from("#trial .s", { y: 30, opacity: 0, duration: 0.4 }, mid);
  tl.to("#trial", { opacity: 0, duration: 0.25 }, p1.end - 0.25);
  tl.set("#trial", { display: "none" }, p1.end);
  tl.seek(0);
})();
