"use strict";

function tileAt(x, y) {
  const cell = FS.config.level.grid[Math.floor(y)]?.[Math.floor(x)] ?? 1;
  if (cell !== 3) return cell;
  const door = FS.config.level.doors.find(d => d.cell[0] === Math.floor(x) && d.cell[1] === Math.floor(y));
  return door && FS.state.progress.doors[door.id] ? 0 : 3;
}

function solid(x, y) {
  return tileAt(x, y) !== 0;
}

function stationKind(id) {
  return FS.config?.level.stations.find(s => s.id === id)?.kind;
}

function condition(rule) {
  if (!rule || !Object.keys(rule).length) return true;
  if (rule.all) return rule.all.every(condition);
  if (rule.any) return rule.any.some(condition);
  if (rule.zone) {
    const p = FS.state.player,
      z = rule.zone;
    return p.x >= z[0] && p.y >= z[1] && p.x <= z[2] && p.y <= z[3];
  }
  for (const [k, v] of Object.entries({
      objective: 'objectives',
      door_open: 'doors',
      station_used: 'stations',
      trigger: 'triggers',
      wave: 'waves',
      secret: 'secrets'
    }))
    if (rule[k]) return !!FS.state.progress[v][rule[k]];
  if (rule.collected) return FS.state.collected.includes(rule.collected);
  if ('complete' in rule) return FS.state.progress.complete===rule.complete;
  if (rule.enemy_hp_below) {
    const r=rule.enemy_hp_below,e=FS.state.enemies.find(e=>e.id===r.id);
    return !!e && e.active && e.hp>=0 && e.hp<=FS.config.enemies[e.type].hp*r.ratio;
  }
  if (rule.trigger_elapsed) {
    const r=rule.trigger_elapsed, start=FS.state.progress.trigger_times?.[r.id];
    return start!==undefined && FS.state.stats.seconds-start>=r.seconds;
  }
  if (rule.item) return Object.values(FS.state.inventory).some(b => b[rule.item] > 0);
  if (rule.group_defeated) {
    const es = FS.state.enemies.filter(e => e.group === rule.group_defeated);
    return es.length > 0 && es.every(e => e.hp <= 0);
  }
  return false;
}

function areaUnsafe() {
  const p = FS.state.player;
  return FS.state.enemies.some(e => e.active && e.hp > 0 && Math.hypot(e.x - p.x, e.y - p.y) < 6 && clearLine(p.x, p.y, e.x, e.y));
}
// Merge only server-owned fields while realtime movement/combat continue during RPC.
function mergeWorld(reply, before) {
  if (!reply?.state || FS.state.run_id !== reply.state.run_id) return;
  const s = FS.state,
    r = reply.state;
  worldFeedback(s.progress, r.progress);
  s.progress = r.progress;
  s.inventory = r.inventory;
  s.checkpoint = r.checkpoint;
  s.report = r.report;
  for (const k of ['correct', 'attempted', 'streak', 'best_streak', 'secrets']) s.stats[k] = r.stats[k];
  for (const e of s.enemies) {
    const a = r.enemies.find(x => x.id === e.id);
    e.active = a.active;
  }
  // Apply backend resource deltas, not a stale absolute snapshot.
  for (const [w, a] of Object.entries(r.weapons)) {
    if (!s.weapons[w]) s.weapons[w] = clone(a);
    else {
      for (const k of ['loaded', 'reserve']) s.weapons[w][k] = Math.max(0, Math.min(k === 'reserve' ? 999 : reply.config.weapons[w].capacity, s.weapons[w][k] + a[k] - (before.weapons[w]?.[k] ?? a[k])));
      s.weapons[w].mods = a.mods;
    }
  }
  s.player.hp = Math.min(reply.config.level.player_config.max_hp, Math.max(0, s.player.hp + r.player.hp - before.player.hp));
  s.secret_hits = (s.secret_hits || []).filter(id => !r.progress.secrets[id]);
  FS.config = reply.config;
  updateHUD();
}
async function syncWorld() {
  const before = clone(FS.state);
  const r = await rpc('sync', {}, true, before);
  mergeWorld(r, before);
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
  const ox = entity.x,
    oy = entity.y;
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
  return Math.hypot(entity.x - ox, entity.y - oy) < Math.hypot(vx, vy) * .5;
}

