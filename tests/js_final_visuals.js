'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const c={window:{},Image:class{set src(v){}},console};vm.createContext(c);vm.runInContext(fs.readFileSync('ui/frontend/art.js','utf8'),c);const a=c.window.FSArt;
for(const w of ['sawed_off','assault','sniper','lmg','rocket']){
 const p=a.weaponProfiles[w];assert.equal(p.reference,w);assert.equal(a.weaponFrameKey(w,{}),w);assert.equal(a.weaponFrameKey(w,{shotFlash:.12}),w+'_fire');
 for(const ratio of [.95,.5,.05]){
  const expected=w==='sniper'?'sniper_reload':p.reloadStages[ratio>.82?0:ratio>.18?1:2];
  assert.equal(a.weaponFrameKey(w,{reloading:ratio*2,reloadDuration:2,shotFlash:.1,shotElapsed:.2}),expected);
 }
 assert(a.pickupProfiles[w].key===w+'_pickup');
}
assert.equal(a.weaponFrameKey('sniper',{shotElapsed:.2,shotDuration:1}), 'sniper_bolt_back');
assert.equal(a.weaponFrameKey('sniper',{shotElapsed:.4,shotDuration:1}), 'sniper_bolt_forward');
assert.equal(a.weaponFrameKey('sniper',{shotElapsed:.7,shotDuration:1}), 'sniper');
const f={state:{run_id:'r',weapon:'sniper',stats:{ammo_used:0},weapons:{sniper:{loaded:5},assault:{loaded:30}},player:{hp:100}},config:{weapons:{sniper:{cooldown:1},assault:{cooldown:.1}}},shotFlash:0,reloading:0};
let snap=JSON.stringify(f.state);a.weaponVisualState(f,0);assert.equal(JSON.stringify(f.state),snap);
f.state.stats.ammo_used++;f.state.weapons.sniper.loaded--;f.shotFlash=.12;
assert.equal(a.weaponVisualState(f,.1).shotElapsed,0);
f.state.weapon='assault';assert.equal(a.weaponVisualState(f,.11).visualShotFlash,0,'no borrowed sniper flash');
f.state.weapon='sniper';assert.equal(a.weaponVisualState(f,.12).shotElapsed,-1,'no stale bolt on switch');
f.state.stats.ammo_used++;f.state.weapons.sniper.loaded--;a.weaponVisualState(f,.2);f.reloading=1;assert.equal(a.weaponVisualState(f,.3).shotElapsed,-1);
f.reloading=0;f.state=JSON.parse(JSON.stringify(f.state));assert.equal(a.weaponVisualState(f,.4).shotElapsed,-1,'restore clears visuals');
for(const [state,key]of [[{},'idle'],[{movingUntil:11},'walk_1'],[{movingUntil:11,attackUntil:11},'attack'],[{hurtUntil:11,attackUntil:11},'hurt'],[{dead:true},'death']])assert.equal(a.enemyFrameKey('crucible',state,10),'boss_'+key);
assert.equal(a.enemyFrameKey('crucible',{movingUntil:11},10.2),'boss_walk_2');
assert(a.enemyEffect({type:'crucible',boss_mode:'pressure'},{}).color!==a.enemyEffect({type:'crucible',boss_mode:'exposed1'},{}).color);
console.log('Final weapons/boss: selectors, master anchors, reload priority, switches, restore, immutable gameplay OK');
