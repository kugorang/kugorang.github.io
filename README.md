# 김현우 · Hyeonwoo Kim

개인 포트폴리오: <https://hyeonwoo.kugora.ng/>

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
- `CNAME`: `hyeonwoo.kugora.ng`

GitHub Pages가 `main`의 루트를 게시합니다. `CNAME`에 지정한 주소를 저장소 Pages 설정에
등록하고, DNS에서 `hyeonwoo` CNAME을 `kugorang.github.io.`로 연결합니다.
기존 <https://kugorang.github.io/> 주소는 새 주소로 이동합니다.
도메인 변경 시 `scripts/build.py`의 `SITE`도 수정하고 다시 생성합니다.

## 상세 페이지 관리 원칙

이 저장소에는 작품 요약과 링크만 둡니다. 상세 소개·지원·개인정보 페이지는 각 작품 저장소에서 관리합니다.

| 작품 | 관리 저장소 | 상세 페이지 |
| --- | --- | --- |
| 필데이 | `kugorang/Fillday` | <https://fillday.kugora.ng/> |
| 달빛 고물상 | `kugorang/moonjunk-workshop`의 `site/` → `gh-pages` | <https://moonjunk.kugora.ng/> |
| Facet Sudoku | `kugorang/Sudoku`의 `gh-pages` | <https://kugorang.github.io/Sudoku/> |
| 오선로 | `kugorang/oseonro`의 `gh-pages` | <https://kugorang.github.io/oseonro/> |

별도 도메인이 없는 프로젝트 Pages는 계정 포트폴리오의 커스텀 도메인을 상속하므로,
Facet과 오선로의 기존 주소는 `hyeonwoo.kugora.ng/Sudoku/`, `hyeonwoo.kugora.ng/oseonro/`로
이동합니다. 게시 소스는 계속 각각의 저장소입니다.

`app-ads.txt`는 광고 공급자 확인에 사용하므로 유지합니다. 앱 소스, 인증 정보, 비공개 개발 문서는 게시하지 않습니다.
