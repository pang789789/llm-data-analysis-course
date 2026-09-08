# Chapter 02. VS Code에서 시작하는 데이터 분석 환경

## 제출 정보

- GitHub 계정: `pang789789`
- 프로젝트 폴더: `C:\dev\llm-data-analysis-course`

## 환경 확인 결과

| 확인 항목 | 결과 |
| --- | --- |
| 가상환경 | `.venv` 폴더 사용 |
| Notebook 커널 | 프로젝트 `.venv` Python 3.14.7 |
| 데이터 폴더 | `data/raw/` |
| CSV 파일 | `customers.csv`, `products.csv`, `orders.csv`, `order_items.csv` |
| 패키지 목록 | `requirements.txt`에 관리 |

## 프로젝트 구조 확인

```text
llm-data-analysis-course/
├─ data/raw/
│  ├─ customers.csv
│  ├─ products.csv
│  ├─ orders.csv
│  └─ order_items.csv
├─ notebooks/
├─ scripts/generate_sample_data.py
├─ reports/
└─ requirements.txt
```

## 실행 환경에 대한 판단

Notebook에서 선택한 Python 실행 파일이 프로젝트의 `.venv\Scripts\python.exe`를 가리키는 것을 확인했다. 이 설정이 맞지 않으면 설치한 패키지와 Notebook이 사용하는 패키지가 달라져 `ModuleNotFoundError`가 생길 수 있다.

또한 CSV의 상대경로를 노트북 위치에 맞춰 추측하지 않고, 프로젝트 루트를 먼저 찾은 뒤 `data/raw`를 기준으로 사용하도록 했다. 이 방식은 노트북이 `notebooks/` 또는 하위 폴더에 있어도 같은 데이터를 찾는 데 도움이 된다.

## 문제 해결 기록

프로젝트 루트를 찾는 함수에서 `current.parents`를 사용하면 여러 상위 경로의 목록이 되어 경로 연산 오류가 발생했다. 한 단계 위 경로를 뜻하는 `current.parent`로 수정했다.

```python
current = current.parent
```

## 보안 확인

- `.env` 파일은 Git에 올리지 않는다.
- API Key, Token, 비밀번호는 Notebook 출력과 캡처에 포함하지 않는다.

> Evidence 이미지는 실제 설치·커널 선택·환경 확인 화면을 캡처한 뒤 `chapter02/images/`에 추가한다.
