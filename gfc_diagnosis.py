"""
Kⁱ⁰⁷ 삼성생명 GFC | 법인 리스크 사전 진단표 260202
Streamlit 기반 AI 진단 엔진 + KPI 대시보드

설치 : pip install streamlit plotly numpy
실행 : streamlit run gfc_diagnosis.py
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# ═══════════════════════════════════════════════════════════
# DARK THEME CSS
# ═══════════════════════════════════════════════════════════
DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800&display=swap');

.stApp                        { background:#0f1623 !important; color:#cbd5e1 !important; font-family:'Noto Sans KR',sans-serif !important; }
.main .block-container        { padding-top:8px !important; padding-left:18px !important; padding-right:18px !important; max-width:920px !important; margin:0 auto !important; }

/* HEADER BAND */
.gfc-header { background:linear-gradient(135deg,#0a1220 0%,#152238 55%,#1a2d4a 100%); border-bottom:1px solid #1e3a5f;
  padding:24px 22px 20px; border-radius:0; margin:-8px -18px 0; }
.gfc-header h1 { color:#fff; font-size:22px; font-weight:800; margin:0; line-height:1.3; }
.gfc-header h1 span { color:#60a5fa; }
.gfc-header p  { color:#64748b; font-size:11px; margin:6px 0 0; line-height:1.55; max-width:580px; }
.gfc-live { display:inline-flex; align-items:center; gap:6px; margin-bottom:8px; }
.gfc-live-dot { width:7px; height:7px; border-radius:50%; background:#22c55e; animation:pulse 2s infinite; }
.gfc-live span { font-size:10px; color:#60a5fa; font-weight:700; letter-spacing:1.4px; text-transform:uppercase; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

/* TABS */
div[data-testid="stTabs"]              { border-bottom:1px solid #1e3a5f !important; }
button[data-testid="tab-btn"]          { background:none !important; color:#64748b !important; font-size:12px !important; font-weight:600 !important; border:none !important; padding:9px 14px !important; border-bottom:2px solid transparent !important; }
button[data-testid="tab-btn"][aria-selected="true"] { color:#60a5fa !important; border-bottom-color:#60a5fa !important; }

/* EXPANDER */
.streamlit-expander                    { border:1px solid #1e3a5f !important; background:#111d2e !important; border-radius:8px !important; margin-bottom:5px !important; }
.streamlit-expander .streamlit-expander-header { color:#fff !important; font-weight:700 !important; font-size:12.5px !important; }

/* INPUTS */
.stSelectbox label, .stTextInput label { color:#64748b !important; font-size:10px !important; text-transform:uppercase; letter-spacing:.7px; font-weight:700 !important; }
.stSelectbox>div>div               { background:#0f1a2a !important; border:1px solid #1e3a5f !important; color:#fff !important; border-radius:6px !important; font-size:12.5px !important; }
.stTextInput>div>input             { background:#0f1a2a !important; border:1px solid #1e3a5f !important; color:#fff !important; border-radius:6px !important; font-size:12.5px !important; }
.stTextInput>div>input:focus       { border-color:#60a5fa !important; box-shadow:none !important; }
.stTextInput>div>input::placeholder{ color:#475569 !important; }

/* RADIO */
.stRadio label                     { color:#cbd5e1 !important; font-size:11.5px !important; }
.stRadio>div>div label             { color:#cbd5e1 !important; font-size:11.5px !important; }

/* CARDS */
.gfc-card { background:#131f33; border:1px solid #1e3a5f; border-radius:10px; padding:16px 18px; margin-bottom:8px; }
.gfc-card-on { background:#1a2d4a; border-color:#2563eb44; }
.gfc-card h3 { color:#fff; font-size:13px; font-weight:700; margin:0 0 4px; }
.gfc-card p  { color:#64748b; font-size:10.5px; margin:0; line-height:1.5; }

/* KPI GRID */
.gfc-kpi-row { display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px; }
.gfc-kpi { background:#131f33; border:1px solid #1e3a5f; border-radius:10px; padding:14px 16px; flex:1; min-width:130px; text-align:center; }
.gfc-kpi .val { font-size:24px; font-weight:800; line-height:1; margin-bottom:3px; }
.gfc-kpi .lbl { font-size:9.5px; color:#64748b; font-weight:600; }

/* PRIORITY / SOLUTION */
.gfc-pri { background:#131f33; border:1px solid #1e3a5f; border-radius:7px; padding:8px 10px; display:flex; align-items:flex-start; gap:8px; margin-bottom:4px; }
.gfc-pri .rk { font-size:11px; font-weight:800; color:#64748b; width:18px; text-align:center; flex-shrink:0; }
.gfc-pri .info { flex:1; min-width:0; }
.gfc-pri .cat { font-size:9px; color:#64748b; margin-bottom:1px; }
.gfc-pri .txt { font-size:10.5px; color:#cbd5e1; }
.gfc-pri .wtag { font-size:8px; font-weight:700; color:#fff; border-radius:3px; padding:1px 5px; flex-shrink:0; }

.gfc-sol { background:#131f33; border:1px solid #1e3a5f; border-radius:8px; padding:10px 12px; display:flex; align-items:flex-start; gap:8px; margin-bottom:5px; }
.gfc-sol .ico { font-size:18px; flex-shrink:0; }
.gfc-sol .nm { font-size:11px; font-weight:700; color:#fff; margin-bottom:2px; }
.gfc-sol .dc { font-size:9.5px; color:#64748b; line-height:1.45; }

/* SCRIPT PANEL */
.gfc-script { background:#1a2736; border:1px solid #2a4a6b; border-top:2px solid #ca8a04; border-radius:10px; padding:22px 24px; margin-top:8px; }
.gfc-script .sc-hdr { text-align:center; border-bottom:1px solid #2a4a6b; padding-bottom:12px; margin-bottom:16px; }
.gfc-script .sc-hdr h2 { color:#fff; font-size:15px; font-weight:800; margin:0; }
.gfc-script .sc-hdr p  { color:#ca8a04; font-size:9.5px; margin:3px 0 0; font-weight:600; letter-spacing:1px; }
.gfc-script .sc-meta { display:grid; grid-template-columns:1fr 1fr; gap:3px 14px; margin-bottom:14px; font-size:10.5px; color:#64748b; }
.gfc-script .sc-meta strong { color:#fff; font-weight:600; }
.gfc-script .sc-sec { font-size:10.5px; font-weight:700; color:#ca8a04; letter-spacing:.3px; margin:14px 0 6px; display:flex; align-items:center; gap:6px; }
.gfc-script .sc-sec::after { content:''; flex:1; height:1px; background:#2a4a6b; }
.gfc-script .sc-divider { height:1px; background:#2a4a6b; margin:12px 0; }
.gfc-script .sc-intro { background:#151f30; border-left:3px solid #60a5fa; border-radius:6px; padding:14px 16px; font-size:11.5px; color:#cbd5e1; line-height:1.9; }
.gfc-script .sc-block { background:#151f30; border-left:2px solid; border-radius:5px; padding:9px 12px; margin-bottom:4px; }
.gfc-script .sc-block .bq { font-size:9.5px; color:#94a3b8; margin-bottom:2px; }
.gfc-script .sc-block .bt { font-size:10.5px; color:#cbd5e1; line-height:1.6; }
.gfc-script .sc-close { background:#151f30; border-left:3px solid #22c55e; border-radius:6px; padding:14px 16px; font-size:11px; color:#cbd5e1; line-height:1.85; margin-top:6px; }

/* BUTTONS */
.gfc-btn-gen { background:#2563eb; color:#fff; border:none; border-radius:7px; padding:9px 20px; font-size:12px; font-weight:700; cursor:pointer; font-family:inherit; display:inline-flex; align-items:center; gap:5px; }
.gfc-btn-gen:hover { background:#1d4ed8; }

/* MISC */
.gfc-note { background:#0f1a2a; border-top:1px solid #1e3a5f; padding:6px 12px; font-size:10px; color:#64748b; border-radius:0 0 8px 8px; line-height:1.5; }
.gfc-note span { color:#60a5fa; }
.gfc-empty { color:#22c55e; font-size:11px; text-align:center; padding:10px; }
st.sidebar { background:#0a1220 !important; }
</style>
"""

