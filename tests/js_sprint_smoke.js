'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const c={window:{},Image:class{set src(v){}},console};vm.createContext(c);vm.runInContext(fs.readFileSync('ui/frontend/art.js','utf8'),c);const a=c.window.FSArt;
for(const type of a.sprintTypes){
 const profile=a.enemyProfiles[type];
 assert.equal(a.enemyFrameKey(type,{},10),profile.idle);
 assert.equal(a.enemyFrameKey(type,{movingUntil:11},10),profile.walk[0]);
 assert.equal(a.enemyFrameKey(type,{movingUntil:11},10.2),profile.walk[1]);
 assert.equal(a.enemyFrameKey(type,{attackUntil:11,movingUntil:11},10),profile.attack);
 assert.equal(a.enemyFrameKey(type,{hurtUntil:11,attackUntil:11},10),profile.hurt);
 assert.equal(a.enemyFrameKey(type,{dead:true,hurtUntil:11},10),profile.death);
 const f={enemyVisuals:{},state:{immutable:true}},e={id:type,type,active:true,hp:100,x:3,y:3,cooldown:0};
 const before=JSON.stringify(e);a.observeEnemy(f,e,10);assert.equal(JSON.stringify(e),before);
 e.x+=.1;a.observeEnemy(f,e,10.1);assert(f.enemyVisuals[type].movingUntil>10.1);
 e.cooldown=2;a.observeEnemy(f,e,10.2);assert(f.enemyVisuals[type].attackUntil>10.2);
 e.hp=80;a.observeEnemy(f,e,10.3);assert(f.enemyVisuals[type].hurtUntil>10.3);
 e.hp=0;a.observeEnemy(f,e,10.4);const death=f.enemyVisuals[type].deadUntil;assert(death>10.4);
 a.observeEnemy(f,e,13);assert.equal(f.enemyVisuals[type].deadUntil,death,'no immortal corpse');
 assert.deepEqual(f.state,{immutable:true});
 const dormant={id:'sleep',type,active:false,hp:0};a.observeEnemy(f,dormant,14);assert(!f.enemyVisuals.sleep);
}
assert.equal(a.enemyEffect({type:'stalker',stalker_mode:'stalk'},{}).alpha,.48);
assert(a.enemyEffect({type:'foreman',shielded:true},{}).color);
assert(a.enemyEffect({type:'loader',x:1,y:1,facing:0,stun_time:1},{x:0,y:1}).color);
assert(a.enemyEffect({type:'k32',boss_mode:'exhausted'},{}).color);
console.log('Sprint: 8 families, 48 states, observer immutability, telegraphs OK');
