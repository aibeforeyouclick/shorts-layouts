// Three images, a title and a small subtitle. Copied into <video>/vendor/ by tools/storytelling.py; do not edit the copy.
// Reads window.STORY (storytelling.data.js): {phase, title, sub, sub_anchor, sub_n, images: [{src, label, anchor, n}]}.
// Fills the section #<phase>: its own content is hidden. Each image pops in on its spoken word.
(function () {
  const S = window.STORY;
  const tl = (window.__timelines || {}).main;
  const W = window.WORDS;
  const ph = (window.PHASES || {})[S && S.phase];
  if (!S || !tl || !W || !ph) throw new Error("storytelling: missing STORY, main timeline, WORDS or PHASES[" + (S && S.phase) + "]");
  const section = document.getElementById(S.phase);
  if (!section) throw new Error("storytelling: no section #" + S.phase + " in index.html");

  // n counts inside this phase only (same as the check in tools/layoutlib.py).
  function at(word, n) {
    let seen = 0;
    for (const w of W) {
      if (w[1] < ph.start || w[1] >= ph.end) continue;
      if (w[0].toLowerCase().replace(/[^a-z0-9']/g, "") === word && ++seen === n) return w[1];
    }
    throw new Error("storytelling: word not in transcript: " + word + " #" + n);
  }

  const css = `
    #story { width: 960px; font-family: Inter, "Segoe UI", ui-sans-serif, system-ui, sans-serif; text-align: center; }
    #story .imgs { display: flex; gap: 24px; justify-content: center; margin-bottom: 56px; }
    #story .tile { width: 300px; }
    #story .tile .ph { width: 300px; height: 380px; border-radius: 26px; overflow: hidden; background: #1b1d22; box-shadow: 0 18px 50px rgba(0,0,0,0.45); }
    #story .tile img { width: 100%; height: 100%; object-fit: cover; display: block; }
    #story .tile .lb { margin-top: 16px; font-size: 32px; font-weight: 700; color: #c9cede; }
    #story .title { font-size: 84px; font-weight: 900; line-height: 1.05; letter-spacing: -0.02em; color: #fff; }
    #story .sub { margin-top: 22px; font-size: 44px; font-weight: 600; color: #aeb6cc; }
  `;
  const style = document.createElement("style");
  style.textContent = css;
  document.head.appendChild(style);

  for (const child of Array.from(section.children)) child.style.display = "none";
  const box = document.createElement("div");
  box.id = "story";
  box.innerHTML = '<div class="imgs"></div><div class="title"></div><div class="sub"></div>';
  box.querySelector(".title").textContent = S.title;
  box.querySelector(".sub").textContent = S.sub;
  S.images.forEach((im, i) => {
    const tile = document.createElement("div");
    tile.className = "tile";
    tile.id = "story-tile-" + i;
    tile.innerHTML = '<div class="ph"><img alt="" /></div><div class="lb"></div>';
    tile.querySelector("img").src = im.src;
    tile.querySelector(".lb").textContent = im.label || "";
    box.querySelector(".imgs").appendChild(tile);
  });
  section.appendChild(box);

  tl.from("#story .title", { y: 50, opacity: 0, duration: 0.45, ease: "power3.out" }, ph.start);
  S.images.forEach((im, i) => {
    tl.from("#story-tile-" + i, { y: 80, scale: 0.85, opacity: 0, duration: 0.45, ease: "back.out(1.8)" }, at(im.anchor, im.n) - 0.1);
  });
  tl.from("#story .sub", { y: 30, opacity: 0, duration: 0.4 }, S.sub_anchor ? at(S.sub_anchor, S.sub_n) - 0.1 : ph.start + 0.6);
  tl.seek(0);
})();
