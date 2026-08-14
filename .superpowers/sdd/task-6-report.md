# Task 6 Report — useSceneAPI composable

## Status
DONE

## Commit
`ed928da` — `feat(scenes): add useSceneAPI composable`

## Step 2 Output (`npx vue-tsc --noEmit`)

```
src/three/WarehouseScene.vue(122,12): error TS2339: Property 'addEventListener' does not exist on type 'never'.
```

Only the pre-existing `WarehouseScene.vue:122` error remains. **0 new errors** introduced by `useSceneAPI.ts`.

## Acceptance Checklist

- [x] `src/scenes/composables/useSceneAPI.ts` created
- [x] File verbatim — matches brief block-for-block
- [x] Exports `ScenePreset` / `SceneKPI` interfaces
- [x] Exports `useSceneAPI()` factory function
- [x] Returns 5 keys: `currentScene`, `list`, `load`, `getCurrent`, `getKPI`
- [x] `load` sets `currentScene.value = name` on success
- [x] `npx vue-tsc --noEmit` — 0 new errors (pre-existing WarehouseScene.vue:122 only)
- [x] Only `useSceneAPI.ts` committed (1 file changed, 48 insertions)

## Concerns

None. Type check clean for the new file; pre-existing error in WarehouseScene.vue is unrelated and out of scope.