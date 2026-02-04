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
        font-family: 'Noto Sans KR', sans-serif;
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
                             gridcolor="#1e3044", linecolor="#1e3044", rotation=0),
            bgcolor=CARD_BG
        ),
        height=290, margin=dict(l=70, r=80, t=20, b=20),
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

def tab_consultant(data: dict):
    """AI 컨설턴트 탭 — Ken이 대시보드 분석 설명"""
    scores = data["scores"]
    total  = calc_total_risk(scores)
    total_label, _ = risk_label(total)
    
    # 상단: 컨설턴트 프로필
    col_avatar, col_intro = st.columns([0.7, 3.3])
    
    with col_avatar:
        # Ken 아바타 이미지
        st.markdown("""
        <div style="text-align:center; padding:10px;">
        """, unsafe_allow_html=True)
        
        # 업로드된 이미지 사용 (Streamlit Cloud의 경우 static 폴더에 배치)
        try:
            from PIL import Image
            import os
            # 로컬 개발 시: 이미지 파일 경로 지정
            avatar_path = "assets/ken_avatar.jpg"  # 프로젝트에 assets 폴더 생성 후 이미지 저장
            if os.path.exists(avatar_path):
                avatar_img = Image.open(avatar_path)
            else:
                # 파일이 없을 경우 기본 아이콘 표시
                st.markdown("""
                <div style="width:120px; height:120px; background:linear-gradient(135deg, #00d4aa, #00b894);
                           border-radius:50%; display:flex; align-items:center; justify-content:center;
                           font-size:72px; color:#fff; border:3px solid #00d4aa; 
                           box-shadow: 0 4px 12px rgba(0,212,170,0.3); margin:0 auto;">
                    👨‍💼
                </div>
                """, unsafe_allow_html=True)
                avatar_img = None
            
            if avatar_img:
                st.image(avatar_img, width=180, 
                        caption="", 
                        use_container_width=False)
        except:
            # 에러 발생 시 기본 아이콘
            st.markdown("""
            <div style="width:180px; height:180px; background:linear-gradient(135deg, #00d4aa, #00b894);
                       border-radius:50%; display:flex; align-items:center; justify-content:center;
                       font-size:72px; color:#fff; border:3px solid #00d4aa; 
                       box-shadow: 0 4px 12px rgba(0,212,170,0.3); margin:0 auto;">
                👨‍💼
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_intro:
        st.markdown(f"""
        <div style="padding:20px 10px;">
            <div style="font-family: 'Noto Sans KR'; font-size:22px; font-weight:700; color:#00d4aa; margin-bottom:8px;">
                🤝 안녕하세요, GFC 컨설턴트 Ken입니다
            </div>
            <div style="font-size:14px; color:#a0b8c8; line-height:1.7; margin-bottom:12px;">
                20년간 한국-중남미 협력 프로젝트를 수행하며 <b>58개 사이트</b>의 디지털 전환(DX) 전략을 수립한 경험을 바탕으로,
                귀사의 <b>종합 리스크 진단 결과</b>를 데이터 기반으로 상세히 분석해 드리겠습니다.
            </div>
            <div style="font-size:13px; color:#4a6a84;">
                📊 현재 분석 대상: <b style="color:#e0e6ed;">{data["company_name"]}</b> | 
                {data["industry"]} · 종업원 {data["employees"]}명 · 연매출 {data["annual_revenue"]}억원
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 섹션 1: 종합 진단 요약
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #141e2b, #1a2736); 
                padding: 20px; border-radius: 12px; border-left: 4px solid #00d4aa; margin-bottom:20px;">
        <div style="font-size:18px; font-weight:700; color:#00d4aa; margin-bottom:12px;">
            📋 종합 진단 결과 요약
        </div>
        <div style="font-size:15px; color:#e0e6ed; line-height:1.8;">
            귀사의 <b>종합 리스크율은 {total:.1f}%</b>로 <b style="color:{'#00d4aa' if total<30 else '#f5a623' if total<60 else '#ff5c5c'}">{total_label}</b> 수준입니다.<br><br>       
            이는 4가지 핵심 리스크 카테고리를 가중평균하여 산출한 결과로,<br>
            대표자 리스크(35%), 법인 경영 리스크(30%), 리스크 인식(20%), 시나리오(15%)를 반영했습니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 섹션 2: 카테고리별 상세 분석
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown('<div class="section-title">🔍 카테고리별 상세 분석 및 인사이트</div>', unsafe_allow_html=True)
    
    # 각 카테고리별 분석 카드
    categories_analysis = {
        "대표자 리스크": {
            "score": scores.get("대표자 리스크", 0),
            "icon": "👤",
            "description": "CEO 개인에 집중된 경영 리스크",
            "insights": [
                f"현재 대표자 연령: {data['ceo_age']}세 (고령화 리스크 {'높음' if data['ceo_age']>60 else '중간' if data['ceo_age']>50 else '낮음'})",
                f"후계자 준비: {'있음 ✓' if data['has_successor'] else '없음 ✗ (위험)'}", 
                "대표자 의존도가 높을수록 유고 시 경영 공백 위험 증가",
            ],
            "recommendation": "CEO 유고 대비 키맨 보험 및 후계자 육성 프로그램 검토 필요"
        },
        "법인 경영 리스크": {
            "score": scores.get("법인 경영 리스크", 0),
            "icon": "🏢",
            "description": "법인 운영 및 재무 건전성 리스크",
            "insights": [
                f"연매출 {data['annual_revenue']}억원 규모의 {data['industry']} 기업",
                f"종업원 {data['employees']}명 규모 — 노무 리스크 관리 필요",
                "법인세, 부가가치세 등 세무 리스크 존재",
            ],
            "recommendation": "법인보험(재해보장), 퇴직연금 제도 정비, 정기 세무 컨설팅 권장"
        },
        "리스크 인식": {
            "score": scores.get("리스크 인식", 0),
            "icon": "⚠️",
            "description": "리스크 관리 체계 및 보험 보장 수준",
            "insights": [
                f"기업보험 현황: {'미보장 (위험)' if not data.get('insurance_coverage') else '보장 중'}",
                f"퇴직연금 상태: {data.get('pension_status', '미적립')}",
                "리스크 인식이 낮을수록 돌발 상황 대응 능력 부족",
            ],
            "recommendation": "종합 리스크 진단 → 맞춤형 보험 포트폴리오 구축 → 정기 점검"
        },
        "시나리오": {
            "score": scores.get("시나리오", 0),
            "icon": "📈",
            "description": "가업승계 및 장기 전략 준비도",
            "insights": [
                f"후계자 여부: {'준비됨' if data.get('has_successor') else '미준비 (긴급)'}",
                "가업승계 시 증여세/상속세 부담 예상",
                "5~10년 후 기업 지속가능성 시나리오 부재",
            ],
            "recommendation": "가업승계 로드맵 수립, 절세 전략(생전증여 vs 상속), 신탁 활용 검토"
        }
    }
    
    for idx, (cat_name, analysis) in enumerate(categories_analysis.items()):
        score = analysis["score"]
        lbl, css = risk_label(score) if score > 0 else ("미평가", "color-zero")
        
        # 카드 배경색 (리스크 수준에 따라)
        if score < 30:
            card_bg = "#0d2818"
            border_col = "#00d4aa"
        elif score < 60:
            card_bg = "#2a1f0d"
            border_col = "#f5a623"
        else:
            card_bg = "#2a0d0d"
            border_col = "#ff5c5c"
        
        st.markdown(f"""
        <div style="background:{card_bg}; padding:18px; border-radius:10px; 
                    border-left:4px solid {border_col}; margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <div style="font-size:16px; font-weight:700; color:#e0e6ed;">
                    {analysis['icon']} {cat_name}
                </div>
                <div style="font-size:20px; font-weight:700; color:{border_col};">
                    {score}% <span style="font-size:13px; font-weight:600;">({lbl})</span>
                </div>
            </div>
            <div style="font-size:13px; color:#a0b8c8; margin-bottom:12px;">
                {analysis['description']}
            </div>
            <div style="font-size:13px; color:#c8d8e4; line-height:1.7; margin-bottom:10px;">
                <b>📌 주요 발견사항:</b><br>
                {'<br>'.join(['• ' + item for item in analysis['insights']])}
            </div>
            <div style="background:rgba(0,0,0,0.3); padding:10px; border-radius:6px; 
                        font-size:13px; color:#00d4aa; line-height:1.6;">
                <b>💡 컨설팅 제안:</b><br>
                {analysis['recommendation']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 섹션 3: 데이터 기반 종합 제안
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("---")
    st.markdown("### 🎯 Ken의 종합 컨설팅 제안")
    
    # 단기 제안
    st.markdown("""
    <div style='background: linear-gradient(135deg, #0d2818, #1a3a2e); 
                padding: 16px; border-radius: 10px; border-left: 4px solid #00d4aa; margin-bottom: 12px;'>
        <div style='font-size: 15px; font-weight: 700; color: #00d4aa; margin-bottom: 10px;'>
            ⏱️ 1. 단기 (3개월 이내)
        </div>
        <div style='font-size: 13px; color: #c8d8e4; line-height: 1.8;'>
            • 키맨 보험 가입으로 대표자 유고 리스크 대비<br>
            • 기업재해 보장 상품으로 종업원 안전망 구축<br>
            • 퇴직연금 제도 점검 및 최적화
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 중기 제안
    st.markdown("""
    <div style='background: linear-gradient(135deg, #2a1f0d, #3a2f1d); 
                padding: 16px; border-radius: 10px; border-left: 4px solid #f5a623; margin-bottom: 12px;'>
        <div style='font-size: 15px; font-weight: 700; color: #f5a623; margin-bottom: 10px;'>
            📅 2. 중기 (6~12개월)
        </div>
        <div style='font-size: 13px; color: #c8d8e4; line-height: 1.8;'>
            • 가업승계 시뮬레이션 (증여 vs 상속 세금 비교)<br>
            • 법인세 절세 전략 수립 (삼성생명 세무사 협업)<br>
            • 정기 재무 건강검진 체계 구축
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 장기 제안
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e, #2a2a4e); 
                padding: 16px; border-radius: 10px; border-left: 4px solid #6c5ce7; margin-bottom: 12px;'>
        <div style='font-size: 15px; font-weight: 700; color: #a29bfe; margin-bottom: 10px;'>
            🎯 3. 장기 (1~3년)
        </div>
        <div style='font-size: 13px; color: #c8d8e4; line-height: 1.8;'>
            • 후계자 육성 프로그램 및 지분 이전 계획<br>
            • 가족신탁, 재산분할 등 고급 절세 전략<br>
            • 삼성패밀리오피스 연계한 자산관리 (10억 이상 자산가 대상)
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 차별화 포인트
    st.markdown("""
    <div style='background: rgba(0, 212, 170, 0.08); 
                padding: 18px; border-radius: 10px; 
                border: 2px solid #00d4aa; margin-top: 20px;'>
        <div style='font-size: 16px; font-weight: 700; color: #00d4aa; margin-bottom: 12px;'>
            💎 차별화 포인트
        </div>
        <div style='font-size: 14px; color: #e0e6ed; line-height: 1.8;'>
            저는 단순 보험 판매가 아닌, <b style='color: #00d4aa;'>데이터 기반 시뮬레이션 도구</b>를 활용하여 
            "지금 이 상품에 가입하면 10년 후 얼마나 절세되는가"를 실시간으로 보여드립니다.
        </div>
        <div style='font-size: 13px; color: #a0b8c8; margin-top: 10px; line-height: 1.7;'>
            기업 실무데이터 분석 Streamlit-XAI 등 최신 분석 기술로 <b>고객이 스스로 납득</b>할 수 있는 컨설팅을 제공합니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 섹션 4: 다음 단계 액션 플랜
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown("&nbsp;", unsafe_allow_html=True)
    st.markdown("### 📞 다음 단계 — 무료 심층 상담 신청")
    
    st.markdown("""
    <div style='background: #141e2b; padding: 20px; border-radius: 10px; 
                border: 1px solid #1e3044; margin-bottom: 20px;'>
        <div style='font-size: 14px; color: #c8d8e4; line-height: 1.8; margin-bottom: 16px;'>
            위 분석 결과를 바탕으로 <b style='color: #00d4aa;'>귀사 맞춤형 절세 시뮬레이션</b>을 준비해 드리겠습니다.
        </div>
        <div style='background: rgba(245, 166, 35, 0.05); padding: 14px; border-radius: 8px; border-left: 3px solid #f5a623; margin-bottom: 16px;'>
            <div style='font-size: 13px; font-weight: 700; color: #f5a623; margin-bottom: 8px;'>
                📋 상담 신청 시 제공되는 자료
            </div>
            <div style='font-size: 13px; color: #c8d8e4; line-height: 1.7;'>
                • 가업승계 시나리오별 세금 비교표 (증여 vs 상속)<br>
                • 법인보험 가입 시 절세 효과 계산서<br>
                • 퇴직연금 최적화 방안<br>
                • ROI 예측 대시보드 (5년/10년 단위)
            </div>
        </div>
        <div style='background: rgba(0, 212, 170, 0.08); padding: 12px; border-radius: 6px; border: 1px solid #00d4aa; text-align: center;'>
            <span style='font-size: 14px; color: #00d4aa; font-weight: 700;'>
                📧  io7hub@naver.com | ☎ 010-2610-5194
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 하단 타임스탬프
    st.markdown(f"""
    <div style="text-align:right; color:#4a6a84; font-size:11px; margin-top:20px;">
        🤖 AI 컨설턴트 분석 완료 | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────
# 6. 앱 진입점
# ─────────────────────────────────────
def main():
    # 헤더
    st.markdown("""
    <div style="text-align:center; padding: 18px 0 6px;">
        <span style="font-family: 'Noto Sans KR'; font-size:24px; font-weight:700; color:#e0e6ed;">
            🏢 삼성생명 GFC · 기업재무 진단 대시보드
        </span><br>
        <span style="font-size:13px; color:#4a6a84;">
            중소기업 종합 리스크 분석 및 재무 컨설팅 지원 시스템
        </span>
    </div>
    """, unsafe_allow_html=True)

    # 탭
    tab1, tab2, tab3 = st.tabs(["📋 진단", "📊 대시보드", "🤝 AI 컨설턴트"])

    with tab1:
        tab_diagnosis()
    with tab2:
        tab_dashboard(SAMPLE_DATA)
    with tab3:
        tab_consultant(SAMPLE_DATA)

if __name__ == "__main__":
    main()