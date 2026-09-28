# DDI Breach Pump — Implementation Pack v1

## Scope
This pass replaces only the Pump Shotgun viewmodel presentation. Gameplay values, damage, cooldown, ammo, M.A.D. upgrades, campaign persistence and controls remain unchanged.

## Production assets
All authored frames are 160×120 RGBA PNGs with a shared design canvas:

- `shotgun.png` — idle/reference frame
- `shotgun_fire.png` — muzzle flash + recoil pose
- `shotgun_pump_back.png` — mechanical action rearward
- `shotgun_pump_forward.png` — mechanical action returning forward
- `shotgun_reload.png` — reload pose

`shotgun.png` is the reference frame for scale and anchoring. Animation frames are never independently rescaled from their own alpha bounding boxes.

## Runtime state
The viewmodel adds one client-only variable: `FS.pumpAnim`.

- starts at `0.36s` after a Pump Shotgun shot;
- counts down in realtime;
- is never serialized to campaign saves;
- is reset on weapon changes, reload and level start.

Frame order during a normal shot:

`idle → fire → pump_back → pump_forward → idle`

Reload overrides the cycle. The fire frame is displayed while `shotFlash > 0`; the pump cycle continues after the flash expires. This preserves a visible firing frame while keeping the mechanical cycle independent from gameplay authority.

## Authority boundary
The visual animation does **not** decide when the weapon can fire. Existing weapon cooldown remains gameplay authority. The pump timer is presentation-only.

## Fallback
If a raster frame fails to load, the original procedural weapon renderer remains available. Missing art must never cause an engine failure.

## Physical validation checklist
Test in Workshop on PC and mobile:

1. Idle is stable and bottom-anchored.
2. Fire frame is visible exactly once per shot.
3. Pump back is clearly readable.
4. Pump forward returns smoothly toward idle.
5. Reload frame appears without a scale jump.
6. Rapid Pistol ↔ Pump switching does not leave a stale pump pose.
7. Ammo, reload, cooldown and weapon switching behave exactly as before.
8. The weapon does not obscure mobile controls or the central combat view.
