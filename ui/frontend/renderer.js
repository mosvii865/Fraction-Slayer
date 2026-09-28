"use strict";
const Render = (() => {
  const canvas = document.querySelector("#world"),
    ctx = canvas.getContext("2d", {
      alpha: false
    });
  const face = document.querySelector("#face"),
    fc = face.getContext("2d");
  const textures = {};
  let W = 640,
    H = 360,
    zbuf = new Float32Array(W);
  const palette = {
    loader: "#e4a445", foreman: "#e08f45", industrial_node:"#76dced", install: "#72d7cb", armory:"#9eb8c4", utcj:"#e9c768", quest_item:"#84ecdf",
    worker: "#c89a4d", crawler: "#89af54", rivet: "#b55d50", sentinel:"#8f78c9", gunner:"#d85d72", stalker:"#65b9b2", k32:"#b96d86", furnace_hound:"#e57945", forge_brute:"#b86a3c", crucible:"#e05f32", pressure_lock:"#f2a54a",
    mad: "#79dce3",
    terminal: "#6cdbad",
    door: "#eead45",
    cache: "#be91de",
    exit: "#8adaab",
    pistol: "#dcb453",
    shells: "#d97b4c",
    health: "#d56f66",
    armor: "#669cae",
    shotgun: "#c2cbd0", assault:"#82a7b8", sawed_off:"#d5a36d", sniper:"#9bc6d8", lmg:"#a0b2b7", rocket:"#c98952", el_toro:"#e0bd63",
  };

  function sprite(type) {
    if (textures[type]) return textures[type];
    const c = document.createElement("canvas");
    c.width = 48;
    c.height = 64;
    const g = c.getContext("2d");
    const color = palette[type] || "#fff";
    g.fillStyle = "#050b10";
    g.fillRect(7, 59, 34, 4);
    if (type.startsWith('loader')) {
      g.fillStyle='#263b43';g.fillRect(4,40,12,23);g.fillRect(32,40,12,23);
      g.fillStyle=type==='loader_stunned'?'#76dced':type==='loader_warning'?'#ff7150':'#dda54b';
      g.fillRect(4,17,40,31);g.fillRect(1,31,7,20);g.fillRect(40,31,7,20);
      g.fillStyle='#182d35';g.fillRect(13,22,23,18);
      g.fillStyle=type==='loader_rear'?'#76edc6':'#e95c39';g.fillRect(17,27,15,9);
      g.fillStyle='#c7d2c2';g.fillRect(12,8,24,10);g.fillRect(2,53,15,6);g.fillRect(31,53,15,6);
    } else if (type.startsWith('foreman')) {
      g.fillStyle='#263b43';g.fillRect(5,43,12,20);g.fillRect(31,43,12,20);
      g.fillStyle=type==='foreman_protected'?'#6bd5e5':'#df8f45';g.fillRect(5,18,38,32);
      g.fillStyle='#162832';g.fillRect(12,25,24,16);
      g.fillStyle=type==='foreman_protected'?'#baf5ff':'#ff694e';g.fillRect(18,30,12,6);
      g.fillStyle='#b9c8c7';g.fillRect(13,8,22,12);g.fillRect(1,28,9,20);g.fillRect(38,28,9,20);
    } else if (type==='industrial_node') {
      g.strokeStyle='#76dced';g.lineWidth=3;g.strokeRect(8,15,32,36);
      g.fillStyle='#1d4f5a';g.fillRect(12,19,24,28);g.fillStyle='#a9f4ff';g.fillRect(19,26,10,14);
      g.fillStyle='#76dced';g.fillRect(15,53,18,7);
    } else if (type==='sentinel') {
      g.fillStyle='#28333f';g.fillRect(17,42,14,20);g.fillRect(7,54,34,6);
      g.fillStyle='#8f78c9';g.fillRect(8,23,32,21);g.fillStyle='#182630';g.fillRect(13,28,22,11);
      g.fillStyle='#ff765e';g.fillRect(21,31,6,5);g.fillStyle='#9ba8b0';g.fillRect(35,29,12,6);
    } else if (type.startsWith('stalker')) {
      const cloaked=type==='stalker_cloaked', warning=type==='stalker_warning';
      g.globalAlpha=cloaked?.48:1;
      g.fillStyle='#1d3037';g.fillRect(12,43,9,18);g.fillRect(28,43,9,18);
      g.fillStyle=warning?'#e4b15a':'#65b9b2';g.fillRect(9,20,31,29);
      g.fillStyle='#183039';g.fillRect(15,27,20,14);
      g.fillStyle=warning?'#ff765e':'#91eee0';g.fillRect(18,31,5,4);g.fillRect(29,31,5,4);
      g.fillStyle='#9fb8b5';g.fillRect(16,8,20,14);
      if(cloaked){g.strokeStyle='#79e3db';g.setLineDash([3,3]);g.strokeRect(7,17,35,37);g.setLineDash([]);}
      g.globalAlpha=1;
    } else if (type.startsWith('k32')) {
      const overload=type==='k32_overload', exhausted=type==='k32_exhausted';
      g.fillStyle='#27333b';g.fillRect(5,45,13,18);g.fillRect(30,45,13,18);
      g.fillStyle=overload?'#e15f76':exhausted?'#7fd8ce':'#b96d86';g.fillRect(5,18,38,32);
      g.fillStyle='#182630';g.fillRect(12,25,24,17);
      g.fillStyle=overload?'#ffd0a1':'#b6f3e8';g.fillRect(19,29,11,8);
      g.strokeStyle=overload?'#ff8c68':'#79d9d0';g.lineWidth=2;g.strokeRect(2,14,44,40);
      g.fillStyle='#aab7b6';g.fillRect(13,7,22,13);g.fillRect(1,29,8,18);g.fillRect(39,29,8,18);
    } else if (type.startsWith('furnace_hound')) {
      const hot=type==='furnace_hound_hot';
      g.fillStyle='#27343a';g.fillRect(7,39,35,13);g.fillRect(5,49,9,11);g.fillRect(34,49,9,11);
      g.fillStyle=hot?'#ff884c':'#e57945';g.fillRect(10,25,31,18);g.fillRect(33,20,10,13);
      g.fillStyle='#ffd06b';g.fillRect(14,29,6,5);g.fillRect(25,29,6,5);
      g.strokeStyle=hot?'#ffd05d':'#7a4934';g.lineWidth=2;g.strokeRect(8,23,35,22);
    } else if (type==='forge_brute') {
      g.fillStyle='#26333a';g.fillRect(5,44,14,18);g.fillRect(30,44,14,18);
      g.fillStyle='#b86a3c';g.fillRect(3,18,42,31);g.fillStyle='#4b5558';g.fillRect(8,22,32,16);
      g.fillStyle='#ff9a52';g.fillRect(14,28,8,7);g.fillRect(28,28,8,7);
      g.fillStyle='#7b8486';g.fillRect(11,8,28,13);g.fillRect(0,28,9,19);g.fillRect(39,28,9,19);
    } else if (type.startsWith('crucible')) {
      const open=type==='crucible_open';
      g.fillStyle='#202d33';g.fillRect(3,17,42,43);
      g.fillStyle='#7b4a34';g.fillRect(7,20,34,35);
      g.fillStyle=open?'#ffd166':'#e05f32';g.fillRect(15,27,18,19);
      g.strokeStyle=open?'#fff0a5':'#8e3f2e';g.lineWidth=3;g.strokeRect(10,23,28,27);
      g.fillStyle='#9ba5a5';g.fillRect(1,10,10,42);g.fillRect(37,10,10,42);
    } else if (type==='pressure_lock') {
      g.fillStyle='#30383b';g.fillRect(11,18,27,39);g.fillStyle='#f2a54a';g.fillRect(15,22,19,29);
      g.fillStyle='#ffe0a0';g.fillRect(20,28,9,17);g.strokeStyle='#ffcb67';g.lineWidth=2;g.strokeRect(9,16,31,43);
    } else if (type==='utcj') {
      g.fillStyle='#dbc777';g.strokeStyle='#dbc777';g.lineWidth=2;g.strokeRect(4,15,40,35);
      g.font='bold 12px monospace';g.textAlign='center';g.fillText('UTCJ',24,34);
      g.font='8px monospace';g.fillText('PROJECT',24,45);
    } else if (type==='quest_item') {
      g.fillStyle='#bdece4';g.fillRect(17,27,15,31);g.fillStyle='#315c61';g.fillRect(20,33,9,18);
      g.fillStyle='#dba64e';g.fillRect(16,26,17,6);g.fillRect(16,54,17,6);
    } else if (["worker", "rivet", "crawler", "gunner"].includes(type)) {
      if (type === "crawler") {
        g.fillStyle = color;
        g.fillRect(8, 37, 33, 17);
        g.fillRect(5, 47, 8, 13);
        g.fillRect(36, 47, 8, 13);
        g.fillStyle = "#293e36";
        g.fillRect(16, 32, 20, 12);
        g.fillStyle = "#ff795c";
        g.fillRect(19, 36, 4, 4);
        g.fillRect(29, 36, 4, 4);
        g.fillStyle = "#c8d4a2";
        g.fillRect(16, 48, 23, 3);
      } else {
        g.fillStyle = "#27343e";
        g.fillRect(11, 45, 10, 16);
        g.fillRect(28, 45, 10, 16);
        g.fillStyle = color;
        g.fillRect(9, 22, 31, 28);
        g.fillRect(4, 26, 7, 23);
        g.fillRect(38, 26, 7, 23);
        g.fillStyle = "#657179";
        g.fillRect(16, 28, 18, 15);
        g.fillStyle = "#18242e";
        g.fillRect(18, 31, 14, 5);
        g.fillStyle = "#d4b289";
        g.fillRect(15, 7, 21, 17);
        g.fillStyle = color;
        g.fillRect(12, 5, 27, 10);
        g.fillStyle = "#e66b43";
        g.fillRect(16, 16, 18, 4);
        g.fillStyle = "#121f26";
        g.fillRect(23, 20, 9, 6);
        if (type === "rivet" || type === "gunner") {
          g.fillStyle = "#84919b";
          g.fillRect(30, 34, 17, 10);
          g.fillStyle = "#ff875e";
          g.fillRect(43, 35, 5, 7);
        }
      }
    } else if (["terminal", "mad", "cache", "exit", "install", "armory"].includes(type)) {
      g.fillStyle = "#273946";
      g.fillRect(10, 48, 29, 13);
      g.fillRect(20, 34, 9, 20);
      g.fillStyle = color;
      g.globalAlpha = 0.2;
      g.fillRect(3, 5, 42, 38);
      g.globalAlpha = 1;
      g.strokeStyle = color;
      g.lineWidth = 2;
      g.strokeRect(4, 7, 40, 31);
      g.fillStyle = color;
      g.font = "bold 9px monospace";
      g.textAlign = "center";
      g.fillText(
        type === "mad" ?
        "M.A.D." :
        type === "exit" ?
        "EXIT" :
        type === "cache" ?
        "QC+" :
        type === "install" ? "POWER" : type === "armory" ? "ARM" : "QC",
        24,
        25,
      );
      g.fillRect(10, 31, 27, 2);
    } else if (type === "door") {
      g.fillStyle = color;
      g.fillRect(16, 20, 16, 24);
      g.fillStyle = "#30291d";
      g.fillRect(20, 25, 8, 5);
      g.fillRect(20, 34, 8, 5);
    } else {
      g.fillStyle = color;
      g.fillRect(9, 40, 30, 19);
      g.fillStyle = "#182630";
      g.fillRect(12, 43, 24, 12);
      g.fillStyle = color;
      if (type === "health") {
        g.fillRect(21, 43, 6, 13);
        g.fillRect(17, 47, 14, 5);
      } else if (type === "shotgun") {
        g.fillStyle = "#778e9c";
        g.fillRect(5, 47, 35, 5);
        g.fillStyle = "#b58a5d";
        g.fillRect(7, 51, 14, 5);
      } else {
        g.fillRect(17, 46, 3, 9);
        g.fillRect(24, 46, 3, 9);
        g.fillRect(31, 46, 3, 9);
      }
    }
    textures[type] = c;
    return c;
  }

  function resize() {
    const r = canvas.getBoundingClientRect();
    W = Math.min(
      window.FS?.settings.quality === "low" ? 480 : 720,
      Math.round(r.width),
    );
    const hud = document.querySelector("#hud").getBoundingClientRect().height || (r.height < 500 ? 70 : 78);
    H = Math.max(160, Math.round(((r.height - hud) * W) / r.width));
    canvas.width = W;
    canvas.height = H + Math.round((hud * W) / r.width);
    zbuf = new Float32Array(W);
    ctx.imageSmoothingEnabled = false;
  }
  window.addEventListener("resize", resize);
  resize();

  function factory(t) {
    const h = canvas.height;
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, "#102630");
    grad.addColorStop(1, "#080d12");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, h);
    for (let i = 0; i < 9; i++) {
      let x = (i * W) / 8;
      ctx.fillStyle = i % 2 ? "#183039" : "#12252d";
      ctx.fillRect(x, 0, 12, h);
      ctx.fillRect(x + 3, h * 0.13, W / 8, 7);
      ctx.fillRect(x + 3, h * 0.66, W / 8, 10);
      ctx.fillStyle = "#324249";
      ctx.fillRect(x + 22, h * 0.36, W / 11, h * 0.32);
      ctx.fillStyle = "#091820";
      ctx.fillRect(x + 27, h * 0.4, W / 14, h * 0.23);
      ctx.fillStyle = Math.sin(t * 2 + i) > 0.4 ? "#b38742" : "#594727";
      ctx.fillRect(x + 28, h * 0.39, 14, 3);
    }
    ctx.strokeStyle = "#35535b";
    ctx.lineWidth = 8;
    ctx.beginPath();
    ctx.moveTo(0, h * 0.18);
    ctx.lineTo(W, h * 0.18);
    ctx.stroke();
    for (let i = 0; i < 12; i++) {
      const x = (i * 83 + t * 6) % W,
        y = h * 0.7 - ((t * 13 + i * 21) % (h * 0.65));
      ctx.fillStyle = "#87b1bd08";
      ctx.beginPath();
      ctx.ellipse(x, y, 25 + (i % 4) * 8, 14, 0, 0, 7);
      ctx.fill();
    }
    ctx.fillStyle = "#050b1199";
    ctx.fillRect(0, 0, W, h);
  }

  function world(fs, t) {
    const s = fs.state,
      p = s.player,
      grid = fs.config.level.grid;
    let dx = Math.cos(p.angle),
      dy = Math.sin(p.angle),
      plane = 0.64;
    let g = ctx.createLinearGradient(0, 0, 0, H);
    const lab=s.level_id==='laboratory';
    const stability=lab ? ['containment_a','containment_b','containment_c'].filter(id=>s.progress.objectives[id]).length : 0;
    g.addColorStop(0, lab ? (stability>=3?'#123033':'#171a2b') : "#120f0d");
    g.addColorStop(0.5, lab ? (stability>=2?'#3a5552':'#303441') : (s.progress.objectives.power_restored ? "#3b3832" : "#302d29"));
    g.addColorStop(0.501, lab ? '#252b31' : "#252321");
    g.addColorStop(1, lab ? '#0e171d' : "#100f0e");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);

    // Keep the classic FPS horizon clean and stable.
    // Do not use a screen-space checker/floor projection here: high-frequency
    // perspective patterns can produce a distracting swimming effect while moving.
    // The floor is intentionally represented by the existing horizon gradient;
    // wall geometry and sprites provide the depth cues.
    for (let x = 0; x < W; x += 2) {
      const camera = (2 * x) / W - 1,
        rx = dx - dy * plane * camera,
        ry = dy + dx * plane * camera;
      let mx = Math.floor(p.x),
        my = Math.floor(p.y),
        ddx = Math.abs(1 / rx),
        ddy = Math.abs(1 / ry),
        sx = rx < 0 ? -1 : 1,
        sy = ry < 0 ? -1 : 1;
      let sideX = (rx < 0 ? p.x - mx : mx + 1 - p.x) * ddx,
        sideY = (ry < 0 ? p.y - my : my + 1 - p.y) * ddy,
        side = 0,
        tile = 0;
      for (let i = 0; i < grid.length + grid[0].length; i++) {
        if (sideX < sideY) {
          sideX += ddx;
          mx += sx;
          side = 0;
        } else {
          sideY += ddy;
          my += sy;
          side = 1;
        }
        tile = grid[my]?.[mx] ?? 1;
        if (tile === 3) tile = tileAt(mx, my);
        if (tile) break;
      }
      const dist = Math.max(0.1, side ? sideY - ddy : sideX - ddx),
        height = H / dist,
        top = (H - height) / 2;
      zbuf[x] = zbuf[x + 1] = dist;
      let wallX = side ? p.x + dist * rx : p.y + dist * ry;
      wallX -= Math.floor(wallX);
      let shade = Math.max(0.14, 1 / (1 + dist * 0.13)) * (side ? 0.72 : 1),
        base =
        tile === 3 ?
        [148, 96, 42] :
        tile === 2 ?
        [54, 75, 81] :
        [92, 111, 111];
      if (wallX < 0.035 || wallX > 0.965) shade *= 0.5;
      const workshopArt = s.level_id === "workshop" && window.FSArt;
      const texKey = tile === 3 ? "workshop_door" : tile === 2 ? "workshop_panel" : "workshop_wall";
      const wallTex = workshopArt ? window.FSArt.get("textures", texKey) : null;
      if (wallTex) {
        const tx = Math.min(wallTex.naturalWidth - 1, Math.max(0, Math.floor(wallX * wallTex.naturalWidth)));
        ctx.drawImage(wallTex, tx, 0, 1, wallTex.naturalHeight, x, top, 2, height);
        const darkness = Math.min(.78, Math.max(0, 1 - shade));
        ctx.fillStyle = `rgba(3,9,12,${darkness})`;
        ctx.fillRect(x, top, 2, height);
        // Chunky 90s-FPS material accents: panel seams, lower grime and top trim.
        const seam = wallX < 0.035 || wallX > 0.965;
        if (seam) {
          ctx.fillStyle = `rgba(4,7,8,${0.42 * shade})`;
          ctx.fillRect(x, top, 2, height);
        }
        if (tile !== 3 && wallX > 0.10 && wallX < 0.90) {
          ctx.fillStyle = `rgba(8,12,12,${0.16 * shade})`;
          ctx.fillRect(x, top + height * 0.72, 2, Math.max(1, height * 0.08));
          ctx.fillStyle = `rgba(196,145,67,${0.16 * shade})`;
          ctx.fillRect(x, top + height * 0.105, 2, Math.max(1, height * 0.018));
        }
      } else {
        ctx.fillStyle = `rgb(${base.map((v) => Math.round(v * shade)).join(",")})`;
        ctx.fillRect(x, top, 2, height);
        ctx.fillStyle = `rgba(8,18,23,${0.35 * shade})`;
        ctx.fillRect(x, top + height * 0.68, 2, height * 0.07);
        ctx.fillRect(x, top + height * 0.95, 2, height * 0.05);
        if (tile === 3) {
          ctx.fillStyle = (wallX * 8 + dist) % 2 < 1 ? "#bd8c3d" : "#202b2d";
          ctx.fillRect(x, top + height * 0.46, 2, height * 0.07);
        } else if (wallX > 0.14 && wallX < 0.83) {
          ctx.fillStyle = `rgba(126,203,204,${0.7 * shade})`;
          ctx.fillRect(x, top + height * 0.12, 2, height * 0.025);
        }
      }
    }
    fs.debugStage = 'RENDER_ENTITIES';
    const activeForeman=s.enemies.find(e=>e.type==='foreman'&&e.active&&e.hp>0&&e.shielded);
    const nodeObjects=activeForeman ? (fs.config.level.boss_nodes||[]).map((n,i)=>({...n,type:'industrial_node',node_hp:i===0?activeForeman.node_a_hp:activeForeman.node_b_hp})).filter(n=>n.node_hp>0) : [];
    const activeCrucible=s.enemies.find(e=>e.type==='crucible'&&e.active&&e.hp>0);
    const crucibleObjects=activeCrucible ? (fs.config.level.crucible_locks||[]).filter(n=>n.phase===activeCrucible.boss_mode && (activeCrucible[n.field]||0)>0).map(n=>({...n,type:'pressure_lock'})) : [];
    // A killed Worker is removed from authoritative enemy gameplay immediately,
    // but its client-only death frame may remain briefly for visual readability.
    for (const e of s.enemies) window.FSArt?.observeEnemy?.(fs,e,t);
    const deadWorkerObjects=Object.values(fs.enemyVisuals||{}).filter(v=>(v.type==='worker' || v.type==='crawler' || v.type==='rivet' || window.FSArt?.sprintTypes?.has(v.type)) && v.deadUntil>t).map(v=>({
      id:v.id,type:v.type,x:v.deadX,y:v.deadY,_visualDead:true
    }));
    const objects = [
      ...s.enemies.filter((e) => e.active && e.hp > 0),
      ...deadWorkerObjects,
      ...nodeObjects,
      ...crucibleObjects,
      ...fs.config.level.items.filter((i) => !s.collected.includes(i.id)).map(i => ({
        ...i,
        type: i.type === 'weapon' ? i.weapon : i.type === 'ammo' ? (['shotgun','sawed_off'].includes(i.weapon) ? 'shells' : ['assault','sniper','lmg','rocket','el_toro'].includes(i.weapon) ? i.weapon : 'pistol') : i.type
      })),
      ...fs.config.level.secrets.filter(i => i.on_shot && !s.progress.secrets[i.id]).map(i => ({
        ...i,
        type: 'utcj'
      })),
      ...fs.config.level.stations
      .filter((i) => i.kind !== "door" || !s.progress.doors[i.door_id])
      .map((i) => ({
        ...i,
        type: i.kind
      })),
      ...(fs.config.level.props || []).map((i) => ({...i, type: "prop"})),
    ];
    objects.sort(
      (a, b) =>
      (b.x - p.x) ** 2 +
      (b.y - p.y) ** 2 -
      ((a.x - p.x) ** 2 + (a.y - p.y) ** 2),
    );
    for (const o of objects) {
      const ox = o.x - p.x,
        oy = o.y - p.y,
        depth = ox * dx + oy * dy;
      if (depth < 0.12) continue;
      const sideways = -ox * dy + oy * dx;
      const center = (W / 2) * (1 + sideways / (plane * depth));
      const propScale = o.type === "prop" ? (o.scale || .85) : 1;
      let visual=o.art || o.type;
      if (o.type==='worker' || o.type==='crawler' || o.type==='rivet') {
        const ev=(fs.enemyVisuals||{})[o.id] || {};
        visual=window.FSArt?.enemyFrameKey ? window.FSArt.enemyFrameKey(o.type,{
          dead:!!o._visualDead, movingUntil:ev.movingUntil, attackUntil:ev.attackUntil, hurtUntil:ev.hurtUntil
        },t) : o.type;
      } else if (o.type==='loader') {
        const a=Math.atan2(p.y-o.y,p.x-o.x)-o.facing;
        visual=o.stun_time>0?'loader_stunned':['preparing','slamming'].includes(o.charge_state)?'loader_warning':Math.abs(Math.atan2(Math.sin(a),Math.cos(a)))>Math.PI-1?'loader_rear':'loader';
      } else if (o.type==='foreman') visual=o.shielded?'foreman_protected':'foreman';
      else if (o.type==='stalker') visual=o.stalker_mode==='stalk'?'stalker_cloaked':o.stalker_mode==='reveal'?'stalker_warning':'stalker';
      else if (o.type==='k32') visual=o.boss_mode==='overload'?'k32_overload':o.boss_mode==='exhausted'?'k32_exhausted':'k32';
      else if (o.type==='furnace_hound') visual=o.hound_mode==='heat'?'furnace_hound_hot':'furnace_hound';
      else if (o.type==='crucible') visual=['exposed1','exposed2','critical'].includes(o.boss_mode)?'crucible_open':'crucible';
      // Keep original special-state variant as the missing-asset fallback.
      const legacyVisual=visual;
      const sprintEnemy=window.FSArt?.sprintTypes?.has(o.type);
      if(sprintEnemy){
        const ev=(fs.enemyVisuals||{})[o.id]||{};
        visual=window.FSArt.enemyFrameKey(o.type,{...ev,dead:!!o._visualDead},t);
      }
      // Presentation-only pickup path. Original item and collection trigger stay intact.
      const pickupProfile=o.type==='shotgun' && o.weapon==='shotgun' ? window.FSArt?.pickupProfiles?.shotgun : null;
      const pickupArt=pickupProfile ? window.FSArt?.get("pickups",pickupProfile.key) : null;
      if(pickupArt) {
        const [sx,sy,sourceW,sourceH]=pickupProfile.bounds;
        const ph=H/depth*pickupProfile.worldHeight,pw=ph*sourceW/sourceH;
        const floor=H/2+H/(2*depth),pt=floor-ph;
        const y0=Math.max(0,pt),y1=Math.min(H,floor);
        if(y1>y0) for(let col=Math.max(0,Math.ceil(center-pw/2));col<Math.min(W,center+pw/2);col++) {
          if(depth>=zbuf[col]) continue;
          const tx=Math.min(sourceW-1,Math.max(0,Math.floor((col+.5-center+pw/2)/pw*sourceW)));
          // Subtle floor contact; clipped with the same wall depth as the sprite.
          const edge=(col+.5-center)/(pw*.5);
          const contact=Math.sqrt(Math.max(0,1-edge*edge))*ph*.09;
          if(floor<=H){ctx.fillStyle='#05090b66';ctx.fillRect(col,floor-contact,1,contact);}
          ctx.drawImage(pickupArt,sx+tx,sy+(y0-pt)/ph*sourceH,1,(y1-y0)/ph*sourceH,col,y0,1,y1-y0);
        }
        continue;
      }
      const rasterImg = o.type === "prop" ? window.FSArt?.get("props", visual) : window.FSArt?.get("sprites", visual);
      const fallbackVisual = sprintEnemy ? legacyVisual : ['worker','crawler','rivet'].includes(o.type) && String(visual).startsWith(o.type+'_') ? o.type : visual;
      const img = rasterImg || sprite(fallbackVisual);
      const sh = (H / depth) * (o.type === "loader" ? 1.4 : o.type === "foreman" ? 1.5 : o.type === "k32" ? 1.55 : o.type === "crucible" ? 1.8 : o.type === "forge_brute" ? 1.45 : o.type === "furnace_hound" ? .82 : o.type === "crawler" ? (rasterImg && window.FSArt?.enemyProfiles?.crawler ? window.FSArt.enemyProfiles.crawler.worldHeight : 0.85) : ["industrial_node","pressure_lock"].includes(o.type) ? .9 : 1) * propScale;
      let sw = sh * (o.type === "prop" && String(o.art||"").startsWith("sign_") ? 2 : 0.75);
      // Worker (64x80), Crawler (80x56), Rivet (80x80): full authored canvases.
      // Preserve aspect ratio and floor anchor, never fit per-pose alpha bounds.
      if (((o.type==='worker' || o.type==='crawler' || o.type==='rivet') || sprintEnemy) && rasterImg) {
        const rw=rasterImg.naturalWidth||64, rh=rasterImg.naturalHeight||80;
        sw=sh*(rw/Math.max(1,rh));
      }
      // Anchor world sprites to the projected floor instead of the screen center.
      // This keeps every entity standing on the same perspective floor line as walls.
      const floorY = H / 2 + H / (2 * depth);
      let top = floorY - sh;
      if (["pistol", "shells", "health", "armor", "shotgun", "assault", "sawed_off", "sniper", "lmg", "rocket", "el_toro"].includes(o.type))
        top += sh * 0.03;
      const fx=sprintEnemy && rasterImg ? window.FSArt.enemyEffect(o,p) : {alpha:1,color:null};
      ctx.globalAlpha=fx.alpha;
      for (
        let col = Math.max(0, Math.floor(center - sw / 2)); col < Math.min(W, center + sw / 2); col++
      ) {
        if (depth < zbuf[col]) {
          const srcW = Math.max(1, img.naturalWidth || img.width || 48);
          const srcH = Math.max(1, img.naturalHeight || img.height || 64);
          const tx = Math.min(
            srcW - 1,
            Math.max(0, Math.floor(((col - center + sw / 2) / sw) * srcW)),
          );
          ctx.drawImage(img, tx, 0, 1, srcH, col, top, 1, sh);
          // Depth-clipped warning/shield/weak-point marker; HUD state text is unchanged.
          if(fx.color){ctx.fillStyle=fx.color;ctx.fillRect(col,top-4,1,3);}

        }
      }
      ctx.globalAlpha=1;
    }
    for (const b of fs.projectiles) {
      const ox = b.x - p.x,
        oy = b.y - p.y,
        dep = ox * dx + oy * dy;
      if (dep > 0.2) {
        const cx = (W / 2) * (1 + (-ox * dy + oy * dx) / (plane * dep));
        if (cx > 0 && cx < W && dep < zbuf[Math.floor(cx)]) {
          ctx.fillStyle = b.owner==='player' ? "#ffe18a" : b.molten ? "#ff704a" : "#ffb069";
          ctx.fillRect(cx - 2, H / 2 - 2, 5, 5);
        }
      }
    }
    // Original procedural weapon silhouette.
    const bob = Math.sin(t * 10) * fs.moving * 3,
      recoil = Math.max(0, fs.shotFlash) * 30,
      rasterWeaponKey = window.FSArt?.weaponFrameKey
        ? window.FSArt.weaponFrameKey(s.weapon, {reloading: fs.reloading, reloadDuration: fs.config.weapons[s.weapon]?.reload, shotFlash: fs.shotFlash, pumpAnim: fs.pumpAnim})
        : ((s.weapon === "pistol" && fs.reloading > 0) ? "pistol_reload"
          : (s.weapon === "pistol" && fs.shotFlash > 0) ? "pistol_fire" : s.weapon),
      rasterWeapon = window.FSArt?.get("weapons", rasterWeaponKey)
        || (s.weapon==="shotgun" ? window.FSArt?.get("weapons", "shotgun") : null) || null;
    const cx = W * 0.55,
      wy = H + bob + recoil;
    const scale = H / 300;
    ctx.save();
    ctx.translate(cx, wy);
    ctx.scale(scale, scale);
    if (rasterWeapon) ctx.globalAlpha = 0;
    const shotgun = s.weapon === "shotgun", assault=s.weapon==='assault', sawed=s.weapon==='sawed_off', sniper=s.weapon==='sniper', lmg=s.weapon==='lmg', rocket=s.weapon==='rocket', toro=s.weapon==='el_toro';
    ctx.fillStyle = "#8a674a";
    ctx.fillRect(-35, -45, 42, 65);
    ctx.fillStyle = "#243943";
    ctx.fillRect(-22, -78, 47, 90);
    ctx.fillStyle = "#779098";
    ctx.fillRect(-17, -92, 30, 70);
    ctx.fillStyle = "#18272c";
    ctx.fillRect(-10, -96, 18, 26);
    ctx.fillStyle = "#a9bab6";
    ctx.fillRect(-14, -83, 5, 46);
    if (shotgun) {
      ctx.fillStyle = "#526d74";ctx.fillRect(9, -88, 14, 73);ctx.fillStyle = "#a17644";ctx.fillRect(-22, -44, 49, 19);
    } else if (assault) {
      ctx.fillStyle='#526d74';ctx.fillRect(8,-91,28,10);ctx.fillRect(19,-76,10,55);ctx.fillStyle='#6e5542';ctx.fillRect(-25,-46,54,13);
    } else if (sawed) {
      ctx.fillStyle='#a17644';ctx.fillRect(-28,-48,58,19);ctx.fillStyle='#6c818a';ctx.fillRect(-18,-91,12,55);ctx.fillRect(3,-91,12,55);
    } else if (sniper) {
      ctx.fillStyle='#536f7a';ctx.fillRect(-11,-104,18,78);ctx.fillRect(4,-96,38,7);
      ctx.fillStyle='#a8c8d2';ctx.fillRect(-17,-88,31,7);ctx.fillRect(-5,-114,9,19);
      ctx.fillStyle='#6e5542';ctx.fillRect(-25,-46,52,13);
    } else if (lmg) {
      ctx.fillStyle='#53646a';ctx.fillRect(-14,-101,27,82);ctx.fillRect(8,-92,35,10);ctx.fillStyle='#8a8f76';ctx.fillRect(-30,-49,63,15);ctx.fillStyle='#9fb0b3';ctx.fillRect(-5,-112,8,18);
    } else if (rocket) {
      ctx.fillStyle='#5b6669';ctx.fillRect(-24,-97,48,80);ctx.fillStyle='#c47d49';ctx.fillRect(-31,-91,62,17);ctx.fillStyle='#aeb7b3';ctx.fillRect(-18,-106,36,13);
    } else if (toro) {
      ctx.fillStyle='#343f43';ctx.fillRect(-22,-83,44,68);ctx.fillStyle='#d2b05c';ctx.beginPath();ctx.moveTo(-10,-78);ctx.lineTo(-43,-118);ctx.lineTo(-24,-80);ctx.fill();ctx.beginPath();ctx.moveTo(10,-78);ctx.lineTo(43,-118);ctx.lineTo(24,-80);ctx.fill();ctx.fillStyle='#e7cf86';ctx.fillRect(-9,-96,18,30);
    }
    if (s.weapons[s.weapon].mods) {
      ctx.fillStyle = "#78e0e8";
      ctx.fillRect(-10, -60, 20, 4);
    }
    if (fs.shotFlash > 0) {
      ctx.fillStyle = "#ffe5a1";
      ctx.beginPath();
      ctx.moveTo(-5, -94);
      ctx.lineTo(-26, -128);
      ctx.lineTo(-5, -119);
      ctx.lineTo(5, -146);
      ctx.lineTo(12, -120);
      ctx.lineTo(31, -130);
      ctx.lineTo(16, -93);
      ctx.fill();
    }
    ctx.restore();
    if (rasterWeapon) {
      // Cache alpha bounds per frame. They are useful for drawing only visible
      // pixels, but they must NOT define each animation frame's scale/anchor.
      // Pistol idle/fire/reload share a 160x120 design canvas; using the idle
      // frame as the reference prevents the reload pose from growing or
      // jumping simply because its visible alpha box is shorter/wider.
      function alphaBoundsFor(img) {
        const iw = img.naturalWidth || img.width || 160;
        const ih = img.naturalHeight || img.height || 120;
        let bounds = img.__fsAlphaBounds;
        if (!bounds) {
          try {
            const probe = document.createElement("canvas");
            probe.width = iw; probe.height = ih;
            const pg = probe.getContext("2d", {willReadFrequently:true});
            pg.drawImage(img, 0, 0);
            const data = pg.getImageData(0, 0, iw, ih).data;
            let minX = iw, minY = ih, maxX = -1, maxY = -1;
            for (let py = 0; py < ih; py++) {
              for (let px = 0; px < iw; px++) {
                if (data[(py * iw + px) * 4 + 3] > 8) {
                  if (px < minX) minX = px;
                  if (py < minY) minY = py;
                  if (px > maxX) maxX = px;
                  if (py > maxY) maxY = py;
                }
              }
            }
            bounds = maxX >= 0
              ? {x:minX,y:minY,w:maxX-minX+1,h:maxY-minY+1}
              : {x:0,y:0,w:iw,h:ih};
          } catch (_) {
            bounds = {x:0,y:0,w:iw,h:ih};
          }
          try { Object.defineProperty(img, "__fsAlphaBounds", {value: bounds}); } catch (_) {}
        }
        return bounds;
      }

      const frameBounds = alphaBoundsFor(rasterWeapon);
      const profile = window.FSArt?.weaponProfiles?.[s.weapon] || null;
      const referenceKey = profile?.reference || rasterWeaponKey;
      const referenceImage = window.FSArt?.get("weapons", referenceKey) || rasterWeapon;
      const referenceBounds = alphaBoundsFor(referenceImage);
      const refW = referenceImage.naturalWidth || referenceImage.width || 160;
      const refH = referenceImage.naturalHeight || referenceImage.height || 120;
      const frameW = rasterWeapon.naturalWidth || rasterWeapon.width || refW;
      const frameH = rasterWeapon.naturalHeight || rasterWeapon.height || refH;

      const weaponHeight = profile?.height ?? ({
        pistol: 0.215, shotgun: 0.255, sawed_off: 0.245, assault: 0.225,
        sniper: 0.235, lmg: 0.235, rocket: 0.255, el_toro: 0.235
      }[s.weapon] || 0.225);
      const centerX = profile?.centerX ?? 0.52;

      // Scale comes from the REFERENCE frame, not the current animation frame.
      // This is the key rule for stable first-person animation.
      let frameScale = (H * weaponHeight) / Math.max(1, referenceBounds.h);
      const maxReferenceW = W * 0.34;
      const referenceVisibleW = referenceBounds.w * frameScale;
      if (referenceVisibleW > maxReferenceW) frameScale *= maxReferenceW / referenceVisibleW;

      // Map the current frame through the shared source canvas. The reference
      // visible center and bottom are the anchor, so idle/fire/reload preserve
      // their authored offsets instead of being re-centered independently.
      const referenceCenterSrcX = referenceBounds.x + referenceBounds.w * 0.5;
      const referenceBottomSrcY = referenceBounds.y + referenceBounds.h;
      const destCanvasX = W * centerX - referenceCenterSrcX * frameScale;
      const destCanvasY = H + bob + recoil * 0.45 - referenceBottomSrcY * frameScale;
      const dx = destCanvasX + frameBounds.x * frameScale;
      const dy = destCanvasY + frameBounds.y * frameScale;
      const dw = frameBounds.w * frameScale;
      const dh = frameBounds.h * frameScale;

      ctx.drawImage(
        rasterWeapon,
        frameBounds.x, frameBounds.y, frameBounds.w, frameBounds.h,
        dx, dy, dw, dh
      );
      if (s.weapons[s.weapon].mods) {
        ctx.fillStyle = "#78e0e8";
        ctx.fillRect(W * .505, H * .79 + bob, Math.max(14,referenceBounds.w*frameScale*.12), 3);
      }
      if (fs.shotFlash > 0 && !profile?.fire) {
        const fx = W * .53, fy = H * .53 + recoil * .1;
        ctx.fillStyle = "#ffe5a1";
        ctx.beginPath();ctx.moveTo(fx-4,fy);ctx.lineTo(fx-18,fy-28);ctx.lineTo(fx,fy-19);ctx.lineTo(fx+7,fy-38);ctx.lineTo(fx+11,fy-17);ctx.lineTo(fx+25,fy-26);ctx.lineTo(fx+14,fy+2);ctx.fill();
      }
    }
    if (fs.hurtFlash > 0) {
      ctx.fillStyle = `rgba(191,46,30,${fs.hurtFlash * 0.4})`;
      ctx.fillRect(0, 0, W, H);
    }
    if (fs.heatWarning) {
      ctx.save();ctx.textAlign='center';ctx.font='bold 16px monospace';ctx.fillStyle=fs.heatDanger?'#ff654a':'#ffd166';
      ctx.fillText(fs.heatWarning,W/2,H*.19);ctx.restore();
    }
    fs.debugStage = 'RENDER_MINIMAP';
    if (fs.settings.minimap) map(fs);
    drawFace(fs, t);
  }

  function map(fs) {
    const p = fs.state.player,
      g = fs.config.level.grid,
      k = Math.min(3, W * .25 / g[0].length, H * .3 / g.length),
      ox = 6,
      oy = 34;
    ctx.fillStyle = "#02080cb0";
    ctx.fillRect(ox, oy, g[0].length * k, g.length * k);
    for (let y = 0; y < g.length; y++)
      for (let x = 0; x < g[0].length; x++) {
        ctx.fillStyle =
          g[y][x] === 3 ?
          tileAt(x, y) === 0 ?
          "#78ddad" :
          "#e4ac4f" :
          g[y][x] ?
          "#455960" :
          "#152c35";
        ctx.fillRect(ox + x * k, oy + y * k, k - 0.4, k - 0.4);
      }
    for (const hz of (fs.config.level.heat_zones || [])) {
      const z=hz.zone;ctx.fillStyle='#9a4f35';ctx.globalAlpha=.32;
      ctx.fillRect(ox+z[0]*k,oy+z[1]*k,Math.max(1,(z[2]-z[0])*k),Math.max(1,(z[3]-z[1])*k));ctx.globalAlpha=1;
    }
    for (const belt of (fs.config.level.conveyors || [])) {
      const z=belt.zone;ctx.fillStyle=belt.kind==='fast'?'#b28a42':'#486f78';ctx.globalAlpha=.7;
      ctx.fillRect(ox+z[0]*k,oy+z[1]*k,Math.max(1,(z[2]-z[0])*k),Math.max(1,(z[3]-z[1])*k));ctx.globalAlpha=1;
    }
    for (const st of fs.config.level.stations) {
      if (st.hidden_on_minimap && !fs.state.progress.stations[st.id]) continue;
      ctx.fillStyle = palette[st.kind] || "#83ddea";
      ctx.fillRect(ox + st.x * k - 1, oy + st.y * k - 1, 2, 2);
    }
    const destination=fs.config.level.navigation?.find(n=>!fs.state.progress.objectives[n.until]);
    if(destination) {
      ctx.strokeStyle='#f6c46c';ctx.lineWidth=1;ctx.beginPath();
      ctx.moveTo(ox+destination.x*k,oy+destination.y*k-3);ctx.lineTo(ox+destination.x*k+3,oy+destination.y*k);
      ctx.lineTo(ox+destination.x*k,oy+destination.y*k+3);ctx.lineTo(ox+destination.x*k-3,oy+destination.y*k);ctx.closePath();ctx.stroke();
    }
    ctx.fillStyle = "#fff";
    ctx.fillRect(ox + p.x * k - 1, oy + p.y * k - 1, 3, 3);
    ctx.strokeStyle = "#fff";
    ctx.beginPath();
    ctx.moveTo(ox + p.x * k, oy + p.y * k);
    ctx.lineTo(
      ox + (p.x + Math.cos(p.angle) * 1.8) * k,
      oy + (p.y + Math.sin(p.angle) * 1.8) * k,
    );
    ctx.stroke();
  }

  function drawFace(fs, t) {
    fs.debugStage = 'RENDER_HUD';
    const hp = fs.state.player.hp;
    fc.fillStyle = "#10212b";
    fc.fillRect(0, 0, 72, 64);
    fc.fillStyle = "#50767e";
    fc.fillRect(9, 48, 54, 16);
    fc.fillStyle = hp > 40 ? "#c6a079" : "#a87f6a";
    fc.fillRect(20, 17, 34, 35);
    fc.fillRect(16, 26, 42, 14);
    fc.fillStyle = "#303538";
    fc.fillRect(19, 10, 36, 12);
    fc.fillRect(22, 7, 26, 8);
    fc.fillStyle = "#152229";
    const blink = Math.sin(t * 1.2) > 0.998;
    fc.fillRect(24, 29, 8, blink ? 1 : 4);
    fc.fillRect(42, 29, 8, blink ? 1 : 4);
    fc.fillRect(34, 37, 5, 3);
    fc.fillRect(29, 45, 15, fs.faceUntil > t ? 4 : 2);
    if (hp < 80) {
      fc.fillStyle = "#93594f";
      fc.fillRect(44, 35, 7, 3);
    }
    if (hp < 60) {
      fc.fillStyle = "#754f4d";
      fc.fillRect(22, 26, 11, 3);
    }
    if (hp < 40) {
      fc.fillStyle = "#ad4338";
      fc.fillRect(20, 37, 4, 12);
      fc.fillRect(48, 39, 4, 9);
    }
    if (hp < 20) {
      fc.fillStyle = "#da443d";
      fc.fillRect(35, 39, 4, 9);
      fc.strokeStyle = "#f65e48";
      fc.strokeRect(1, 1, 70, 62);
    }
    if (fs.faceUntil > t) {
      fc.strokeStyle =
        fs.faceExpression === "hurt" ?
        "#e86a54" :
        fs.faceExpression === "upgrade" ?
        "#78e0e8" :
        "#e5b560";
      fc.lineWidth = 3;
      fc.strokeRect(2, 2, 68, 60);
      if (fs.faceExpression === "focus") {
        fc.fillStyle = "#253743";
        fc.fillRect(24, 26, 25, 2);
      }
    }
  }
  return {
    resize,
    factory,
    world
  };
})();
