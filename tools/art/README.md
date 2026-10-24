# 부드러운 2.5D 베이커리

승인된 토리의 `../puppy/source.blend` 조명과 색 관리를 사용해 쿠키 5종,
쿠키 10개 탑 2종, 분리되는 파란 띠, 민트·라벤더 도자기 접시, 배경 2종을 렌더링합니다.
강아지·고양이 애니메이션은 기존 원본을 그대로 사용합니다.

재질 색을 선명하게 보이도록 황금빛 쿠키, 진한 토핑, 민트·라벤더 접시와
하늘색 창문을 사용합니다. 넓은 조명은 유지하고 환경광을 0.35로 낮추며,
AgX Medium High Contrast와 노출 -0.15로 부드러운 명암 안에서 색을 살립니다.
시작·지도 배경의 흰색 덮개도 낮춰 렌더링한 색이 충분히 보이게 합니다.

```powershell
blender --background --python tools/art/render_assets.py -- --output-dir work/bakery-render
node tools/art/package.mjs work/bakery-render
node tools/art/embed.mjs
```

Blender 5.2/Cycles, Node.js, FFmpeg가 필요합니다. 렌더 스크립트의 프로세스 기록은 Windows 기준입니다.
출력의 `bakery-room.blend`에는 수정 가능한 전체 모델이 보존됩니다.
이번에 생성한 모델도 `source.blend`에 함께 보관했습니다.
PNG에서 WebP로 변환한 원본은 `assets/`, 화면 배치와 색상은 `style.css`에 있습니다.
쿠키는 192×144, 탑·띠는 96×320, 접시는 640×320, 배경은 1280×500/720입니다.

`embed.mjs`는 12개 이미지를 HTML 안에 넣으므로 실행 중 외부 요청이 없습니다.
쿠키 이동·10개 묶기·띠 풀기에서 기존 DOM과 애니메이션을 재사용합니다.
띠는 별도 레이어라서 받아내림 때 쿠키 탑과 분리되어 사라집니다.
