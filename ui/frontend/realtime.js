"use strict";
function solid(x, y) {
  const tile = FS.config.level.grid[Math.floor(y)]?.[Math.floor(x)] ?? 1;
  return tile !== 0 && !(tile === 3 && FS.state.progress.door_open);
}
function clearLine(x, y, tx, ty) {
  const d = Math.hypot(tx - x, ty - y),
    steps = Math.ceil(d / 0.12);
  for (let i = 1; i <= steps; i++)
    if (solid(x + ((tx - x) * i) / steps, y + ((ty - y) * i) / steps))
      return false;
  return true;
}
function move(entity, vx, vy, r = 0.2) {
  if (
    !solid(entity.x + vx + Math.sign(vx) * r, entity.y - r) &&
    !solid(entity.x + vx + Math.sign(vx) * r, entity.y + r)
  )
    entity.x += vx;
  if (
    !solid(entity.x - r, entity.y + vy + Math.sign(vy) * r) &&
    !solid(entity.x + r, entity.y + vy + Math.sign(vy) * r)
  )
    entity.y += vy;
}
function selectWeapon(w) {
  if (!FS.state?.weapons[w]) {
    toast("Encuentra la escopeta en la sala inicial");
    return;
  }
  FS.state.weapon = w;
  FS.reloading = 0;
  FS.cooldown = 0.2;
  updateHUD();
}
function reload() {
  if (!FS.playing || FS.reloading) return;
  const w = FS.state.weapons[FS.state.weapon],
    cfg = FS.config.weapons[FS.state.weapon];
  if (w.loaded >= cfg.capacity || w.reserve <= 0) return;
  FS.reloading = cfg.reload;
  toast("RECARGANDO…");
  sound("reload");
}
function shoot() {
  if (!FS.playing || FS.cooldown > 0 || FS.reloading > 0) return;
  const s = FS.state,
    w = s.weapons[s.weapon],
    cfg = FS.config.weapons[s.weapon];
  if (w.loaded <= 0) {
    if (w.reserve) reload();
    else {
      toast("Sin munición. Busca recursos o calibra una estación.");
      FS.cooldown = 0.5;
    }
    return;
  }
  w.loaded--;
  s.stats.ammo_used++;
  FS.cooldown = cfg.cooldown;
  FS.shotFlash = 0.12;
  sound("shot");
  const p = s.player,
    targets = s.enemies
      .filter((e) => e.hp > 0)
      .map((e) => {
        let a = Math.atan2(e.y - p.y, e.x - p.x) - p.angle;
        a = Math.atan2(Math.sin(a), Math.cos(a));
        return { e, a, d: Math.hypot(e.x - p.x, e.y - p.y) };
      })
      .filter(
        (t) =>
          Math.abs(t.a) < cfg.spread + Math.atan2(0.26, t.d) &&
          t.d < cfg.range &&
          clearLine(p.x, p.y, t.e.x, t.e.y),
      )
      .sort((a, b) => a.d - b.d);
  // Pistol hits the closest target; shotgun's cone can hit several with falloff.
  for (const t of targets.slice(0, s.weapon === "shotgun" ? 3 : 1)) {
    const falloff =
      s.weapon === "shotgun" ? Math.max(0.25, 1 - t.d / (cfg.range * 1.3)) : 1;
    t.e.hp = Math.max(0, t.e.hp - cfg.damage * falloff);
    if (t.e.hp <= 0) {
      s.stats.kills++;
      toast(`${FS.config.enemies[t.e.type].name} fuera de servicio`);
    }
  }
  updateHUD();
}
function hurt(amount) {
  const p = FS.state.player,
    absorbed = Math.min(p.armor, amount * 0.5);
  p.armor = Math.max(0, p.armor - absorbed);
  const dmg = Math.min(p.hp, amount - absorbed);
  p.hp = Math.max(0, p.hp - dmg);
  FS.state.stats.damage += dmg;
  FS.hurtFlash = 0.7;
  expression("hurt");
  sound("hurt");
  updateHUD();
  if (p.hp <= 0) death();
}
function pickups() {
  const s = FS.state,
    p = s.player;
  for (const item of FS.config.level.items) {
    if (
      s.collected.includes(item.id) ||
      Math.hypot(item.x - p.x, item.y - p.y) > 0.65
    )
      continue;
    if (
      (item.type === "health" && p.hp >= 100) ||
      (item.type === "armor" && p.armor >= 100) ||
      (item.type === "shells" && !s.weapons.shotgun)
    )
      continue;
    s.collected.push(item.id);
    if (item.type === "shotgun") {
      s.weapons.shotgun = {
        loaded: 8,
        reserve: FS.config.difficulty.shotgun_reserve,
        mods: 0,
      };
      selectWeapon("shotgun");
      expression("smile");
      toast("ESCOPETA DE CORREDERA · 8 CARTUCHOS");
    } else if (item.type === "health") {
      p.hp = Math.min(100, p.hp + item.amount);
      toast("BOTIQUÍN +" + item.amount);
    } else if (item.type === "armor") {
      p.armor = Math.min(100, p.armor + item.amount);
      toast("ARMADURA +" + item.amount);
    } else {
      const key = item.type === "pistol" ? "pistol" : "shotgun";
      s.weapons[key].reserve += item.amount;
      toast("MUNICIÓN +" + item.amount);
    }
    sound("pickup");
    updateHUD();
  }
}
function updateHUD() {
  if (!FS.state) return;
  const s = FS.state,
    w = s.weapons[s.weapon];
  $("#ammo").textContent = w.loaded;
  $("#health").textContent = Math.ceil(s.player.hp);
  $("#armor").textContent = Math.ceil(s.player.armor);
  $("#healthbar").style.width = s.player.hp + "%";
  $("#weaponname").textContent = s.weapon === "pistol" ? "PISTOLA" : "ESCOPETA";
  $("#mod").textContent =
    "MOD " + (w.mods ? "I" : "0") + " · TOCA PARA CAMBIAR";
  $("#reserve").textContent = "RESERVA " + w.reserve;
  $("#objective").textContent =
    `${s.difficulty.toUpperCase()} // ${s.progress.door_open ? "LLEGA AL FIN DE TURNO" : s.stats.kills === s.enemies.length ? "CALIBRA LA PUERTA ÁMBAR" : "LIMPIA LA ARENA"} · ${s.stats.kills}/${s.enemies.length}`;
}
async function checkpoint(cp) {
  const r = await rpc("checkpoint", { checkpoint: cp });
  if (r) {
    FS.state.checkpoint = r.state.checkpoint;
    toast("CHECKPOINT // " + cp.toUpperCase());
  }
}
function tick(dt, t) {
  if (!FS.playing || !$("#connection").classList.contains("hidden")) return;
  const s = FS.state,
    p = s.player;
  FS.shotFlash = Math.max(0, FS.shotFlash - dt);
  FS.hurtFlash = Math.max(0, FS.hurtFlash - dt);
  FS.cooldown = Math.max(0, FS.cooldown - dt);
  s.stats.seconds += dt;
  if (FS.reloading > 0) {
    FS.reloading -= dt;
    if (FS.reloading <= 0) {
      const w = s.weapons[s.weapon],
        need = FS.config.weapons[s.weapon].capacity - w.loaded,
        n = Math.min(need, w.reserve);
      w.loaded += n;
      w.reserve -= n;
      updateHUD();
    }
  }
  let forward = (FS.keys.KeyW ? 1 : 0) - (FS.keys.KeyS ? 1 : 0) - FS.move.y,
    strafe = (FS.keys.KeyD ? 1 : 0) - (FS.keys.KeyA ? 1 : 0) + FS.move.x;
  const len = Math.hypot(forward, strafe);
  if (len > 1) {
    forward /= len;
    strafe /= len;
  }
  FS.moving = Math.min(1, len);
  p.angle +=
    ((FS.keys.ArrowRight ? 1 : 0) - (FS.keys.ArrowLeft ? 1 : 0)) * dt * 2.2;
  p.angle = Math.atan2(Math.sin(p.angle), Math.cos(p.angle));
  const speed = 3.7 * dt;
  move(
    p,
    (Math.cos(p.angle) * forward - Math.sin(p.angle) * strafe) * speed,
    (Math.sin(p.angle) * forward + Math.cos(p.angle) * strafe) * speed,
  );
  if (FS.fireHeld) shoot();
  pickups();
  for (const e of s.enemies) {
    if (!FS.playing) break;
    if (e.hp <= 0) continue;
    const cfg = FS.config.enemies[e.type],
      dx = p.x - e.x,
      dy = p.y - e.y,
      d = Math.hypot(dx, dy);
    e.cooldown = Math.max(0, (e.cooldown || 0) - dt);
    if (d > 11 || !clearLine(e.x, e.y, p.x, p.y)) continue;
    if (d > cfg.range * 0.85) {
      const v = cfg.speed * FS.config.difficulty.speed * dt;
      move(e, (dx / d) * v, (dy / d) * v, 0.18);
    }
    if (d < cfg.range && e.cooldown <= 0) {
      e.cooldown = FS.config.difficulty.attack_interval;
      if (e.type === "rivet") {
        FS.projectiles.push({
          x: e.x,
          y: e.y,
          vx: (dx / d) * 4.5,
          vy: (dy / d) * 4.5,
          life: 3,
        });
      } else hurt(FS.config.difficulty.damage);
    }
  }
  for (let i = FS.projectiles.length - 1; i >= 0; i--) {
    if (!FS.playing) break;
    const b = FS.projectiles[i];
    b.x += b.vx * dt;
    b.y += b.vy * dt;
    b.life -= dt;
    if (Math.hypot(b.x - p.x, b.y - p.y) < 0.3) {
      FS.projectiles.splice(i, 1);
      hurt(FS.config.difficulty.damage);
      continue;
    }
    if (b.life <= 0 || solid(b.x, b.y)) FS.projectiles.splice(i, 1);
  }
  FS.nearest =
    FS.config.level.stations
      .map((st) => ({ ...st, d: Math.hypot(st.x - p.x, st.y - p.y) }))
      .filter(
        (st) =>
          st.d < 1.9 &&
          clearLine(
            p.x,
            p.y,
            st.id === "door" ? Math.min(st.x, 20.8) : st.x,
            st.y,
          ),
      )
      .sort((a, b) => a.d - b.d)[0] || null;
  $("#hint").textContent = FS.nearest ? "[ E / USAR ] " + FS.nearest.label : "";
  if (!Bridge.busy && FS.playing) {
    if (s.checkpoint === "inicio" && p.x > 10.5 && p.x < 14)
      checkpoint("arena");
    else if (
      s.checkpoint !== "final" &&
      p.x > 18 &&
      s.enemies.every((e) => e.hp <= 0)
    )
      checkpoint("final");
    else if (t - FS.lastSync > 10) {
      FS.lastSync = t;
      rpc("sync");
    }
  }
}
