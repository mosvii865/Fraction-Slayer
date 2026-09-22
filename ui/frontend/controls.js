"use strict";
// Multitouch: independent pointer capture for movement, camera, fire and use.
let padPointer = null,
  lookPointer = null,
  lastLook = 0;
$("#pad").onpointerdown = (e) => {
  e.preventDefault();
  padPointer = e.pointerId;
  $("#pad").setPointerCapture(e.pointerId);
  padMove(e);
};
function padMove(e) {
  if (e.pointerId !== padPointer || !FS.playing) return;
  const r = $("#pad").getBoundingClientRect(),
    x = e.clientX - r.left - r.width / 2,
    y = e.clientY - r.top - r.height / 2,
    d = Math.hypot(x, y);
  if (d < 12) {
    FS.move = { x: 0, y: 0 };
    return;
  }
  const angle = (Math.round(Math.atan2(y, x) / (Math.PI / 4)) * Math.PI) / 4;
  FS.move = { x: Math.cos(angle), y: Math.sin(angle) };
  $("#stick").style.transform =
    `translate(${Math.cos(angle) * Math.min(d, 30)}px,${Math.sin(angle) * Math.min(d, 30)}px)`;
}
$("#pad").onpointermove = padMove;
for (const event of ["pointerup", "pointercancel", "lostpointercapture"])
  $("#pad").addEventListener(event, () => {
    padPointer = null;
    FS.move = { x: 0, y: 0 };
    $("#stick").style.transform = "";
  });
$("#look").onpointerdown = (e) => {
  if (!FS.playing) return;
  if (e.pointerType === "mouse") {
    if (document.pointerLockElement) shoot();
    else lockMouse();
    return;
  }
  lookPointer = e.pointerId;
  lastLook = e.clientX;
  $("#look").setPointerCapture(e.pointerId);
  e.preventDefault();
};
$("#look").onpointermove = (e) => {
  if (e.pointerId === lookPointer && FS.playing) {
    FS.state.player.angle +=
      (e.clientX - lastLook) * 0.006 * FS.settings.sensitivity;
    lastLook = e.clientX;
  }
};
for (const event of ["pointerup", "pointercancel", "lostpointercapture"])
  $("#look").addEventListener(event, () => (lookPointer = null));
$("#fire").onpointerdown = (e) => {
  e.preventDefault();
  $("#fire").setPointerCapture(e.pointerId);
  FS.fireHeld = true;
  shoot();
};
for (const event of ["pointerup", "pointercancel", "lostpointercapture"])
  $("#fire").addEventListener(event, () => (FS.fireHeld = false));
button("interact", interact);
button("reload", reload);
button("weapon", () => {
  if (FS.playing)
    selectWeapon(FS.state.weapon === "pistol" ? "shotgun" : "pistol");
});
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
$("#world").onmousedown = (e) => {
  if (!FS.playing) return;
  if (document.pointerLockElement) {
    if (e.button === 0) {
      FS.fireHeld = true;
      shoot();
    }
  } else lockMouse();
};
window.addEventListener("mouseup", () => (FS.fireHeld = false));
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
  if (e.target.tagName === "INPUT") return;
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
window.addEventListener("resize", () => {
  if (
    window.innerWidth < window.innerHeight &&
    window.innerWidth < 1000 &&
    FS.playing
  )
    pauseMenu(!Bridge.busy);
});
document.addEventListener("pointerlockchange", () => {
  if (!document.pointerLockElement && FS.playing) pauseMenu(!Bridge.busy);
});
window.addEventListener("contextmenu", (e) => e.preventDefault());
let prev = performance.now();
function frame(now) {
  const dt = Math.min(0.04, (now - prev) / 1000);
  prev = now;
  const t = now / 1000;
  tick(dt, t);
  if (FS.state && !$("#hud").classList.contains("hidden")) Render.world(FS, t);
  else Render.factory(t);
  requestAnimationFrame(frame);
}
mainMenu();
requestAnimationFrame(frame);
