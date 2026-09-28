'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
class Image {set src(v){this.url=v;}}
const c={window:{},Image,console};vm.createContext(c);vm.runInContext(fs.readFileSync('ui/frontend/art.js','utf8'),c);
const art=c.window.FSArt;
const choose=(remaining,extra={})=>art.weaponFrameKey('shotgun',{reloading:remaining,reloadDuration:2.4,shotFlash:.1,pumpAnim:.3,...extra});
assert.equal(choose(2.4),'shotgun_reload_start');
assert.equal(choose(2.25),'shotgun_reload_insert');
assert.equal(choose(2.1),'shotgun_reload_start');
assert.equal(choose(.08),'shotgun_reload_end');
assert.equal(choose(0,{shotFlash:0,pumpAnim:0}),'shotgun');
const before=JSON.stringify({reloading:1,reloadDuration:2.4});const obj=JSON.parse(before);art.weaponFrameKey('shotgun',obj);assert.equal(JSON.stringify(obj),before,'pure selector');
assert.equal(art.weaponFrameKey('pistol',{reloading:0,shotFlash:0}),'pistol');
assert.equal(choose(0,{shotFlash:0,pumpAnim:0}),'shotgun','switch back has no retained reload');
assert.equal(choose(0,{shotFlash:.1,pumpAnim:.36}),'shotgun_fire','validated firing lead-in');
assert.equal(choose(0,{shotFlash:0,pumpAnim:.3}),'shotgun_pump_back');
assert.equal(choose(0,{shotFlash:0,pumpAnim:.1}),'shotgun_pump_forward');
assert.equal(art.weaponProfiles.shotgun.reference,'shotgun');
assert.equal(art.pickupProfiles.shotgun.key,'shotgun_pickup');
for(const duration of [.15,.5,2.4,5]){
 assert.equal(art.weaponFrameKey('shotgun',{reloading:duration,reloadDuration:duration}),'shotgun_reload_start');
 assert.equal(art.weaponFrameKey('shotgun',{reloading:duration*.5,reloadDuration:duration}).startsWith('shotgun_reload_'),true);
 assert.equal(art.weaponFrameKey('shotgun',{reloading:Math.min(.01,duration*.01),reloadDuration:duration}),'shotgun_reload_end');
}
console.log('shotgun polish visual contract: OK');
