import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# ─────────────────────────────────────
# 0. 글로벌 스타일 (다크 테마)
# ─────────────────────────────────────
st.markdown("""
<style>
    .stApp {
        background-color: #0f1923;
        color: #e0e6ed;
        font-family: 'Segoe UI', sans-serif;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }
    /* 탭 스타일 */
    .stTabs [data-baseid="TabsTabList"] {
        background-color: #141e2b;
        border-bottom: 2px solid #1e2f42;
        border-radius: 10px 10px 0 0;
        padding: 0 12px;
    }
    .stTabs [role="tab"] {
        color: #6b8299;
        font-size: 15px;
        font-weight: 600;
        padding: 10px 20px;
        border: none !important;
    }
    .stTabs [role="tab"][aria-selected="true"] {
        color: #00d4aa;
        border-bottom: 3px solid #00d4aa !important;
        background: transparent;
    }
    .stTabs [role="tab"]:hover {
        color: #a0c4db;
    }
    /* KPI 카드 */
    .kpi-card {
        background: linear-gradient(135deg, #141e2b, #1a2736);
        border: 1px solid #1e3044;
        border-radius: 14px;
        padding: 20px 14px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.35);
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        margin: 4px 0;
    }
    .kpi-label {
        font-size: 12px;
        color: #6b8299;
        margin-top: 2px;
    }
    .kpi-status {
        font-size: 13px;
        font-weight: 600;
        margin-top: 6px;
    }
    .color-good   { color: #00d4aa; }
    .color-warn   { color: #f5a623; }
    .color-danger { color: #ff5c5c; }
    .color-zero   { color: #4a6a84; }

    /* 섹션 타이틀 */
    .section-title {
        font-size: 14px;
        color: #6b8299;
        font-weight: 600;
        letter-spacing: 0.8px;
        margin: 18px 0 8px 0;
        text-transform: uppercase;
    }
    /* 진단 폼 스타일 */
    .stSelectbox, .stTextInput {
        background-color: #141e2b !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #00d4aa, #00b894);
        color: #fff;
        border: none;
        border-radius: 8px;
        padding: 10px 28px;
        font-weight: 700;
        font-size: 15px;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    .stButton > button:hover {
        opacity: 0.85;
    }
    /* 스크립트 코드블록 */
    .stCode {
        background-color: #141e2b !important;
        border: 1px solid #1e3044;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────
# 1. 샘플 진단 데이터 (테스트용)
# ─────────────────────────────────────
SAMPLE_DATA = {
    "company_name": "테스트 (주)",
    "industry": "제조업",
    "employees": 45,
    "annual_revenue": 12,          # 억원
    "ceo_age": 58,
    "has_successor": True,
    "insurance_coverage": False,
    "pension_status": "부분",
    # 카테고리별 리스크율 (0~100)
    "scores": {
        "대표자 리스크":    62,
        "법인 경영 리스크": 45,
        "리스크 인식":      78,
        "시나리오":         30,
    }
}

# ─────────────────────────────────────
# 2. 유틸리티 함수
# ─────────────────────────────────────
def calc_total_risk(scores: dict) -> float:
    """가중평균으로 종합 리스크율 계산"""
    weights = {"대표자 리스크": 0.35, "법인 경영 리스크": 0.30,
               "리스크 인식": 0.20, "시나리오": 0.15}
    total = sum(scores[k] * weights.get(k, 0.25) for k in scores)
    return round(total, 1)

def risk_label(val: float):
    """리스크율 → (텍스트, CSS클래스)"""
    if val < 30:  return "양호",   "color-good"
    if val < 60:  return "주의",   "color-warn"
    return               "위험",   "color-danger"

def status_color(val: float):
    if val == 0:  return "color-zero"
    if val < 30:  return "color-good"
    if val < 60:  return "color-warn"
    return               "color-danger"

# ─────────────────────────────────────
# 3. 차트 생성 함수
# ─────────────────────────────────────
DARK_BG   = "#0f1923"
CARD_BG   = "#141e2b"
TEXT_COL  = "#a0b8c8"
ACCENT    = "#00d4aa"

def draw_gauge(value: float, label_text: str, css_class: str):
    """종합 리스크 게이지 차트"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(font=dict(size=38, color="#e0e6ed"), suffix="%"),
        gauge=dict(
            axis=dict(range=[0, 100], tickcolor=TEXT_COL,
                      tickfont=dict(size=11, color=TEXT_COL)),
            bar=dict(color=ACCENT if value < 30 else ("#f5a623" if value < 60 else "#ff5c5c"),
                     thickness=0.28),
            bgcolor="#1a2736",
            steps=[
                dict(range=[0, 30],  color="#1a2e3d"),
                dict(range=[30, 60], color="#1f3040"),
                dict(range=[60, 100],color="#261f2e"),
            ],
            threshold=dict(line=dict(color="#ffffff", width=2), value=value)
        )
    ))
    fig.update_layout(
        height=260, margin=dict(l=20, r=20, t=10, b=30),
        paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
        font=dict(color=TEXT_COL)
    )
    # 하단 라벨
    fig.add_annotation(x=0.5, y=-0.08, xref="paper", yref="paper",
                       text=label_text, showarrow=False,
                       font=dict(size=16, color=(
                           "#00d4aa" if css_class=="color-good" else
                           "#f5a623" if css_class=="color-warn" else "#ff5c5c")))
    return fig