function selectWeapon(w) {
  if (!FS.state?.weapons[w]) {
    toast("Encuentra la escopeta en el mapa");
    return;
  }
  if (FS.state.weapon !== w) window.InputControls?.haptic("weapon");
  FS.state.weapon = w;
  FS.reloading = 0;
  // Preserve remaining shot cooldown across weapon switches.
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
  window.InputControls?.haptic("shot");
  const p = s.player,
    targets = s.enemies
    .filter((e) => e.active && e.hp > 0)
    .map((e) => {
      let a = Math.atan2(e.y - p.y, e.x - p.x) - p.angle;
      a = Math.atan2(Math.sin(a), Math.cos(a));
      return {
        e,
        a,
        d: Math.hypot(e.x - p.x, e.y - p.y)
      };
    })
    .filter(
      (t) =>
      Math.abs(t.a) < cfg.spread + Math.atan2(FS.config.enemies[t.e.type].radius + .08, t.d) &&
      t.d < cfg.range &&
      clearLine(p.x, p.y, t.e.x, t.e.y),
    )
    .sort((a, b) => a.d - b.d);
  // Pistol hits the closest target; shotgun's cone can hit several with falloff.
  for (const t of targets.slice(0, s.weapon === "shotgun" ? 3 : 1)) {
    const falloff =
      s.weapon === "shotgun" ? Math.max(0.25, 1 - t.d / (cfg.range * 1.3)) : 1;
    const ec = FS.config.enemies[t.e.type],
      back = Math.atan2(p.y - t.e.y, p.x - t.e.x) - t.e.facing;
    const rear = Math.abs(Math.atan2(Math.sin(back), Math.cos(back))) > Math.PI - ec.rear_angle ? ec.rear_multiplier : 1;
    t.e.hp = Math.max(0, t.e.hp - cfg.damage * falloff * rear);
    t.e.last_known = {
      x: p.x,
      y: p.y
    };
    if (t.e.type !== "loader") t.e.ai_state = 'pursuing';
    t.e.search_time = ec.search_seconds;
    FS.worldDirty = true;
    if (t.e.hp <= 0) {
      s.stats.kills++;
      toast(`${FS.config.enemies[t.e.type].name} fuera de servicio`);
    }
  }
  for (const secret of FS.config.level.secrets) {
    if (!secret.on_shot || s.progress.secrets[secret.id]) continue;
    const d = Math.hypot(secret.x - p.x, secret.y - p.y),
      a = Math.atan2(secret.y - p.y, secret.x - p.x) - p.angle;
    if (d < cfg.range && Math.abs(Math.atan2(Math.sin(a), Math.cos(a))) < cfg.spread + Math.atan2(.25, d) && clearLine(p.x, p.y, secret.x, secret.y) && (!targets.length || d < targets[0].d)) {
      s.secret_hits = [...new Set([...(s.secret_hits || []), secret.id])];
      FS.worldDirty = true;
      toast('PROJECT U.T.C.J. // IDENTIFICADO');
    }
  }
  updateHUD();
}

