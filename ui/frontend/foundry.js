"use strict";
// Foundry-only realtime systems: thermal cycles, Furnace Hound, Forge Brute,
// The Crucible and heavy-weapon effects. Progression/save authority remains Python.

function updateFurnaceHound(e, cfg, dt) {
  const p=FS.state.player, dx=p.x-e.x, dy=p.y-e.y, d=Math.hypot(dx,dy);
  const sees=d<cfg.vision && clearLine(e.x,e.y,p.x,p.y);
  e.phase_time=Math.max(0,(e.phase_time||0)-dt);
  e.cooldown=Math.max(0,(e.cooldown||0)-dt);

  if (e.hound_mode==='heat') {
    e.ai_state='preparing';e.facing=Math.atan2(dy,dx);
    if (!e.phase_time) {
      e.hound_mode='leap';e.phase_time=cfg.leap_time*(FS.state.difficulty==='doom'?.82:1);
      sound('bad');FS.worldDirty=true;
    }
    return;
  }
  if (e.hound_mode==='leap') {
    e.ai_state='charging';
    const vx=Math.cos(e.facing)*cfg.leap_speed*dt,vy=Math.sin(e.facing)*cfg.leap_speed*dt;
    const blocked=move(e,vx,vy,cfg.radius);
    if (Math.hypot(e.x-p.x,e.y-p.y)<cfg.radius+.32) {
      hurt(FS.config.difficulty.damage*1.45);
      e.hound_mode='recovery';e.phase_time=cfg.recovery;
    } else if (blocked || !e.phase_time) {
      e.hound_mode='recovery';e.phase_time=cfg.recovery*(blocked?.75:1);
      if (blocked) toast('FURNACE HOUND // IMPACTO · VULNERABLE');
    }
    FS.worldDirty=true;return;
  }
  if (e.hound_mode==='recovery') {
    e.ai_state='recovering';
    if (!e.phase_time) {e.hound_mode='track';e.cooldown=cfg.track_delay*(FS.state.difficulty==='doom'?.72:1);FS.worldDirty=true;}
    return;
  }

  if (sees) {e.last_known={x:p.x,y:p.y};e.search_time=cfg.search_seconds;e.ai_state='pursuing';}
  else if (e.last_known && e.search_time>0) {e.search_time=Math.max(0,e.search_time-dt);e.ai_state='searching';}
  else {e.ai_state='idle';e.last_known=null;return;}

  if (sees && d<5.4 && d>1.0 && e.cooldown<=0) {
    e.hound_mode='heat';e.phase_time=cfg.heat_time*(FS.state.difficulty==='doom'?.75:1);
    e.facing=Math.atan2(dy,dx);e.attack_index=(e.attack_index||0)+1;
    toast('FURNACE HOUND // CARGA TÉRMICA · ESQUIVA');sound('bad');FS.worldDirty=true;return;
  }
  if (sees && d<cfg.range && e.cooldown<=0) {
    hurt(FS.config.difficulty.damage*1.15);e.cooldown=.85;return;
  }
  const t=e.last_known,tx=t.x-e.x,ty=t.y-e.y,td=Math.hypot(tx,ty);
  if (td>.2) {
    e.facing=Math.atan2(ty,tx);
    const v=cfg.speed*FS.config.difficulty.speed*dt;
    if (move(e,tx/td*v,ty/td*v,cfg.radius)) move(e,-ty/td*v,tx/td*v,cfg.radius);
  }
}

