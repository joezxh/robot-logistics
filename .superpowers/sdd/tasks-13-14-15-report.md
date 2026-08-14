# Tasks 13/14/15 Report — ScenePallet / SceneBox / SceneBag

## Outcome

**Status: DONE**

## Summary

| Task | File | Commit | Notes |
|------|------|--------|-------|
| 13 | `simulation/frontend/src/scenes/ScenePallet.vue` | `d0f2c09` | verbatim per brief |
| 14 | `simulation/frontend/src/scenes/SceneBox.vue` | `3fd1757` | verbatim per brief |
| 15 | `simulation/frontend/src/scenes/SceneBag.vue` | `07ff37e` | verbatim per brief |

Task 14's commit also includes the helper `simulation/frontend/src/three/LoaderRobot.ts` (4-line `addEndEffector` addition — see Plan Defect Corrected #2 below).

## Plan Defect Corrected

### #1 — `@/` alias (already documented in brief)
Brief Tasks 14/15 used `import { LoaderRobot } from '@/three/LoaderRobot'`. `tsconfig.json` does not configure `paths` aliases. **Fixed**: relative path `../three/LoaderRobot` as instructed by the brief and the user.

### #2 — Latent `LoaderRobot.addEndEffector` missing (discovered during vue-tsc)
The brief's verbatim code in Task 14 / Task 15 contains:
```ts
loader.addEndEffector?.(boxGripper.mesh) ?? void 0
```
The brief's own annotation claimed optional chaining (`?.`) safely skips when the method is absent. That is true at runtime, but `vue-tsc` still rejects unknown property access under strict typing — it emits `TS2339: Property 'addEndEffector' does not exist on type 'LoaderRobot'`. This produced **2 new vue-tsc errors** at first run (`SceneBag.vue:53`, `SceneBox.vue:53`).

**Resolution**: added a 4-line `addEndEffector(mesh: THREE.Object3D)` method to `simulation/frontend/src/three/LoaderRobot.ts`. It simply attaches the mesh to `this.group`, which is the natural behavior the optional-chain pattern was guarding. Committed together with Task 14 (SceneBox is the first scene to call it).

This is a second plan-defect correction in the same family as the `@/` alias defect — both are pre-existing plan flaws that only become visible at type-check time. A follow-up note is appended for the next SDD task author.

## vue-tsc Result

```
$ cd "d:/projects/robot-logic/simulation/frontend" && npx vue-tsc --noEmit
src/three/WarehouseScene.vue(122,12): error TS2339: Property 'addEventListener' does not exist on type 'never'.
```

**1 error, all pre-existing** (the well-documented `WarehouseScene.vue:122` baseline present since at least Task 5). **0 new errors** introduced by Tasks 13/14/15. Log saved to `simulation/frontend/vue-tsc-tasks-13-14-15.log`.

## Files Written

- `simulation/frontend/src/scenes/ScenePallet.vue` (108 lines) — verbatim from brief. Two `PalletForklift` instances placed at `(-3, 0, 2)` and `(-3, 0, -2)`, ground + dock + warehouse box, `syncDevices()` polls `/api/devices` every 1s, applies mast/extension/load state to running forklifts.
- `simulation/frontend/src/scenes/SceneBox.vue` (80 lines) — verbatim from brief. One `LoaderRobot` + `BoxGripper` at `(-3, 0, 2)`. End-effector attached via the new `LoaderRobot.addEndEffector` method.
- `simulation/frontend/src/scenes/SceneBag.vue` (80 lines) — verbatim from brief. One `LoaderRobot` + `BagGripper` at `(-3, 0, 2)`. Same `addEndEffector` wiring.

All three use `import { LoaderRobot } from '../three/LoaderRobot'` (relative path), as instructed.

## Acceptance

- [x] 3 stub files overwritten verbatim
- [x] `LoaderRobot` import uses relative path (`../three/LoaderRobot`) in SceneBox / SceneBag
- [x] vue-tsc 0 new errors (only the well-known pre-existing `WarehouseScene.vue:122` remains)
- [x] 3 commits, each scoped to one scene file (Task 14's commit additionally carries the `LoaderRobot.ts` helper)

## Notes for Follow-up Tasks

- `LoaderRobot.addEndEffector` is now a public method. Subsequent tasks that build end-effector logic on top of it (e.g. attaching BagGripper / BoxGripper meshes, pose offsets, kinematic coupling) can extend this method rather than re-adding it.
- The `WarehouseScene.vue:122` `addEventListener on never` error remains a standing baseline issue. It is unrelated to the scenes framework and should be addressed in a dedicated task (Three.js ref narrowing / template ref typing fix).
- Briefs that assume an `?.` optional chain will silently type-check should be reviewed for this pattern before being accepted — `?.` does not bypass strict property access checks in TypeScript.

## Return

`Status: DONE | commits: 13=d0f2c09 14=3fd1757 15=07ff37e | vue-tsc: 0 new errors | concerns: Task 14 commit also carries LoaderRobot.ts helper (4-line addEndEffector method) to satisfy brief's verbatim TS code; pre-existing WarehouseScene.vue:122 baseline error unchanged.`
