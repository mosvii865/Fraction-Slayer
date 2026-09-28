'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const c={window:{},Image:class{set src(v){}},console,performance:{now:()=>10000}};
vm.createContext(c);vm.runInContext(fs.readFileSync('ui/frontend/art.js','utf8'),c);
const art=c.window.FSArt;
for(const type of ['crawler','worker']) {
 assert.equal(art.enemyFrameKey(type,{},10),type+'_idle');
 assert.equal(art.enemyFrameKey(type,{movingUntil:11},10),type+'_walk_1');
 assert.equal(art.enemyFrameKey(type,{movingUntil:11},10.2),type+'_walk_2');
 assert.equal(art.enemyFrameKey(type,{movingUntil:11,attackUntil:11},10),type+'_attack');
 assert.equal(art.enemyFrameKey(type,{movingUntil:11,attackUntil:11,hurtUntil:11},10),type+'_hurt');
 assert.equal(art.enemyFrameKey(type,{dead:true,hurtUntil:11,attackUntil:11},10),type+'_death');
 assert.equal(art.enemyFrameKey(type,{movingUntil:9,attackUntil:9,hurtUntil:9},10),type+'_idle');
}
// Execute the existing visual-only helpers, not a duplicate selector implementation.
const source=fs.readFileSync('ui/frontend/realtime.js','utf8');
const start=source.indexOf('function enemyVisualState(');
const end=source.indexOf('\nfunction ',source.indexOf('function markEnemyVisualHit(')+10);
c.FS={enemyVisuals:{},state:{sentinel:'unchanged'}};
vm.runInContext(source.slice(start,end),c);
const e={id:'crawler-test',type:'crawler',x:1,y:1,hp:30};
c.updateEnemyVisualMotion(e,10);e.x+=.1;c.updateEnemyVisualMotion(e,10);
assert.equal(c.FS.enemyVisuals[e.id].movingUntil,10.16);
c.markEnemyVisualAttack(e,10);assert.equal(c.FS.enemyVisuals[e.id].attackUntil,10.24);
c.markEnemyVisualHit(e,true,10);assert.equal(c.FS.enemyVisuals[e.id].deadUntil,11.15);
assert.equal(e.hp,30);assert.deepEqual(c.FS.state,{sentinel:'unchanged'});
console.log('Crawler/Worker selectors + visual cues: OK');