def draw_radar(scores: dict):
    """카테고리별 리스크 레이더 차트"""
    cats   = list(scores.keys())
    vals   = list(scores.values())
    # 닫힌 다각형
    cats_closed = cats + [cats[0]]
    vals_closed = vals + [vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_closed, theta=cats_closed,
        fill="toself",
        fillcolor="rgba(0,212,170,0.12)",
        line=dict(color=ACCENT, width=2),
        marker=dict(size=7, color=ACCENT),
        name="리스크율"
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                            tickvals=[25, 50, 75, 100],
                            tickfont=dict(size=10, color=TEXT_COL),
                            gridcolor="#1e3044", linecolor="#1e3044"),
            angularaxis=dict(tickfont=dict(size=12, color="#c8d8e4"),
                             gridcolor="#1e3044", linecolor="#1e3044"),
            bgcolor=CARD_BG
        ),
        height=290, margin=dict(l=45, r=45, t=15, b=15),
        paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG,
        showlegend=False
    )
    return fig

def draw_hbar(scores: dict):
    """카테고리별 수평 바 차트"""
    cats = list(scores.keys())
    vals = list(scores.values())
    colors = []
    for v in vals:
        colors.append("#00d4aa" if v < 30 else ("#f5a623" if v < 60 else "#ff5c5c"))

    fig = go.Figure(go.Bar(
        x=vals, y=cats, orientation="h",
        marker_color=colors,
        text=[f"{v}%" for v in vals],
        textposition="outside",
        textfont=dict(size=13, color="#e0e6ed"),
        width=0.45
    ))
    fig.update_layout(
        height=220, margin=dict(l=100, r=60, t=10, b=30),
        paper_bgcolor=DARK_BG, plot_bgcolor=DARK_BG,
        xaxis=dict(range=[0, 110], showgrid=True, gridcolor="#1e3044",
                   tickfont=dict(size=11, color=TEXT_COL), title_text="",
                   zeroline=False),
        yaxis=dict(tickfont=dict(size=13, color="#c8d8e4"), title_text=""),
        bargap=0.3
    )
    return fig