function hurt(amount) {
  if (FS.state.player.grace > 0) return;
  const p = FS.state.player,
    absorbed = Math.min(p.armor, amount * 0.5);
  p.armor = Math.max(0, p.armor - absorbed);
  const dmg = Math.min(p.hp, amount - absorbed);
  p.hp = Math.max(0, p.hp - dmg);
  FS.state.stats.damage += dmg;
  FS.hurtFlash = 0.7;
  expression("hurt");
  sound("hurt");
  window.InputControls?.haptic("hurt");
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
    const limits = FS.config.level.player_config;
    if ((item.type === 'health' && p.hp >= limits.max_hp) || (item.type === 'armor' && p.armor >= limits.max_armor)) continue;
    switch (item.type) {
      case 'weapon':
        if (!FS.config.weapons[item.weapon]) continue;
        if (!s.weapons[item.weapon]) s.weapons[item.weapon] = {
          loaded: FS.config.weapons[item.weapon].capacity,
          reserve: item.reserve ?? (FS.config.difficulty[item.weapon + '_reserve'] || 0),
          mods: 0
        };
        selectWeapon(item.weapon);
        expression('smile');
        toast(FS.config.weapons[item.weapon].name);
        break;
      case 'ammo':
        if (!s.weapons[item.weapon]) continue;
        s.weapons[item.weapon].reserve = Math.min(999, s.weapons[item.weapon].reserve + item.amount);
        toast('MUNICIÓN +' + item.amount);
        break;
      case 'health':
        p.hp = Math.min(limits.max_hp, p.hp + item.amount);
        toast('BOTIQUÍN +' + item.amount);
        break;
      case 'armor':
        p.armor = Math.min(limits.max_armor, p.armor + item.amount);
        toast('ARMADURA +' + item.amount);
        break;
      case 'quest_item':
      case 'key_item':
        if (!item.item_id) continue;
        toast('OBJETO // ' + (item.label || item.item_id));
        break;
      case 'secret_item':
        if (!FS.config.level.secrets.some(x => x.id === item.secret_id)) continue;
        break;
      default:
        if (!FS.badPickups?.has(item.id)) {
          FS.badPickups ??= new Set();
          FS.badPickups.add(item.id);
          console.warn('Pickup desconocido', item.id, item.type);
          toast('Recurso incompatible: ' + item.id);
        }
        continue;
    }
    s.collected.push(item.id);
    FS.worldDirty = true;
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
  $("#healthbar").style.width = (s.player.hp / FS.config.level.player_config.max_hp * 100) + "%";
  $("#weaponname").textContent = s.weapon === "pistol" ? "PISTOLA" : "ESCOPETA";
  $("#mod").textContent =
    "MOD " + (w.mods ? "I" : "0") + " · TOCA PARA CAMBIAR";
  $("#reserve").textContent = "RESERVA " + w.reserve;
  const objectives = FS.config.level.objectives;
  $('#objective').textContent = `${s.difficulty.toUpperCase()} // OBJETIVOS ${objectives.filter(o=>s.progress.objectives[o.id]).length}/${objectives.length} · ENEMIES ${s.stats.kills}/${s.enemies.length}`;

  const hint = FS.config.level.objective_hints?.find(o=>!s.progress.objectives[o.until]);
  if (hint) {
    const zone=FS.config.level.zones.find(z=>condition({zone:z.zone}));
    $('#objective').textContent=(zone?zone.label+' // ':'')+hint.text;
  }
  const boss=s.enemies.find(e=>e.type==='loader' && e.active && e.hp>0);
  $('#bossbar').classList.toggle('hidden',!boss || !FS.playing);
  if (boss) {
    $('#bosshp').max=FS.config.enemies[boss.type].hp; $('#bosshp').value=boss.hp;
    $('#bosslabel').textContent='LOADER MK-I // '+(boss.stun_time>0?'STUNNED':boss.charge_state.toUpperCase());
  }
}
async function checkpoint(cp) {
  const before = clone(FS.state);
  const r = await rpc("checkpoint", {
    checkpoint: cp
  }, true, before);
  mergeWorld(r, before);
  if (r) {
    FS.state.checkpoint = r.state.checkpoint;
    toast("CHECKPOINT // " + cp.toUpperCase());
  }
}

