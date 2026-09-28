"use strict";
// Laboratory-only realtime behaviors. Python remains authoritative for progression/save.

function updateStalker(e, cfg, dt) {
  const p=FS.state.player, dx=p.x-e.x, dy=p.y-e.y, d=Math.hypot(dx,dy);
  const sees=d<cfg.vision && clearLine(e.x,e.y,p.x,p.y);
  e.phase_time=Math.max(0,(e.phase_time||0)-dt);
  e.cooldown=Math.max(0,(e.cooldown||0)-dt);

  if (e.stalker_mode==='reveal') {
    e.ai_state='preparing';
    e.facing=Math.atan2(dy,dx);
    if (!e.phase_time) {
      e.stalker_mode='lunge';
      e.phase_time=cfg.lunge_time*(FS.state.difficulty==='doom'?.86:1);
      sound('bad');
      FS.worldDirty=true;
    }
    return;
  }

  if (e.stalker_mode==='lunge') {
    e.ai_state='charging';
    const vx=Math.cos(e.facing)*cfg.lunge_speed*dt, vy=Math.sin(e.facing)*cfg.lunge_speed*dt;
    const blocked=move(e,vx,vy,cfg.radius);
    if (Math.hypot(e.x-p.x,e.y-p.y)<cfg.radius+.35) {
      hurt(FS.config.difficulty.damage*1.55);
      e.stalker_mode='recovery';
      e.phase_time=cfg.recovery;
      FS.worldDirty=true;
    } else if (blocked || !e.phase_time) {
      e.stalker_mode='recovery';
      e.phase_time=cfg.recovery;
      FS.worldDirty=true;
    }
    return;
  }

  if (e.stalker_mode==='recovery') {
    e.ai_state='recovering';
    if (!e.phase_time) {
      e.stalker_mode='stalk';
      e.cooldown=cfg.stalk_delay*(FS.state.difficulty==='doom'?.72:1);
      FS.worldDirty=true;
    }
    return;
  }

  // STALK: partially camouflaged. It can move and reposition but never deal damage.
  if (sees) {
    e.last_known={x:p.x,y:p.y};
    e.search_time=cfg.search_seconds;
    e.ai_state='pursuing';
    if (d<5.8 && e.cooldown<=0) {
      e.stalker_mode='reveal';
      e.phase_time=cfg.reveal_time*(FS.state.difficulty==='doom'?.72:1);
      e.facing=Math.atan2(dy,dx);
      toast('STALKER // SEÑAL DE ATAQUE · MUÉVETE');
      sound('bad');
      FS.worldDirty=true;
      return;
    }
  } else if (e.last_known && e.search_time>0) {
    e.search_time=Math.max(0,e.search_time-dt);
    e.ai_state='searching';
  } else {
    e.ai_state='idle';
    e.last_known=null;
    return;
  }

  const t=e.last_known, tx=t.x-e.x, ty=t.y-e.y, td=Math.hypot(tx,ty);
  if (td>.25) {
    // A lateral bias makes the silhouette move around cover instead of beelining every time.
    const side=e.id.length%2?1:-1;
    const v=cfg.speed*FS.config.difficulty.speed*dt;
    e.facing=Math.atan2(ty,tx);
    const vx=(tx/td*.82 - ty/td*.28*side)*v;
    const vy=(ty/td*.82 + tx/td*.28*side)*v;
    if (move(e,vx,vy,cfg.radius)) move(e,tx/td*v,ty/td*v,cfg.radius);
  }
}

