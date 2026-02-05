"""
Kⁱ⁰⁷ 삼성생명 GFC | 법인 리스크 사전 진단표 v2.0 (Refactored)
Streamlit 기반 AI 진단 엔진 + KPI 대시보드 + AI 컨설턴트

주요 개선사항:
- 코드 구조 개선 및 모듈화
- 상수 및 설정 분리
- 재사용 가능한 컴포넌트 함수 추출
- 타입 힌트 추가
- 중복 코드 제거

설치: pip install streamlit plotly numpy
실행: streamlit run gfc_diagnosis_refactored.py
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import OrderedDict

# ═══════════════════════════════════════════════════════════
# CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════

@dataclass
class RiskLevel:
    """리스크 레벨 정의"""
    name: str
    color: str
    threshold: float

RISK_LEVELS = [
    RiskLevel("양호", "#22c55e", 20),
    RiskLevel("주의", "#ca8a04", 45),
    RiskLevel("경계", "#ea580c", 70),
    RiskLevel("위험", "#dc2626", 100),
]

WEIGHT_COLORS = {
    1: "#64748b",
    2: "#64748b", 
    3: "#3b82f6",
    4: "#ca8a04",
    5: "#ea580c",
}

RESPONSE_OPTIONS = ["예", "일부 해당", "아니오"]
RESPONSE_SCORES = {"예": 1.0, "일부 해당": 0.5, "아니오": 0.0}

# ═══════════════════════════════════════════════════════════
# DIAGNOSTIC DATA
# ═══════════════════════════════════════════════════════════

KEYMAN_QUESTIONS = [
    ("대표자 유고 시 의사결정 공백이 발생할 수 있다", 4),
    ("회사 주요 거래·의사결정이 대표자 개인에게 집중되어 있다", 5),
    ("대표자가 개인 보증을 서고 있다", 4),
    ("대표자 개인 재무와 법인 재무가 명확히 분리되어 있지 않다", 3),
    ("가업 승계 또는 지분 이전 계획이 명확하지 않다", 5),
    ("대표자 건강·사고 리스크에 대한 대비가 충분하지 않다", 5),
]

CORPORATE_QUESTIONS = [
    ("매출이 특정 거래처에 과도하게 집중되어 있다", 4),
    ("핵심 인력 이탈 시 업무 공백이 크다", 4),
    ("설비·투자 회수 구조가 장기적이거나 불확실하다", 3),
    ("현금흐름 변동성이 크다", 4),
    ("외부 환경 변화(환율·정책·시장)에 취약하다", 3),
    ("예상치 못한 사고 발생 시 즉각 대응 체계가 부족하다", 5),
]

AWARENESS_QUESTIONS = [
    ("대표자 리스크가 곧바로 법인 리스크로 이어질 수 있다", 
     ["그렇다", "보통", "아니다"], 
     {"그렇다": 0.0, "보통": 0.5, "아니다": 1.0}, 3),
    ("매출 중단이나 큰 사고 발생 시, 회사가 정상 운영을 유지할 수 있는 기간(비상자금)을 파악하고 있다", 
     ["예 (3개월 이상)", "대략 파악", "모름"], 
     {"예 (3개월 이상)": 0.0, "대략 파악": 0.5, "모름": 1.0}, 4),
    ("리스크 발생 시 대응 순서와 책임자가 정리되어 있다", 
     ["예", "아니오"], 
     {"예": 0.0, "아니오": 1.0}, 4),
]

SCENARIO_QUESTIONS = [
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

SOLUTIONS = [
    {
        "name": "대표자 리스크 관리",
        "icon": "👔",
        "color": "#9333ea",
        "desc": "CEO Plan · Key-Man 보험 등을 통해 대표자 유고·부적격 시 경영 연속성을 보장합니다.",
        "trigger": "keyman"
    },
    {
        "name": "종업원 단체보험",
        "icon": "👨‍👩‍👧‍👦",
        "color": "#ea580c",
        "desc": "핵심 인력 이탈·재해 시 기업 운영 안정을 위한 단체보험 설계.",
        "trigger": "corp"
    },
    {
        "name": "가업승계 컨설팅",
        "icon": "🏢",
        "color": "#ca8a04",
        "desc": "지분 이전·상속·증여를 체계적으로 구조화하여 세금 부담을 최소화합니다.",
        "trigger": "keyman"
    },
    {
        "name": "법인 절세 컨설팅",
        "icon": "📋",
        "color": "#16a34a",
        "desc": "법인·개인 재무 분리와 절세 구조를 정리하여 불필요한 세금 부담을 줄입니다.",
        "trigger": "keyman"
    },
    {
        "name": "현금흐름 & 위기대응",
        "icon": "📊",
        "color": "#0891b2",
        "desc": "현금흐름 변동성 대비와 단일 사고 대응 구조를 체계적으로 설계합니다.",
        "trigger": "corp"
    },
    {
        "name": "종합 재무컨설팅",
        "icon": "📈",
        "color": "#2563eb",
        "desc": "전체 리스크를 종합적으로 평가하여 최적의 구조 설계와 실행 계획을 제안합니다.",
        "trigger": "all"
    },
]

# ═══════════════════════════════════════════════════════════
# STYLES & UI COMPONENTS
# ═══════════════════════════════════════════════════════════

def load_dark_theme_css() -> str:
    """다크 테마 CSS 반환"""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800&display=swap');
    
    .stApp { 
        background: #0f1623 !important; 
        color: #cbd5e1 !important; 
        font-family: 'Noto Sans KR', sans-serif !important; 
    }
    
    .main .block-container { 
        padding-top: 8px !important; 
        padding-left: 18px !important; 
        padding-right: 18px !important; 
        max-width: 960px !important; 
        margin: 0 auto !important; 
    }
    
    .gfc-header { 
        background: linear-gradient(135deg, #0a1220 0%, #152238 55%, #1a2d4a 100%); 
        border-bottom: 1px solid #1e3a5f;
        padding: 24px 22px 20px; 
        border-radius: 0; 
        margin: -8px -18px 0; 
    }
    
    .gfc-header h1 { 
        color: #fff; 
        font-size: 22px; 
        font-weight: 800; 
        margin: 0; 
        line-height: 1.3; 
    }
    
    .gfc-header h1 span { 
        color: #60a5fa; 
    }
    
    .gfc-header p { 
        color: #64748b; 
        font-size: 11px; 
        margin: 6px 0 0; 
        line-height: 1.55; 
        max-width: 700px; 
    }
    
    .gfc-live { 
        display: inline-flex; 
        align-items: center; 
        gap: 6px; 
        margin-bottom: 8px; 
    }
    
    .gfc-live-dot { 
        width: 7px; 
        height: 7px; 
        border-radius: 50%; 
        background: #22c55e; 
        animation: pulse 2s infinite; 
    }
    
    .gfc-live span { 
        font-size: 10px; 
        color: #60a5fa; 
        font-weight: 700; 
        letter-spacing: 1.4px; 
        text-transform: uppercase; 
    }
    
    @keyframes pulse { 
        0%, 100% { opacity: 1 } 
        50% { opacity: 0.4 } 
    }
    
    div[data-testid="stTabs"] { 
        border-bottom: 1px solid #1e3a5f !important; 
    }
    
    button[data-testid="tab-btn"] { 
        background: none !important; 
        color: #64748b !important; 
        font-size: 12px !important; 
        font-weight: 600 !important; 
        border: none !important; 
        padding: 9px 14px !important; 
        border-bottom: 2px solid transparent !important; 
    }
    
    button[data-testid="tab-btn"][aria-selected="true"] { 
        color: #60a5fa !important; 
        border-bottom-color: #60a5fa !important; 
    }
    
    .streamlit-expander { 
        border: 1px solid #1e3a5f !important; 
        background: #111d2e !important; 
        border-radius: 8px !important; 
        margin-bottom: 5px !important; 
    }
    
    .streamlit-expander .streamlit-expander-header { 
        color: #fff !important; 
        font-weight: 700 !important; 
        font-size: 12.5px !important; 
    }
    
    .stSelectbox label, .stTextInput label { 
        color: #64748b !important; 
        font-size: 10px !important; 
        text-transform: uppercase; 
        letter-spacing: 0.7px; 
        font-weight: 700 !important; 
    }
    
    .stSelectbox > div > div { 
        background: #0f1a2a !important; 
        border: 1px solid #1e3a5f !important; 
        color: #fff !important; 
        border-radius: 6px !important; 
        font-size: 12.5px !important; 
    }
    
    .stTextInput > div > input { 
        background: #0f1a2a !important; 
        border: 1px solid #1e3a5f !important; 
        color: #fff !important; 
        border-radius: 6px !important; 
        font-size: 12.5px !important; 
    }
    
    .stTextInput > div > input:focus { 
        border-color: #60a5fa !important; 
        box-shadow: none !important; 
    }
    
    .stTextInput > div > input::placeholder { 
        color: #475569 !important; 
    }
    
    .stRadio label { 
        color: #cbd5e1 !important; 
        font-size: 11.5px !important; 
    }
    
    .stRadio > div > div label { 
        color: #cbd5e1 !important; 
        font-size: 11.5px !important; 
    }
    
    .gfc-kpi-row { 
        display: flex; 
        gap: 10px; 
        flex-wrap: wrap; 
        margin-bottom: 12px; 
    }
    
    .gfc-kpi { 
        background: #131f33; 
        border: 1px solid #1e3a5f; 
        border-radius: 10px; 
        padding: 14px 16px; 
        flex: 1; 
        min-width: 130px; 
        text-align: center; 
    }
    
    .gfc-kpi .val { 
        font-size: 24px; 
        font-weight: 800; 
        line-height: 1; 
        margin-bottom: 3px; 
    }
    
    .gfc-kpi .lbl { 
        font-size: 9.5px; 
        color: #64748b; 
        font-weight: 600; 
    }
    
    .gfc-pri { 
        background: #131f33; 
        border: 1px solid #1e3a5f; 
        border-radius: 7px; 
        padding: 8px 10px; 
        display: flex; 
        align-items: flex-start; 
        gap: 8px; 
        margin-bottom: 4px; 
    }
    
    .gfc-pri .rk { 
        font-size: 11px; 
        font-weight: 800; 
        color: #64748b; 
        width: 18px; 
        text-align: center; 
        flex-shrink: 0; 
    }
    
    .gfc-pri .info { 
        flex: 1; 
        min-width: 0; 
    }
    
    .gfc-pri .cat { 
        font-size: 9px; 
        color: #64748b; 
        margin-bottom: 1px; 
    }
    
    .gfc-pri .txt { 
        font-size: 10.5px; 
        color: #cbd5e1; 
    }
    
    .gfc-pri .wtag { 
        font-size: 8px; 
        font-weight: 700; 
        color: #fff; 
        border-radius: 3px; 
        padding: 1px 5px; 
        flex-shrink: 0; 
    }
    
    .gfc-sol { 
        background: #131f33; 
        border: 1px solid #1e3a5f; 
        border-radius: 8px; 
        padding: 10px 12px; 
        display: flex; 
        align-items: flex-start; 
        gap: 8px; 
        margin-bottom: 5px; 
    }
    
    .gfc-sol .ico { 
        font-size: 18px; 
        flex-shrink: 0; 
    }
    
    .gfc-sol .nm { 
        font-size: 11px; 
        font-weight: 700; 
        color: #fff; 
        margin-bottom: 2px; 
    }
    
    .gfc-sol .dc { 
        font-size: 9.5px; 
        color: #64748b; 
        line-height: 1.45; 
    }
    
    .gfc-script { 
        background: #1a2736; 
        border: 1px solid #2a4a6b; 
        border-top: 2px solid #ca8a04; 
        border-radius: 10px; 
        padding: 22px 24px; 
        margin-top: 8px; 
    }
    
    .gfc-script .sc-hdr { 
        text-align: center; 
        border-bottom: 1px solid #2a4a6b; 
        padding-bottom: 12px; 
        margin-bottom: 16px; 
    }
    
    .gfc-script .sc-hdr h2 { 
        color: #fff; 
        font-size: 15px; 
        font-weight: 800; 
        margin: 0; 
    }
    
    .gfc-script .sc-hdr p { 
        color: #ca8a04; 
        font-size: 9.5px; 
        margin: 3px 0 0; 
        font-weight: 600; 
        letter-spacing: 1px; 
    }
    
    .gfc-script .sc-meta { 
        display: grid; 
        grid-template-columns: 1fr 1fr; 
        gap: 3px 14px; 
        margin-bottom: 14px; 
        font-size: 10.5px; 
        color: #64748b; 
    }
    
    .gfc-script .sc-meta strong { 
        color: #fff; 
        font-weight: 600; 
    }
    
    .gfc-script .sc-sec { 
        font-size: 10.5px; 
        font-weight: 700; 
        color: #ca8a04; 
        letter-spacing: 0.3px; 
        margin: 14px 0 6px; 
        display: flex; 
        align-items: center; 
        gap: 6px; 
    }
    
    .gfc-script .sc-sec::after { 
        content: ''; 
        flex: 1; 
        height: 1px; 
        background: #2a4a6b; 
    }
    
    .gfc-script .sc-intro { 
        background: #151f30; 
        border-left: 3px solid #60a5fa; 
        border-radius: 6px; 
        padding: 14px 16px; 
        font-size: 11.5px; 
        color: #cbd5e1; 
        line-height: 1.9; 
    }
    
    .gfc-script .sc-block { 
        background: #151f30; 
        border-left: 2px solid; 
        border-radius: 5px; 
        padding: 9px 12px; 
        margin-bottom: 4px; 
    }
    
    .gfc-script .sc-block .bq { 
        font-size: 9.5px; 
        color: #94a3b8; 
        margin-bottom: 2px; 
    }
    
    .gfc-script .sc-block .bt { 
        font-size: 10.5px; 
        color: #cbd5e1; 
        line-height: 1.6; 
    }
    
    .gfc-script .sc-close { 
        background: #151f30; 
        border-left: 3px solid #22c55e; 
        border-radius: 6px; 
        padding: 14px 16px; 
        font-size: 11px; 
        color: #cbd5e1; 
        line-height: 1.85; 
        margin-top: 6px; 
    }
    
    .gfc-empty { 
        color: #22c55e; 
        font-size: 11px; 
        text-align: center; 
        padding: 10px; 
    }
    </style>
    """