# ─────────────────────────────────────
# 4. KPI 카드 렌더링
# ─────────────────────────────────────
def render_kpi_cards(scores: dict, total: float):
    total_label, total_cls = risk_label(total)
    cols = st.columns(5)

    # ── 종합 리스크율
    with cols[0]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value {total_cls}">{total:.0f}%</div>
            <div class="kpi-label">종합 리스크율</div>
            <div class="kpi-status {total_cls}">{total_label}</div>
        </div>""", unsafe_allow_html=True)

    # ── 카테고리별
    for i, (key, val) in enumerate(scores.items()):
        lbl, cls = risk_label(val) if val > 0 else ("미평가", "color-zero")
        with cols[i + 1]:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value {cls}">{val}%</div>
                <div class="kpi-label">{key}</div>
                <div class="kpi-status {cls}">{lbl}</div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────
# 5. 탭 콘텐츠
# ─────────────────────────────────────
def tab_diagnosis():
    """진단 탭 — 기본 정보 입력 폼"""
    st.markdown('<div class="section-title">📋 기업 기본 정보</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        company = st.text_input("법인명", value=SAMPLE_DATA["company_name"])
        industry = st.selectbox("업종", ["제조업", "건설업", "서비스업", "유통업", "IT·소프트웨어", "기타"])
        employees = st.number_input("종업원 수", min_value=1, value=SAMPLE_DATA["employees"])
    with col2:
        revenue = st.number_input("연매출 (억원)", min_value=0.0, value=float(SAMPLE_DATA["annual_revenue"]), step=0.5)
        ceo_age = st.number_input("대표자 나이", min_value=30, max_value=90, value=SAMPLE_DATA["ceo_age"])
        successor = st.selectbox("후계자 여부", ["있음", "없음"], index=0 if SAMPLE_DATA["has_successor"] else 1)

    st.markdown('<div class="section-title">📌 리스크 진단 항목</div>', unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        ins = st.selectbox("기업보험 보장 여부", ["미보장", "부분보장", "충분보장"])
        pension = st.selectbox("퇴직연금 현황", ["미적립", "부분", "충분"])
    with col4:
        succession_plan = st.selectbox("가업승계 계획", ["미수립", "검토 중", "수립 완료"])
        tax_consult = st.selectbox("세무 컨설팅 경험", ["없음", "일부", "정기적"])

    st.markdown("&nbsp;", unsafe_allow_html=True)
    if st.button("🔍  진단 실행", use_container_width=False):
        st.success("✅ 진단이 완료되었습니다. **대시보드** 탭에서 결과를 확인하세요.")

def tab_dashboard(data: dict):
    """대시보드 탭 — 시각화"""
    scores = data["scores"]
    total  = calc_total_risk(scores)
    total_label, total_cls = risk_label(total)

    # KPI 카드
    render_kpi_cards(scores, total)
    st.markdown("&nbsp;", unsafe_allow_html=True)

    # ── 게이지 + 레이더
    col_left, col_right = st.columns([1, 1], gap="medium")
    with col_left:
        st.markdown('<div class="section-title">종합 리스크 게이지</div>', unsafe_allow_html=True)
        st.plotly_chart(draw_gauge(total, total_label, total_cls), use_container_width=True)
    with col_right:
        st.markdown('<div class="section-title">카테고리별 리스크 레이더</div>', unsafe_allow_html=True)
        st.plotly_chart(draw_radar(scores), use_container_width=True)

    # ── 수평 바
    st.markdown('<div class="section-title">카테고리별 리스크율 비교</div>', unsafe_allow_html=True)
    st.plotly_chart(draw_hbar(scores), use_container_width=True)

    # ── 진단 시간표시
    st.markdown(f'<div style="color:#4a6a84; font-size:12px; text-align:right; margin-top:8px;">진단일: {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)

def tab_script():
    """스크립트 탭 — 현재 소스 코드 열기"""
    st.markdown('<div class="section-title">📄 현재 스크립트 소스</div>', unsafe_allow_html=True)
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            code = f.read()
        st.code(code, language="python")
    except Exception:
        st.info("스크립트 파일을 읽을 수 없습니다.")

# ─────────────────────────────────────
# 6. 앱 진입점
# ─────────────────────────────────────
def main():
    # 헤더
    st.markdown("""
    <div style="text-align:center; padding: 18px 0 6px;">
        <span style="font-size:24px; font-weight:700; color:#e0e6ed;">
            🏢 삼성생명 GFC · 기업재무 진단 대시보드
        </span><br>
        <span style="font-size:13px; color:#4a6a84;">
            중소기업 종합 리스크 분석 및 재무 컨설팅 지원 시스템
        </span>
    </div>
    """, unsafe_allow_html=True)

    # 탭
    tab1, tab2, tab3 = st.tabs(["📋 진단", "📊 대시보드", "📝 스크립트"])

    with tab1:
        tab_diagnosis()
    with tab2:
        tab_dashboard(SAMPLE_DATA)
    with tab3:
        tab_script()

if __name__ == "__main__":
    main()