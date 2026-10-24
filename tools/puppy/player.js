/* One decoded atlas per character; one loop draws only visible characters. */
window.Puppy25 = (() => {
  'use strict';
  const models = {
    tori: {assets: PUPPY_ASSETS, label: '강아지 토리'},
    bora: {assets: CAT_ASSETS, label: '고양이 보라'}
  };
  for (const model of Object.values(models)) {
    model.meta = model.assets.manifest;
    model.atlas = new Image();
    model.ready = false;
  }
  const instances = new Map();
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let raf = 0, lastTick = 0;

  function markup(kind = 'tori') {
    const {assets, label} = models[kind];
    return `<span class="chr puppy25" data-character="${kind}" data-mood="normal" role="img" aria-label="${label}"><img class="puppy-poster" src="${assets.poster}" alt="" draggable="false"><canvas width="320" height="320" aria-hidden="true"></canvas></span>`;
  }
  function paws(kind = 'tori') {
    const {assets} = models[kind];
    return `<span class="puppy-paws" aria-hidden="true"><img class="p p1" src="${assets.paw}" alt="" draggable="false"><img class="p p2" src="${assets.paw}" alt="" draggable="false"></span>`;
  }
  function attach() {
    document.querySelectorAll('.puppy25').forEach(el => {
      if (instances.has(el)) return;
      const canvas = el.querySelector('canvas');
      const bust = !!el.closest('#chTori, #chBora');
      const model = models[el.dataset.character || 'tori'];
      canvas.height = bust ? 306 : 320;
      el.classList.toggle('puppy-bust', bust);
      instances.set(el, {el, model, canvas, ctx: canvas.getContext('2d'), bust, clip: '', started: 0, frame: -1, visible: false, hop: ''});
    });
    for (const [el] of instances) if (!el.isConnected) instances.delete(el);
    wake();
  }
  function isVisible(el) {
    const screen = el.closest('.screen');
    return el.isConnected && (!screen || screen.classList.contains('on'));
  }
  function requestedClip(el, meta) {
    const mood = el.dataset.mood;
    if (mood === 'eat') return meta.clips.eat ? 'eat' : 'happy';
    if (mood === 'happy') return 'happy';
    if (mood === 'sad' || mood === 'wow') return mood;
    return el.dataset.look === 'left' ? 'lookLeft' : el.dataset.look === 'right' ? 'lookRight' : 'normal';
  }
  function draw(state, now) {
    const {meta, atlas} = state.model;
    let clip = requestedClip(state.el, meta);
    if (clip === 'normal' && state.clip === 'happy' && !reduceMotion.matches) {
      const duration = meta.clips.happy.count / meta.fps * 1000;
      // A short cookie response must land before returning to idle.
      if (now - state.started < duration) clip = 'happy';
    }
    const hop = state.el.dataset.hop || '';
    if (state.clip !== clip || state.hop !== hop || !state.visible) {
      state.clip = clip; state.started = now; state.frame = -1; state.hop = hop;
    }
    state.visible = true;
    const info = meta.clips[clip];
    const local = reduceMotion.matches ? 0 : Math.floor((now - state.started) * meta.fps / 1000) % info.count;
    const index = info.start + local;
    if (index === state.frame) return;
    state.frame = index;
    const x = (index % meta.columns) * meta.cell, y = Math.floor(index / meta.columns) * meta.cell;
    const ctx = state.ctx;
    ctx.clearRect(0, 0, state.canvas.width, state.canvas.height);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    if (state.bust) {
      const [cx, cy, cw, ch] = meta.crop;
      ctx.drawImage(atlas, x + cx, y + cy, cw, ch, 0, 0, state.canvas.width, state.canvas.height);
    } else {
      ctx.drawImage(atlas, x, y, meta.cell, meta.cell, 0, 0, state.canvas.width, state.canvas.height);
    }
    state.el.classList.add('puppy-ready');
  }
  function tick(now) {
    raf = 0;
    if (document.hidden) return;
    let active = false;
    const due = now - lastTick >= 1000 / 15 - 2;
    for (const state of instances.values()) {
      if (state.model.ready && isVisible(state.el)) {
        active = true;
        if (due) draw(state, now);
      } else state.visible = false;
    }
    if (due) lastTick = now;
    if (active && !reduceMotion.matches) raf = requestAnimationFrame(tick);
  }
  function wake() {
    if (Object.values(models).some(m => m.ready) && !document.hidden && !raf) {
      lastTick = 0;
      raf = requestAnimationFrame(tick);
    }
  }
  function hop(el) {
    if (!el) return;
    el.dataset.hop = String((Number(el.dataset.hop) || 0) + 1);
    wake();
  }
  function look(el, side) {
    if (el) el.dataset.look = side || '';
    wake();
  }
  for (const model of Object.values(models)) {
    model.atlas.onload = () => { model.ready = true; attach(); };
    model.atlas.onerror = () => { console.warn(`${model.label}: animation unavailable; static preview retained.`); };
    model.atlas.src = model.assets.atlas;
  }
  new MutationObserver(records => {
    if (records.some(r => r.type === 'childList')) attach();
    else wake();
  }).observe(document.body, {subtree: true, childList: true, attributes: true, attributeFilter: ['data-mood', 'data-look', 'data-hop', 'class']});
  document.addEventListener('visibilitychange', () => {
    if (document.hidden && raf) { cancelAnimationFrame(raf); raf = 0; }
    else wake();
  });
  reduceMotion.addEventListener('change', () => {
    for (const s of instances.values()) s.frame = -1;
    wake();
  });
  attach();
  return Object.freeze({markup, paws, hop, look});
})();
