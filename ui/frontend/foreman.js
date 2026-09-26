"use strict";
// Foreman MK-II realtime behavior. Campaign/progression remains Python-owned.
function updateForeman(e, cfg, dt) {
  const p=FS.state.player, dx=p.x-e.x, dy=p.y-e.y, d=Math.hypot(dx,dy), max=cfg.hp;
  const sees=d<cfg.vision && clearLine(e.x,e.y,p.x,p.y);
  e.phase_time=Math.max(0,(e.phase_time||0)-dt);
  e.cooldown=Math.max(0,(e.cooldown||0)-dt);

  const threshold = e.shield_cycles===0 ? .67 : e.shield_cycles===1 ? .34 : -1;
  if (!e.shielded && threshold>0 && e.hp/max<=threshold) {
    e.shielded=true; e.shield_cycles+=1; e.boss_mode='protected';
    e.node_a_hp=cfg.node_hp; e.node_b_hp=cfg.node_hp; e.phase_time=.7;
    bossAlert('FOREMAN MK-II — ESCUDO ACTIVADO', '¡DESTRUYE LOS 2 NODOS DE ENERGÍA!', 'warning', 3200);
    toast('FOREMAN // ESCUDO ACTIVADO · DESTRUYE LOS NODOS');
    sound('bad'); FS.worldDirty=true; return;
  }
  if (e.shielded) {
    e.ai_state='pursuing'; e.boss_mode='protected';
    if (e.node_a_hp<=0 && e.node_b_hp<=0) {
      e.shielded=false; e.boss_mode='recovering'; e.phase_time=1.0;
      bossAlert('ESCUDO DESACTIVADO', '¡ATACA AL FOREMAN!', 'success', 2300);
      toast('FOREMAN // ESCUDO DESACTIVADO · VULNERABLE'); sound('good'); FS.worldDirty=true;
    }
    return;
  }
  if (e.boss_mode==='recovering') {
    e.ai_state='recovering';
    if (!e.phase_time) {e.boss_mode='offensive';e.cooldown=.45;}
    return;
  }
  if (e.boss_mode==='ramming') {
    e.ai_state='charging';
    const vx=Math.cos(e.facing)*cfg.ram_speed*dt,vy=Math.sin(e.facing)*cfg.ram_speed*dt;
    move(e,vx,vy,cfg.radius);
    if (Math.hypot(e.x-p.x,e.y-p.y)<cfg.radius+.38) {
      hurt(FS.config.difficulty.damage*1.75);e.boss_mode='recovering';e.phase_time=cfg.recovery;
    } else if (!e.phase_time) {e.boss_mode='recovering';e.phase_time=cfg.recovery;}
    return;
  }
  if (e.boss_mode==='slamming') {
    e.ai_state='slamming';
    if (!e.phase_time) {
      if (d<cfg.slam_radius && sees) hurt(FS.config.difficulty.damage*1.6);
      toast('FOREMAN // GOLPE DE ÁREA');sound('hurt');e.boss_mode='recovering';e.phase_time=cfg.recovery;
    }
    return;
  }

  if (sees) {e.last_known={x:p.x,y:p.y};e.search_time=cfg.search_seconds;e.ai_state='pursuing';}
  else if (e.last_known && e.search_time>0) {e.search_time=Math.max(0,e.search_time-dt);e.ai_state='searching';}
  else {e.ai_state='idle';e.last_known=null;return;}

  if (sees && e.cooldown<=0) {
    e.attack_index=(e.attack_index||0)+1;
    e.facing=Math.atan2(dy,dx);
    const mode=e.attack_index%4;
    if (mode===1 && d>2.2) {
      // Burst fire: three visible projectiles with light angular spread.
      for (const off of [-.055,0,.055]) {
        const a=e.facing+off;
        FS.projectiles.push({x:e.x,y:e.y,vx:Math.cos(a)*cfg.projectile_speed,vy:Math.sin(a)*cfg.projectile_speed,life:3});
      }
      e.cooldown=FS.state.difficulty==='doom'?.75:1.05;
      toast('FOREMAN // RÁFAGA');
    } else if (mode===2 && d>2.4 && d<9) {
      e.boss_mode='ramming';e.phase_time=cfg.ram_duration*(FS.state.difficulty==='doom'?.88:1);
      toast('FOREMAN // EMBESTIDA');sound('bad');FS.worldDirty=true;
    } else if (mode===3 && d<4) {
      e.boss_mode='slamming';e.phase_time=cfg.slam_prepare*(FS.state.difficulty==='doom'?.82:1);
      toast('FOREMAN // GOLPE DE ÁREA · RETROCEDE');sound('bad');FS.worldDirty=true;
    } else {
      // A compact single burst if geometry prevents the preferred attack.
      FS.projectiles.push({x:e.x,y:e.y,vx:(dx/Math.max(d,.01))*cfg.projectile_speed,vy:(dy/Math.max(d,.01))*cfg.projectile_speed,life:3});
      e.cooldown=.8;
    }
    if (e.boss_mode!=='offensive') return;
  }

  const t=e.last_known,tx=t.x-e.x,ty=t.y-e.y,td=Math.hypot(tx,ty);
  if (td>.3 && (!sees || d>cfg.range*.72)) {
    e.facing=Math.atan2(ty,tx);
    const v=cfg.speed*FS.config.difficulty.speed*dt;
    if (move(e,tx/td*v,ty/td*v,cfg.radius)) move(e,-ty/td*v,tx/td*v,cfg.radius);
  }
}
