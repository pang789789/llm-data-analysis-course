# 주문 취소 위험 Streamlit 대시보드

## 1. 모델 학습 및 저장

```powershell
.\.venv\Scripts\python.exe scripts\train_ch10_model.py
```

## 2. 대시보드 실행

```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard\app.py
```

대시보드는 `models/ch10_cancel_model.joblib`을 불러와 주문 취소 확률을 실시간으로 예측합니다.
