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
    worker: "#c89a4d",
    crawler: "#89af54",
    rivet: "#b55d50",
    mad: "#79dce3",
    terminal: "#6cdbad",
    door: "#eead45",
    cache: "#be91de",
    exit: "#8adaab",
    pistol: "#dcb453",
    shells: "#d97b4c",
    health: "#d56f66",
    armor: "#669cae",
    shotgun: "#c2cbd0",
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
    if (["worker", "rivet", "crawler"].includes(type)) {
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
        if (type === "rivet") {
          g.fillStyle = "#84919b";
          g.fillRect(30, 34, 17, 10);
          g.fillStyle = "#ff875e";
          g.fillRect(43, 35, 5, 7);
        }
      }
    } else if (["terminal", "mad", "cache", "exit"].includes(type)) {
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
        "QC",
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
    g.addColorStop(0, "#0b1821");
    g.addColorStop(0.5, "#29383c");
    g.addColorStop(0.501, "#272e2e");
    g.addColorStop(1, "#111b22");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
    for (let j = 1; j <= 8; j++) {
      const y = H / 2 + H / (j * 2.2);
      ctx.strokeStyle = "#9ab6ad0b";
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      ctx.stroke();
    }
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
    const objects = [
      ...s.enemies.filter((e) => e.active && e.hp > 0),
      ...fs.config.level.items.filter((i) => !s.collected.includes(i.id)).map(i => ({
        ...i,
        type: i.type === 'weapon' ? i.weapon : i.type === 'ammo' ? (i.weapon === 'shotgun' ? 'shells' : 'pistol') : i.type
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
      const sh = (H / depth) * (o.type === "crawler" ? 0.85 : 1),
        sw = sh * 0.75;
      let top = H / 2 - sh / 2;
      if (["pistol", "shells", "health", "armor", "shotgun"].includes(o.type))
        top += sh * 0.03;
      const img = sprite(o.type);
      for (
        let col = Math.max(0, Math.floor(center - sw / 2)); col < Math.min(W, center + sw / 2); col++
      ) {
        if (depth < zbuf[col]) {
          const tx = Math.min(
            47,
            Math.max(0, Math.floor(((col - center + sw / 2) / sw) * 48)),
          );
          ctx.drawImage(img, tx, 0, 1, 64, col, top, 1, sh);
        }
      }
    }
    for (const b of fs.projectiles) {
      const ox = b.x - p.x,
        oy = b.y - p.y,
        dep = ox * dx + oy * dy;
      if (dep > 0.2) {
        const cx = (W / 2) * (1 + (-ox * dy + oy * dx) / (plane * dep));
        if (cx > 0 && cx < W && dep < zbuf[Math.floor(cx)]) {
          ctx.fillStyle = "#ffb069";
          ctx.fillRect(cx - 2, H / 2 - 2, 5, 5);
        }
      }
    }
    // Original procedural weapon silhouette.
    const bob = Math.sin(t * 10) * fs.moving * 3,
      recoil = Math.max(0, fs.shotFlash) * 30;
    const cx = W * 0.55,
      wy = H + bob + recoil;
    const scale = H / 300;
    ctx.save();
    ctx.translate(cx, wy);
    ctx.scale(scale, scale);
    const shotgun = s.weapon === "shotgun";
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
      ctx.fillStyle = "#526d74";
      ctx.fillRect(9, -88, 14, 73);
      ctx.fillStyle = "#a17644";
      ctx.fillRect(-22, -44, 49, 19);
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
    if (fs.hurtFlash > 0) {
      ctx.fillStyle = `rgba(191,46,30,${fs.hurtFlash * 0.4})`;
      ctx.fillRect(0, 0, W, H);
    }
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
    for (const st of fs.config.level.stations) {
      ctx.fillStyle = palette[st.kind] || "#83ddea";
      ctx.fillRect(ox + st.x * k - 1, oy + st.y * k - 1, 2, 2);
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