def render_header():
    """앱 헤더 렌더링"""
    st.markdown("""
    <div class="gfc-header">
      <div class="gfc-live">
        <div class="gfc-live-dot"></div>
        <span>삼성생명 GFC · 법인 리스크 사전 진단표 v2.0</span>
      </div>
      <h1>종합 기업 재무 컨설팅<br><span>AI 진단 엔진 + 데이터 기반 컨설팅</span></h1>
      <p>문항별 가중치(1~5)를 반영한 정량 평가 엔진과 분석 로직을 통해 법인 리스크를 진단하고,
         GFC 상담용 스크립트 및 AI 컨설턴트 분석을 자동 생성합니다. | Powered by K¹⁰⁷ XAI</p>
    </div>
    """, unsafe_allow_html=True)

def render_question_with_weight(text: str, weight: int, index: int, key_prefix: str, 
                                 options: List[str] = None) -> str:
    """가중치 배지가 포함된 질문 렌더링"""
    color = WEIGHT_COLORS.get(weight, "#64748b")
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:3px">'
        f'<span style="background:{color};color:#fff;font-size:8px;font-weight:800;'
        f'border-radius:3px;padding:1px 5px;flex-shrink:0">{weight}</span>'
        f'<span style="font-size:12px;color:#cbd5e1">{text}</span></div>',
        unsafe_allow_html=True
    )
    
    options = options or RESPONSE_OPTIONS
    answer = st.radio(
        "", 
        options, 
        index=len(options) - 1, 
        key=f"{key_prefix}_{index}", 
        horizontal=True, 
        label_visibility="hidden"
    )
    st.markdown('<hr style="border:none;border-top:1px solid #1e3a5f;margin:6px 0">', 
                unsafe_allow_html=True)
    return answer

