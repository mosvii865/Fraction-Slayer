"use strict";
/* Every contact keeps its role from pointerdown until up/cancel/lost capture.
 * Never filter isPrimary: secondary fingers operate all action buttons.
 * Only pause/death/rotation/connection loss releases all contacts together.
 */
const InputControls = (window.InputControls = (() => {
  const active = new Map();
  const app = $("#app"),
    pad = $("#pad"),
    zone = $("#move-zone");
  let moveId = null,
    lookId = null,
    touchMode = matchMedia('(pointer: coarse)').matches;
  let lastVibration = 0;
  const presets = {
    small: {
      fire: 96,
      auxiliary: 68,
      radius: .85,
      gap: 12,
      picker: 106
    },
    medium: {
      fire: 116,
      auxiliary: 82,
      radius: 1,
      gap: 14,
      picker: 120
    },
    large: {
      fire: 136,
      auxiliary: 96,
      radius: 1.15,
      gap: 16,
      picker: 136
    },
  };
  if (!presets[FS.settings.controlSize]) FS.settings.controlSize = 'medium';
  if (!['half', 'corner'].includes(FS.settings.movementZone)) FS.settings.movementZone = 'half';
  const savedRadius = Number(FS.settings.joystickRadius);
  FS.settings.joystickRadius = Number.isFinite(savedRadius) ? Math.max(40, Math.min(85, savedRadius)) : 60;
  FS.settings.vibration = FS.settings.vibration === true;
  let radius = 60,
    deadZone = 10;
  const canPlay = () => FS.playing && $('#connection').classList.contains('hidden');

  function refreshFire() {
    FS.fireHeld = [...active.values()].some(p => p.role === 'fire');
  }

  function closePicker() {
    $('#weapon-picker').classList.add('hidden');
    $('#weapon-toggle').setAttribute('aria-expanded', 'false');
    $('#weapon').setAttribute('aria-expanded', 'false');
  }

  function togglePicker() {
    if (!canPlay()) return;
    const picker = $('#weapon-picker');
    if (!picker.classList.contains('hidden')) {
      closePicker();
      return;
    }
    picker.querySelectorAll('[data-select-weapon]').forEach(b => {
      const key = b.dataset.selectWeapon,
        w = FS.state.weapons[key];
      b.disabled = !w;
      b.setAttribute('aria-pressed', FS.state.weapon === key);
      b.querySelector('.weapon-ammo').textContent = w ? `${w.loaded} / ${w.reserve} · MOD ${w.mods?'I':'0'}` : 'SIN RECOGER';
    });
    picker.classList.remove('hidden');
    $('#weapon-toggle').setAttribute('aria-expanded', 'true');
    $('#weapon').setAttribute('aria-expanded', 'true');
  }

  function layout() {
    app.classList.toggle('touch-controls', touchMode);
    app.dataset.movementZone = FS.settings.movementZone;
    const p = presets[FS.settings.controlSize];
    const rect = $('#controls').getBoundingClientRect();
    // Keep big controls inside the playable viewport on shorter phones.
    const scale = Math.max(.65, Math.min(1, (rect.height - 24) / (p.fire + p.auxiliary + p.gap),
      (rect.width * .52 - 24) / (p.fire + p.auxiliary + p.gap)));
    app.style.setProperty('--fire-size', `${Math.round(p.fire*scale)}px`);
    app.style.setProperty('--aux-size', `${Math.round(p.auxiliary*scale)}px`);
    app.style.setProperty('--control-gap', `${Math.max(8,Math.round(p.gap*scale))}px`);
    app.style.setProperty('--picker-width', `${Math.max(120,Math.round(p.picker*scale))}px`);
    app.style.setProperty('--picker-height', `${Math.max(48,Math.min(Math.round(p.auxiliary*scale),Math.floor((rect.height-92)/2)))}px`);
    // Freeze the active stick's geometry as well as its origin until release.
    if (moveId === null) {
      radius = Math.max(30, FS.settings.joystickRadius * p.radius * scale);
      deadZone = Math.max(7, radius * .16);
      app.style.setProperty('--joystick-size', `${radius*2}px`);
      app.style.setProperty('--stick-size', `${Math.max(40,radius*.82)}px`);
    }
  }

  function enableTouch(e) {
    if (e.pointerType === 'mouse') return false;
    if (!touchMode) {
      touchMode = true;
      layout();
    }
    return true;
  }

  function claim(e, role, element) {
    if (!canPlay() || active.has(e.pointerId)) return null;
    if (e.pointerType === 'mouse' && e.button !== 0 && !(e.button === 2 && role === 'look')) return null;
    enableTouch(e);
    e.preventDefault();
    e.stopPropagation();
    const p = {
      role,
      element,
      x: e.clientX,
      y: e.clientY,
      originX: e.clientX,
      originY: e.clientY,
      radius,
      deadZone
    };
    active.set(e.pointerId, p);
    try {
      element.setPointerCapture(e.pointerId);
    } catch {} // OS can cancel between events.
    return p;
  }

  function finish(e) {
    const p = active.get(e.pointerId);
    if (!p) return;
    active.delete(e.pointerId);
    if (moveId === e.pointerId) {
      moveId = null;
      FS.move = {
        x: 0,
        y: 0
      };
      pad.classList.remove('active');
      $('#stick').style.transform = '';
    }
    if (lookId === e.pointerId) lookId = null;
    refreshFire();
    try {
      if (p.element.hasPointerCapture(e.pointerId)) p.element.releasePointerCapture(e.pointerId);
    } catch {}
  }

  function reset() {
    const pointers = [...active.entries()];
    active.clear();
    moveId = null;
    lookId = null;
    FS.move = {
      x: 0,
      y: 0
    };
    FS.fireHeld = false;
    pad.classList.remove('active');
    $('#stick').style.transform = '';
    closePicker();
    for (const [id, p] of pointers) try {
      if (p.element.hasPointerCapture(id)) p.element.releasePointerCapture(id);
    } catch {}
  }
  zone.addEventListener('pointerdown', e => {
    if (e.pointerType === 'mouse') return;
    const p = claim(e, moveId === null ? 'move' : 'ignored', zone);
    if (!p || p.role === 'ignored') return;
    moveId = e.pointerId;
    FS.move = {
      x: 0,
      y: 0
    };
    const box = $('#controls').getBoundingClientRect();
    pad.style.left = `${e.clientX-box.left}px`;
    pad.style.top = `${e.clientY-box.top}px`;
    pad.classList.add('active');
  });

  function mouseStage(e, element) {
    if (!canPlay()) return;
    if (e.button === 2) {
      if (lookId !== null) return;
      if (claim(e, 'look', element)) lookId = e.pointerId;
    } else if (e.button === 0 && claim(e, 'fire', element)) {
      refreshFire();
      shoot();
      if (!document.pointerLockElement && !FS.mouseLockDenied) lockMouse();
    }
  }
  $('#look').addEventListener('pointerdown', e => {
    if (e.pointerType === 'mouse') {
      mouseStage(e, $('#look'));
      return;
    }
    const p = claim(e, lookId === null ? 'look' : 'ignored', $('#look'));
    if (p && p.role === 'look') lookId = e.pointerId;
  });
  document.addEventListener('pointermove', e => {
    const p = active.get(e.pointerId);
    if (!p || !canPlay()) return;
    e.preventDefault();
    if (p.role === 'move') {
      const dx = e.clientX - p.originX,
        dy = e.clientY - p.originY,
        d = Math.hypot(dx, dy);
      // Continuous analog direction covers all eight directions without diagonal snapping.
      const magnitude = Math.max(0, Math.min(1, (d - p.deadZone) / (p.radius - p.deadZone)));
      FS.move = d ? {
        x: dx / d * magnitude,
        y: dy / d * magnitude
      } : {
        x: 0,
        y: 0
      };
      const visual = d ? Math.min(d, p.radius) / d : 0;
      $('#stick').style.transform = `translate(${dx*visual}px,${dy*visual}px)`;
    } else if (p.role === 'look') {
      if (e.pointerType !== 'mouse' || !document.pointerLockElement)
        FS.state.player.angle += (e.clientX - p.x) * .006 * FS.settings.sensitivity;
    }
    p.x = e.clientX;
    p.y = e.clientY;
  }, {
    passive: false
  });
  for (const type of ['pointerup', 'pointercancel', 'lostpointercapture']) document.addEventListener(type, finish);

  function actionButton(element, action, role = 'button') {
    element.addEventListener('pointerdown', e => {
      if (element.disabled) return;
      const p = claim(e, role, element);
      if (!p) return;
      if (role === 'fire') refreshFire();
      action();
    });
    // Keyboard / assistive activation has detail=0. Physical pointers act on down.
    element.addEventListener('click', e => {
      e.preventDefault();
      e.stopPropagation();
      if (e.detail === 0 && canPlay() && !element.disabled) action();
    });
  }
  actionButton($('#fire'), shoot, 'fire');
  actionButton($('#interact'), interact);
  actionButton($('#reload-touch'), reload);
  actionButton($('#reload'), reload);
  actionButton($('#weapon-toggle'), togglePicker);
  actionButton($('#weapon'), () => {
    if (touchMode) return togglePicker();
    const order=['pistol','shotgun','assault','sawed_off'].filter(w=>FS.state.weapons[w]);
    if (!order.length) return;
    const i=Math.max(0,order.indexOf(FS.state.weapon));
    selectWeapon(order[(i+1)%order.length]);
  });
  actionButton($('#weapon-close'), closePicker);
  document.querySelectorAll('[data-select-weapon]').forEach(b => actionButton(b, () => {
    selectWeapon(b.dataset.selectWeapon);
    closePicker();
  }));
  $('#world').addEventListener('pointerdown', e => {
    if (e.pointerType !== 'mouse' || !canPlay()) return;
    mouseStage(e, $('#world'));
  });

  function haptic(kind) {
    if (!touchMode || !FS.settings.vibration || typeof navigator.vibrate !== 'function') return;
    const now = performance.now();
    if (now - lastVibration < 50) return;
    lastVibration = now;
    try {
      navigator.vibrate({
        shot: 6,
        hurt: 14,
        weapon: 8
      } [kind] || 6);
    } catch {}
  }
  layout();
  return {
    active,
    reset,
    layout,
    haptic,
    closePicker,
    get touchMode() {
      return touchMode
    },
    get movementPointer() {
      return moveId
    },
    get cameraPointer() {
      return lookId
    }
  };
})());
button("pause", () => pauseMenu());
button("fullscreen", async () => {
  try {
    if (!document.fullscreenElement) await $("#app").requestFullscreen();
    else await document.exitFullscreen();
  } catch {
    toast(
      "Tu navegador no permite pantalla completa aquí. Usa horizontal y oculta la barra del navegador.",
    );
  }
});
window.addEventListener("mousemove", (e) => {
  if (FS.playing && document.pointerLockElement)
    FS.state.player.angle += e.movementX * 0.0025 * FS.settings.sensitivity;
});
window.addEventListener("keydown", (e) => {
  if (modalQuestion?.mode === "manual") {
    if (/^[0-9./,]$/.test(e.key)) {
      e.preventDefault();
      keypad(e.key === "," ? "." : e.key);
    } else if (e.key === "Backspace") {
      e.preventDefault();
      keypad("⌫");
    } else if (e.key === "Enter") {
      e.preventDefault();
      submitAnswer(manual);
    }
    return;
  }
  if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) return;
  if (e.target.closest('button') && ['Space', 'Enter'].includes(e.code)) return;
  if (e.code === 'Escape' && !$('#weapon-picker').classList.contains('hidden')) {
    InputControls.closePicker();
    return;
  }
  if (FS.playing) {
    if (
      [
        "KeyW",
        "KeyA",
        "KeyS",
        "KeyD",
        "ArrowLeft",
        "ArrowRight",
        "Space",
      ].includes(e.code)
    )
      e.preventDefault();
    FS.keys[e.code] = true;
    if (!e.repeat) {
      if (e.code === "KeyE") interact();
      if (e.code === "KeyR") reload();
      if (e.code === "Digit1") selectWeapon("pistol");
      if (e.code === "Digit2") selectWeapon("shotgun");
      if (e.code === "Digit3") selectWeapon("assault");
      if (e.code === "Digit4") selectWeapon("sawed_off");
      if (e.code === "Escape") pauseMenu();
      if (e.code === "Space") shoot();
    }
  }
});
window.addEventListener("keyup", (e) => delete FS.keys[e.code]);
window.addEventListener("blur", () => {
  releaseInput();
  if (FS.playing) pauseMenu(!Bridge.busy);
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    releaseInput();
    if (FS.playing) pauseMenu(!Bridge.busy);
  }
});
let layoutFrame = null;
let viewport = {
  w: innerWidth,
  h: innerHeight,
  portrait: innerWidth < innerHeight
};

