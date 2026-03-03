# HASIRA Music Prompt Factory CLI

Notion 데이터베이스(`Romantic Kitchen Prompt Factory`)에서 `Status=idea` 레코드를 읽어,
Romantic Kitchen 전용 프롬프트 12개를 생성하고 점수화한 뒤,
`Prompt Pack`, `Top Prompts`, `Score`, `Status=generated`로 업데이트하는 Python CLI입니다.

## 프로젝트 구조

```text
/app
  - main.py
  - notion_client.py
  - prompt_engine.py
  - scorer.py
  - config.py
.env.example
```

## 환경 변수

`.env.example`를 참고하여 아래 값을 설정하세요.

- `NOTION_TOKEN`
- `NOTION_DB_ID`
- `OPENAI_API_KEY`

## 실행 방법

```bash
cd /workspace/Codex_RewriteEngine
python app/main.py generate
```

## 동작 요약

1. Notion DB에서 `Status=idea` 항목을 최대 10개 조회
2. 레코드 텍스트(Title/Name/Idea/Keywords)를 기반으로 키워드 장면 확장
3. Romantic Kitchen 고정 템플릿으로 프롬프트 12개 생성
4. 점수 계산(가산/감점 룰 적용)
5. `Prompt Pack`, `Top Prompts`, `Score`, `Status=generated` 업데이트