def render_priority_item(item: Dict, rank: int):
    """우선 대응 항목 렌더링"""
    color = WEIGHT_COLORS.get(item["w"], "#64748b")
    response = "예" if item["score"] == 1.0 else "일부 해당"
    
    st.markdown(f"""
    <div class="gfc-pri">
      <span class="rk" style="color:{color}">#{rank}</span>
      <div class="info">
        <div class="cat">{item['section']}</div>
        <div class="txt">{item['text']}</div>
      </div>
      <span class="wtag" style="background:{color}">가중치 {item['w']}</span>
      <span class="wtag" style="background:#475569">{response}</span>
    </div>
    """, unsafe_allow_html=True)

def render_solution_card(solution: Dict):
    """솔루션 카드 렌더링"""
    st.markdown(f"""
    <div class="gfc-sol">
      <span class="ico">{solution['icon']}</span>
      <div>
        <div class="nm" style="color:{solution['color']}">{solution['name']}</div>
        <div class="dc">{solution['desc']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# BUSINESS LOGIC
# ═══════════════════════════════════════════════════════════

def get_risk_level(percentage: float) -> Tuple[str, str]:
    """리스크율에 따른 레벨과 색상 반환"""
    for level in RISK_LEVELS:
        if percentage <= level.threshold:
            return level.name, level.color
    return RISK_LEVELS[-1].name, RISK_LEVELS[-1].color

def calculate_section_score(questions: List[Tuple], answers: List[str], 
                            section_name: str, score_map: Dict = None) -> Tuple[float, List[Dict]]:
    """섹션별 리스크율 및 아이템 계산"""
    score_map = score_map or RESPONSE_SCORES
    total_weight = 0
    weighted_sum = 0
    items = []
    
    for i, (text, weight) in enumerate(questions):
        total_weight += weight
        score = score_map.get(answers[i], 0.0)
        weighted_sum += score * weight
        
        items.append({
            "text": text,
            "w": weight,
            "score": score,
            "section": section_name
        })
    
    percentage = (weighted_sum / total_weight * 100) if total_weight > 0 else 0
    return percentage, items

def calculate_custom_section_score(questions: List[Tuple], answers: List[str], 
                                   section_name: str) -> Tuple[float, List[Dict]]:
    """커스텀 스코어맵을 사용하는 섹션 계산 (Awareness, Scenario)"""
    total_weight = 0
    weighted_sum = 0
    items = []
    
    for i, (text, options, score_map, weight) in enumerate(questions):
        total_weight += weight
        score = score_map.get(answers[i], 0.0)
        weighted_sum += score * weight
        
        items.append({
            "text": text,
            "w": weight,
            "score": score,
            "section": section_name
        })
    
    percentage = (weighted_sum / total_weight * 100) if total_weight > 0 else 0
    return percentage, items

def calculate_all_scores(km_answers: List[str], cr_answers: List[str], 
                        aw_answers: List[str], sc_answers: List[str]) -> Dict:
    """전체 리스크 점수 계산"""
    # 각 섹션별 계산
    km_pct, km_items = calculate_section_score(KEYMAN_QUESTIONS, km_answers, "대표자 리스크")
    cr_pct, cr_items = calculate_section_score(CORPORATE_QUESTIONS, cr_answers, "법인 경영 리스크")
    aw_pct, aw_items = calculate_custom_section_score(AWARENESS_QUESTIONS, aw_answers, "리스크 인식")
    sc_pct, sc_items = calculate_custom_section_score(SCENARIO_QUESTIONS, sc_answers, "시나리오")
    
    # 가중치 합산
    km_wt = sum(w for _, w in KEYMAN_QUESTIONS)
    cr_wt = sum(w for _, w in CORPORATE_QUESTIONS)
    aw_wt = sum(q[3] for q in AWARENESS_QUESTIONS)
    sc_wt = sum(q[3] for q in SCENARIO_QUESTIONS)
    total_wt = km_wt + cr_wt + aw_wt + sc_wt
    
    # 종합 리스크율 (가중평균)
    total_pct = (km_pct * km_wt + cr_pct * cr_wt + aw_pct * aw_wt + sc_pct * sc_wt) / total_wt if total_wt > 0 else 0
    
    return {
        "km_pct": km_pct,
        "cr_pct": cr_pct,
        "aw_pct": aw_pct,
        "sc_pct": sc_pct,
        "total_pct": total_pct,
        "km_wt": km_wt,
        "cr_wt": cr_wt,
        "aw_wt": aw_wt,
        "sc_wt": sc_wt,
        "total_wt": total_wt,
        "all_items": km_items + cr_items + aw_items + sc_items,
    }

def get_priority_items(all_items: List[Dict], limit: int = 5) -> List[Dict]:
    """우선 대응 항목 추출"""
    risky_items = [item for item in all_items if item["score"] > 0]
    return sorted(risky_items, key=lambda x: (-x["score"], -x["w"]))[:limit]

def get_recommended_solutions(all_items: List[Dict]) -> List[Dict]:
    """추천 솔루션 필터링"""
    has_keyman = any(item["score"] > 0 and item["section"] == "대표자 리스크" for item in all_items)
    has_corp = any(item["score"] > 0 and item["section"] == "법인 경영 리스크" for item in all_items)
    has_any = any(item["score"] > 0 for item in all_items)
    
    recommended = []
    for solution in SOLUTIONS:
        if solution["trigger"] == "keyman" and has_keyman:
            recommended.append(solution)
        elif solution["trigger"] == "corp" and has_corp:
            recommended.append(solution)
        elif solution["trigger"] == "all" and has_any:
            recommended.append(solution)
    
    return recommended

# ═══════════════════════════════════════════════════════════
# CHART GENERATION
# ═══════════════════════════════════════════════════════════

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Noto Sans KR", color="#cbd5e1", size=11),
    margin=dict(l=10, r=10, t=10, b=10),
)

def create_gauge_chart(percentage: float) -> go.Figure:
    """종합 리스크율 게이지 차트"""
    label, color = get_risk_level(percentage)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        number=dict(font=dict(size=28, color="#fff", family="Noto Sans KR"), suffix="%"),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickvals=[0, 20, 45, 70, 100],
                ticktext=["양호", "주의", "경계", "위험", ""],
                tickfont=dict(size=9, color="#64748b")
            ),
            bar=dict(color=color, thickness=0.5),
            bgcolor="#1a2736",
            steps=[
                dict(range=[0, 20], color="#1a2e3d"),
                dict(range=[20, 45], color="#1f3040"),
                dict(range=[45, 70], color="#261f2e"),
                dict(range=[70, 100], color="#2a1a1a"),
            ],
            threshold=dict(line=dict(color=color, width=3), value=percentage),
        )
    ))
    
    layout_config = {**PLOT_LAYOUT, 'height': 235, 'margin': dict(l=40, r=40, t=10, b=10)}
    fig.update_layout(**layout_config)
    fig.add_annotation(
        text=f"<b>{label}</b>",
        x=0.5, y=-0.01,
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=14, color=color, family="Noto Sans KR")
    )
    return fig

def create_radar_chart(km: float, cr: float, aw: float, sc: float) -> go.Figure:
    """4축 레이더 차트"""
    categories = ["대표자<br>리스크", "법인 경영<br>리스크", "리스크 인식<br>부족", "시나리오<br>대응 미흡"]
    values = [km, cr, aw, sc]
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        fillcolor="rgba(220,38,38,0.15)",
        line=dict(color="#dc2626", width=2),
        marker=dict(size=6, color="#dc2626"),
        name="리스크율",
        hovertemplate="%{theta}<br>%{r:.0f}%<extra></extra>"
    ))
    
    layout_config = {**PLOT_LAYOUT}
    layout_config.update({
        'polar': dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                gridcolor="#1e3a5f",
                tickfont=dict(size=8, color="#475569")
            ),
            angularaxis=dict(
                gridcolor="#1e3a5f",
                tickfont=dict(size=11, color="#94a3b8"),
                rotation=0
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        'height': 290,
        'margin': dict(l=70, r=80, t=20, b=20),
        'showlegend': False
    })
    fig.update_layout(**layout_config)
    return fig

def create_bar_chart(km: float, cr: float, aw: float, sc: float) -> go.Figure:
    """카테고리별 수평 바 차트"""
    categories = ["시나리오 대응 미흡", "리스크 인식 부족", "법인 경영", "대표자"]
    values = [sc, aw, cr, km]
    colors = [get_risk_level(v)[1] for v in values]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation="h",
        marker=dict(color=colors, line=dict(color=colors, width=0)),
        text=[f"{v:.0f}%" for v in values],
        textposition="inside",
        textfont=dict(size=11, color="#fff"),
        hovertemplate="%{y}<br>리스크율: %{x:.0f}%<extra></extra>"
    ))
    
    fig.update_layout(
        xaxis=dict(
            range=[0, 100],
            showgrid=True,
            gridcolor="#1e3a5f",
            tickvals=[0, 25, 50, 75, 100],
            tickfont=dict(size=9, color="#64748b")
        ),
        yaxis=dict(tickfont=dict(size=11, color="#94a3b8")),
        bargap=0.4,
        **PLOT_LAYOUT,
        height=180
    )
    return fig

# ═══════════════════════════════════════════════════════════
# SCRIPT & CONSULTANT GENERATION
# ═══════════════════════════════════════════════════════════

def generate_consultation_script(info: Dict, scores: Dict, priority_items: List[Dict], 
                                 solutions: List[Dict]) -> str:
    """상담 스크립트 생성"""
    total_pct = scores["total_pct"]
    label, _ = get_risk_level(total_pct)
    
    company = info.get("company", "WOORI(주)") or "WOORI(주)"
    industry = info.get("industry", "") or "업종 미입력"
    employees = info.get("employees", "") or "?"
    ceo = info.get("ceo", "대표자") or "대표자"
    est = info.get("est", "") or "미입력"
    revenue = info.get("revenue", "") or "미입력"
    
    lines = [
        "=" * 52,
        "   GFC 상담 스크립트  |  삼성생명 기업재무컨설팅",
        "   진단 기반 자동생성",
        "=" * 52,
        "",
        f"  기업명    : {company}",
        f"  업종      : {industry}",
        f"  종업원 수 : {employees}명",
        f"  대표자    : {ceo}",
        f"  설립 연차 : {est}",
        f"  연 매출   : {revenue}",
        f"  진단 충족율: {total_pct:.0f}% ({label})",
        f"  생성일    : {datetime.now().strftime('%Y.%m.%d %H:%M')}",
        "",
        "─" * 52,
        " 1. 도입 인사",
        "─" * 52,
    ]
    
    top_section = priority_items[0]["section"] if priority_items else "주요 영역"
    lines.append(f"""
안녕하세요, {ceo}님. 삼성생명 GFC 기업재무컨설팅 담당 컨설턴트입니다.

오늘 귀사의 법인 리스크 사전 진단을 완료했는데,
종합 리스크율이 {total_pct:.0f}%({label}) 수준으로 나왔습니다.

특히 '{top_section}' 부분에서 즉각적인 대비가 필요한
사항들이 도출되었습니다.

오늘 주요 내용을 안내드리고, 귀사에 맞는
종합 컨설팅 제안까지 함께 검토하겠습니다.
""")
    
    lines.extend(["─" * 52, " 2. 리스크별 상세 상담", "─" * 52])
    
    # 섹션별 그룹화
    grouped = OrderedDict()
    for item in priority_items:
        section = item["section"]
        grouped.setdefault(section, []).append(item)
    
    for section, items in grouped.items():
        lines.append(f"\n▸ {section} ({len(items)}건 해당)")
        lines.append("-" * 40)
        for item in items:
            response = "예" if item['score'] == 1.0 else "일부 해당" if item['score'] == 0.5 else "아니오"
            lines.append(f"  📌 진단 항목 (가중치 {item['w']})")
            lines.append(f"     질문 : {item['text']}")
            lines.append(f"     응답 : {response}")
            lines.append("")
    
    lines.extend(["─" * 52, " 3. 추천 솔루션 제안", "─" * 52])
    for solution in solutions:
        lines.append(f"\n  {solution['icon']} {solution['name']}")
        lines.append(f"     {solution['desc']}")
    
    lines.extend(["\n" + "─" * 52, " 4. 마무리 및 다음 단계", "─" * 52])
    lines.append("""
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
# TAB RENDERERS
# ═══════════════════════════════════════════════════════════

def render_diagnostic_tab():
    """진단 탭 렌더링"""
    # Ⅰ. 기본 정보
    with st.expander("⚙️  Ⅰ. 기본 정보 (Fact Check)", expanded=True):
        c1, c2 = st.columns(2)
        company = c1.text_input("기업명", placeholder="예: WOORI(주)", key="inp_co")
        industry = c2.text_input("업종", placeholder="예: 제조업", key="inp_in")
        
        c3, c4 = st.columns(2)
        ceo = c3.text_input("대표자명", placeholder="예: 김흥해", key="inp_ceo")
        est = c4.selectbox("법인 설립 연차", 
                          ["─ 선택 ─", "5년 미만", "5~10년", "10~20년", "20년 이상"], 
                          key="sel_est")
        
        c5, c6 = st.columns(2)
        employees = c5.selectbox("임직원 수", 
                                ["─ 선택 ─", "10명 미만", "10~30명", "30~100명", "100명 이상"], 
                                key="sel_emp")
        revenue = c6.selectbox("연 매출 규모", 
                              ["─ 선택 ─", "50억 미만", "50~100억", "100~300억", "300억 이상"], 
                              key="sel_rev")
        
        c7, c8 = st.columns(2)
        c7.selectbox("대표자 연령대", ["─ 선택 ─", "40대 이하", "50대", "60대 이상"], key="sel_age")
        c8.selectbox("대표자 지분율", ["─ 선택 ─", "50% 미만", "50~80%", "80% 이상"], key="sel_shr")
    
    info = {
        "company": company,
        "industry": industry,
        "ceo": ceo,
        "est": est if est != "─ 선택 ─" else "",
        "employees": employees.replace("명", "").replace("─ 선택 ─", "") if employees != "─ 선택 ─" else "",
        "revenue": revenue if revenue != "─ 선택 ─" else "",
    }
    
    # Ⅱ. Key-Man Risk
    with st.expander("⚖️  Ⅱ. 대표자 리스크 진단 (Key-Man Risk)  ·  가중치 적용", expanded=True):
        st.markdown(
            '<p style="color:#64748b;font-size:10.5px;margin:0 0 10px">'
            '아래 항목 중 현재 회사 상황에 가장 가까운 항목을 선택하세요. '
            '<span style="color:#dc2626">숫자 배지 = 가중치</span></p>',
            unsafe_allow_html=True
        )
        km_answers = [
            render_question_with_weight(text, weight, i, "km")
            for i, (text, weight) in enumerate(KEYMAN_QUESTIONS)
        ]
    
    # Ⅲ. Corporate Risk
    with st.expander("🏢  Ⅲ. 법인 경영 리스크 진단 (Corporate Risk)  ·  가중치 적용", expanded=True):
        st.markdown(
            '<p style="color:#64748b;font-size:10.5px;margin:0 0 10px">'
            '아래 항목 중 현재 회사 상황에 가장 가까운 항목을 선택하세요. '
            '<span style="color:#dc2626">숫자 배지 = 가중치</span></p>',
            unsafe_allow_html=True
        )
        cr_answers = [
            render_question_with_weight(text, weight, i, "cr")
            for i, (text, weight) in enumerate(CORPORATE_QUESTIONS)
        ]
    
    # Ⅳ. 인식 점검
    with st.expander("🧠  Ⅳ. 리스크 대응 준비도 점검", expanded=True):
        st.markdown(
            '<p style="color:#64748b;font-size:10.5px;margin:0 0 10px">'
            '우리 회사의 위기 대응 능력과 준비 수준을 점검합니다.</p>',
            unsafe_allow_html=True
        )
        aw_answers = [
            render_question_with_weight(text, weight, i, "aw", options)
            for i, (text, options, _, weight) in enumerate(AWARENESS_QUESTIONS)
        ]
    
    # Ⅴ. 시나리오
    with st.expander("🎯  Ⅴ. 시나리오 기반 점검", expanded=True):
        st.markdown(
            '<p style="color:#64748b;font-size:10.5px;margin:0 0 10px">'
            '아래 상황이 발생할 경우를 가정해 보십시오.</p>',
            unsafe_allow_html=True
        )
        sc_answers = []
        for i, (text, options, _, weight) in enumerate(SCENARIO_QUESTIONS):
            color = WEIGHT_COLORS.get(weight, "#64748b")
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:3px">'
                f'<span style="background:{color};color:#fff;font-size:8px;font-weight:800;'
                f'border-radius:3px;padding:1px 5px;flex-shrink:0">{weight}</span>'
                f'<span style="font-size:12px;color:#cbd5e1">{i+1}. {text}</span></div>',
                unsafe_allow_html=True
            )
            answer = st.radio("", options, index=0, key=f"sc_{i}", horizontal=True, 
                            label_visibility="hidden")
            sc_answers.append(answer)
            st.markdown('<hr style="border:none;border-top:1px solid #1e3a5f;margin:6px 0">', 
                       unsafe_allow_html=True)
    
    # 세션에 저장
    st.session_state.update({
        "info": info,
        "km_answers": km_answers,
        "cr_answers": cr_answers,
        "aw_answers": aw_answers,
        "sc_answers": sc_answers,
        "scores": calculate_all_scores(km_answers, cr_answers, aw_answers, sc_answers)
    })
    
    # Quick summary
    scores = st.session_state["scores"]
    label, color = get_risk_level(scores["total_pct"])
    
    st.markdown(f"""
    <div style="background:#111d2e;border:1px solid #1e3a5f;border-radius:8px;padding:12px 16px;
         display:flex;align-items:center;justify-content:center;gap:24px;margin-top:16px;flex-wrap:wrap">
      <div style="text-align:center">
        <div style="font-size:9px;color:#64748b;margin-bottom:2px;text-transform:uppercase;letter-spacing:.6px">
          종합 리스크율
        </div>
        <div style="font-size:26px;font-weight:800;color:{color}">{scores['total_pct']:.0f}%</div>
        <div style="font-size:11px;font-weight:700;color:{color}">{label}</div>
      </div>
      <div style="width:1px;height:50px;background:#1e3a5f"></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px 18px;font-size:10px;color:#64748b">
        <span>대표자 리스크: <strong style="color:#cbd5e1">{scores['km_pct']:.0f}%</strong></span>
        <span>법인 경영 리스크: <strong style="color:#cbd5e1">{scores['cr_pct']:.0f}%</strong></span>
        <span>리스크 인식 부족: <strong style="color:#cbd5e1">{scores['aw_pct']:.0f}%</strong></span>
        <span>시나리오 대응 미흡: <strong style="color:#cbd5e1">{scores['sc_pct']:.0f}%</strong></span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#60a5fa;font-size:10px;text-align:center;margin-top:6px">'
        '→ 대시보드 탭에서 상세 분석 확인</p>',
        unsafe_allow_html=True
    )

def render_dashboard_tab():
    """대시보드 탭 렌더링"""
    # 기본값 설정
    default_scores = calculate_all_scores(
        ["아니오"] * len(KEYMAN_QUESTIONS),
        ["아니오"] * len(CORPORATE_QUESTIONS),
        [q[1][-1] for q in AWARENESS_QUESTIONS],
        [q[1][0] for q in SCENARIO_QUESTIONS]
    )
    
    scores = st.session_state.get("scores", default_scores)
    
    # KPI 카드
    total_pct = scores["total_pct"]
    label, color = get_risk_level(total_pct)
    
    st.markdown(f"""
    <div class="gfc-kpi-row">
      <div class="gfc-kpi">
        <div class="val" style="color:{color}">{total_pct:.0f}%</div>
        <div class="lbl">종합 리스크율</div>
        <div style="font-size:10px;font-weight:700;color:{color};margin-top:2px">{label}</div>
      </div>
      <div class="gfc-kpi">
        <div class="val" style="color:{get_risk_level(scores['km_pct'])[1]}">{scores['km_pct']:.0f}%</div>
        <div class="lbl">대표자 리스크</div>
      </div>
      <div class="gfc-kpi">
        <div class="val" style="color:{get_risk_level(scores['cr_pct'])[1]}">{scores['cr_pct']:.0f}%</div>
        <div class="lbl">법인 경영 리스크</div>
      </div>
      <div class="gfc-kpi">
        <div class="val" style="color:{get_risk_level(scores['aw_pct'])[1]}">{scores['aw_pct']:.0f}%</div>
        <div class="lbl">리스크 인식 부족</div>
      </div>
      <div class="gfc-kpi">
        <div class="val" style="color:{get_risk_level(scores['sc_pct'])[1]}">{scores['sc_pct']:.0f}%</div>
        <div class="lbl">시나리오 대응 미흡</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("", unsafe_allow_html=True)
    st.markdown("", unsafe_allow_html=True)
    
    # 차트
    c1, c2 = st.columns([1, 1], gap="medium")
    with c1:
        st.markdown(
            '<p style="color:#64748b;font-size:10px;text-align:center;margin:0 0 2px;'
            'font-weight:600;letter-spacing:.5px">종합 리스크 게이지</p>',
            unsafe_allow_html=True
        )
        st.plotly_chart(create_gauge_chart(total_pct), use_container_width=True, 
                       config={"displayModeBar": False})
    
    with c2:
        st.markdown(
            '<p style="color:#64748b;font-size:10px;text-align:center;margin:0 0 2px;'
            'font-weight:600;letter-spacing:.5px">카테고리별 리스크 레이더</p>',
            unsafe_allow_html=True
        )
        st.plotly_chart(
            create_radar_chart(scores['km_pct'], scores['cr_pct'], scores['aw_pct'], scores['sc_pct']),
            use_container_width=True,
            config={"displayModeBar": False}
        )
        st.markdown(
            '<p style="color:#64748b;font-size:8.5px;text-align:center;margin-top:-8px">'
            '💡 모든 지표는 점수가 낮을수록 안전합니다</p>',
            unsafe_allow_html=True
        )
    
    st.markdown(
        '<p style="color:#64748b;font-size:10px;margin:4px 0 2px;font-weight:600;'
        'letter-spacing:.5px">카테고리별 리스크율 비교</p>',
        unsafe_allow_html=True
    )
    st.plotly_chart(
        create_bar_chart(scores['km_pct'], scores['cr_pct'], scores['aw_pct'], scores['sc_pct']),
        use_container_width=True,
        config={"displayModeBar": False}
    )
    st.markdown(
        '<div style="display:flex;gap:12px;justify-content:center;margin-top:-4px;font-size:8.5px;color:#64748b">'
        '<span>🟢 0-20% 양호</span>'
        '<span>🟡 21-45% 주의</span>'
        '<span>🟠 46-70% 경계</span>'
        '<span>🔴 71-100% 위험</span>'
        '</div>',
        unsafe_allow_html=True
    )
    
    # 우선 대응 항목
    st.markdown(
        '<p style="color:#fff;font-size:12px;font-weight:700;margin:16px 0 6px">'
        '🔥 우선 대응 항목 <span style="color:#64748b;font-size:9px;font-weight:500">'
        '(리스크율 > 0 인 항목 중 가중치 높은 5건)</span></p>',
        unsafe_allow_html=True
    )
    
    priority_items = get_priority_items(scores["all_items"])
    
    if not priority_items:
        st.markdown('<div class="gfc-empty">모든 항목 양호 🎉</div>', unsafe_allow_html=True)
    else:
        for i, item in enumerate(priority_items, 1):
            render_priority_item(item, i)
    
    # 추천 솔루션
    st.markdown(
        '<p style="color:#fff;font-size:12px;font-weight:700;margin:16px 0 6px">'
        '💎 추천 솔루션 <span style="color:#64748b;font-size:9px;font-weight:500">'
        '(리스크 유형별 대응 제품)</span></p>',
        unsafe_allow_html=True
    )
    
    recommended_solutions = get_recommended_solutions(scores["all_items"])
    
    if not recommended_solutions:
        st.markdown(
            '<div class="gfc-empty">현재 추천 솔루션 없음 — 모든 항목 양호 🎉</div>',
            unsafe_allow_html=True
        )
    else:
        for solution in recommended_solutions:
            render_solution_card(solution)
    
    # 세션에 저장
    st.session_state.update({
        "priority": priority_items,
        "sol_shown": recommended_solutions
    })

def render_consultant_tab():
    """AI 컨설턴트 탭 렌더링"""
    scores = st.session_state.get("scores", {})
    info = st.session_state.get("info", {})
    priority_items = st.session_state.get("priority", [])
    
    if not scores:
        st.markdown(
            '<p style="color:#64748b;font-size:12px;text-align:center;padding:40px 0">'
            '먼저 진단 탭에서 답변을 입력해주세요.</p>',
            unsafe_allow_html=True
        )
        return
    
    total_pct = scores["total_pct"]
    label, color = get_risk_level(total_pct)
    company = info.get("company", "○○(주)") or "○○(주)"
    industry = info.get("industry", "") or "미입력"
    employees = info.get("employees", "") or "?"
    revenue = info.get("revenue", "") or "미입력"
    
    # 헤더
    st.markdown('''
    <div style="font-family: 'Noto Sans KR'; font-size: 26px; font-weight: 700; 
         color: #00d4aa; margin-bottom: 8px;">
        🤝 AI 컨설턴트 Ken의 종합 분석
    </div>
    ''', unsafe_allow_html=True)
    
    # 프로필
    st.markdown(f'''
    <div style="background: #111d2e; border: 1px solid #1e3a5f; border-radius: 10px; 
         padding: 18px; margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="flex-shrink: 0;">
                <div style="width: 80px; height: 80px; 
                     background: linear-gradient(135deg, #00d4aa, #00b894); 
                     border-radius: 50%; display: flex; align-items: center; 
                     justify-content: center; font-size: 36px; color: #fff; 
                     border: 3px solid #00d4aa; 
                     box-shadow: 0 4px 12px rgba(0,212,170,0.3);">
                    👨‍💼
                </div>
            </div>
            <div style="flex: 1;">
                <div style="font-family: 'Noto Sans KR'; font-size: 16px; font-weight: 700; 
                     color: #00d4aa; margin-bottom: 8px;">
                    👋 안녕하세요, GFC 컨설턴트 Ken입니다
                </div>
                <div style="font-size: 12px; color: #94a3b8; line-height: 1.7; margin-bottom: 10px;">
                    20년간 한국-중남미 협력 프로젝트를 수행하며 <b>58개 사이트</b>의 
                    디지털 전환(DX) 전략을 수립한 경험을 바탕으로, 귀사의 
                    <b>종합 리스크 진단 결과</b>를 데이터 기반으로 상세히 분석해 드리겠습니다.
                </div>
                <div style="font-size:13px; color:#4a6a84;">
                    📊 현재 분석 대상: <b style="color:#e0e6ed;">{company}</b> | 
                    {industry} · 종업원 {employees}명 · 연매출 {revenue}
                </div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # 종합 진단
    st.markdown(f'''
    <div style="background: linear-gradient(135deg, #141e2b, #1a2736); padding: 18px; 
         border-radius: 10px; border-left: 4px solid {color}; margin-bottom: 16px;">
        <div style="font-size: 15px; font-weight: 700; color: {color}; margin-bottom: 10px;">
            📋 종합 진단 결과
        </div>
        <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
            귀사의 <b>종합 리스크율은 {total_pct:.0f}%</b>로 
            <b style="color: {color};">{label}</b> 수준입니다.<br><br>
            4가지 핵심 리스크 카테고리를 가중평균하여 산출한 결과이며,<br>
            대표자 리스크({scores["km_pct"]:.0f}%), 법인 경영 리스크({scores["cr_pct"]:.0f}%), 
            리스크 인식 부족({scores["aw_pct"]:.0f}%), 시나리오 대응 미흡({scores["sc_pct"]:.0f}%)을 반영했습니다.
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # 우선 대응 항목
    st.markdown(
        '<div style="font-size: 14px; font-weight: 700; color: #fff; margin: 16px 0 8px;">'
        '🔥 우선 대응 항목</div>',
        unsafe_allow_html=True
    )
    
    if not priority_items:
        st.markdown('<div class="gfc-empty">모든 항목 양호 🎉</div>', unsafe_allow_html=True)
    else:
        for i, item in enumerate(priority_items[:5], 1):
            render_priority_item(item, i)
    
    # Ken의 제안
    st.markdown(
        '<div style="font-size: 14px; font-weight: 700; color: #fff; margin: 20px 0 8px;">'
        '🎯 Ken의 종합 컨설팅 제안</div>',
        unsafe_allow_html=True
    )
    
    # 단기/중기/장기 제안
    proposals = [
        ("⏱️ 1. 단기 (3개월 이내)", "#00d4aa", 
         "• 키맨 보험 가입으로 대표자 유고 리스크 대비<br>"
         "• 기업재해 보장 상품으로 종업원 안전망 구축<br>"
         "• 퇴직연금 제도 점검 및 최적화"),
        ("📅 2. 중기 (6~12개월)", "#f5a623",
         "• 가업승계 시뮬레이션 (증여 vs 상속 세금 비교)<br>"
         "• 법인세 절세 전략 수립 (삼성생명 세무사 협업)<br>"
         "• 정기 재무 건강검진 체계 구축"),
        ("🎯 3. 장기 (1~3년)", "#a29bfe",
         "• 후계자 육성 프로그램 및 지분 이전 계획<br>"
         "• 가족신탁, 재산분할 등 고급 절세 전략<br>"
         "• 삼성패밀리오피스 연계한 자산관리 (10억 이상 자산가 대상)"),
    ]
    
    bg_gradients = {
        "#00d4aa": "linear-gradient(135deg, #0d2818, #1a3a2e)",
        "#f5a623": "linear-gradient(135deg, #2a1f0d, #3a2f1d)",
        "#a29bfe": "linear-gradient(135deg, #1a1a2e, #2a2a4e)",
    }
    
    for title, color_code, content in proposals:
        st.markdown(f'''
        <div style="background: {bg_gradients[color_code]}; padding: 14px; border-radius: 8px; 
             border-left: 4px solid {color_code}; margin-bottom: 10px;">
            <div style="font-size: 13px; font-weight: 700; color: {color_code}; 
                 margin-bottom: 8px;">{title}</div>
            <div style="font-size: 12px; color: #c8d8e4; line-height: 1.7;">{content}</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # 차별화 포인트
    st.markdown('''
    <div style="background: rgba(0, 212, 170, 0.08); padding: 16px; border-radius: 8px; 
         border: 2px solid #00d4aa; margin-top: 16px;">
        <div style="font-size: 14px; font-weight: 700; color: #00d4aa; margin-bottom: 10px;">
            💎 차별화 포인트
        </div>
        <div style="font-size: 13px; color: #cbd5e1; line-height: 1.8;">
            제조 기업의 지속 가능한 성장과 가치 창출 프로세스를 이해하고, 그 가치의 근원을 데이터로 분석하며
            <b style="color: #00d4aa;">경영 리스크를 최소화</b>하는 실전 컨설팅을 수행해 왔습니다.<br><br> 
            기업이 땀 흘려 만든 가치가 세금과 리스크로 훼손되지 않도록, 삼성생명의 전문가 네트워크(세무사·회계사·법무사)와 협업하여    
            귀사의 <b>영속적 경영과 안정적 가업승계</b>를 설계해 드리겠습니다.
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # 다음 단계
    st.markdown('''
    <div style="background: #141e2b; padding: 16px; border-radius: 8px; 
         border: 1px solid #1e3a5f; margin-top: 16px;">
        <div style="font-size: 14px; font-weight: 700; color: #f5a623; margin-bottom: 10px;">
            📞 다음 단계 — 무료 심층 상담 신청
        </div>
        <div style="font-size: 12px; color: #c8d8e4; line-height: 1.7; margin-bottom: 12px;">
            위 분석 결과를 바탕으로 <b style="color: #00d4aa;">귀사 맞춤형 절세 시뮬레이션</b>을 
            준비해 드리겠습니다.
        </div>
        <div style="background: rgba(245, 166, 35, 0.05); padding: 12px; border-radius: 6px; 
             border-left: 3px solid #f5a623; margin-bottom: 12px;">
            <div style="font-size: 11px; font-weight: 700; color: #f5a623; margin-bottom: 6px;">
                📋 상담 신청 시 제공되는 자료
            </div>
            <div style="font-size: 11px; color: #c8d8e4; line-height: 1.6;">
                • 가업승계 시나리오별 세금 비교표 (증여 vs 상속)<br>
                • 법인보험 가입 시 절세 효과 계산서<br>
                • 퇴직연금 최적화 방안<br>
                • ROI 예측 대시보드 (5년/10년 단위)
            </div>
        </div>
        <div style="background: rgba(0, 212, 170, 0.08); padding: 10px; border-radius: 6px; 
             border: 1px solid #00d4aa; text-align: center;">
            <span style="font-size: 12px; color: #00d4aa; font-weight: 700;">
                📧 io7hub@naver.com | ☎ 010-2610-5194
            </span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown(
        f'<div style="text-align: right; color: #64748b; font-size: 10px; margin-top: 16px;">'
        f'🤖 AI 컨설턴트 분석 완료 | {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )

def render_script_tab():
    """스크립트 탭 렌더링"""
    scores = st.session_state.get("scores", {})
    info = st.session_state.get("info", {})
    priority_items = st.session_state.get("priority", [])
    solutions = st.session_state.get("sol_shown", [])
    
    if not scores:
        st.markdown(
            '<p style="color:#64748b;font-size:12px;text-align:center;padding:40px 0">'
            '먼저 진단 탭에서 답변을 입력해주세요.</p>',
            unsafe_allow_html=True
        )
        return
    
    st.markdown('''
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px">
      <div style="display:flex;align-items:center;gap:7px">
        <span style="font-size:17px">📝</span>
        <span style="font-size:15px;font-weight:700;color:#fff">GFC 상담 스크립트</span>
      </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # 스크립트 생성
    script_text = generate_consultation_script(info, scores, priority_items, solutions)
    total_pct = scores["total_pct"]
    label, color = get_risk_level(total_pct)
    
    company = info.get("company", "○○(주)") or "○○(주)"
    industry = info.get("industry", "") or "미입력"
    employees = info.get("employees", "") or "?"
    ceo = info.get("ceo", "대표자") or "대표자"
    est = info.get("est", "") or "미입력"
    
    # 스크립트 헤더
    st.markdown(f"""
    <div class="gfc-script">
      <div class="sc-hdr">
        <h2>GFC 상담 스크립트</h2>
        <p>삼성생명 기업재무컨설팅 · 진단 기반 자동생성</p>
      </div>
      <div class="sc-meta">
        <span><strong>기업명:</strong> {company}</span>
        <span><strong>업종:</strong> {industry}</span>
        <span><strong>종업원 수:</strong> {employees}명</span>
        <span><strong>대표자:</strong> {ceo}</span>
        <span><strong>설립 연차:</strong> {est}</span>
        <span><strong>진단 충족율:</strong> 
          <span style="color:{color};font-weight:700">{total_pct:.0f}% ({label})</span>
        </span>
      </div>

      <div class="sc-sec">1. 도입 인사</div>
      <div class="sc-intro">
        안녕하세요, {ceo} 대표님. 삼성생명 GFC 기업재무컨설팅 
        <strong>{company.replace('(주)','').replace('(유)','').replace('㈜','')}</strong> 
        담당 컨설턴트 Ken입니다.<br><br>
        오늘 우리회사의 법인 리스크 사전 진단을 완료했는데, 종합 리스크율이 
        <strong style="color:{color}">{total_pct:.0f}%({label})</strong> 수준으로 나왔습니다.<br>
        특히 <strong>'{priority_items[0]['section'] if priority_items else '주요 영역'}'</strong> 
        부분에서 즉각적인 대비가 필요한 사항들이 도출되었습니다.<br><br>
        오늘 주요 내용을 안내드리고, 우리기업에 맞는 종합 컨설팅 제안까지 함께 검토하겠습니다.
      </div>
    """, unsafe_allow_html=True)
    
    # 리스크 블록
    grouped = OrderedDict()
    for item in priority_items:
        grouped.setdefault(item["section"], []).append(item)
    
    if grouped:
        st.markdown('<div class="sc-sec" style="margin-top:14px">2. 리스크별 상세 상담</div>', 
                   unsafe_allow_html=True)
        
        for section, items in grouped.items():
            st.markdown(
                f'<div style="font-size:11px;font-weight:700;color:#fff;margin:10px 0 5px">'
                f'▸ {section} '
                f'<span style="background:#475569;color:#fff;font-size:8px;font-weight:700;'
                f'border-radius:3px;padding:1px 5px">{len(items)}건</span></div>',
                unsafe_allow_html=True
            )
            
            for item in items:
                item_color = WEIGHT_COLORS.get(item["w"], "#64748b")
                response = "예" if item["score"] == 1.0 else "일부 해당"
                
                st.markdown(f"""
                <div class="sc-block" style="border-color:{item_color}">
                  <div class="bq">📌 진단 항목 (가중치 {item['w']}) — {item['section']}</div>
                  <div class="bt">
                    <strong>질문:</strong> {item['text']}<br>
                    <strong>응답:</strong> {response}
                  </div>
                </div>
                """, unsafe_allow_html=True)
    
    # 솔루션
    if solutions:
        st.markdown('<div class="sc-sec" style="margin-top:14px">3. 추천 솔루션 제안</div>', 
                   unsafe_allow_html=True)
        
        for solution in solutions:
            st.markdown(f"""
            <div style="display:flex;gap:7px;align-items:flex-start;margin-bottom:5px">
              <span style="background:{solution['color']};color:#fff;font-size:8px;
                   font-weight:700;border-radius:3px;padding:2px 6px;white-space:nowrap;
                   flex-shrink:0">{solution['icon']} {solution['name']}</span>
              <span style="font-size:10.5px;color:#cbd5e1;line-height:1.6">
                {solution['desc']}
              </span>
            </div>
            """, unsafe_allow_html=True)
    
    # 마무리
    st.markdown("""
      <div class="sc-sec" style="margin-top:14px">4. 마무리 및 다음 단계</div>
      <div class="sc-close">
        오늘 진단 결과를 기반으로, 우리기업에 맞는 
        <strong>종합 법인 재무 컨설팅 제안서</strong>를 별도로 작성하여 드리겠습니다.<br><br>
        세무사, 회계사, 법무사 등 전문가와 협업하여 <strong>최적의 구조</strong>를 설계드리고,
        삼성생명 GFC의 교육과 지원 체계와 함께 단계별 실행 계획까지 제안드리겠습니다.<br><br>
        다음 단계로 <strong>상세 제안서 검토 일정</strong>을 잡아드리면 되겠습니다. 
        언제 가능하신가요?
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 다운로드 버튼
    st.download_button(
        label="📥  스크립트 다운로드 (.txt)",
        data=script_text.encode("utf-8"),
        file_name=f"GFC_스크립트_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        help="스크립트를 텍스트 파일로 다운로드합니다."
    )

# ═══════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════

def main():
    """메인 애플리케이션"""
    # 페이지 설정
    st.set_page_config(
        page_title="Kⁱ⁰⁷ 삼성생명 GFC | 법인 리스크 사전 진단표 v2.0",
        page_icon="⚖️",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    
    # CSS 로드
    st.markdown(load_dark_theme_css(), unsafe_allow_html=True)
    
    # 헤더
    render_header()
    
    # 탭 생성
    tab_diag, tab_dash, tab_consult, tab_script = st.tabs([
        "📋  진단",
        "📊  대시보드",
        "🤝  AI 컨설턴트",
        "📝  스크립트"
    ])
    
    # 각 탭 렌더링
    with tab_diag:
        render_diagnostic_tab()
    
    with tab_dash:
        render_dashboard_tab()
    
    with tab_consult:
        render_consultant_tab()
    
    with tab_script:
        render_script_tab()

if __name__ == "__main__":
    main()