function updateForgeBrute(e,cfg,dt) {
  const p=FS.state.player,dx=p.x-e.x,dy=p.y-e.y,d=Math.hypot(dx,dy);
  const sees=d<cfg.vision && clearLine(e.x,e.y,p.x,p.y);
  e.cooldown=Math.max(0,(e.cooldown||0)-dt);
  e.phase_time=Math.max(0,(e.phase_time||0)-dt);
  if (sees) {e.last_known={x:p.x,y:p.y};e.search_time=cfg.search_seconds;e.ai_state='pursuing';}
  else if (e.last_known && e.search_time>0) {e.search_time=Math.max(0,e.search_time-dt);e.ai_state='searching';}
  else {e.ai_state='idle';e.last_known=null;return;}

  if (e.charge_state==='slamming') {
    e.ai_state='slamming';
    if (!e.phase_time) {
      if (d<cfg.shock_radius && sees) hurt(FS.config.difficulty.damage*1.7);
      e.charge_state='recovering';e.phase_time=.85;toast('FORGE BRUTE // IMPACTO TÉRMICO');sound('hurt');
    }
    return;
  }
  if (e.charge_state==='recovering') {
    e.ai_state='recovering';if (!e.phase_time){e.charge_state='idle';e.cooldown=.5;}return;
  }
  if (sees && e.cooldown<=0) {
    e.attack_index=(e.attack_index||0)+1;e.facing=Math.atan2(dy,dx);
    if (d<2.25) {
      e.charge_state='slamming';e.phase_time=FS.state.difficulty==='doom'?.55:.75;
      toast('FORGE BRUTE // GOLPE DE SUELO · RETROCEDE');sound('bad');FS.worldDirty=true;return;
    }
    if (d<cfg.range) {
      const a=e.facing,speed=cfg.projectile_speed;
      FS.projectiles.push({x:e.x,y:e.y,vx:Math.cos(a)*speed,vy:Math.sin(a)*speed,life:3.4,molten:true});
      e.cooldown=FS.state.difficulty==='doom'?.9:1.25;toast('FORGE BRUTE // ESCORIA FUNDIDA');
    }
  }
  const t=e.last_known,tx=t.x-e.x,ty=t.y-e.y,td=Math.hypot(tx,ty);
  if (td>.4 && (!sees || d>3.0)) {
    e.facing=Math.atan2(ty,tx);const v=cfg.speed*FS.config.difficulty.speed*dt;
    if (move(e,tx/td*v,ty/td*v,cfg.radius)) move(e,-ty/td*v,tx/td*v,cfg.radius);
  }
}

function crucibleActiveLocks(boss) {
  if (!boss) return [];
  return (FS.config.level.crucible_locks||[]).filter(lock=>lock.phase===boss.boss_mode && (boss[lock.field]||0)>0);
}

function hitCrucibleLock(p,cfg,targets) {
  const boss=FS.state.enemies.find(e=>e.type==='crucible'&&e.active&&e.hp>0);
  if (!boss) return false;
  const lockTargets=crucibleActiveLocks(boss).map(lock=>{
    let a=Math.atan2(lock.y-p.y,lock.x-p.x)-p.angle;a=Math.atan2(Math.sin(a),Math.cos(a));
    return {lock,a,d:Math.hypot(lock.x-p.x,lock.y-p.y)};
  }).filter(t=>t.d<cfg.range && Math.abs(t.a)<cfg.spread+Math.atan2(.32,t.d) && clearLine(p.x,p.y,t.lock.x,t.lock.y)).sort((a,b)=>a.d-b.d);
  if (!lockTargets.length || (targets.length && lockTargets[0].d>targets[0].d+.2)) return false;
  const t=lockTargets[0], field=t.lock.field;
  boss[field]=Math.max(0,boss[field]-cfg.damage);
  FS.worldDirty=true;
  if (boss[field]<=0) {
    const remaining=crucibleActiveLocks(boss).length;
    bossAlert('PRESSURE LOCK DESTRUIDO',remaining?`${remaining} ${remaining===1?'LOCK RESTANTE':'LOCKS RESTANTES'}`:'NÚCLEO LISTO PARA EXPONERSE','success',1900);
    toast(`${t.lock.id.toUpperCase()} // DESTRUIDO`);
  } else toast(`${t.lock.id.toUpperCase()} // ${Math.ceil(boss[field])} HP`);
  return true;
}