# ═══════════════════════════════════════════════════════════
# DATA DEFINITIONS
# ═══════════════════════════════════════════════════════════
# Ⅱ. Key-Man Risk  –  (항목, 가중치)
KEYMAN = [
    ("대표자 유고 시 의사결정 공백이 발생할 수 있다",            4),
    ("회사 주요 거래·의사결정이 대표자 개인에게 집중되어 있다",  5),
    ("대표자가 개인 보증을 서고 있다",                           4),
    ("대표자 개인 재무와 법인 재무가 명확히 분리되어 있지 않다", 3),
    ("가업 승계 또는 지분 이전 계획이 명확하지 않다",            5),
    ("대표자 건강·사고 리스크에 대한 대비가 충분하지 않다",      5),
]

# Ⅲ. Corporate Risk
CORP = [
    ("매출이 특정 거래처에 과도하게 집중되어 있다",              4),
    ("핵심 인력 이탈 시 업무 공백이 크다",                       4),
    ("설비·투자 회수 구조가 장기적이거나 불확실하다",            3),
    ("현금흐름 변동성이 크다",                                   4),
    ("외부 환경 변화(환율·정책·시장)에 취약하다",               3),
    ("예상치 못한 사고 발생 시 즉각 대응 체계가 부족하다",       5),
]

# 응답 옵션 → 리스크 점수 매핑  (예=highest risk)
RESP_OPTIONS = ["예", "일부 해당", "아니오"]
RESP_SCORE   = {"예": 1.0, "일부 해당": 0.5, "아니오": 0.0}   # 1=리스크 최대

# Ⅳ. 리스크 구조 인식
AWARENESS = [
    ("대표자 리스크가 곧바로 법인 리스크로 이어질 수 있다", ["그렇다", "보통", "아니다"], {"그렇다": 0.0, "보통": 0.5, "아니다": 1.0}, 3),
    ("단일 사고 발생 시 회사가 버틸 수 있는 기간을 알고 있다", ["예", "아니오"],        {"예": 0.0, "아니오": 1.0},                  4),
    ("리스크 발생 시 대응 순서와 책임자가 정리되어 있다",       ["예", "아니오"],        {"예": 0.0, "아니오": 1.0},                  4),
]

# Ⅴ. 시나리오
SCENARIOS = [
    ("대표자가 6개월 이상 경영에서 이탈할 경우",
     ["큰 영향 없음", "부분적 영향", "경영 전반에 중대한 영향"],
     {"큰 영향 없음": 0.0, "부분적 영향": 0.5, "경영 전반에 중대한 영향": 1.0}, 5),
    ("핵심 인력 1~2명이 동시에 이탈할 경우",
     ["대응 가능", "일부 차질", "심각한 차질"],
     {"대응 가능": 0.0, "일부 차질": 0.5, "심각한 차질": 1.0}, 4),
    ("대규모 투자 또는 외부 충격 발생 시",
     ["내부 대응 가능", "단기 대응 필요", "구조적 대응 필요"],
     {"내부 대응 가능": 0.0, "단기 대응 필요": 0.5, "구조적 대응 필요": 1.0}, 4),
]

