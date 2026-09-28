"use strict";
const fs = require("fs");
const vm = require("vm");
const assert = require("assert");

let damageTaken = 0;
global.FS = {
  state: { player: {x: 0, y: 0}, difficulty: "clasico" },
  config: { difficulty: {speed: 1, damage: 8} },
  projectiles: [],
  worldDirty: false,
};
global.clearLine = () => true;
global.move = (entity, vx, vy) => { entity.x += vx; entity.y += vy; return false; };
global.hurt = (damage) => { damageTaken += damage; };
global.sound = () => {};
global.toast = () => {};
global.bossAlert = () => {};

vm.runInThisContext(fs.readFileSync("ui/frontend/laboratory.js", "utf8"), {filename: "laboratory.js"});

const stalkerCfg = {
  vision: 15, search_seconds: 9, radius: .22, reveal_time: .85,
  lunge_time: .48, lunge_speed: 4.8, recovery: 1.15, stalk_delay: 1.35, speed: 1.28,
};
const stalker = {
  id: "stalker-smoke", x: 3, y: 0, stalker_mode: "stalk", phase_time: 0,
  cooldown: 0, ai_state: "idle", last_known: null, search_time: 0, facing: 0,
};
updateStalker(stalker, stalkerCfg, .016);
assert.strictEqual(stalker.stalker_mode, "reveal");
assert.strictEqual(damageTaken, 0, "Stalker must never damage while camouflaged/stalking");
stalker.phase_time = 0;
updateStalker(stalker, stalkerCfg, .016);
assert.strictEqual(stalker.stalker_mode, "lunge");
stalker.x = .2; stalker.y = 0; stalker.phase_time = .3;
updateStalker(stalker, stalkerCfg, .016);
assert.strictEqual(stalker.stalker_mode, "recovery");
assert(damageTaken > 0, "Lunge should be able to deal telegraphed damage");

const k32Cfg = {
  hp: 450, vision: 19, search_seconds: 14, radius: .5, speed: 1.14,
  overload_seconds: 5.8, exhausted_seconds: 3.2, energy_speed: 4.5,
  ram_speed: 5.1, range: 1.05, projectile_speed: 4.8,
};
const k32 = {
  id: "k32-smoke", x: 4, y: 0, hp: 305, boss_mode: "hunting", overload_cycles: 0,
  phase_time: 0, cooldown: 0, ai_state: "idle", charge_state: "idle",
  last_known: null, search_time: 0, attack_index: 0, facing: 0,
};
updateK32(k32, k32Cfg, .016);
assert.strictEqual(k32.boss_mode, "overload");
assert.strictEqual(k32.overload_cycles, 1);
k32.phase_time = 0; k32.cooldown = 0;
updateK32(k32, k32Cfg, .016);
assert.strictEqual(k32.boss_mode, "exhausted");
assert(FS.projectiles.length >= 8, "Overload should emit a readable radial projectile pulse");
k32.phase_time = 0;
updateK32(k32, k32Cfg, .016);
assert.strictEqual(k32.boss_mode, "hunting");

console.log("Laboratory JS smoke: OK");
