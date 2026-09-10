# LLM Data Analysis Course

LLM을 활용한 데이터 분석 수업의 실습 코드, 노트북, 과제 결과를 정리한 저장소입니다.

## 학습 내용

- Python 기반 데이터 전처리 및 분석
- Jupyter Notebook을 활용한 실습
- LLM 프롬프트 설계와 데이터 분석 자동화
- 수업 과제 및 분석 보고서 정리

## Project structure

- `data/raw/` - 원본 데이터
- `data/processed/` - 전처리된 데이터
- `data/external/` - 외부 데이터
- `notebooks/` - Jupyter Notebook 실습
- `scripts/` - 데이터 생성 및 유틸리티 스크립트
- `reports/` - 분석 결과와 보고서
- `prompts/` - LLM 프롬프트
- `src/` - 프로젝트 소스 코드
- `automation/` - 자동화 코드
- `data_analysis_assignments/` - 데이터 분석 수업 과제

## 실습 환경 설정

프로젝트 루트에서 Python 가상 환경을 생성하고 필요한 패키지를 설치합니다.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

3~4장 실습에 필요한 샘플 CSV 파일은 `data/raw/`에 포함되어 있습니다. 데이터를 다시 생성하려면 프로젝트 루트에서 다음 명령을 실행합니다.

```powershell
python scripts/generate_sample_data.py
```

`notebooks/ch03_data_overview.ipynb` 또는 `notebooks/ch04_pandas_basic.ipynb`를 열 때는 `.venv` Python 커널을 선택합니다.
