from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "ch10_cancel_model.joblib"

st.set_page_config(
    page_title="주문 취소 위험 대시보드",
    page_icon="◉",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root { --ink:#102331; --navy:#12324a; --blue:#1f6f8b; --mint:#57c5b6; --paper:#f4f7f8; }
    .stApp { background: linear-gradient(145deg, #eef4f5 0%, #f9fbfb 48%, #eef2f4 100%); }
    .block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 3rem; }
    h1, h2, h3 { color: var(--ink); letter-spacing: -0.03em; }
    .eyebrow { color:#1f6f8b; font-weight:700; letter-spacing:.12em; text-transform:uppercase; font-size:.78rem; }
    .hero { padding:1.6rem 1.8rem; border:1px solid #d6e2e5; border-radius:20px; background:rgba(255,255,255,.78); box-shadow:0 14px 40px rgba(18,50,74,.08); margin-bottom:1.4rem; }
    .hero h1 { margin:.25rem 0 .4rem; font-size:2.25rem; }
    .hero p { color:#506674; margin:0; font-size:1rem; }
    .risk-card { border-radius:18px; padding:1.4rem; background:#102f45; color:white; min-height:210px; }
    .risk-card h2 { color:white; margin:.25rem 0; font-size:2.8rem; }
    .risk-card p { color:#cfe3e7; }
    .status-pill { display:inline-block; padding:.35rem .7rem; border-radius:999px; background:#dff5ef; color:#116555; font-weight:700; font-size:.82rem; }
    [data-testid="stMetric"] { background:rgba(255,255,255,.78); border:1px solid #dbe5e8; padding:1rem; border-radius:14px; }
    div[data-testid="stForm"] { background:rgba(255,255,255,.72); border:1px solid #d6e2e5; border-radius:18px; padding:1.2rem; }
    .small-note { color:#617784; font-size:.84rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_artifact() -> dict:
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            "저장된 모델이 없습니다. scripts/train_ch10_model.py를 먼저 실행하세요."
        )
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_order_history() -> pd.DataFrame:
    raw_dir = PROJECT_ROOT / "data" / "raw"
    orders = pd.read_csv(raw_dir / "orders.csv")
    items = pd.read_csv(raw_dir / "order_items.csv")
    customers = pd.read_csv(raw_dir / "customers.csv")

    orders = orders.loc[orders["order_status"].isin(["completed", "cancelled"])].copy()
    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
    items["line_total"] = items["quantity"] * items["unit_price"]
    order_features = items.groupby("order_id", as_index=False).agg(
        item_count=("product_id", "nunique"),
        total_quantity=("quantity", "sum"),
        order_amount=("line_total", "sum"),
    )
    history = orders.merge(order_features, on="order_id", how="inner", validate="1:1")
    history = history.merge(
        customers[["customer_id", "age", "gender", "city"]],
        on="customer_id",
        how="inner",
        validate="m:1",
    )
    probabilities = artifact["model"].predict_proba(history[artifact["features"]])[:, 1]
    history["cancel_probability"] = probabilities
    threshold = float(artifact["threshold"])
    history["risk_level"] = np.select(
        [probabilities >= max(0.7, threshold), probabilities >= threshold],
        ["높음", "주의"],
        default="낮음",
    )
    history["actual_status"] = history["order_status"].map(
        {"completed": "완료", "cancelled": "취소"}
    )
    return history.sort_values(["order_date", "order_id"], ascending=False).reset_index(drop=True)


def format_feature_name(name: str) -> str:
    label_map = {
        "age": "고객 연령",
        "item_count": "상품 종류 수",
        "total_quantity": "총 수량",
        "order_amount": "주문 금액",
        "gender": "성별",
        "city": "도시",
        "payment_method": "결제 수단",
    }
    clean = name.split("__", 1)[-1]
    for raw, label in label_map.items():
        if clean == raw:
            return label
        if clean.startswith(raw + "_"):
            return f"{label}: {clean[len(raw) + 1:]}"
    return clean


def explain_prediction(input_data: pd.DataFrame) -> pd.DataFrame:
    pipeline = artifact["model"]
    preprocessor = pipeline.named_steps["preprocessor"]
    classifier = pipeline.named_steps["classifier"]
    if not hasattr(classifier, "coef_"):
        return pd.DataFrame()

    transformed = preprocessor.transform(input_data)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    feature_names = preprocessor.get_feature_names_out()
    contributions = np.asarray(transformed)[0] * classifier.coef_[0]
    explanation = pd.DataFrame(
        {
            "요인": [format_feature_name(name) for name in feature_names],
            "영향값": contributions,
        }
    )
    explanation["방향"] = np.where(
        explanation["영향값"] >= 0, "취소 위험 증가", "취소 위험 감소"
    )
    explanation["영향도"] = explanation["영향값"].abs()
    return explanation.sort_values("영향도", ascending=False).head(5)


artifact = load_artifact()
metrics = artifact["metrics"]
ranges = artifact["ranges"]
categories = artifact["categories"]
history = load_order_history()

st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">CHAPTER 10 · MODEL SERVING</div>
      <h1>주문 취소 위험 대시보드</h1>
      <p>주문 직후 확인 가능한 정보로 취소 가능성을 추정하고 대응 우선순위를 정합니다.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
metric_cols[0].metric("서빙 모델", artifact["model_name"])
metric_cols[1].metric("판정 임계값", f"{artifact['threshold']:.0%}")
metric_cols[2].metric("Test F1", f"{metrics['f1']:.3f}")
metric_cols[3].metric("Test ROC-AUC", f"{metrics['roc_auc']:.3f}")

left, right = st.columns([1.05, 0.95], gap="large")

with left:
    st.subheader("주문 정보 입력")
    with st.form("prediction_form"):
        row1 = st.columns(2)
        age = row1[0].number_input(
            "고객 연령",
            min_value=int(ranges["age"]["min"]),
            max_value=int(ranges["age"]["max"]),
            value=int(ranges["age"]["median"]),
        )
        gender = row1[1].selectbox("성별", categories["gender"])

        row2 = st.columns(2)
        city = row2[0].selectbox("도시", categories["city"])
        payment_method = row2[1].selectbox("결제 수단", categories["payment_method"])

        row3 = st.columns(2)
        item_count = row3[0].number_input(
            "상품 종류 수", min_value=1, value=max(1, int(ranges["item_count"]["median"])), step=1
        )
        total_quantity = row3[1].number_input(
            "총 수량", min_value=1, value=max(1, int(ranges["total_quantity"]["median"])), step=1
        )
        order_amount = st.number_input(
            "주문 금액 (원)",
            min_value=0,
            value=int(ranges["order_amount"]["median"]),
            step=1000,
        )
        submitted = st.form_submit_button("취소 위험 예측", width="stretch")

with right:
    st.subheader("예측 결과")
    if submitted:
        input_data = pd.DataFrame(
            [
                {
                    "age": age,
                    "gender": gender,
                    "city": city,
                    "payment_method": payment_method,
                    "item_count": item_count,
                    "total_quantity": total_quantity,
                    "order_amount": order_amount,
                }
            ]
        )
        probability = float(artifact["model"].predict_proba(input_data)[0, 1])
        threshold = float(artifact["threshold"])
        predicted_cancel = probability >= threshold

        if probability >= max(0.7, threshold):
            level, action = "높음", "결제 오류 여부를 즉시 확인하고 이탈 방지 안내를 우선 노출하세요."
        elif predicted_cancel:
            level, action = "주의", "결제 직후 안내 메시지 또는 보조 혜택 제공을 검토하세요."
        else:
            level, action = "낮음", "일반 주문 흐름을 유지하고 별도 개입은 최소화하세요."

        st.markdown(
            f"""
            <div class="risk-card">
              <span class="status-pill">위험도 {level}</span>
              <h2>{probability:.1%}</h2>
              <p>예측된 주문 취소 확률</p>
              <strong>{'취소 위험 주문' if predicted_cancel else '정상 주문 예상'}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(probability)
        st.info(action)

        explanation = explain_prediction(input_data)
        if not explanation.empty:
            st.markdown("#### 주요 판단 요인")
            for _, row in explanation.iterrows():
                icon = "▲" if row["영향값"] >= 0 else "▼"
                st.markdown(
                    f"**{icon} {row['요인']}** · {row['방향']} "
                    f"(상대 영향 {row['영향도']:.2f})"
                )
            st.caption(
                "영향도는 이 예측에서 모델 점수를 움직인 상대적 크기입니다. "
                "원인이나 정책 효과를 의미하지 않습니다."
            )
    else:
        st.markdown(
            """
            <div class="risk-card">
              <span class="status-pill">대기 중</span>
              <h2>—</h2>
              <p>왼쪽에서 주문 정보를 입력하고 예측 버튼을 누르세요.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

with st.expander("모델 평가 정보"):
    cols = st.columns(4)
    cols[0].metric("Accuracy", f"{metrics['accuracy']:.3f}")
    cols[1].metric("Precision", f"{metrics['precision']:.3f}")
    cols[2].metric("Recall", f"{metrics['recall']:.3f}")
    cols[3].metric("평가 주문", f"{metrics['test_size']}건")
    st.markdown(
        f"<p class='small-note'>학습 데이터 {artifact['training_rows']}건 · 모델 생성 {artifact['trained_at']}</p>",
        unsafe_allow_html=True,
    )

st.divider()
st.subheader("주문 내역과 위험 모니터링")
st.caption("완료·취소 주문을 현재 모델로 다시 평가한 결과입니다. 고객 이름 등 직접 식별정보는 표시하지 않습니다.")

summary_cols = st.columns(4)
summary_cols[0].metric("분석 주문", f"{len(history):,}건")
summary_cols[1].metric("실제 취소", f"{(history['actual_status'] == '취소').sum():,}건")
summary_cols[2].metric("위험 주문", f"{history['risk_level'].isin(['주의', '높음']).sum():,}건")
summary_cols[3].metric("평균 취소 확률", f"{history['cancel_probability'].mean():.1%}")

filter_cols = st.columns([1, 1, 2])
risk_filter = filter_cols[0].multiselect(
    "위험도",
    options=["높음", "주의", "낮음"],
    default=["높음", "주의", "낮음"],
)
status_filter = filter_cols[1].multiselect(
    "실제 상태",
    options=["완료", "취소"],
    default=["완료", "취소"],
)
search_order = filter_cols[2].text_input("주문번호 검색", placeholder="예: 125")

filtered = history.loc[
    history["risk_level"].isin(risk_filter)
    & history["actual_status"].isin(status_filter)
].copy()
if search_order.strip():
    filtered = filtered.loc[
        filtered["order_id"].astype(str).str.contains(search_order.strip(), regex=False)
    ]

chart_col, detail_col = st.columns([0.7, 1.3], gap="large")
with chart_col:
    st.markdown("#### 위험도 분포")
    risk_counts = (
        filtered["risk_level"]
        .value_counts()
        .reindex(["높음", "주의", "낮음"], fill_value=0)
        .rename("주문 수")
    )
    st.bar_chart(risk_counts, color="#1f6f8b", height=300)

with detail_col:
    st.markdown("#### 최근 주문")
    display = filtered[
        [
            "order_id",
            "order_date",
            "payment_method",
            "item_count",
            "total_quantity",
            "order_amount",
            "cancel_probability",
            "risk_level",
            "actual_status",
        ]
    ].rename(
        columns={
            "order_id": "주문번호",
            "order_date": "주문일",
            "payment_method": "결제수단",
            "item_count": "상품종류",
            "total_quantity": "총수량",
            "order_amount": "주문금액",
            "cancel_probability": "취소확률",
            "risk_level": "위험도",
            "actual_status": "실제상태",
        }
    )
    st.dataframe(
        display,
        width="stretch",
        hide_index=True,
        height=360,
        column_config={
            "주문일": st.column_config.DateColumn(format="YYYY-MM-DD"),
            "주문금액": st.column_config.NumberColumn(format="₩%d"),
            "취소확률": st.column_config.ProgressColumn(
                format="%.1f%%", min_value=0, max_value=1
            ),
        },
    )

with st.expander("대시보드 해석 방법"):
    st.markdown(
        """
        - **취소 확률**은 입력 정보와 유사한 주문이 취소될 가능성을 모델이 추정한 값입니다.
        - **주의/높음**은 Validation 데이터에서 선택한 임계값을 기준으로 분류합니다.
        - **주요 판단 요인**은 현재 입력이 모델 점수를 어느 방향으로 움직였는지 보여줍니다.
        - **실제 상태**는 사후 결과이며 모델 입력에는 사용하지 않습니다. 모델 예측과 실제 결과를 비교하는 용도입니다.
        - 표본과 모델 성능이 제한적이므로 고객 불이익을 주는 자동 의사결정에는 사용하지 마세요.
        """
    )

st.caption("이 결과는 운영 판단을 보조하는 예측값이며 주문 취소를 확정하는 정보가 아닙니다.")