# 솔루션 매핑  –  키맨/법인/인식/시나리오 리스크별 추천
SOLUTIONS = [
    {"name": "대표자 리스크 관리", "icon": "👔", "color": "#9333ea",
     "desc": "CEO Plan · Key-Man 보험 등을 통해 대표자 유고·부적격 시 경영 연속성을 보장합니다.",
     "trigger": "keyman"},
    {"name": "종업원 단체보험", "icon": "👨‍👩‍👧‍👦", "color": "#ea580c",
     "desc": "핵심 인력 이탈·재해 시 기업 운영 안정을 위한 단체보험 설계.",
     "trigger": "corp"},
    {"name": "가업승계 컨설팅", "icon": "🏢", "color": "#ca8a04",
     "desc": "지분 이전·상속·증여를 체계적으로 구조화하여 세금 부담을 최소화합니다.",
     "trigger": "keyman"},
    {"name": "법인 절세 컨설팅", "icon": "📋", "color": "#16a34a",
     "desc": "법인·개인 재무 분리와 절세 구조를 정리하여 불필요한 세금 부담을 줄입니다.",
     "trigger": "keyman"},
    {"name": "현금흐름 & 위기대응", "icon": "📊", "color": "#0891b2",
     "desc": "현금흐름 변동성 대비와 단일 사고 대응 구조를 체계적으로 설계합니다.",
     "trigger": "corp"},
    {"name": "종합 재무컨설팅", "icon": "📈", "color": "#2563eb",
     "desc": "전체 리스크를 종합적으로 평가하여 최적의 구조 설계와 실행 계획을 제안합니다.",
     "trigger": "all"},
]

# ═══════════════════════════════════════════════════════════
# HELPER: 리스크 레벨
# ═══════════════════════════════════════════════════════════
def risk_level(pct):
    """pct = 리스크율(0~100). 높을수록 위험."""
    if pct <= 20: return "양호",  "#22c55e"
    if pct <= 45: return "주의",  "#ca8a04"
    if pct <= 70: return "경계",  "#ea580c"
    return               "위험",  "#dc2626"

def weight_color(w):
    return ["#64748b","#64748b","#3b82f6","#ca8a04","#ea580c","#dc2626"][w]

# ═══════════════════════════════════════════════════════════
# SCORING ENGINE
# ═══════════════════════════════════════════════════════════
def calc_scores(km_answers, cr_answers, aw_answers, sc_answers):
    """
    Returns dict with all KPIs.
    각 섹션별 가중평균 리스크율(0-100)과 전체 종합 리스크율을 계산.
    """
    # ── Keyman ──
    km_wt, km_wd = 0, 0.0
    km_items = []
    for i, (txt, w) in enumerate(KEYMAN):
        km_wt += w
        score = RESP_SCORE.get(km_answers[i], 0.0)
        km_wd += score * w
        km_items.append({"text": txt, "w": w, "score": score, "section": "대표자 리스크"})
    km_pct = (km_wd / km_wt * 100) if km_wt else 0

    # ── Corporate ──
    cr_wt, cr_wd = 0, 0.0
    cr_items = []
    for i, (txt, w) in enumerate(CORP):
        cr_wt += w
        score = RESP_SCORE.get(cr_answers[i], 0.0)
        cr_wd += score * w
        cr_items.append({"text": txt, "w": w, "score": score, "section": "법인 경영 리스크"})
    cr_pct = (cr_wd / cr_wt * 100) if cr_wt else 0

    # ── Awareness ──
    aw_wt, aw_wd = 0, 0.0
    aw_items = []
    for i, (txt, opts, smap, w) in enumerate(AWARENESS):
        aw_wt += w
        score = smap.get(aw_answers[i], 0.0)
        aw_wd += score * w
        aw_items.append({"text": txt, "w": w, "score": score, "section": "리스크 인식"})
    aw_pct = (aw_wd / aw_wt * 100) if aw_wt else 0

    # ── Scenario ──
    sc_wt, sc_wd = 0, 0.0
    sc_items = []
    for i, (txt, opts, smap, w) in enumerate(SCENARIOS):
        sc_wt += w
        score = smap.get(sc_answers[i], 0.0)
        sc_wd += score * w
        sc_items.append({"text": txt, "w": w, "score": score, "section": "시나리오"})
    sc_pct = (sc_wd / sc_wt * 100) if sc_wt else 0

    # ── 종합 ──
    total_wt = km_wt + cr_wt + aw_wt + sc_wt
    total_wd = km_wd + cr_wd + aw_wd + sc_wd
    total_pct = (total_wd / total_wt * 100) if total_wt else 0

    all_items = km_items + cr_items + aw_items + sc_items

    return {
        "km_pct": km_pct, "cr_pct": cr_pct, "aw_pct": aw_pct, "sc_pct": sc_pct,
        "total_pct": total_pct,
        "km_wt": km_wt, "cr_wt": cr_wt, "aw_wt": aw_wt, "sc_wt": sc_wt,
        "total_wt": total_wt,
        "all_items": all_items,
    }

# ═══════════════════════════════════════════════════════════
# PLOTLY CHART BUILDERS  (dark theme)
# ═══════════════════════════════════════════════════════════
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Noto Sans KR", color="#cbd5e1", size=11),
    margin=dict(l=10, r=10, t=10, b=10),
)

