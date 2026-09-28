# Fraction Slayer — DDI Breach Pump Asset v1

- Replaced the legacy Pump Shotgun placeholder with the approved DDI Breach Pump industrial design.
- Added idle, fire, pump-back, pump-forward and reload RGBA frames.
- Added a client-only pump animation timer; no save format or campaign state changes.
- Shared `shotgun.png` reference scale/anchor across all animation frames.
- Prevented duplicate procedural muzzle flash when an authored fire frame exists.
- Kept all weapon gameplay values unchanged.
- Added automated regressions for asset dimensions and shotgun frame-state selection.