function viewportChanged(event) {
  const next = {
    w: innerWidth,
    h: innerHeight,
    portrait: innerWidth < innerHeight
  };
  const strong = next.portrait !== viewport.portrait || Math.abs(next.w - viewport.w) > 64 || Math.abs(next.h - viewport.h) > Math.max(120, viewport.h * .35);
  if (strong) releaseInput();
  if (next.portrait && (InputControls.touchMode || next.w < 1000) && FS.playing) pauseMenu(!Bridge.busy);
  viewport = next;
  cancelAnimationFrame(layoutFrame);
  layoutFrame = requestAnimationFrame(() => {
    InputControls.layout();
    Render.resize();
  });
}
window.addEventListener('resize', viewportChanged);
window.addEventListener('orientationchange', () => requestAnimationFrame(viewportChanged));
window.visualViewport?.addEventListener('resize', viewportChanged);
document.addEventListener("pointerlockchange", () => {
  if (!document.pointerLockElement && FS.playing) pauseMenu(!Bridge.busy);
});
$("#app").addEventListener("contextmenu", (e) => {
  if (FS.playing) e.preventDefault();
});
// Diagnostic switch: false hides details, never suppresses the error itself.
const DEBUG_ENGINE_ERRORS = true;
function reportEngineError(error) {
  const report = {
    name: error?.name || 'Error', message: error?.message || String(error),
    stack: String(error?.stack || '').split('\n').slice(0, 12).join('\n'),
    stage: FS.debugStage, level_id: FS.state?.level_id ?? null,
    checkpoint: FS.state?.checkpoint ?? null, bridge_busy: Bridge.busy,
    last_event: Bridge.last_event, state_null: FS.state === null,
    state_undefined: FS.state === undefined, timestamp: new Date().toISOString(),
    player: FS.state?.player ? {x:FS.state.player.x,y:FS.state.player.y,hp:FS.state.player.hp} : null,
    checkpoint_ids: FS.config?.level?.checkpoints?.map(c=>c.id) ?? null
  };
  FS.lastEngineError = report;
  console.error('Fraction Slayer frame error', report, error);
  FS.engineFault = true;
  freeze();
  const text = JSON.stringify(report, null, 2);
  panel('<h2>ERROR DE MOTOR</h2><p>El estado se conserva. Puedes reintentar o volver al menú.</p>' +
    (DEBUG_ENGINE_ERRORS ? '<pre id="engine-error-details" tabindex="0">'+esc(text)+'</pre><button id="copy-engine-error">COPIAR ERROR</button><p id="copy-error-status" role="status"></p>' : '') +
    '<button id="retry-frame">REINTENTAR</button><button id="fault-menu">MENÚ</button>', 'engine-error-panel');
  button('copy-engine-error', async()=>{
    try {if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');await navigator.clipboard.writeText(text);$('#copy-error-status').textContent='Error copiado.';}
    catch {const range=document.createRange();range.selectNodeContents($('#engine-error-details'));const selection=getSelection();selection.removeAllRanges();selection.addRange(range);$('#copy-error-status').textContent='Mantén pulsado el texto para copiarlo.';}
  });
  button('retry-frame',()=>{FS.engineFault=false;FS.state?resume():mainMenu();});
  button('fault-menu',()=>{FS.engineFault=false;mainMenu();});
}
let prev = performance.now();

function frame(now) {
  const dt = Math.min(0.04, (now - prev) / 1000);
  prev = now;
  const t = now / 1000;
  try {
    if (!FS.engineFault) {
      FS.debugStage = 'FRAME_START';
      FS.debugStage = 'STATE_VALIDATE';
      tick(dt, t);
      FS.debugStage = 'RENDER_WORLD';
      if (FS.state && !$('#hud').classList.contains('hidden')) Render.world(FS, t);
      else Render.factory(t);
      FS.debugStage = 'FRAME_END';
    }
  } catch (error) {
    reportEngineError(error);
  } finally {
    requestAnimationFrame(frame);
  }

}
mainMenu();
requestAnimationFrame(frame);
