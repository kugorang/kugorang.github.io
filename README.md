# 김현우 · Hyeonwoo Kim

개인 포트폴리오: <https://hw.kugora.ng/>

| 페이지 | 역할 |
| --- | --- |
| `/` | 프로필, 대표 작업, 소개, 연락처 |
| `/apps/` | 앱 목록과 검색·분야 필터 |
| `/games/` | 게임 목록과 검색·분야 필터 |

## 작품 추가 및 수정

1. `data/projects.json`에 작품 정보를 추가하거나 수정합니다. 배열 순서대로 표시됩니다.
2. `category`는 `apps` 또는 `games`, `featured: true`는 메인 대표 작업입니다.
3. `url`은 해당 작품의 공식 상세 페이지, `tags`의 첫 항목은 분야 필터입니다.
4. `visual`은 기존 일러스트 키를 선택하거나 생략합니다. 생략하면 이름의 첫 글자로 표지를 표시합니다.
5. 아래 명령으로 페이지를 생성하고 확인한 뒤 생성 파일도 함께 커밋합니다.

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 -m http.server 4173 --bind 127.0.0.1
```

<http://127.0.0.1:4173/>에서 메인·앱·게임 페이지의 화면, 검색, 필터와 상세 링크를 확인합니다.
Python 3 표준 라이브러리만 사용합니다. 별도 패키지 설치나 서버는 필요 없습니다.
목록·개수·필터·대표 작업은 같은 카탈로그에서 생성됩니다. HTML에 전체 목록을 포함하므로
JavaScript를 사용할 수 없어도 소개와 링크를 볼 수 있습니다.

## 디자인과 배포

- `scripts/build.py`: 공유 HTML 구성, 소개 문구, 메타데이터와 사이트맵
- `assets/site.css`: 반응형 디자인과 작품 표지
- `assets/catalog.js`: 검색, 분야 필터, 결과 개수와 초기화
- `assets/profile.png`: 사용자가 제공한 프로필 이미지 원본
- `CNAME`: `hw.kugora.ng`

GitHub Pages가 `main`의 루트를 게시합니다. `CNAME`에 지정한 주소를 저장소 Pages 설정에
등록하고, DNS에서 `hw` CNAME을 `kugorang.github.io.`로 연결합니다.
기존 <https://kugorang.github.io/> 주소는 새 주소로 이동합니다.
도메인 변경 시 `scripts/build.py`의 `SITE`도 수정하고 다시 생성합니다.

## 상세 페이지 관리 원칙

이 저장소에는 작품 요약과 링크만 둡니다. 상세 소개·지원·개인정보 페이지는 각 작품의 게시 원본 저장소에서 관리합니다.

| 작품 | 관리 저장소 | 상세 페이지 |
| --- | --- | --- |
| 필데이 | `kugorang/Fillday` | <https://fillday.kugora.ng/> |
| 달빛 고물상 | `kugorang/moonjunk-pages`의 `main` 루트 | <https://moonjunk.kugora.ng/> |
| Facet | `kugorang/Sudoku`의 `gh-pages` | <https://facet.kugora.ng/> |
| 오선로 | `kugorang/oseonro`의 `gh-pages` | <https://hw.kugora.ng/oseonro/> |

Facet의 공식 공개 주소는 `facet.kugora.ng`이며 작품 카드도 직접 연결합니다.
`/Facet/`는 기존 링크를 위한 이동 페이지입니다. 기존 `/Sudoku/`는 GitHub Pages가
공식 주소로 이동시킵니다. 저장소 이름을 신규 공개 링크에 사용하지 않습니다.
오선로는 기존 `hw.kugora.ng/oseonro/`에서 별도 저장소가 게시합니다.

달빛 고물상의 공개 소개·안내 문서·디자인·실제 플레이 캡처는 `kugorang/moonjunk-pages`에서
함께 관리하고 전체 사이트를 게시합니다. 안내 문구나 호스팅을 변경할 때도 스타일과 이미지가
포함된 전체 사이트를 유지하며, 해당 저장소의 README에 적힌 검증 절차를 따릅니다.

`app-ads.txt`는 광고 공급자 확인에 사용하므로 유지합니다. 앱 소스, 인증 정보, 비공개 개발 문서는 게시하지 않습니다.

미출시 작품은 브랜드, 짧은 소개와 개발 중 표시를 중심으로 소개합니다. 테스트 빌드 번호, 구매·광고 검증 상태와 내부 운영 계획은 공개 소개에 넣지 않습니다.

## 언어와 공개 상태

웹은 Fillday의 실제 선택 언어 `ko/en/ja`와 Facet의 실제 선택 언어
`ko-KR/en-US/ja-JP/de-DE/fr-FR/es/pt-BR`의 합집합을 지원합니다.
Facet의 스토어 메타에서 스페인어 지역을 나누더라도 웹의 `es`는 공통 스페인어입니다.
언어 이름과 URL 코드는 `data/languages.json`, 문구는 `data/locales/*.json`에 있습니다.
번역 키·자리표시자가 누락되거나 개발 중 작업에 설치 링크를 넣으면 빌드가 실패합니다.
작품의 한국어 `headline`·`description`을 수정할 때 한국어 locale과 나머지 번역도 함께 수정합니다.
이름·기존 영문 브랜드·지원 이메일·도메인·저작권 표기는 번역하지 않습니다.

- 직접 링크: `/ko/`, `/en/`, `/ja/`, `/de/`, `/fr/`, `/es/`, `/pt-BR/`.
- 각 언어 아래 `/apps/`, `/games/`, `/404.html`, 기존 `/Facet/` 이동 페이지가 있습니다.
- 기존 `/`, `/apps/`, `/games/`는 보존됩니다. JavaScript를 사용하면 URL의 `lang` 파라미터,
  저장된 선택, 브라우저의 첫 지원 언어, 영어 순서로 언어 URL을 선택합니다.
- 직접 언어 URL은 브라우저·저장된 설정보다 우선합니다. 언어 메뉴는 현재 페이지·query·anchor를 유지합니다.
- JavaScript 없이도 언어별 내용과 언어 선택 링크를 사용할 수 있습니다.
- canonical은 각 언어 URL, hreflang은 모든 언어와 기존 URL의 `x-default`를 연결합니다.
- 언어 메뉴는 기본 HTML `details`로 구현했으며 Enter/Space/Tab과 Escape를 지원합니다.

`data/projects.json`의 `status`는 `released` 또는 `development`입니다.
`stores`는 실제 공개된 작업에만 추가하며 공식 App Store·Google Play 주소만 허용합니다.
메인 대표 작업은 Fillday와 Facet입니다. Facet은 대표 작업이어도 개발 중 상태이며,
달빛 고물상과 오선로는 개발 중 목록에서 유지합니다. 확정되지 않은 출시일은 표시하지 않습니다.

## 검증

```sh
python3 -B scripts/build.py --check
python3 -B -m unittest discover -s tests -v
node --check assets/catalog.js
node --check assets/language.js
git diff --check
python3 -B tests/serve.py
```

`tests/serve.py`는 `http://127.0.0.1:4174/`에서 GitHub Pages의 사용자 정의 404도 재현합니다.
`tests/browser-qa.cjs`는 Playwright와 기존 Mac Chrome을 사용한 선택적 화면 검사입니다.
QA 출력은 `QA_OUTPUT_ROOT`, 별도 설치 Playwright는 `QA_PLAYWRIGHT_MODULE`로 지정합니다.
프로젝트 소스·앱 저장소에는 QA 패키지나 브라우저 프로필을 설치하지 않습니다.
Mac mini에서는 T7 APFS UUID를 먼저 검증하고 임시파일·스크린샷·증거를 전용 외장 경로에 둡니다.

게시 방법은 기존 `main` 루트의 GitHub Pages이며 도메인·계정·스택은 바꾸지 않습니다.
검토된 소스와 생성 HTML을 함께 반영해야 합니다. 이번 변경의 push와 공개 게시에는
이 작업에 대한 별도 승인이 필요합니다.
