from pathlib import Path
from html import escape

import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_PATH = Path(__file__).with_name("book_bestseller_clean.csv")


st.set_page_config(page_title="야옹데브 도서 추천", page_icon="🐱", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');
    :root {
        --cream: #fffaf1;
        --paper: #fffdf8;
        --peach: #f7e5d2;
        --pink: #fbe3e2;
        --pink2: #f8d5d2;
        --brown: #685044;
        --muted: #9b8173;
    }
    .stApp {
        background:
          radial-gradient(circle at 12% 18%, rgba(239,196,178,.12) 0 2px, transparent 3px) 0 0/30px 30px,
          var(--cream);
        color: var(--brown);
        font-family: 'Gowun Dodum', 'Malgun Gothic', sans-serif;
    }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { opacity: .25; }
    .block-container { max-width: 1050px; padding-top: 1.1rem; padding-bottom: 3rem; }
    h1, h2, h3, p { color: var(--brown) !important; }
    .blog-top {
        display:flex; justify-content:space-between; align-items:center;
        padding: 5px 6px 12px; font-size: .82rem; color:#846c60;
    }
    .blog-brand { font-weight:800; letter-spacing:.02em; }
    .blog-search {
        padding:7px 13px; min-width:220px; border:1px solid #ead8c6;
        border-radius:999px; background:#fffdf9; color:#ac9689;
    }
    .hero {
        position:relative; overflow:hidden; padding:22px 28px;
        border:1px solid #ead4bc; border-radius:22px 22px 8px 8px;
        background:linear-gradient(135deg,#fff8eb,#f7ead8);
    }
    .hero:after {
        content:'🐈'; position:absolute; right:24px; bottom:-19px;
        font-size:72px; opacity:.16; transform:scaleX(-1);
    }
    .hero-title {font-size:1.45rem;font-weight:800;margin-bottom:4px;color:#59443a;}
    .hero-sub {font-size:.9rem;color:#9b8173;}
    .nav-pills {
        display:flex; justify-content:center; flex-wrap:wrap; gap:8px;
        margin:0 0 22px; padding:12px 16px;
        border:1px solid #ecd8c5; border-top:0; border-radius:0 0 22px 22px;
        background:#fff7eb;
    }
    .nav-pill {font-size:.86rem;font-weight:700;color:#765d51;padding:4px 9px;}
    .sidebar-box {
        min-height:430px; padding:18px 16px; border-radius:12px;
        border:1px solid #ead8c8;
        background:
          radial-gradient(circle,rgba(182,139,113,.13) 0 2px,transparent 2.5px) 0 0/24px 24px,
          #f8eadb;
    }
    .sidebar-title {font-size:1rem;font-weight:800;margin-bottom:13px;color:#604a3f;}
    .category-item {
        display:flex;justify-content:space-between;align-items:center;
        padding:7px 4px;border-bottom:1px dashed rgba(150,110,90,.13);
        color:#70594d;font-size:.88rem;
    }
    .new-badge {font-size:.62rem;padding:2px 6px;border-radius:999px;background:#f2a7a1;color:white;}
    .content-head {
        display:flex;justify-content:space-between;align-items:flex-end;
        border-bottom:2px solid #ead3c6;margin-bottom:14px;padding:2px 2px 10px;
    }
    .content-title {font-size:1.16rem;font-weight:800;color:#59443a;}
    .content-label {font-size:.78rem;color:#a08779;}
    .intro-note {
        margin:0 0 13px;padding:10px 13px;border-radius:12px;
        background:#fff6ef;color:#8b7164;font-size:.84rem;
    }
    div[data-baseweb="select"] > div {
        background: #fffdf9; border-color: #e9cfc4; border-radius: 13px;
    }
    div.stButton > button {
        width:100%;border:1px solid #e9beb5;border-radius:999px;
        background:#f7d8d4;color:#5b463c;font-weight:800;
    }
    div.stButton > button:hover { background: #ffddd9; border-color: #eab8ab; }
    .cat-card {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin:8px 0;padding:10px 14px;border:1px solid #f0cfcb;
        border-radius:18px;background:
          linear-gradient(90deg,rgba(255,255,255,.18),rgba(255,255,255,0)),#fae3e2;
        box-shadow:0 2px 7px rgba(126,91,74,.06);
        transition:transform .18s ease, background .18s ease;
    }
    .cat-card:hover {transform:translateY(-2px);background:#f9d9d7;}
    .cat-book { font-weight: 700; color: #554139; }
    .cat-meta { margin-top: 3px; color: #8a7064; font-size: .88rem; }
    .cat-score {
        flex: 0 0 auto;
        padding:5px 10px;
        border-radius: 999px;
        background:#f5d7ad;
        color: #6d5140;
        font-weight: 700;
    }
    .footer-note {text-align:center;color:#ad9385;font-size:.76rem;margin-top:25px;}
    @media (max-width: 720px) {
        .blog-search {display:none}.hero{padding:18px}.nav-pills{gap:1px}.nav-pill{font-size:.75rem}
        .sidebar-box{min-height:auto;margin-bottom:12px}.block-container{padding-left:1rem;padding-right:1rem}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=["상품명"]).reset_index(drop=True)
    for column in ["상품명", "저자", "출판사", "분야"]:
        if column in df.columns:
            df[column] = df[column].fillna("").astype(str)
    return df


@st.cache_resource
def build_recommender(df: pd.DataFrame):
    # 제목뿐 아니라 저자·출판사·분야도 함께 사용해 추천 품질을 높입니다.
    text_columns = [column for column in ["상품명", "저자", "출판사", "분야"] if column in df.columns]
    corpus = df[text_columns].agg(" ".join, axis=1)
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
    matrix = vectorizer.fit_transform(corpus)
    return matrix


def format_book(index: int) -> str:
    title = df.loc[index, "상품명"]
    author = df.loc[index, "저자"] if "저자" in df.columns else ""
    return f"{title} | {author}" if author else title


def recommend_books(df: pd.DataFrame, matrix, selected_index: int, top_n: int = 5) -> pd.DataFrame:
    similarities = cosine_similarity(matrix[selected_index], matrix).ravel()
    similarities[selected_index] = -1
    top_indices = similarities.argsort()[::-1][: min(top_n, len(df) - 1)]
    columns = [column for column in ["상품명", "저자", "출판사", "분야"] if column in df.columns]
    result = df.iloc[top_indices][columns].copy()
    result["유사도"] = similarities[top_indices]
    return result


def render_recommendations(result: pd.DataFrame) -> None:
    for _, book in result.iterrows():
        title = escape(str(book.get("상품명", "제목 없음")))
        author = escape(str(book.get("저자", "")))
        publisher = escape(str(book.get("출판사", "")))
        category = escape(str(book.get("분야", "")))
        meta = " · ".join(value for value in [author, publisher, category] if value)
        st.markdown(
            f"""
            <div class="cat-card">
              <div>
                <div class="cat-book">🐾 {title}</div>
                <div class="cat-meta">{meta}</div>
              </div>
              <div class="cat-score">{book['유사도']:.3f} 😸</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


df = load_data()
title_matrix = build_recommender(df)

st.markdown(
    """
    <div class="blog-top">
      <span class="blog-brand">Ⓝ blog　|　야옹데브</span>
      <span class="blog-search">이 블로그에서 검색　 🔍</span>
    </div>
    <div class="hero">
      <div class="hero-title">🐾 야옹데브의 AI 도서 연구소</div>
      <div class="hero-sub">데이터로 발견하는 나의 다음 책 · 포근한 고양이 추천소</div>
    </div>
    <div class="nav-pills">
      <span class="nav-pill">🐾 프롤로그</span><span class="nav-pill">🐱 블로그</span>
      <span class="nav-pill">🐾 지도</span><span class="nav-pill">🐱 도서 및 알림</span>
      <span class="nav-pill">🐾 카테고리</span><span class="nav-pill">🐱 개발 과정</span>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1, 3], gap="large")

with left:
    st.markdown(
        """
        <div class="sidebar-box">
          <div class="sidebar-title">카테고리</div>
          <div class="category-item"><span>🐈 개발 관련 열림</span><span>〰</span></div>
          <div class="category-item"><span>🐾 데이터 분석</span><span class="new-badge">NEW</span></div>
          <div class="category-item"><span>🐈 도서 추천</span><span>〰</span></div>
          <div class="category-item"><span>🐾 자연어 처리</span><span>〰</span></div>
          <div class="category-item"><span>🐈 집사 일지</span><span>〰</span></div>
          <div class="category-item"><span>🐾 프로젝트 기록</span><span>〰</span></div>
          <div class="category-item"><span>🐈 기타</span><span>〰</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        """
        <div class="content-head">
          <span class="content-title">이 블로그 AI 도서 추천 글</span>
          <span class="content-label">유사도</span>
        </div>
        <div class="intro-note">🐱 읽고 싶은 기준 도서를 고른 뒤 추천 버튼을 눌러보세요.</div>
        """,
        unsafe_allow_html=True,
    )
    selected_index = st.selectbox(
        "기준 도서를 선택하세요",
        options=df.index.tolist(),
        format_func=format_book,
        label_visibility="collapsed",
    )
    if st.button("🐾 비슷한 도서 5권 추천"):
        st.session_state["recommendations"] = recommend_books(
            df, title_matrix, selected_index, top_n=5
        )
    if "recommendations" in st.session_state:
        render_recommendations(st.session_state["recommendations"])

st.markdown(
    '<div class="footer-note">🐾 데이터와 고양이를 좋아하는 야옹데브의 작은 추천 연구소 🐾</div>',
    unsafe_allow_html=True,
)