function tick(dt, t) {
  if (!FS.playing || FS.recovering || !$("#connection").classList.contains("hidden")) return;
  const s = FS.state,
    p = s.player;
  FS.debugStage = 'PLAYER_UPDATE';
  FS.shotFlash = Math.max(0, FS.shotFlash - dt);
  FS.hurtFlash = Math.max(0, FS.hurtFlash - dt);
  FS.cooldown = Math.max(0, FS.cooldown - dt);
  s.stats.seconds += dt;
  p.grace = Math.max(0, (p.grace || 0) - dt);
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
  FS.debugStage = 'PICKUP_UPDATE';
  pickups();
  FS.debugStage = 'ENEMY_UPDATE';
  for (const e of s.enemies) {
    if (!FS.playing) break;
    if (!e.active || e.hp <= 0) continue;
    const cfg = FS.config.enemies[e.type],
      dx = p.x - e.x,
      dy = p.y - e.y,
      d = Math.hypot(dx, dy);
    if (e.type === "loader") { updateLoader(e,cfg,dt); continue; }
    e.cooldown = Math.max(0, (e.cooldown || 0) - dt);
    if (e.stun_time > 0) {
      e.stun_time = Math.max(0, e.stun_time - dt);
      e.ai_state = 'stunned';
      continue;
    }
    const sees = d < cfg.vision && clearLine(e.x, e.y, p.x, p.y);
    if (sees) {
      e.last_known = {
        x: p.x,
        y: p.y
      };
      e.search_time = cfg.search_seconds;
      e.ai_state = 'pursuing';
    } else if (e.last_known && e.search_time > 0) {
      e.search_time = Math.max(0, e.search_time - dt);
      e.ai_state = 'searching';
    } else {
      e.ai_state = 'idle';
      e.last_known = null;
      continue;
    }
    if (e.charge_state === 'charging') {
      e.ai_state = 'charging';
      e.charge_blocked = move(e, Math.cos(e.facing) * cfg.charge_speed * dt, Math.sin(e.facing) * cfg.charge_speed * dt, cfg.radius);
      if (e.charge_blocked) {
        e.charge_state = 'blocked';
        e.stun_time = cfg.stun_seconds;
        e.ai_state = 'stunned';
      }
      continue;
    }
    const target = e.last_known,
      tx = target.x - e.x,
      ty = target.y - e.y,
      td = Math.hypot(tx, ty);
    if (td > .2 && (!sees || d > cfg.range * .85)) {
      e.facing = Math.atan2(ty, tx);
      const v = cfg.speed * FS.config.difficulty.speed * dt;
      const blocked = move(e, tx / td * v, ty / td * v, cfg.radius);
      if (blocked) {
        const side = e.id.length % 2 ? 1 : -1;
        move(e, -ty / td * v * side, tx / td * v * side, cfg.radius);
      }
    }
    if (sees && d < cfg.range && e.cooldown <= 0) {
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
  FS.debugStage = 'STATION_UPDATE';
  FS.nearest = FS.config.level.stations.map(st => ({
      ...st,
      d: Math.hypot(st.interaction_point.x - p.x, st.interaction_point.y - p.y)
    }))
    .filter(st => !(st.kind === "install" && s.progress.stations[st.id]) && st.d < st.interaction_distance && clearLine(p.x, p.y, st.interaction_point.x, st.interaction_point.y)).sort((a, b) => a.d - b.d)[0] || null;
  $('#hint').textContent = FS.nearest ? '[ E / USAR ] ' + FS.nearest.label : '';
  if (t-(FS.lastHud || 0)>.15) {updateHUD();FS.lastHud=t;}
  const exit=FS.config.level.exit;
  const exitStation=FS.config.level.stations.find(st=>st.id===exit.station);
  if (exit.auto_zone && condition({zone:exit.auto_zone}) && condition(exit.condition) && FS.playing && !Bridge.busy && exitStation && Math.hypot(p.x-exitStation.interaction_point.x,p.y-exitStation.interaction_point.y)<exitStation.interaction_distance) {
    FS.nearest=exitStation; interact(); return;
  }
  FS.debugStage = 'CHECKPOINT_UPDATE';
  if (!Bridge.busy && FS.playing) {
    FS.checkpointAttempts ??= {};
    const current = FS.config.level.checkpoints.find(c => c.id === s.checkpoint);
    const currentOrder = current?.order ?? -1;
    const next = FS.config.level.checkpoints.filter(c => c.order > currentOrder && condition(c.prerequisites) && condition({
      zone: c.zone
    })).sort((a, b) => a.order - b.order)[0];
    if (next && t - (FS.checkpointAttempts[next.id] || -100) > 3) {
      FS.checkpointAttempts[next.id] = t;
      checkpoint(next.id);
    } else if (t - FS.lastSync > ((FS.worldDirty || FS.config.level.triggers.some(tr => !s.progress.triggers[tr.id] && condition(tr.condition))) ? .5 : 10)) {
      FS.lastSync = t;
      FS.worldDirty = false;
      syncWorld();
    }
  }
}
