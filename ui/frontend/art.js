"use strict";
// Visual Upgrade Pass 1A — optional raster art with zero-failure fallbacks.
// Every renderer call can continue with procedural art while PNG assets load or if one is missing.
window.FSArt = (() => {
  const manifest = {
    sprites: ["boss_idle","boss_walk_1","boss_walk_2","boss_attack","boss_hurt","boss_death",
      "sentinel_idle","sentinel_walk_1","sentinel_walk_2","sentinel_attack","sentinel_hurt","sentinel_death","gunner_idle","gunner_walk_1","gunner_walk_2","gunner_attack","gunner_hurt","gunner_death","stalker_idle","stalker_walk_1","stalker_walk_2","stalker_attack","stalker_hurt","stalker_death","specimen_k32_idle","specimen_k32_walk_1","specimen_k32_walk_2","specimen_k32_attack","specimen_k32_hurt","specimen_k32_death","furnace_hound_idle","furnace_hound_walk_1","furnace_hound_walk_2","furnace_hound_attack","furnace_hound_hurt","furnace_hound_death","forge_brute_idle","forge_brute_walk_1","forge_brute_walk_2","forge_brute_attack","forge_brute_hurt","forge_brute_death","loader_idle","loader_walk_1","loader_walk_2","loader_attack","loader_hurt","loader_death","foreman_mk2_idle","foreman_mk2_walk_1","foreman_mk2_walk_2","foreman_mk2_attack","foreman_mk2_hurt","foreman_mk2_death",
      "worker","worker_idle","worker_walk_1","worker_walk_2","worker_attack","worker_hurt","worker_death",
      "crawler","crawler_idle","crawler_walk_1","crawler_walk_2","crawler_attack","crawler_hurt","crawler_death","rivet","rivet_idle","rivet_walk_1","rivet_walk_2","rivet_attack","rivet_hurt","rivet_death","loader","loader_warning","loader_stunned","loader_rear",
      "terminal","mad","install","exit"
    ],
    weapons: ["sawed_off","sawed_off_fire","sawed_off_break_open","sawed_off_reload_insert","sawed_off_close","assault","assault_fire","assault_reload_start","assault_reload_swap","assault_reload_end","sniper","sniper_fire","sniper_bolt_back","sniper_bolt_forward","sniper_reload","lmg","lmg_fire","lmg_reload_start","lmg_reload_box","lmg_reload_end","rocket","rocket_fire","rocket_reload_open","rocket_reload_insert","rocket_reload_close","pistol","pistol_fire","pistol_reload","shotgun","shotgun_fire","shotgun_pump_back","shotgun_pump_forward","shotgun_reload","shotgun_reload_start","shotgun_reload_insert","shotgun_reload_end"],
    pickups: ["sawed_off_pickup","assault_pickup","sniper_pickup","lmg_pickup","rocket_pickup","shotgun_pickup"],
    textures: ["workshop_wall","workshop_panel","workshop_door","workshop_floor","workshop_ceiling"],
    props: [
      "crate","barrel","tool_chest","locker","extinguisher","electrical_cabinet","pipe_cluster",
      "pallet","workbench","sign_qc","sign_tools","sign_assembly","sign_power","sign_exit","sign_generator"
    ]
  };
  const images = {sprites:{},weapons:{},textures:{},props:{},pickups:{}};
  const failed = new Set();
  let loaded = 0;
  let total = 0;

  function load(kind, key) {
    total += 1;
    const img = new Image();
    img.decoding = "async";
    img.onload = () => { loaded += 1; };
    img.onerror = () => { failed.add(`${kind}:${key}`); };
    img.src = `art/${kind}/${key}.png`;
    images[kind][key] = img;
  }
  Object.entries(manifest).forEach(([kind, keys]) => keys.forEach(k => load(kind, k)));

  function get(kind, key) {
    const img = images[kind]?.[key];
    return img && img.complete && img.naturalWidth > 0 ? img : null;
  }
  function has(kind, key) { return !!get(kind, key); }
  function status() { return {loaded,total,failed:[...failed]}; }

  // Weapon viewmodel metadata.  A weapon family shares one source canvas and
  // one reference frame so animation states never change apparent scale or
  // anchor merely because their transparent alpha bounds differ.
  const weaponProfiles = {
    sawed_off: {"finalVisual":true,"idle": "sawed_off", "fire": "sawed_off_fire", "reference": "sawed_off", "height": 0.28, "centerX": 0.54, "reload": "sawed_off_reload_insert", "reloadStages": ["sawed_off_break_open", "sawed_off_reload_insert", "sawed_off_close"]},
    assault: {"finalVisual":true,"idle": "assault", "fire": "assault_fire", "reference": "assault", "height": 0.28, "centerX": 0.54, "reload": "assault_reload_swap", "reloadStages": ["assault_reload_start", "assault_reload_swap", "assault_reload_end"]},
    sniper: {"finalVisual":true,"idle": "sniper", "fire": "sniper_fire", "reference": "sniper", "height": 0.28, "centerX": 0.54, "reload": "sniper_reload", "boltBack": "sniper_bolt_back", "boltForward": "sniper_bolt_forward"},
    lmg: {"finalVisual":true,"idle": "lmg", "fire": "lmg_fire", "reference": "lmg", "height": 0.29, "centerX": 0.54, "reload": "lmg_reload_box", "reloadStages": ["lmg_reload_start", "lmg_reload_box", "lmg_reload_end"]},
    rocket: {"finalVisual":true,"idle": "rocket", "fire": "rocket_fire", "reference": "rocket", "height": 0.29, "centerX": 0.54, "reload": "rocket_reload_insert", "reloadStages": ["rocket_reload_open", "rocket_reload_insert", "rocket_reload_close"]},

    pistol: {
      idle: "pistol",
      fire: "pistol_fire",
      reload: "pistol_reload",
      reference: "pistol",
      height: 0.215,
      centerX: 0.52
    },
    shotgun: {
      idle: "shotgun",
      fire: "shotgun_fire",
      pumpBack: "shotgun_pump_back",
      pumpForward: "shotgun_pump_forward",
      reload: "shotgun_reload", // fallback for callers without duration metadata
      reloadStart: "shotgun_reload_start",
      reloadInsert: "shotgun_reload_insert",
      reloadEnd: "shotgun_reload_end",
      reference: "shotgun",
      height: 0.285,
      centerX: 0.51,
      pumpSplit: 0.18
    }
  };

  // Pure presentation: derived from the existing reload countdown. No mutable
  // animation state, ammo writes or save fields; interruption clears itself.
  function reloadFrameKey(profile, remaining, duration) {
    if (!(duration > 0) || !Number.isFinite(duration)) return profile.reload;
    const elapsed=Math.max(0,duration-remaining);
    const bookend=Math.min(.1,duration*.2);
    if (remaining<=bookend) return profile.reloadEnd;
    if (elapsed<bookend) return profile.reloadStart;
    // A short withdrawal/reach between insertions keeps a long real reload alive.
    return ((elapsed-bookend)%.28)<.16 ? profile.reloadInsert : profile.reloadStart;
  }

  function weaponFrameKey(weapon, state={}) {
    const profile = weaponProfiles[weapon];
    if (!profile) return weapon;
    if ((state.reloading || 0) > 0 && profile.reload) {
      if(profile.reloadStages){
        const duration=state.reloadDuration;
        const progress=duration>0 ? Math.max(0,Math.min(1,1-state.reloading/duration)) : .5;
        return profile.reloadStages[progress<.18?0:progress<.82?1:2];
      }
      return profile.reloadStart ? reloadFrameKey(profile,state.reloading,state.reloadDuration) : profile.reload;
    }
    // Fire is shown before the mechanical pump cycle; pumpAnim starts on the
    // same shot and continues after shotFlash has expired.
    const flash=profile.finalVisual ? (state.visualShotFlash ?? state.shotFlash) : state.shotFlash;
    if ((flash || 0) > 0 && profile.fire) return profile.fire;
    if ((state.pumpAnim || 0) > 0 && profile.pumpBack && profile.pumpForward) {
      return state.pumpAnim > (profile.pumpSplit || 0.18)
        ? profile.pumpBack
        : profile.pumpForward;
    }
    if(profile.boltBack && state.shotElapsed>=0){
      const duration=Math.max(.36,state.shotDuration||1);
      if(state.shotElapsed<duration*.28)return profile.boltBack;
      if(state.shotElapsed<duration*.52)return profile.boltForward;
    }
    return profile.idle || weapon;
  }

  function weaponVisualState(fs,t){
    const s=fs.state;let v=fs.finalWeaponVisual;
    if(!v || v.state!==s){
      v=fs.finalWeaponVisual={state:s,weapon:s.weapon,used:s.stats.ammo_used,loaded:{},shotAt:null};
    }
    if(v.weapon!==s.weapon){v.weapon=s.weapon;v.shotAt=null;}
    if(s.stats.ammo_used>v.used && Number.isFinite(v.loaded[s.weapon]) && s.weapons[s.weapon].loaded<v.loaded[s.weapon])v.shotAt=t;
    v.used=s.stats.ammo_used;
    for(const [key,w] of Object.entries(s.weapons))v.loaded[key]=w.loaded;
    if(fs.reloading>0 || s.player.hp<=0)v.shotAt=null;
    return {shotElapsed:v.shotAt===null?-1:Math.max(0,t-v.shotAt),shotDuration:fs.config.weapons[s.weapon]?.cooldown,visualShotFlash:v.shotAt===null?0:fs.shotFlash};
  }

  // Enemy sprite profiles follow the same stability rule as weapon viewmodels:
  // one authored canvas/anchor for every animation state. The renderer chooses
  // a frame, but never rescales individual poses from their alpha bounds.
  const enemyProfiles = {
    crucible:{idle:"boss_idle",walk:["boss_walk_1","boss_walk_2"],attack:"boss_attack",hurt:"boss_hurt",death:"boss_death",reference:"boss_idle"},
    sentinel: {idle:"sentinel_idle",walk:["sentinel_walk_1","sentinel_walk_2"],attack:"sentinel_attack",hurt:"sentinel_hurt",death:"sentinel_death",reference:"sentinel_idle"},
    gunner: {idle:"gunner_idle",walk:["gunner_walk_1","gunner_walk_2"],attack:"gunner_attack",hurt:"gunner_hurt",death:"gunner_death",reference:"gunner_idle"},
    stalker: {idle:"stalker_idle",walk:["stalker_walk_1","stalker_walk_2"],attack:"stalker_attack",hurt:"stalker_hurt",death:"stalker_death",reference:"stalker_idle"},
    k32: {idle:"specimen_k32_idle",walk:["specimen_k32_walk_1","specimen_k32_walk_2"],attack:"specimen_k32_attack",hurt:"specimen_k32_hurt",death:"specimen_k32_death",reference:"specimen_k32_idle"},
    furnace_hound: {idle:"furnace_hound_idle",walk:["furnace_hound_walk_1","furnace_hound_walk_2"],attack:"furnace_hound_attack",hurt:"furnace_hound_hurt",death:"furnace_hound_death",reference:"furnace_hound_idle"},
    forge_brute: {idle:"forge_brute_idle",walk:["forge_brute_walk_1","forge_brute_walk_2"],attack:"forge_brute_attack",hurt:"forge_brute_hurt",death:"forge_brute_death",reference:"forge_brute_idle"},
    loader: {idle:"loader_idle",walk:["loader_walk_1","loader_walk_2"],attack:"loader_attack",hurt:"loader_hurt",death:"loader_death",reference:"loader_idle"},
    foreman: {idle:"foreman_mk2_idle",walk:["foreman_mk2_walk_1","foreman_mk2_walk_2"],attack:"foreman_mk2_attack",hurt:"foreman_mk2_hurt",death:"foreman_mk2_death",reference:"foreman_mk2_idle"},

    rivet: {
      idle: "rivet_idle", walk: ["rivet_walk_1", "rivet_walk_2"],
      attack: "rivet_attack", hurt: "rivet_hurt", death: "rivet_death",
      reference: "rivet_idle"
    },
    crawler: {
      idle: "crawler_idle", walk: ["crawler_walk_1", "crawler_walk_2"],
      attack: "crawler_attack", hurt: "crawler_hurt", death: "crawler_death",
      reference: "crawler_idle", worldHeight: .68
    },
    worker: {
      idle: "worker_idle",
      walk: ["worker_walk_1", "worker_walk_2"],
      attack: "worker_attack",
      hurt: "worker_hurt",
      death: "worker_death",
      reference: "worker_idle"
    }
  };

  function enemyFrameKey(type, state={}, time=0) {
    const profile = enemyProfiles[type];
    if (!profile) return type;
    if (state.dead && profile.death) return profile.death;
    if ((state.hurtUntil || 0) > time && profile.hurt) return profile.hurt;
    if ((state.attackUntil || 0) > time && profile.attack) return profile.attack;
    if ((state.movingUntil || 0) > time && profile.walk?.length) {
      return profile.walk[Math.floor(time * 6) % profile.walk.length];
    }
    return profile.idle || type;
  }


  // Render-only observer: never mutates authoritative enemies, timers, ammo or save.
  const sprintTypes = new Set(['crucible','sentinel','gunner','stalker','k32','furnace_hound','forge_brute','loader','foreman']);
  function observeEnemy(fs,e,t) {
    if (!sprintTypes.has(e.type) || !e.active) return;
    fs.enemyVisuals ||= {};
    let v=fs.enemyVisuals[e.id];
    if (!v) v=fs.enemyVisuals[e.id]={id:e.id,type:e.type,lastX:e.x,lastY:e.y,lastHP:e.hp,lastCooldown:e.cooldown||0,movingUntil:0,attackUntil:0,hurtUntil:0,deadUntil:0};
    if (e.hp<v.lastHP) {
      v.hurtUntil=t+.18;
      if(e.hp<=0){v.deadUntil=t+1.15;v.deadX=e.x;v.deadY=e.y;}
    }
    if(e.hp>0){
      if(Math.hypot(e.x-v.lastX,e.y-v.lastY)>.002)v.movingUntil=t+.16;
      if((e.cooldown||0)>v.lastCooldown+.05 || ['charging','slamming','ramming'].includes(e.charge_state) || ['ramming','slamming'].includes(e.boss_mode) || e.stalker_mode==='lunge' || e.hound_mode==='leap')v.attackUntil=t+.24;
    }
    v.lastX=e.x;v.lastY=e.y;v.lastHP=e.hp;v.lastCooldown=e.cooldown||0;
  }
  function enemyEffect(e,player) {
    if(e._visualDead)return {alpha:1,color:null};
    if(e.type==='stalker')return {alpha:e.stalker_mode==='stalk'?.48:1,color:e.stalker_mode==='reveal'?'#ff765e':null};
    if(e.type==='loader'){
      const a=Math.atan2(player.y-e.y,player.x-e.x)-(e.facing||0);
      return {alpha:1,color:e.stun_time>0?'#76edc6':['preparing','slamming'].includes(e.charge_state)?'#ff7150':Math.abs(Math.atan2(Math.sin(a),Math.cos(a)))>Math.PI-1?'#76edc6':null};
    }
    if(e.type==='crucible')return {alpha:1,color:['pressure','meltdown'].includes(e.boss_mode)?'#ff704a':'#76edc6'};
    if(e.type==='foreman')return {alpha:1,color:e.shielded?'#76dced':null};
    if(e.type==='k32')return {alpha:1,color:e.boss_mode==='overload'?'#ff567d':e.boss_mode==='exhausted'?'#76edc6':null};
    if(e.type==='furnace_hound')return {alpha:1,color:e.hound_mode==='heat'?'#ff884c':null};
    if(e.type==='forge_brute')return {alpha:1,color:e.charge_state==='slamming'?'#ff884c':null};
    return {alpha:1,color:null};
  }

  const pickupProfiles={sawed_off:{"key": "sawed_off_pickup", "worldHeight": 0.18, "bounds": [18, 6, 30, 33]},assault:{"key": "assault_pickup", "worldHeight": 0.18, "bounds": [14, 10, 34, 29]},sniper:{"key": "sniper_pickup", "worldHeight": 0.18, "bounds": [15, 10, 34, 28]},lmg:{"key": "lmg_pickup", "worldHeight": 0.22, "bounds": [15, 6, 34, 33]},rocket:{"key": "rocket_pickup", "worldHeight": 0.22, "bounds": [14, 11, 35, 23]},shotgun:{key:"shotgun_pickup",worldHeight:.16,bounds:[2,15,60,17]}};
  return {weaponVisualState,sprintTypes,observeEnemy,enemyEffect,get,has,status,manifest,weaponProfiles,weaponFrameKey,enemyProfiles,enemyFrameKey,pickupProfiles};
})();
