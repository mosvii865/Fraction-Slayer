// Test-only accelerated walkthrough. Real collision, shots, cooldowns and RPCs.
// Grace is refreshed while routing; isolated attack tests below test actual damage.
window.walkTest = {
  path(tx,ty) {
    const p=FS.state.player,start=[Math.floor(p.x),Math.floor(p.y)],goal=[Math.floor(tx),Math.floor(ty)];
    const key=(x,y)=>x+','+y,q=[start],seen=new Map([[key(...start),null]]);
    for(let i=0;i<q.length;i++) {
      const [x,y]=q[i];if(x===goal[0]&&y===goal[1])break;
      for(const [a,b] of [[x+1,y],[x-1,y],[x,y+1],[x,y-1]]) {
        const k=key(a,b);if(!seen.has(k)&&!solid(a+.5,b+.5)){seen.set(k,[x,y]);q.push([a,b]);}
      }
    }
    if(!seen.has(key(...goal)))throw Error('Unreachable test destination '+goal);
    const path=[];let a=goal;while(a){path.unshift([a[0]+.5,a[1]+.5]);a=seen.get(key(...a));}
    // First recenter in the current tile to avoid clipping a doorway corner.
    path.push([tx,ty]);return path;
  },
  batch(target, groups=[], combat=false) {
    FS.playing=true;FS.lastSync=1e12;FS.checkpointAttempts=Object.fromEntries(FS.config.level.checkpoints.map(c=>[c.id,1e12]));
    let path=this.path(...target),i=0;
    try {
      for(let n=0;n<40;n++) {
        const p=FS.state.player;
        p.grace=2; // Fixture only: routing is not a difficulty/balance measurement.
        const enemies=FS.state.enemies.filter(e=>e.active&&e.hp>0&&(!groups.length||groups.includes(e.group)));
        const visible=enemies.filter(e=>clearLine(p.x,p.y,e.x,e.y)).sort((a,b)=>Math.hypot(a.x-p.x,a.y-p.y)-Math.hypot(b.x-p.x,b.y-p.y));
        const aim=visible[0];
        if(aim) {
          const d=Math.hypot(aim.x-p.x,aim.y-p.y);
          const shotgun=FS.state.weapons.shotgun;
          const chosen=shotgun && d<5.5 && shotgun.loaded+shotgun.reserve>0?'shotgun':'pistol';
          if(FS.state.weapon!==chosen)selectWeapon(chosen);
          p.angle=Math.atan2(aim.y-p.y,aim.x-p.x);
          if(d<FS.config.weapons[chosen].range)shoot();
        }
        while(i<path.length-1&&Math.hypot(path[i][0]-p.x,path[i][1]-p.y)<.12)i++;
        let dx=path[i][0]-p.x,dy=path[i][1]-p.y,d=Math.hypot(dx,dy);
        const nearEnemy=combat&&aim&&Math.hypot(aim.x-p.x,aim.y-p.y)<1.7;
        if(d>.08&&!nearEnemy) {
          const speed=Math.min(1,d/(3.7*.025));dx=dx/d*speed;dy=dy/d*speed;
          FS.move.x=-Math.sin(p.angle)*dx+Math.cos(p.angle)*dy;
          FS.move.y=-(Math.cos(p.angle)*dx+Math.sin(p.angle)*dy);
        } else FS.move={x:0,y:0};
        tick(.025,100); // production tick, with bridge/checkpoints tested separately
        if(!FS.playing) break;
      }
      Render.world(FS,FS.state.stats.seconds);
      return {p:clone(FS.state.player),ammo:clone(FS.state.weapons),kills:FS.state.stats.kills};
    } finally {FS.playing=false;releaseInput();}
  },
  loaderAttacks() {
    const saved=clone(FS.state), projectiles=FS.projectiles;
    const e=FS.state.enemies.find(e=>e.type==='loader'),cfg=FS.config.enemies.loader,p=FS.state.player;
    const reset=()=>{Object.assign(e,{x:28.5,y:25.5,hp:250,active:true,charge_state:'idle',ai_state:'idle',phase_time:0,stun_time:0,cooldown:0,attack_index:0,facing:0});Object.assign(p,{x:29.3,y:25.5,hp:100,armor:0,grace:0});FS.playing=true;};
    try {
      reset();updateLoader(e,cfg,.01);const melee=p.hp<100;
      reset();e.attack_index=1;updateLoader(e,cfg,.01);const slamTelegraph=e.charge_state==='slamming';updateLoader(e,cfg,1);const slam=p.hp<100;
      reset();p.x=32;updateLoader(e,cfg,.01);const prep=e.charge_state==='preparing';const direction=e.facing;p.y=22.5;updateLoader(e,cfg,1);const locked=e.facing===direction&&e.charge_state==='charging';
      for(let i=0;i<80&&e.stun_time===0;i++)updateLoader(e,cfg,.025);
      const wall=e.charge_blocked&&e.stun_time===1.75&&e.ai_state==='stunned';
      updateLoader(e,cfg,1.75);const recovery=e.charge_state==='recovering';
      reset();e.x=29.5;p.x=28.5;p.angle=0;e.facing=Math.PI;
      FS.state.weapon='pistol';FS.state.weapons.pistol.loaded=12;FS.cooldown=FS.reloading=0;shoot();const front=250-e.hp;
      e.hp=250;e.facing=0;FS.cooldown=0;shoot();const rear=250-e.hp;
      return {melee,slamTelegraph,slam,prep,locked,wall,recovery,front,rear};
    } finally {FS.state=saved;FS.projectiles=projectiles;FS.playing=false;FS.cooldown=FS.reloading=0;}
  }
};
