"use strict";
// Loader-only realtime behavior. Progression/waves/loot remain Python-owned.
function updateLoader(e, cfg, dt) {
  const p = FS.state.player, dx=p.x-e.x, dy=p.y-e.y, d=Math.hypot(dx,dy);
  const sees = d < cfg.vision && clearLine(e.x,e.y,p.x,p.y);
  e.phase_time = Math.max(0,(e.phase_time || 0)-dt);
  if (e.stun_time > 0) {
    e.stun_time=Math.max(0,e.stun_time-dt); e.ai_state='stunned';
    if (!e.stun_time) {e.charge_state='recovering'; e.phase_time=cfg.recovery;}
    return;
  }
  if (e.charge_state==='preparing') {
    e.ai_state='preparing';
    if (!e.phase_time) {e.charge_state='charging'; e.phase_time=cfg.charge_duration; sound('bad');}
    return;
  }
  if (e.charge_state==='charging') {
    e.ai_state='charging';
    // Charge cannot slide along a wall: any blocked axis is an impact.
    const vx=Math.cos(e.facing)*cfg.charge_speed*dt, vy=Math.sin(e.facing)*cfg.charge_speed*dt;
    const ox=e.x, oy=e.y;
    move(e,vx,vy,cfg.radius);
    e.charge_blocked=Math.hypot((e.x-ox)-vx,(e.y-oy)-vy)>.001;
    if (e.charge_blocked) {
      e.charge_state='blocked'; e.stun_time=cfg.stun_seconds; e.ai_state='stunned';
      toast('LOADER // STUNNED · Rodea la máquina'); sound('hurt'); FS.worldDirty=true;
    } else if (Math.hypot(e.x-p.x,e.y-p.y)<cfg.radius+.4) {
      hurt(FS.config.difficulty.damage*2); e.charge_state='recovering'; e.phase_time=cfg.recovery;
    } else if (!e.phase_time) {e.charge_state='recovering'; e.phase_time=cfg.recovery;}
    return;
  }
  if (e.charge_state==='slamming') {
    e.ai_state='slamming';
    if (!e.phase_time) {
      if (d<cfg.slam_radius && sees) hurt(FS.config.difficulty.damage*1.8);
      sound('hurt'); toast('LOADER // IMPACTO');
      e.charge_state='recovering'; e.phase_time=cfg.recovery;
    }
    return;
  }
  if (e.charge_state==='recovering') {
    e.ai_state='recovering';
    if (!e.phase_time) {e.charge_state='idle'; e.cooldown=FS.config.difficulty.attack_interval;}
    return;
  }
  e.cooldown=Math.max(0,(e.cooldown || 0)-dt);
  if (sees) {e.last_known={x:p.x,y:p.y}; e.search_time=cfg.search_seconds; e.ai_state='pursuing';}
  else if (e.last_known && e.search_time>0) {e.search_time=Math.max(0,e.search_time-dt);e.ai_state='searching';}
  else {e.ai_state='idle'; e.last_known=null; return;}
  if (sees && e.cooldown<=0) {
    e.attack_index=(e.attack_index || 0)+1;
    e.facing=Math.atan2(dy,dx);
    if (d<cfg.range && e.attack_index%2===1) {
      hurt(FS.config.difficulty.damage*cfg.damage_multiplier);
      e.charge_state='recovering'; e.phase_time=cfg.recovery;
    } else if (d<3.2 && e.attack_index%2===0) {
      e.charge_state='slamming';e.phase_time=cfg.slam_prepare;
      toast('LOADER // GROUND SLAM · Aléjate');sound('bad');
    } else if (d>2 && d<10) {
      e.charge_state='preparing';e.charge_blocked=false;
      e.phase_time=cfg.charge_prepare*(FS.state.difficulty==='doom'?.8:1);
      toast('LOADER // CHARGE · Aparta de la línea');sound('bad');
    } else e.cooldown=.6;
    if (e.charge_state!=='idle') {FS.worldDirty=true;return;}
  }
  const tx=e.last_known.x-e.x,ty=e.last_known.y-e.y,td=Math.hypot(tx,ty);
  if (td>.25 && (!sees || d>cfg.range*.8)) {
    e.facing=Math.atan2(ty,tx);
    const v=cfg.speed*FS.config.difficulty.speed*dt;
    if (move(e,tx/td*v,ty/td*v,cfg.radius)) move(e,-ty/td*v,tx/td*v,cfg.radius);
  }
}

function worldFeedback(before, after) {
  for (const tr of [...FS.config.level.triggers].sort((a,b)=>(a.priority || 0)-(b.priority || 0))) {
    if (tr.message && !before.triggers[tr.id] && after.triggers[tr.id]) {
      toast(tr.message);sound(tr.id==='loader_warning'?'bad':'good');
    }
  }
  if (after.utcj_found.length>before.utcj_found.length) {
    toast(`PROJECT U.T.C.J. // ${after.utcj_found.length}/${FS.config.level.campaign_secrets || 4} · SIGNAL REGISTERED`);
    sound('good');
  }
}
