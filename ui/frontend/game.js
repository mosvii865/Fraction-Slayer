"use strict";
const $ = (s) => document.querySelector(s),
  clone = (x) => JSON.parse(JSON.stringify(x));
const esc = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[
        c
      ],
  );
const FS = (window.FS = {
  state: null,
  config: null,
  playing: false,
  settings: { sensitivity: 1, sound: true, minimap: true, quality: "normal" },
  keys: {},
  move: { x: 0, y: 0 },
  moving: 0,
  projectiles: [],
  shotFlash: 0,
  hurtFlash: 0,
  faceUntil: 0,
  faceExpression: "normal",
  cooldown: 0,
  reloading: 0,
  fireHeld: false,
  elapsed: 0,
  lastSync: 0,
  nearest: null,
});
let slot = null,
  lastStats = null,
  modalQuestion = null,
  manual = "",
  currentStation = null,
  currentWeapon = "pistol",
  audio = null,
  toastTimer = null;
try {
  slot = JSON.parse(localStorage.getItem("fraction-slayer-save"));
  lastStats = JSON.parse(localStorage.getItem("fraction-slayer-stats"));
  Object.assign(
    FS.settings,
    JSON.parse(localStorage.getItem("fraction-slayer-settings") || "{}"),
  );
} catch {}
function store(reply) {
  if (reply.save) {
    slot = reply.save;
    try {
      localStorage.setItem("fraction-slayer-save", JSON.stringify(slot));
    } catch {
      toast("Guardado local no disponible. Exporta tu partida desde Pausa.");
    }
  }
  if (reply.stats) {
    lastStats = reply.stats;
    try {
      localStorage.setItem("fraction-slayer-stats", JSON.stringify(lastStats));
    } catch {}
  }
}
function toast(text) {
  $("#toast").textContent = text;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => ($("#toast").textContent = ""), 3400);
}
function sound(kind) {
  if (!FS.settings.sound) return;
  try {
    audio = audio || new (window.AudioContext || window.webkitAudioContext)();
    audio.resume();
    const o = audio.createOscillator(),
      g = audio.createGain();
    o.connect(g);
    g.connect(audio.destination);
    o.type = kind === "shot" ? "sawtooth" : "sine";
    const freq =
      { shot: 110, hurt: 70, pickup: 650, good: 880, bad: 130, reload: 220 }[
        kind
      ] || 300;
    o.frequency.setValueAtTime(freq, audio.currentTime);
    o.frequency.exponentialRampToValueAtTime(
      freq * 0.35,
      audio.currentTime + 0.15,
    );
    g.gain.setValueAtTime(0.055, audio.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, audio.currentTime + 0.18);
    o.start();
    o.stop(audio.currentTime + 0.2);
  } catch {}
}
function expression(type) {
  FS.faceExpression = type;
  FS.faceUntil = performance.now() / 1000 + 1.3;
}
function lockMouse() {
  try {
    const p = $("#world").requestPointerLock?.();
    p?.catch(() => toast("Mouse libre: usa ← → para girar."));
  } catch {
    toast("Usa ← → para girar.");
  }
}
function releaseInput() {
  FS.keys = {};
  FS.move = { x: 0, y: 0 };
  FS.fireHeld = false;
  $("#stick").style.transform = "";
}
FS.releaseInput = releaseInput;
function freeze() {
  FS.playing = false;
  releaseInput();
  if (document.pointerLockElement) document.exitPointerLock();
}
function overlay(html) {
  if (html) {
    clearTimeout(toastTimer);
    $("#toast").textContent = "";
  }
  $("#overlay").innerHTML = html;
}
function uiGameplay(show) {
  for (const id of ["topbar", "hud", "controls", "crosshair"])
    $("#" + id).classList.toggle("hidden", !show);
  if (!show) $("#hint").textContent = "";
}
function panel(content, cls = "") {
  overlay(`<section class="panel ${cls}">${content}</section>`);
}
function button(id, fn) {
  $("#" + id)?.addEventListener("click", fn);
}
async function rpc(action, data = {}, snapshot = true) {
  if (Bridge.busy) {
    toast("Sincronizando con Python…");
    return null;
  }
  try {
    const reply = await Bridge.request(action, {
      ...data,
      ...(snapshot && FS.state ? { snapshot: clone(FS.state) } : {}),
    });
    if (reply.error) {
      toast(reply.error);
      return null;
    }
    store(reply);
    return reply;
  } catch (e) {
    toast(e.message);
    return null;
  }
}
function applyStart(r) {
  if (!r) return;
  FS.state = r.state;
  FS.config = r.config;
  FS.projectiles = [];
  FS.reloading = 0;
  FS.cooldown = 0;
  FS.hurtFlash = 0;
  modalQuestion = null;
  FS.lastSync = performance.now() / 1000;
  resume();
  toast(
    `Bienvenido, ${FS.state.name}. Esto no estaba en el convenio de estadías.`,
  );
}
function resume() {
  overlay("");
  uiGameplay(true);
  if (FS.state.player.hp <= 0) {
    death();
    return;
  }
  if (FS.state.progress.complete) {
    mission(lastStats);
    return;
  }
  FS.playing = true;
  releaseInput();
  Render.resize();
  updateHUD();
}
function mainMenu() {
  freeze();
  uiGameplay(false);
  overlay(
    `<main class="menu"><div class="hero"><div class="eyebrow">DDI / QUALITY CONTROL DIVISION</div><h1>FRACTION<br><em>SLAYER</em></h1><span class="badge">ESTADÍAS PROFESIONALES • V0.1</span><p>Primer día. Una fábrica fuera de control.<br>Y una máquina que no sabe redondear.</p><p>La matemática no te impide jugar.<br>Te permite jugar mejor.</p></div><nav class="nav"><button class="primary" id="new">NUEVA PARTIDA <small>01</small></button><button id="continue" ${slot ? "" : "disabled"}>CONTINUAR <small>02</small></button><button id="stats">ESTADÍSTICAS <small>03</small></button><button id="settings">CONFIGURACIÓN <small>04</small></button><button id="credits">CRÉDITOS <small>05</small></button><div class="footer">SISTEMA INGLÉS / FRACCIONAL ↔ DECIMAL<br>ORIGINAL PROTOTYPE · SIN TURNO DE SALIDA</div></nav></main>`,
  );
  button("new", newGame);
  button("continue", async () => {
    const r = await rpc("load", { save: slot }, false);
    applyStart(r);
  });
  button("stats", () => statistics(mainMenu));
  button("settings", () => settings(mainMenu));
  button("credits", credits);
}
function newGame() {
  panel(
    `<div class="eyebrow">UTCJ / DDI</div><h2>ESTADÍAS PROFESIONALES</h2><label for="name">NOMBRE DEL PRACTICANTE</label><input id="name" maxlength="24" autocomplete="given-name" placeholder="Tu nombre"><p>ÁREA ASIGNADA: <b>QUALITY CONTROL</b></p><div class="row"><button id="back" class="quiet">VOLVER</button><button id="next" class="primary">ASIGNAR TURNO →</button></div><p>Una nueva partida reemplaza el slot al comenzar. Puedes exportarlo desde Configuración.</p>`,
  );
  button("back", mainMenu);
  button("next", () => difficulty($("#name").value.trim() || "Practicante"));
  $("#name").addEventListener("keydown", (e) => {
    if (e.key === "Enter") $("#next").click();
  });
}
function difficulty(name) {
  let diff = "clasico";
  panel(
    `<div class="eyebrow">EXPEDIENTE // ${esc(name)}</div><h2>SELECCIONA DIFICULTAD</h2><div class="difficulties"><button id="classic" class="difficulty selected"><b>CLÁSICO</b><span>Enemigos moderados · Más recursos<br>Preguntas progresivas<br>Más opción múltiple<br>Recomendado para primera partida</span></button><button id="doom" class="difficulty"><b>DOOM</b><span>Más agresividad · Menos recursos<br>MOD II + respuestas manuales<br>Las conversiones importan más<br>No recomendado para tu primer día de estadías.</span></button></div><div class="row"><button id="back" class="quiet">VOLVER</button><button id="start" class="primary">ENTRAR A DDI →</button></div>`,
  );
  button("classic", () => {
    diff = "clasico";
    $("#classic").classList.add("selected");
    $("#doom").classList.remove("selected");
  });
  button("doom", () => {
    diff = "doom";
    $("#doom").classList.add("selected");
    $("#classic").classList.remove("selected");
  });
  button("back", newGame);
  button("start", async () => {
    $("#start").disabled = true;
    const r = await rpc("new", { name, difficulty: diff }, false);
    if (r) {
      applyStart(r);
      intro();
    } else if ($("#start")) $("#start").disabled = false;
  });
}
function intro() {
  freeze();
  panel(
    `<div class="eyebrow">DDI // REGISTRO DE INGRESO</div><h2>BIENVENIDO A QUALITY CONTROL</h2><p>Tu asesor dijo que solo había que medir unas piezas. <b>The Converter</b> tenía otros planes.</p><p><b>Objetivo:</b> cruza el pasillo, limpia la arena y calibra la puerta ámbar. La terminal verde da munición; el M.A.D. azul mejora un arma; la escopeta está en la sala inicial.</p><p><b>Móvil:</b> pad izquierdo de 8 direcciones · arrastra a la derecha para girar · DISPARAR / USAR. Toca el arma del HUD para cambiarla.</p><p><b>PC:</b> WASD · clic en la vista para capturar mouse · clic dispara · E usa · R recarga · 1/2 armas · Esc pausa. Flechas ← → también giran.</p><div class="row"><button id="enter" class="primary">ESTO SÍ LO VOY A PONER EN EL REPORTE →</button></div>`,
  );
  button("enter", resume);
}
function statHTML(s) {
  s = s || {
    kills: 0,
    correct: 0,
    attempted: 0,
    accuracy: 0,
    seconds: 0,
    score: 0,
  };
  const vals = [
    ["ENEMIES", s.kills],
    ["CONVERSIONS", `${s.correct}/${s.attempted}`],
    ["ACCURACY", `${s.accuracy || 0}%`],
    ["TIME", formatTime(s.seconds)],
    ["SCORE", s.score || 0],
    ["MEJOR RACHA", s.best_streak || 0],
  ];
  return `<div class="stats">${vals.map(([label, v]) => `<div class="stat"><small>${label}</small><b>${v}</b></div>`).join("")}</div><p>Secretos: ${s.secrets || 0} · Daño recibido: ${Math.round(s.damage || 0)} · Munición usada: ${s.ammo_used || 0}</p>`;
}
function formatTime(n) {
  return `${Math.floor(n / 60)}:${String(Math.floor(n % 60)).padStart(2, "0")}`;
}
function statistics(back) {
  panel(
    `<div class="eyebrow">EXPEDIENTE // ÚLTIMO REGISTRO</div><h2>ESTADÍSTICAS</h2>${statHTML(lastStats)}<div class="row"><button id="back">VOLVER</button></div>`,
  );
  button("back", back);
}
function credits() {
  panel(
    `<div class="eyebrow">FRACTION SLAYER / V0.1</div><h2>CRÉDITOS</h2><p>Diseño y concepto<br><b>Esteban Montaño</b></p><p>Proyecto académico<br><b>Universidad Tecnológica de Ciudad Juárez</b></p><p>Tema: Sistema inglés · Fraccional ↔ Decimal</p><p>Gráficos procedurales y sonidos sintetizados originales.<br>Espacio reservado para futuras atribuciones de assets.</p><p>“La matemática no te impide jugar. Te permite jugar mejor.”</p><button id="back">VOLVER</button>`,
  );
  button("back", mainMenu);
}
function settings(back) {
  panel(
    `<div class="eyebrow">DDI // AJUSTES DE OPERADOR</div><h2>CONFIGURACIÓN</h2><div class="settings"><label>Sensibilidad <input id="sensitivity" type="range" min="0.4" max="2" step="0.1" value="${FS.settings.sensitivity}"></label><label>Sonido <input type="checkbox" id="sound" ${FS.settings.sound ? "checked" : ""}></label><label>Minimapa de orientación <input type="checkbox" id="minimap" ${FS.settings.minimap ? "checked" : ""}></label><label>Resolución reducida <input type="checkbox" id="quality" ${FS.settings.quality === "low" ? "checked" : ""}></label></div><div class="row"><button id="export" ${slot ? "" : "disabled"}>EXPORTAR JSON</button><button id="import">IMPORTAR JSON</button><input id="file" class="hidden" type="file" accept=".json,application/json"></div><p>Un slot por navegador. Exporta una copia para cambiar de dispositivo.</p><div class="row"><button id="back" class="primary">GUARDAR Y VOLVER</button></div>`,
  );
  button("export", exportSave);
  button("import", () => $("#file").click());
  $("#file").onchange = importSave;
  button("back", () => {
    FS.settings = {
      sensitivity: Number($("#sensitivity").value),
      sound: $("#sound").checked,
      minimap: $("#minimap").checked,
      quality: $("#quality").checked ? "low" : "normal",
    };
    try {
      localStorage.setItem(
        "fraction-slayer-settings",
        JSON.stringify(FS.settings),
      );
    } catch {}
    Render.resize();
    back();
  });
}
function exportSave() {
  if (!slot) return;
  const a = document.createElement("a"),
    url = URL.createObjectURL(
      new Blob([JSON.stringify(slot, null, 2)], { type: "application/json" }),
    );
  a.href = url;
  a.download = "fraction-slayer-save.json";
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
async function importSave(e) {
  const file = e.target.files[0];
  if (!file) return;
  if (file.size > 100000) {
    toast("Archivo demasiado grande");
    return;
  }
  try {
    const save = JSON.parse(await file.text());
    const r = await rpc("load", { save }, false);
    if (r) {
      applyStart(r);
      pauseMenu(false);
    }
  } catch {
    toast("JSON inválido");
  }
}
async function pauseMenu(sync = true) {
  freeze();
  if (sync && !Bridge.busy) await rpc("pause");
  panel(
    `<div class="eyebrow">TURNO SUSPENDIDO // ${esc(FS.state?.name || "")}</div><h2>PAUSA</h2><div class="nav"><button id="resume" class="primary">CONTINUAR</button><button id="settings">CONFIGURACIÓN / GUARDADO</button><button id="stats">ESTADÍSTICAS</button><button id="restart">REINICIAR CHECKPOINT</button><button id="menu">SALIR AL MENÚ</button></div>`,
  );
  button("resume", resume);
  button("settings", () => settings(() => pauseMenu(false)));
  button("stats", () => statistics(() => pauseMenu(false)));
  button("restart", async () => applyStart(await rpc("restart", {}, false)));
  button("menu", mainMenu);
}
function death() {
  freeze();
  panel(
    `<div class="eyebrow">DDI // INCIDENTE NO PLANIFICADO</div><h2 class="error">YOU DIED</h2><p>ESTADÍAS: INCOMPLETAS</p><p>Esto no estaba en el convenio de estadías.</p><div class="row"><button id="restart" class="primary">REINICIAR CHECKPOINT</button><button id="menu">SALIR AL MENÚ</button></div>`,
  );
  button("restart", async () => applyStart(await rpc("restart", {}, false)));
  button("menu", async () => {
    if (!Bridge.busy) await rpc("menu");
    mainMenu();
  });
}
function mission(stats) {
  freeze();
  panel(
    `<div class="eyebrow">QUALITY CONTROL // TURNO CERRADO</div><h2 class="success">MISSION COMPLETE</h2>${statHTML(stats)}<p>Primer día de estadías: sobrevivido. The Converter sigue esperando.</p><div class="row"><button id="export">EXPORTAR PARTIDA</button><button id="menu" class="primary">VOLVER AL MENÚ</button></div>`,
  );
  button("export", exportSave);
  button("menu", mainMenu);
}
async function ask(station, weapon = "pistol") {
  if (Bridge.busy) {
    toast("Sincronizando… Intenta de nuevo.");
    return;
  }
  freeze();
  expression("focus");
  currentStation = station;
  currentWeapon = weapon;
  panel(
    '<div class="eyebrow">ENLACE QC</div><h2>CALIBRANDO…</h2><p>Conectando con el módulo de cálculo.</p>',
    "hologram",
  );
  const r = await rpc("question", { station, weapon });
  if (r) showQuestion(r.question, station);
  else resume();
}
function showQuestion(q, station) {
  modalQuestion = q;
  manual = "";
  const manualUI = q.mode === "manual";
  panel(
    `<div class="eyebrow">${station === "mad" ? "M.A.D. // MÓDULO DE AJUSTE DIMENSIONAL" : station === "door" ? "ACCESS CONTROL // PUERTA" : station === "cache" ? "SECURE CACHE // RECURSOS" : "QC // TERMINAL DE CALIBRACIÓN"}</div><h2>${esc(q.prompt)}</h2>${manualUI ? `<div class="entry"><div><div class="answer-display" id="answer-display">_</div><p>Usa punto o coma para decimales.<br>Usa / para fracciones.</p><div class="row"><button id="confirm" class="primary">CONFIRMAR</button><button id="cancel" class="quiet">CANCELAR</button></div></div><div class="numpad">${["1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "0", "⌫", "/", "−", "C"].map((k) => `<button data-key="${k}">${k}</button>`).join("")}</div></div>` : `<div class="choices">${q.choices.map((c, i) => `<button data-choice="${i}">${esc(c)}</button>`).join("")}</div><div class="row"><button id="cancel" class="quiet">CANCELAR</button></div>`}`,
    "hologram " + (station === "door" ? "door" : ""),
  );
  document
    .querySelectorAll("[data-choice]")
    .forEach(
      (b) =>
        (b.onclick = () => submitAnswer(q.choices[Number(b.dataset.choice)])),
    );
  document
    .querySelectorAll("[data-key]")
    .forEach((b) => (b.onclick = () => keypad(b.dataset.key)));
  button("confirm", () => submitAnswer(manual));
  button("cancel", () => {
    modalQuestion = null;
    resume();
  });
}
function keypad(k) {
  if (k === "⌫") manual = manual.slice(0, -1);
  else if (k === "C") manual = "";
  else if (manual.length < 24) manual += k === "−" ? "-" : k;
  $("#answer-display").textContent = manual || "_";
}
async function submitAnswer(answer) {
  if (!modalQuestion || Bridge.busy) return;
  if (!String(answer).trim()) {
    toast("Introduce una respuesta");
    return;
  }
  const q = modalQuestion;
  modalQuestion = null;
  document
    .querySelectorAll("#overlay button")
    .forEach((b) => (b.disabled = true));
  const r = await rpc("answer", { question_id: q.id, answer });
  if (!r) {
    showQuestion(q, currentStation);
    return;
  }
  FS.state = r.state;
  FS.config = r.config;
  updateHUD();
  sound(r.correct ? "good" : "bad");
  if (r.correct && currentStation === "mad") expression("upgrade");
  panel(
    `<div class="eyebrow">CALIBRATION HOLOGRAM</div><h2 class="${r.correct ? "success" : "error"}">${r.correct ? (currentStation === "door" ? "ACCESS GRANTED" : currentStation === "mad" ? "MOD I INSTALADO" : "CALIBRATION COMPLETE") : "CALIBRATION ERROR"}</h2><p>${esc(r.explanation)}</p>${r.correct ? `<p>${currentStation === "mad" ? esc(r.reward) + " · Ajuste dimensional aplicado." : currentStation === "terminal" ? "+12 municiones de pistola." : currentStation === "cache" ? "+35 vida · +24 municiones · Secreto encontrado." : "Acceso desbloqueado."}</p>` : "<p>Puedes volver a intentarlo con otra pregunta.</p>"}<div class="row">${!r.correct ? '<button id="again" class="primary">REINTENTAR</button>' : ""}<button id="return">VOLVER AL JUEGO</button></div>`,
    "hologram " + (currentStation === "door" ? "door" : ""),
  );
  button("again", () => ask(currentStation, currentWeapon));
  button("return", resume);
}
function interact() {
  if (!FS.playing || !FS.nearest) return;
  const st = FS.nearest.id;
  const flags = {
    terminal: "terminal_used",
    mad: "mad_used",
    door: "door_open",
    cache: "cache_used",
  };
  if (st === "exit") {
    if (FS.state.enemies.some((e) => e.hp > 0)) {
      toast("Hay enemigos activos. Completa la inspección de la arena.");
      return;
    }
    if (Bridge.busy) return;
    freeze();
    rpc("finish").then((r) => {
      if (r) {
        FS.state = r.state;
        mission(r.stats);
      } else resume();
    });
    return;
  }
  if (FS.state.progress[flags[st]]) {
    toast(
      st === "mad"
        ? "M.A.D. consumido · Un ajuste por dron."
        : "Estación ya calibrada.",
    );
    return;
  }
  if (st === "mad") {
    freeze();
    panel(
      `<div class="eyebrow">M.A.D. // AJUSTE ÚNICO</div><h2>SELECCIONA ARMA</h2><p>El dron admite una calibración. Elige tu mejora.</p><div class="choices">${Object.keys(
        FS.state.weapons,
      )
        .map(
          (w) =>
            `<button data-weapon="${w}">${w === "pistol" ? "PISTOLA<br>Precision Barrel · +15% daño" : "ESCOPETA<br>Tight Choke · mejor alcance"}</button>`,
        )
        .join(
          "",
        )}</div><div class="row"><button id="cancel">CANCELAR</button></div>`,
      "hologram",
    );
    document
      .querySelectorAll("[data-weapon]")
      .forEach((b) => (b.onclick = () => ask("mad", b.dataset.weapon)));
    button("cancel", resume);
  } else ask(st);
}