def fig_gauge(pct):
    """종합 리스크율 게이지"""
    lbl, clr = risk_level(pct)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number=dict(font=dict(size=28, color="#fff", family="Noto Sans KR"), suffix="%"),
        gauge=dict(
            axis=dict(range=[0, 100], tickvals=[0, 20, 45, 70, 100],
                      ticktext=["양호", "주의", "경계", "위험", ""],
                      tickfont=dict(size=9, color="#64748b")),
            bar=dict(color=clr, thickness=0.5),
            steps=[
                dict(range=[0, 20],  color="#1a2d4a"),
                dict(range=[20, 45], color="#1a2d4a"),
                dict(range=[45, 70], color="#1a2d4a"),
                dict(range=[70, 100],color="#1a2d4a"),
            ],
            threshold=dict(line=dict(color=clr, width=3), value=pct),
        )
    ))
    fig.update_layout(**PLOT_LAYOUT, height=220)
    fig.add_annotation(text=f"<b>{lbl}</b>", x=0.5, y=-0.08,
                       xref="paper", yref="paper", showarrow=False,
                       font=dict(size=14, color=clr, family="Noto Sans KR"))
    return fig

def fig_radar(km, cr, aw, sc):
    """4축 레이더 – 리스크율"""
    cats = ["대표자<br>리스크", "법인 경영<br>리스크", "리스크<br>인식", "시나리오"]
    vals = [km, cr, aw, sc]
    vals_closed = vals + [vals[0]]   # close the polygon
    cats_closed = cats + [cats[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals_closed, theta=cats_closed,
        fill="toself",
        fillcolor="rgba(220,38,38,0.15)",
        line=dict(color="#dc2626", width=2),
        marker=dict(size=6, color="#dc2626"),
        name="리스크율",
        hovertemplate="%{theta}<br>%{r:.0f}%<extra></extra>"
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickvals=[0, 25, 50, 75, 100],
                            gridcolor="#1e3a5f", tickfont=dict(size=8, color="#475569")),
            angularaxis=dict(gridcolor="#1e3a5f", tickfont=dict(size=10, color="#94a3b8")),
            bgcolor="rgba(0,0,0,0)"
        ),
        **PLOT_LAYOUT, height=260, showlegend=False
    )
    return fig

def fig_bars(km, cr, aw, sc):
    """카테고리별 수평 바"""
    cats  = ["시나리오", "리스크 인식", "법인 경영", "대표자"]
    vals  = [sc, aw, cr, km]
    colors = [risk_level(v)[1] for v in vals]

    fig = go.Figure(go.Bar(
        x=vals, y=cats, orientation="h",
        marker=dict(color=colors, line=dict(color=colors, width=0)),
        text=[f"{v:.0f}%" for v in vals],
        textposition="inside",
        textfont=dict(size=11, color="#fff"),
        hovertemplate="%{y}<br>리스크율: %{x:.0f}%<extra></extra>"
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 100], showgrid=True, gridcolor="#1e3a5f",
                   tickvals=[0, 25, 50, 75, 100], tickfont=dict(size=9, color="#64748b")),
        yaxis=dict(tickfont=dict(size=11, color="#94a3b8")),
        bargap=0.4,
        **PLOT_LAYOUT, height=180
    )
    return fig

# ═══════════════════════════════════════════════════════════
# SCRIPT GENERATION
# ═══════════════════════════════════════════════════════════
def build_script(info, scores, priority_items, sol_list):
    total_pct = scores["total_pct"]
    lbl, _ = risk_level(total_pct)
    co   = info.get("company","○○(주)")  or "○○(주)"
    ind  = info.get("industry","")        or "업종 미입력"
    emp  = info.get("employees","")       or "?"
    ceo  = info.get("ceo","대표자")       or "대표자"
    est  = info.get("est","")             or "미입력"
    rev  = info.get("revenue","")         or "미입력"

    lines = []
    lines.append("=" * 52)
    lines.append("   GFC 상담 스크립트  |  삼성생명 기업재무컨설팅")
    lines.append("   진단 기반 자동생성")
    lines.append("=" * 52)
    lines.append("")
    lines.append(f"  기업명    : {co}")
    lines.append(f"  업종      : {ind}")
    lines.append(f"  종업원 수 : {emp}명")
    lines.append(f"  대표자    : {ceo}")
    lines.append(f"  설립 연차 : {est}")
    lines.append(f"  연 매출   : {rev}")
    lines.append(f"  진단 충족율: {total_pct:.0f}% ({lbl})")
    lines.append(f"  생성일    : {datetime.now().strftime('%Y.%m.%d %H:%M')}")
    lines.append("")
    lines.append("─" * 52)
    lines.append(" 1. 도입 인사")
    lines.append("─" * 52)
    top_sec = priority_items[0]["section"] if priority_items else "주요 영역"
    lines.append(f"""
안녕하세요, {ceo}님. 삼성생명 GFC 기업재무컨설팅 담당 컨설턴트입니다.

오늘 귀사의 법인 리스크 사전 진단을 완료했는데,
종합 리스크율이 {total_pct:.0f}%({lbl}) 수준으로 나왔습니다.

특히 '{top_sec}' 부분에서 즉각적인 대비가 필요한
사항들이 도출되었습니다.

오늘 주요 내용을 안내드리고, 귀사에 맞는
종합 컨설팅 제안까지 함께 검토하겠습니다.
""")
    lines.append("─" * 52)
    lines.append(" 2. 리스크별 상세 상담")
    lines.append("─" * 52)

    # group by section
    from collections import OrderedDict
    grouped = OrderedDict()
    for it in priority_items:
        s = it["section"]
        grouped.setdefault(s, []).append(it)

    for sec, items in grouped.items():
        lines.append(f"\n▸ {sec} ({len(items)}건 해당)")
        lines.append("-" * 40)
        for it in items:
            lines.append(f"  📌 진단 항목 (가중치 {it['w']})")
            lines.append(f"     질문 : {it['text']}")
            lines.append(f"     응답 : {'예' if it['score']==1.0 else '일부 해당' if it['score']==0.5 else '아니오'}")
            lines.append("")

    lines.append("─" * 52)
    lines.append(" 3. 추천 솔루션 제안")
    lines.append("─" * 52)
    for s in sol_list:
        lines.append(f"\n  {s['icon']} {s['name']}")
        lines.append(f"     {s['desc']}")

    lines.append("\n─" * 26)
    lines.append(" 4. 마무리 및 다음 단계")
    lines.append("─" * 52)
    lines.append(f"""
오늘 진단 결과를 기반으로, 귀사에 맞는
'종합 법인 재무 컨설팅 제안서'를 별도로 작성하여 드리겠습니다.

세무사, 회계사, 법무사 등 전문가와 협업하여
최적의 구조를 설계드리고, 단계별 실행 계획까지
제안드리겠습니다.

다음 단계로 상세 제안서 검토 일정을 잡아드리면 되겠습니다.
언제 가능하신가요?
""")
    lines.append("=" * 52)
    return "\n".join(lines)