function updateK32(e, cfg, dt) {
  const p=FS.state.player, dx=p.x-e.x, dy=p.y-e.y, d=Math.hypot(dx,dy), max=cfg.hp;
  const sees=d<cfg.vision && clearLine(e.x,e.y,p.x,p.y);
  e.phase_time=Math.max(0,(e.phase_time||0)-dt);
  e.cooldown=Math.max(0,(e.cooldown||0)-dt);

  const threshold=e.overload_cycles===0?.68:e.overload_cycles===1?.36:-1;
  if (e.boss_mode==='hunting' && threshold>0 && e.hp/max<=threshold) {
    e.overload_cycles+=1;
    e.boss_mode='overload';
    e.charge_state='idle';
    e.phase_time=cfg.overload_seconds*(FS.state.difficulty==='doom'?.78:1);
    e.cooldown=.15;
    e.ai_state='pursuing';
    bossAlert('K-32 — SOBRECARGA DIMENSIONAL','¡MANTÉN LA DISTANCIA!','warning',3000);
    toast('K-32 // SOBRECARGA · SOBREVIVE HASTA QUE SE AGOTE');
    sound('bad');
    FS.worldDirty=true;
    return;
  }

  if (e.boss_mode==='overload') {
    e.ai_state='pursuing';
    e.facing=Math.atan2(dy,dx);
    // K-32 becomes dangerous through movement and readable radial energy pulses.
    if (e.cooldown<=0) {
      const count=FS.state.difficulty==='doom'?10:8;
      for (let j=0;j<count;j++) {
        const a=(Math.PI*2*j/count)+(e.attack_index||0)*.13;
        FS.projectiles.push({x:e.x,y:e.y,vx:Math.cos(a)*cfg.energy_speed,vy:Math.sin(a)*cfg.energy_speed,life:3.2,k32:true});
      }
      e.attack_index=(e.attack_index||0)+1;
      e.cooldown=FS.state.difficulty==='doom'?.72:.95;
    }
    if (d>1.8) {
      const v=cfg.speed*1.45*FS.config.difficulty.speed*dt;
      move(e,dx/Math.max(d,.01)*v,dy/Math.max(d,.01)*v,cfg.radius);
    }
    if (!e.phase_time) {
      e.boss_mode='exhausted';
      e.phase_time=cfg.exhausted_seconds*(FS.state.difficulty==='doom'?.72:1);
      e.cooldown=0;
      e.ai_state='recovering';
      bossAlert('K-32 — INESTABLE','¡AHORA! · DAÑO AUMENTADO','success',2500);
      toast('K-32 // EXHAUSTED · VENTANA DE ATAQUE');
      sound('good');
      FS.worldDirty=true;
    }
    return;
  }

  if (e.boss_mode==='exhausted') {
    e.ai_state='recovering';
    if (!e.phase_time) {
      e.boss_mode='hunting';
      e.cooldown=.55;
      e.ai_state='pursuing';
      FS.worldDirty=true;
    }
    return;
  }

  if (e.charge_state==='charging') {
    e.ai_state='charging';
    const vx=Math.cos(e.facing)*cfg.ram_speed*dt,vy=Math.sin(e.facing)*cfg.ram_speed*dt;
    const blocked=move(e,vx,vy,cfg.radius);
    if (Math.hypot(e.x-p.x,e.y-p.y)<cfg.radius+.4) {
      hurt(FS.config.difficulty.damage*1.8);
      e.charge_state='idle';e.cooldown=1.05;
    } else if (blocked || !e.phase_time) {
      e.charge_state='idle';e.cooldown=.8;
    }
    return;
  }

  if (sees) {
    e.last_known={x:p.x,y:p.y};e.search_time=cfg.search_seconds;e.ai_state='pursuing';
  } else if (e.last_known && e.search_time>0) {
    e.search_time=Math.max(0,e.search_time-dt);e.ai_state='searching';
  } else {
    e.ai_state='idle';e.last_known=null;return;
  }

  if (sees && e.cooldown<=0) {
    e.attack_index=(e.attack_index||0)+1;
    e.facing=Math.atan2(dy,dx);
    if (e.attack_index%2===1 && d>2.2 && d<10) {
      e.charge_state='charging';
      e.phase_time=(FS.state.difficulty==='doom'?.62:.78);
      toast('K-32 // EMBESTIDA · SAL DE LA LÍNEA');
      sound('bad');
      FS.worldDirty=true;
      return;
    }
    const count=3;
    for (let j=0;j<count;j++) {
      const a=e.facing+(j-1)*.09;
      FS.projectiles.push({x:e.x,y:e.y,vx:Math.cos(a)*cfg.projectile_speed,vy:Math.sin(a)*cfg.projectile_speed,life:3.2,k32:true});
    }
    e.cooldown=FS.state.difficulty==='doom'?.72:1.05;
  }

  const t=e.last_known,tx=t.x-e.x,ty=t.y-e.y,td=Math.hypot(tx,ty);
  if (td>.35 && (!sees || d>cfg.range*2.4)) {
    e.facing=Math.atan2(ty,tx);
    const v=cfg.speed*FS.config.difficulty.speed*dt;
    if (move(e,tx/td*v,ty/td*v,cfg.radius)) move(e,-ty/td*v,tx/td*v,cfg.radius);
  } else if (sees && d<cfg.range && e.cooldown<=.05) {
    hurt(FS.config.difficulty.damage*1.35);
    e.cooldown=.9;
  }
}
