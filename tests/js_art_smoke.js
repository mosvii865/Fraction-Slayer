"use strict";
const fs = require("fs");
const vm = require("vm");

class FakeImage {
  constructor(){ this.complete=false; this.naturalWidth=0; this.naturalHeight=0; this.decoding=""; }
  set src(_v){}
}
const context = {window:{}, Image:FakeImage, console};
vm.createContext(context);
vm.runInContext(fs.readFileSync("ui/frontend/art.js", "utf8"), context);
const art = context.window.FSArt;
function assert(cond, msg){ if(!cond) throw new Error(msg); }
assert(art.weaponFrameKey("pistol", {reloading:0, shotFlash:0}) === "pistol", "idle frame");
assert(art.weaponFrameKey("pistol", {reloading:0, shotFlash:0.1}) === "pistol_fire", "fire frame");
assert(art.weaponFrameKey("pistol", {reloading:1.0, shotFlash:0}) === "pistol_reload", "reload frame");
assert(art.weaponFrameKey("pistol", {reloading:1.0, shotFlash:0.1}) === "pistol_reload", "reload priority");
assert(art.weaponFrameKey("shotgun", {reloading:0, shotFlash:0, pumpAnim:0}) === "shotgun", "shotgun idle frame");
assert(art.weaponFrameKey("shotgun", {reloading:0, shotFlash:0.1, pumpAnim:0.36}) === "shotgun_fire", "shotgun fire frame");
assert(art.weaponFrameKey("shotgun", {reloading:0, shotFlash:0, pumpAnim:0.30}) === "shotgun_pump_back", "shotgun pump back frame");
assert(art.weaponFrameKey("shotgun", {reloading:0, shotFlash:0, pumpAnim:0.10}) === "shotgun_pump_forward", "shotgun pump forward frame");
assert(art.weaponFrameKey("shotgun", {reloading:1.0, shotFlash:0.1, pumpAnim:0.30}) === "shotgun_reload", "shotgun reload priority");

assert(art.enemyFrameKey("worker", {}, 10) === "worker_idle", "worker idle frame");
assert(art.enemyFrameKey("worker", {movingUntil:11}, 10) === (Math.floor(10*6)%2 ? "worker_walk_2" : "worker_walk_1"), "worker walk frame");
assert(art.enemyFrameKey("worker", {attackUntil:11,movingUntil:11}, 10) === "worker_attack", "worker attack priority");
assert(art.enemyFrameKey("worker", {hurtUntil:11,attackUntil:11,movingUntil:11}, 10) === "worker_hurt", "worker hurt priority");
assert(art.enemyFrameKey("worker", {dead:true,hurtUntil:11}, 10) === "worker_death", "worker death priority");
console.log("art smoke: OK");