# ═══════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════
def main():
    st.set_page_config(
        page_title="Kⁱ⁰⁷ 삼성생명 GFC | 법인 리스크 사전 진단표",
        page_icon="⚖️",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown(DARK_CSS, unsafe_allow_html=True)

    # ── HEADER ──
    st.markdown("""
    <div class="gfc-header">
      <div class="gfc-live"><div class="gfc-live-dot"></div><span>삼성생명 GFC · 법인 리스크 사전 진단표</span></div>
      <h1>종합 기업 재무 컨설팅<br><span>AI 진단 및 스크립트 자동 생성</span></h1>
      <p>문항별 가중치(1~5)를 반영한 정량 평가 엔진과 분석 로직을 통해 법인 리스크를 진단하고,
         GFC 상담용 스크립트를 자동 생성합니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── TABS ──
    tab_diag, tab_dash, tab_script = st.tabs(["📋  진단", "📊  대시보드", "📝  스크립트"])

    # ════════════════════════════════════════════════════
    # TAB 1: 진단
    # ════════════════════════════════════════════════════
    with tab_diag:
        # ── Ⅰ. 기본 정보 ──
        with st.expander("⚙️  Ⅰ. 기본 정보 (Fact Check)", expanded=True):
            c1, c2 = st.columns(2)
            company  = c1.text_input("기업명", placeholder="예: ○○(주)", key="inp_co")
            industry = c2.text_input("업종", placeholder="예: 제조업", key="inp_in")
            c3, c4 = st.columns(2)
            ceo      = c3.text_input("대표자명", placeholder="예: 김○○", key="inp_ceo")
            est      = c4.selectbox("법인 설립 연차", ["─ 선택 ─", "5년 미만", "5~10년", "10~20년", "20년 이상"], key="sel_est")
            c5, c6 = st.columns(2)
            employees= c5.selectbox("임직원 수",     ["─ 선택 ─", "10명 미만", "10~30명", "30~100명", "100명 이상"], key="sel_emp")
            revenue  = c6.selectbox("연 매출 규모",  ["─ 선택 ─", "50억 미만", "50~100억", "100~300억", "300억 이상"], key="sel_rev")
            c7, c8 = st.columns(2)
            ceo_age  = c7.selectbox("대표자 연령대",  ["─ 선택 ─", "40대 이하", "50대", "60대 이상"], key="sel_age")
            ceo_share= c8.selectbox("대표자 지분율",  ["─ 선택 ─", "50% 미만", "50~80%", "80% 이상"], key="sel_shr")

        info = {
            "company": company, "industry": industry, "ceo": ceo,
            "est": est if est != "─ 선택 ─" else "",
            "employees": employees.replace("명","").replace("─ 선택 ─","") if employees != "─ 선택 ─" else "",
            "revenue": revenue if revenue != "─ 선택 ─" else "",
        }

        # ── Ⅱ. Key-Man Risk ──
        with st.expander("⚖️  Ⅱ. 대표자 리스크 진단 (Key-Man Risk)  ·  가중치 적용", expanded=True):
            st.markdown('<p style="color:#64748b;font-size:10.5px;margin:0 0 10px">아래 항목 중 현재 회사 상황에 가장 가까운 항목을 선택하세요. <span style="color:#dc2626">숫자 배지 = 가중치</span></p>', unsafe_allow_html=True)
            km_answers = []
            for i, (txt, w) in enumerate(KEYMAN):
                wc = weight_color(w)
                st.markdown(f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:3px"><span style="background:{wc};color:#fff;font-size:8px;font-weight:800;border-radius:3px;padding:1px 5px;flex-shrink:0">{w}</span><span style="font-size:12px;color:#cbd5e1">{txt}</span></div>', unsafe_allow_html=True)
                ans = st.radio("", RESP_OPTIONS, index=2, key=f"km_{i}", horizontal=True, label_visibility="hidden")
                km_answers.append(ans)
                st.markdown('<hr style="border:none;border-top:1px solid #1e3a5f;margin:6px 0">', unsafe_allow_html=True)

        # ── Ⅲ. Corporate Risk ──
        with st.expander("🏢  Ⅲ. 법인 경영 리스크 진단 (Corporate Risk)  ·  가중치 적용", expanded=True):
            st.markdown('<p style="color:#64748b;font-size:10.5px;margin:0 0 10px">아래 항목 중 현재 회사 상황에 가장 가까운 항목을 선택하세요. <span style="color:#dc2626">숫자 배지 = 가중치</span></p>', unsafe_allow_html=True)
            cr_answers = []
            for i, (txt, w) in enumerate(CORP):
                wc = weight_color(w)
                st.markdown(f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:3px"><span style="background:{wc};color:#fff;font-size:8px;font-weight:800;border-radius:3px;padding:1px 5px;flex-shrink:0">{w}</span><span style="font-size:12px;color:#cbd5e1">{txt}</span></div>', unsafe_allow_html=True)
                ans = st.radio("", RESP_OPTIONS, index=2, key=f"cr_{i}", horizontal=True, label_visibility="hidden")
                cr_answers.append(ans)
                st.markdown('<hr style="border:none;border-top:1px solid #1e3a5f;margin:6px 0">', unsafe_allow_html=True)

        # ── Ⅳ. 인식 점검 ──
        with st.expander("🧠  Ⅳ. 리스크 구조 인식 점검", expanded=True):
            st.markdown('<p style="color:#64748b;font-size:10.5px;margin:0 0 10px">현재 리스크 관리 수준에 대한 인식 점검입니다.</p>', unsafe_allow_html=True)
            aw_answers = []
            for i, (txt, opts, smap, w) in enumerate(AWARENESS):
                wc = weight_color(w)
                st.markdown(f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:3px"><span style="background:{wc};color:#fff;font-size:8px;font-weight:800;border-radius:3px;padding:1px 5px;flex-shrink:0">{w}</span><span style="font-size:12px;color:#cbd5e1">{txt}</span></div>', unsafe_allow_html=True)
                ans = st.radio("", opts, index=len(opts)-1, key=f"aw_{i}", horizontal=True, label_visibility="hidden")
                aw_answers.append(ans)
                st.markdown('<hr style="border:none;border-top:1px solid #1e3a5f;margin:6px 0">', unsafe_allow_html=True)

        # ── Ⅴ. 시나리오 ──
        with st.expander("🎯  Ⅴ. 시나리오 기반 점검", expanded=True):
            st.markdown('<p style="color:#64748b;font-size:10.5px;margin:0 0 10px">아래 상황이 발생할 경우를 가정해 보십시오.</p>', unsafe_allow_html=True)
            sc_answers = []
            for i, (txt, opts, smap, w) in enumerate(SCENARIOS):
                wc = weight_color(w)
                st.markdown(f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:3px"><span style="background:{wc};color:#fff;font-size:8px;font-weight:800;border-radius:3px;padding:1px 5px;flex-shrink:0">{w}</span><span style="font-size:12px;color:#cbd5e1">{i+1}. {txt}</span></div>', unsafe_allow_html=True)
                ans = st.radio("", opts, index=0, key=f"sc_{i}", horizontal=True, label_visibility="hidden")
                sc_answers.append(ans)
                st.markdown('<hr style="border:none;border-top:1px solid #1e3a5f;margin:6px 0">', unsafe_allow_html=True)

        # ── 저장 세션 ──
        st.session_state["info"]       = info
        st.session_state["km_answers"] = km_answers
        st.session_state["cr_answers"] = cr_answers
        st.session_state["aw_answers"] = aw_answers
        st.session_state["sc_answers"] = sc_answers

        scores = calc_scores(km_answers, cr_answers, aw_answers, sc_answers)
        st.session_state["scores"]     = scores

        # quick summary strip
        lbl, clr = risk_level(scores["total_pct"])
        st.markdown(f"""
        <div style="background:#111d2e;border:1px solid #1e3a5f;border-radius:8px;padding:12px 16px;
             display:flex;align-items:center;justify-content:center;gap:24px;margin-top:16px;flex-wrap:wrap">
          <div style="text-align:center">
            <div style="font-size:9px;color:#64748b;margin-bottom:2px;text-transform:uppercase;letter-spacing:.6px">종합 리스크율</div>
            <div style="font-size:26px;font-weight:800;color:{clr}">{scores['total_pct']:.0f}%</div>
            <div style="font-size:11px;font-weight:700;color:{clr}">{lbl}</div>
          </div>
          <div style="width:1px;height:50px;background:#1e3a5f"></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px 18px;font-size:10px;color:#64748b">
            <span>대표자 리스크: <strong style="color:#cbd5e1">{scores['km_pct']:.0f}%</strong></span>
            <span>법인 경영 리스크: <strong style="color:#cbd5e1">{scores['cr_pct']:.0f}%</strong></span>
            <span>리스크 인식: <strong style="color:#cbd5e1">{scores['aw_pct']:.0f}%</strong></span>
            <span>시나리오: <strong style="color:#cbd5e1">{scores['sc_pct']:.0f}%</strong></span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<p style="color:#60a5fa;font-size:10px;text-align:center;margin-top:6px">→ 대시보드 탭에서 상세 분석 확인</p>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════
    # TAB 2: 대시보드
    # ════════════════════════════════════════════════════
    with tab_dash:
        scores = st.session_state.get("scores", calc_scores(
            ["아니오"]*6, ["아니오"]*6, [AWARENESS[i][1][-1] for i in range(3)], [SCENARIOS[i][1][0] for i in range(3)]
        ))
        info = st.session_state.get("info", {})

        total_pct = scores["total_pct"]
        km_pct    = scores["km_pct"]
        cr_pct    = scores["cr_pct"]
        aw_pct    = scores["aw_pct"]
        sc_pct    = scores["sc_pct"]
        lbl, clr  = risk_level(total_pct)

        # ── KPI ROW ──
        st.markdown(f"""
        <div class="gfc-kpi-row">
          <div class="gfc-kpi">
            <div class="val" style="color:{clr}">{total_pct:.0f}%</div>
            <div class="lbl">종합 리스크율</div>
            <div style="font-size:10px;font-weight:700;color:{clr};margin-top:2px">{lbl}</div>
          </div>
          <div class="gfc-kpi">
            <div class="val" style="color:{risk_level(km_pct)[1]}">{km_pct:.0f}%</div>
            <div class="lbl">대표자 리스크</div>
          </div>
          <div class="gfc-kpi">
            <div class="val" style="color:{risk_level(cr_pct)[1]}">{cr_pct:.0f}%</div>
            <div class="lbl">법인 경영 리스크</div>
          </div>
          <div class="gfc-kpi">
            <div class="val" style="color:{risk_level(aw_pct)[1]}">{aw_pct:.0f}%</div>
            <div class="lbl">리스크 인식</div>
          </div>
          <div class="gfc-kpi">
            <div class="val" style="color:{risk_level(sc_pct)[1]}">{sc_pct:.0f}%</div>
            <div class="lbl">시나리오</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── CHARTS ROW ──
        c1, c2 = st.columns([1, 1], gap="small")
        with c1:
            st.markdown('<p style="color:#64748b;font-size:10px;text-align:center;margin:0 0 2px;font-weight:600;letter-spacing:.5px">종합 리스크 게이지</p>', unsafe_allow_html=True)
            st.plotly_chart(fig_gauge(total_pct), use_container_width=True, config={"displayModeBar": False})
        with c2:
            st.markdown('<p style="color:#64748b;font-size:10px;text-align:center;margin:0 0 2px;font-weight:600;letter-spacing:.5px">카테고리별 리스크 레이더</p>', unsafe_allow_html=True)
            st.plotly_chart(fig_radar(km_pct, cr_pct, aw_pct, sc_pct), use_container_width=True, config={"displayModeBar": False})

        st.markdown('<p style="color:#64748b;font-size:10px;margin:4px 0 2px;font-weight:600;letter-spacing:.5px">카테고리별 리스크율 비교</p>', unsafe_allow_html=True)
        st.plotly_chart(fig_bars(km_pct, cr_pct, aw_pct, sc_pct), use_container_width=True, config={"displayModeBar": False})

        # ── 우선 대응 항목 ──
        st.markdown('<p style="color:#fff;font-size:12px;font-weight:700;margin:16px 0 6px">🔥 우선 대응 항목 <span style="color:#64748b;font-size:9px;font-weight:500">(리스크율 > 0 인 항목 중 가중치 높은 5건)</span></p>', unsafe_allow_html=True)
        all_items = scores["all_items"]
        priority  = sorted([it for it in all_items if it["score"] > 0], key=lambda x: (-x["score"], -x["w"]))[:5]
        if not priority:
            st.markdown('<div class="gfc-empty">모든 항목 양호 🎉</div>', unsafe_allow_html=True)
        else:
            for i, it in enumerate(priority):
                wc = weight_color(it["w"])
                resp = "예" if it["score"]==1.0 else "일부 해당"
                st.markdown(f"""
                <div class="gfc-pri">
                  <span class="rk" style="color:{wc}">#{i+1}</span>
                  <div class="info">
                    <div class="cat">{it['section']}</div>
                    <div class="txt">{it['text']}</div>
                  </div>
                  <span class="wtag" style="background:{wc}">가중치 {it['w']}</span>
                  <span class="wtag" style="background:#475569">{resp}</span>
                </div>
                """, unsafe_allow_html=True)

        # ── 추천 솔루션 ──
        st.markdown('<p style="color:#fff;font-size:12px;font-weight:700;margin:16px 0 6px">💎 추천 솔루션 <span style="color:#64748b;font-size:9px;font-weight:500">(리스크 유형별 대응 제품)</span></p>', unsafe_allow_html=True)
        has_km = any(it["score"] > 0 and it["section"] == "대표자 리스크" for it in all_items)
        has_cr = any(it["score"] > 0 and it["section"] == "법인 경영 리스크" for it in all_items)
        has_any = any(it["score"] > 0 for it in all_items)
        sol_shown = []
        for s in SOLUTIONS:
            if s["trigger"] == "keyman" and has_km:
                sol_shown.append(s)
            elif s["trigger"] == "corp" and has_cr:
                sol_shown.append(s)
            elif s["trigger"] == "all" and has_any:
                sol_shown.append(s)
        if not sol_shown:
            st.markdown('<div class="gfc-empty">현재 추천 솔루션 없음 — 모든 항목 양호 🎉</div>', unsafe_allow_html=True)
        else:
            for s in sol_shown:
                st.markdown(f"""
                <div class="gfc-sol">
                  <span class="ico">{s['icon']}</span>
                  <div>
                    <div class="nm" style="color:{s['color']}">{s['name']}</div>
                    <div class="dc">{s['desc']}</div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

        st.session_state["priority"]  = priority
        st.session_state["sol_shown"] = sol_shown

    # ════════════════════════════════════════════════════
    # TAB 3: 스크립트
    # ════════════════════════════════════════════════════
    with tab_script:
        scores     = st.session_state.get("scores", {})
        info       = st.session_state.get("info", {})
        priority   = st.session_state.get("priority", [])
        sol_shown  = st.session_state.get("sol_shown", [])

        if not scores:
            st.markdown('<p style="color:#64748b;font-size:12px;text-align:center;padding:40px 0">먼저 진단 탭에서 답변을 입력해주세요.</p>', unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
              <div style="display:flex;align-items:center;gap:7px">
                <span style="font-size:17px">📝</span>
                <span style="font-size:15px;font-weight:700;color:#fff">GFC 상담 스크립트</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            script_text = build_script(info, scores, priority, sol_shown)

            # 생성 표시
            total_pct = scores.get("total_pct", 0)
            lbl, clr  = risk_level(total_pct)

            st.markdown(f"""
            <div class="gfc-script">
              <div class="sc-hdr">
                <h2>GFC 상담 스크립트</h2>
                <p>삼성생명 기업재무컨설팅 · 진단 기반 자동생성</p>
              </div>
              <div class="sc-meta">
                <span><strong>기업명:</strong> {info.get('company','○○(주)') or '○○(주)'}</span>
                <span><strong>업종:</strong> {info.get('industry','') or '미입력'}</span>
                <span><strong>종업원 수:</strong> {info.get('employees','') or '?'}명</span>
                <span><strong>대표자:</strong> {info.get('ceo','대표자') or '대표자'}</span>
                <span><strong>설립 연차:</strong> {info.get('est','') or '미입력'}</span>
                <span><strong>진단 충족율:</strong> <span style="color:{clr};font-weight:700">{total_pct:.0f}% ({lbl})</span></span>
              </div>

              <div class="sc-sec">1. 도입 인사</div>
              <div class="sc-intro">
                안녕하세요, {info.get('ceo','대표자') or '대표자'}님. 삼성생명 GFC 기업재무컨설팅 <strong>{(info.get('company','') or '○○(주)').replace('(주)','').replace('(유)','').replace('㈜','')}</strong> 담당 컨설턴트입니다.<br><br>
                오늘 귀사의 법인 리스크 사전 진단을 완료했는데, 종합 리스크율이 <strong style="color:{clr}">{total_pct:.0f}%({lbl})</strong> 수준으로 나왔습니다.<br>
                특히 <strong>'{priority[0]['section'] if priority else '주요 영역'}'</strong> 부분에서 즉각적인 대비가 필요한 사항들이 도출되었습니다.<br><br>
                오늘 주요 내용을 안내드리고, 귀사에 맞는 종합 컨설팅 제안까지 함께 검토하겠습니다.
              </div>
            """, unsafe_allow_html=True)

            # Risk blocks
            from collections import OrderedDict
            grouped = OrderedDict()
            for it in priority:
                grouped.setdefault(it["section"], []).append(it)

            if grouped:
                st.markdown('<div class="sc-sec" style="margin-top:14px">2. 리스크별 상세 상담</div>', unsafe_allow_html=True)
                for sec, items in grouped.items():
                    st.markdown(f'<div style="font-size:11px;font-weight:700;color:#fff;margin:10px 0 5px">▸ {sec} <span style="background:#475569;color:#fff;font-size:8px;font-weight:700;border-radius:3px;padding:1px 5px">{len(items)}건</span></div>', unsafe_allow_html=True)
                    for it in items:
                        wc = weight_color(it["w"])
                        resp = "예" if it["score"] == 1.0 else "일부 해당"
                        st.markdown(f"""
                        <div class="sc-block" style="border-color:{wc}">
                          <div class="bq">📌 진단 항목 (가중치 {it['w']}) — {it['section']}</div>
                          <div class="bt"><strong>질문:</strong> {it['text']}<br><strong>응답:</strong> {resp}</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Solutions
            if sol_shown:
                st.markdown('<div class="sc-sec" style="margin-top:14px">3. 추천 솔루션 제안</div>', unsafe_allow_html=True)
                for s in sol_shown:
                    st.markdown(f"""
                    <div style="display:flex;gap:7px;align-items:flex-start;margin-bottom:5px">
                      <span style="background:{s['color']};color:#fff;font-size:8px;font-weight:700;border-radius:3px;padding:2px 6px;white-space:nowrap;flex-shrink:0">{s['icon']} {s['name']}</span>
                      <span style="font-size:10.5px;color:#cbd5e1;line-height:1.6">{s['desc']}</span>
                    </div>
                    """, unsafe_allow_html=True)

            # Closing
            st.markdown(f"""
              <div class="sc-sec" style="margin-top:14px">4. 마무리 및 다음 단계</div>
              <div class="sc-close">
                오늘 진단 결과를 기반으로, 귀사에 맞는 <strong>종합 법인 재무 컨설팅 제안서</strong>를 별도로 작성하여 드리겠습니다.<br><br>
                세무사, 회계사, 법무사 등 전문가와 협업하여 <strong>최적의 구조</strong>를 설계드리고,
                삼성생명 GFC의 교육과 지원 체계와 함께 단계별 실행 계획까지 제안드리겠습니다.<br><br>
                다음 단계로 <strong>상세 제안서 검토 일정</strong>을 잡아드리면 되겠습니다. 언제 가능하신가요?
              </div>
            </div>
            """, unsafe_allow_html=True)

            # 복사용 텍스트 다운로드
            st.download_button(
                label="📥  스크립트 다운로드 (.txt)",
                data=script_text.encode("utf-8"),
                file_name=f"GFC_스크립트_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                help="스크립트를 텍스트 파일로 다운로드합니다."
            )
#            st.text_area("📋  클리핑용 텍스트", value=script_text, height=320, disabled=True, key="script_clip")


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()