function foundryDamageMultiplier(e,p) {
  const cfg=FS.config.enemies[e.type];
  if (e.type==='forge_brute') {
    const toward=Math.atan2(p.y-e.y,p.x-e.x),delta=Math.abs(Math.atan2(Math.sin(toward-e.facing),Math.cos(toward-e.facing)));
    if (delta<1.05) return cfg.frontal_multiplier??.42;
    return cfg.weak_multiplier??1.45;
  }
  if (e.type==='crucible') return ['pressure','meltdown'].includes(e.boss_mode)?0:1;
  return 1;
}

function applyFoundryBossClamp(e,dealt) {
  if (e.type!=='crucible') return Math.max(0,e.hp-dealt);
  const max=FS.config.enemies.crucible.hp;
  if (e.boss_mode==='exposed1') {
    const threshold=max*.50;
    if (e.hp>threshold && e.hp-dealt<threshold) return threshold;
  }
  if (e.boss_mode==='exposed2') {
    const threshold=max*.20;
    if (e.hp>threshold && e.hp-dealt<threshold) return threshold;
  }
  return Math.max(0,e.hp-dealt);
}

function explodePlayerRocket(b) {
  const radius=b.blast||2.6, p=FS.state.player;
  for (const e of FS.state.enemies) {
    if (!e.active||e.hp<=0) continue;
    const d=Math.hypot(e.x-b.x,e.y-b.y);if(d>radius||!clearLine(b.x,b.y,e.x,e.y))continue;
    const mult=foundryDamageMultiplier(e,{x:b.x,y:b.y});
    const dealt=b.damage*Math.max(.35,1-d/radius*.65)*mult;
    e.hp=applyFoundryBossClamp(e,dealt);e.last_known={x:p.x,y:p.y};FS.worldDirty=true;
    if(e.hp<=0){FS.state.stats.kills++;toast(`${FS.config.enemies[e.type].name} fuera de servicio`);}
  }
  const pd=Math.hypot(p.x-b.x,p.y-b.y);
  if(pd<radius*.8) hurt(Math.max(8,b.damage*.16*(1-pd/(radius*.8))));
  FS.shotFlash=.16;sound('hurt');
}

