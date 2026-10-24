# Lesson presentation

`math.html` remains the standalone offline game. The approved Blender puppy and
cat, arithmetic generators and learning levels are preserved.

The presentation changes follow the user's original video review:

| Reference observation | Adaptation in this game |
| --- | --- |
| Objects and answer choices appear in separate stages | Brief problem cue, cookies land, equation appears, then input unlocks |
| Attention is directed to changing quantities | Focused plate and ten-dot/one-bundle card during carrying and borrowing |
| An outline remains where an object was removed | Brief dashed outline at the source of a moving cookie |
| Green correct ring, white border, stars and rays | Layered ring with controlled rays, followed by staggered answer exit |
| Dimmed background and a filling arrow during explanation | Arrow first, then vertical calculation with one highlighted step at a time |
| Large pastel stars cover the scene | Overlapping gradient stars with depth and staggered timing |
| Reward ribbon appears after the clear screen | Brief gem reward reveal after the characters and stars appear |

The original video sampled for these decisions is the user's
`video_2026-10-23_23-37-40.mp4` (cookie explanation around 00:50–01:01 and clear
transition/reward around 02:04–02:11), plus the correct-feedback sequence in
`video_2026-10-23_22-50-10.mp4` around 07:26–07:29. This is an adaptation of observed
staging, not a claim to recover the original source code or exact animation curves.

## Extra learning controls

The explanation normally advances after eight seconds. **천천히 보기** stops
automatic advancement, **풀이 다시 보기** restarts the explanation, and **다음 문제**
advances immediately. Replaying a paused explanation stays paused. Borrowing
shows both revised digits (for example, 82 becomes 7 tens and 12 ones). An
operation that groups received subtraction cookies is labeled **10개 묶기**,
not **받아올림**.

All deferred lesson callbacks are scoped to a problem. Leaving during an exchange
removes the focus layer and prevents stale callbacks from modifying the next
screen. Progress reaches 100% on the final correct answer.

## Editing and embedding

- `experience.css`: focus, feedback, explanation, transition and reward styling.
- `experience.js`: helper functions embedded inside the existing game closure.
- Core game integration points are in `math.html` (`startProblem`, `bundle`,
  `unpack`, `onCorrect`, `showExplain`, `starWipe`, `finishRound`).
- Run `node tools/presentation/embed.mjs` after editing helpers.
- The embedder includes the repository's full Korean WOFF font for all new text.
  Arrow/star symbols fall back to system fonts because the source font has blank
  symbol glyphs. No runtime font download or Python dependency is required.

Browser checks cover carrying, borrowing, answer choices and keypad, pause/replay,
leaving during an exchange, a full six-question round, and the clear/reward scene.
Physical tablet performance has not been measured.
