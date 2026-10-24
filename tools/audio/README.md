# 짧고 부드러운 효과음

나무 타격음, 감쇠가 빠른 말렛 음, 저역 통과한 짧은 공기 소리로 15개 큐를 합성합니다.
외부 샘플·사운드폰트는 사용하지 않습니다. 이전 GM/금관악기 생성기는 보관용입니다.
클릭·착지의 작은 소리와 정답·완료의 멜로디는 서로 다른 최대 음량을 사용합니다.

```powershell
node tools/audio/generate.mjs tools/sfx work/audio-build
node tools/audio/embed.mjs
node tools/audio/check-player.cjs
```

Node.js와 FFmpeg가 필요합니다. `work/audio-build`에 WAV, 레벨 측정값,
종료된 인코딩 프로세스 기록을 저장합니다. MP3는 `tools/sfx/`에 보존됩니다.
`embed.mjs`는 MP3와 `player.js`를 `math.html`에 넣습니다.

플레이어는 중복 소리를 짧게 제한하고 최대 8개 음성을 관리합니다.
종료 시 노드를 해제하고, 오래된 음성은 감쇠 후 정지합니다. 마지막 믹스에는
컴프레서를 적용하고 높은 피치를 1.7배로 제한합니다.
설정에서 끄기 또는 작게(0.45)·보통(0.8)·크게(1.0)를 선택할 수 있습니다.
실제 체감 음량은 태블릿 스피커와 기기 볼륨에 따라 달라집니다.