function updateCrucible(e,cfg,dt) {
  const p=FS.state.player,dx=p.x-e.x,dy=p.y-e.y,d=Math.hypot(dx,dy),max=cfg.hp;
  e.cooldown=Math.max(0,(e.cooldown||0)-dt);e.phase_time=Math.max(0,(e.phase_time||0)-dt);
  e.ai_state='pursuing';e.facing=Math.atan2(dy,dx);

  if (e.boss_mode==='pressure' && crucibleActiveLocks(e).length===0) {
    e.boss_mode='exposed1';e.phase_time=cfg.exposure_seconds;e.exposure_cycles=(e.exposure_cycles||0)+1;
    bossAlert('THE CRUCIBLE — CORE EXPOSED','¡ATACA EL NÚCLEO!','success',2600);toast('CRUCIBLE // CORE EXPOSED');sound('good');FS.worldDirty=true;
  }
  if (e.boss_mode==='exposed1' && e.hp<=max*.50) {
    e.boss_mode='meltdown';e.phase_time=0;e.emergency_a_hp=cfg.emergency_lock_hp;e.emergency_b_hp=cfg.emergency_lock_hp;
    bossAlert('MELTDOWN SEQUENCE','¡DESTRUYE LOS 2 EMERGENCY LOCKS!','warning',3100);toast('CRUCIBLE // MELTDOWN');sound('bad');FS.worldDirty=true;return;
  } else if (e.boss_mode==='exposed1' && !e.phase_time) {
    e.boss_mode='pressure';e.lock_a_hp=cfg.lock_hp*.6;e.lock_b_hp=cfg.lock_hp*.6;e.lock_c_hp=cfg.lock_hp*.6;
    bossAlert('CORE SEALED','PRESSURE LOCKS REACTIVATED','warning',2300);FS.worldDirty=true;
  }
  if (e.boss_mode==='meltdown' && crucibleActiveLocks(e).length===0) {
    e.boss_mode='exposed2';e.phase_time=cfg.exposure_seconds*(FS.state.difficulty==='doom'?.82:1);
    bossAlert('THE CRUCIBLE — CORE EXPOSED','SEGUNDA VENTANA DE DAÑO','success',2500);sound('good');FS.worldDirty=true;
  }
  if (e.boss_mode==='exposed2' && e.hp<=max*.20) {
    e.boss_mode='critical';e.phase_time=0;
    bossAlert('THE CRUCIBLE — CRITICAL FAILURE','¡DESTRÚYELO!','warning',3000);toast('CRUCIBLE // CORE PERMANENTLY EXPOSED');sound('bad');FS.worldDirty=true;
  } else if (e.boss_mode==='exposed2' && !e.phase_time) {
    e.boss_mode='meltdown';e.emergency_a_hp=cfg.emergency_lock_hp*.65;e.emergency_b_hp=cfg.emergency_lock_hp*.65;FS.worldDirty=true;
  }

  // Installation attacks remain readable: targeted molten bolts plus radial pulses.
  if (e.cooldown<=0 && e.hp>0) {
    e.attack_index=(e.attack_index||0)+1;
    const aggressive=e.boss_mode==='critical';
    if (e.attack_index%3===0) {
      const count=aggressive?10:8;
      for(let j=0;j<count;j++){
        const a=Math.PI*2*j/count+e.attack_index*.11;
        FS.projectiles.push({x:e.x,y:e.y,vx:Math.cos(a)*cfg.projectile_speed,vy:Math.sin(a)*cfg.projectile_speed,life:3.0,molten:true});
      }
    } else {
      for(const off of [-.06,.06]){
        const a=Math.atan2(dy,dx)+off;
        FS.projectiles.push({x:e.x,y:e.y,vx:Math.cos(a)*cfg.projectile_speed,vy:Math.sin(a)*cfg.projectile_speed,life:3.4,molten:true});
      }
    }
    e.cooldown=FS.state.difficulty==='doom'?(aggressive?.58:.82):(aggressive?.82:1.10);
  }
}

function updateHeatCycles(dt) {
  if (FS.state.level_id!=='foundry') {FS.heatWarning='';FS.heatDanger=false;return;}
  const boss=FS.state.enemies.find(e=>e.type==='crucible'&&e.active&&e.hp>0);
  const p=FS.state.player,t=FS.state.stats.seconds;
  FS._heatSeen ||= {};
  let warning='',danger=false;
  for(const hz of (FS.config.level.heat_zones||[])){
    if(hz.boss_only && !boss) continue;
    const z=hz.zone,inside=p.x>=z[0]&&p.y>=z[1]&&p.x<=z[2]&&p.y<=z[3];
    const period=(boss?.boss_mode==='critical'&&hz.boss_only)?Math.max(5.6,hz.period*.76):hz.period;
    const phase=((t+(hz.offset||0))%period+period)%period;
    const start=period-hz.warning-hz.active,activeStart=period-hz.active;
    if(inside && phase>=start && phase<activeStart){
      warning='PURGA TÉRMICA // ¡SAL DE LA ZONA!';
      const cycle=Math.floor((t+(hz.offset||0))/period);
      if(FS._heatSeen[hz.id]!==cycle){FS._heatSeen[hz.id]=cycle;bossAlert('PURGA TÉRMICA DETECTADA','¡SAL DE LA ZONA MARCADA!','warning',1800);sound('bad');}
    }
    if(inside && phase>=activeStart){
      danger=true;warning='PURGA TÉRMICA ACTIVA';
      FS._heatDamage ||= {};
      if((FS._heatDamage[hz.id]||0)<=t){hurt(hz.damage);FS._heatDamage[hz.id]=t+.55;}
    }
  }
  FS.heatWarning=warning;FS.heatDanger=danger;
}
