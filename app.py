import streamlit as st
import pandas as pd
from google import genai
import time

st.set_page_config(page_title="AI 면담일지 대시보드", layout="wide")

st.markdown("""
<style>
div.block-container { padding-top: 5rem !important; padding-bottom: 2rem !important; }

/* 사이드바 */
.spot-badge {
    font-size: 11px; padding: 3px 10px; border-radius: 99px;
    background: #eff6ff; color: #1d4ed8; font-weight: 600;
    display: inline-block; margin-bottom: 6px;
}
.emp-item {
    padding: 8px 10px; border-radius: 8px; cursor: pointer;
    font-size: 14px; color: #334155; margin-bottom: 2px;
}
.emp-item:hover { background: #f1f5f9; }
.emp-active { background: #eff6ff !important; color: #1d4ed8 !important; font-weight: 600; }

/* 상단 배너 */
.blue-banner {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    border-radius: 16px; padding: 24px 28px; margin-bottom: 14px;
}
.banner-title { font-size: 20px; font-weight: 800; color: #fff; margin-bottom: 4px; }
.banner-sub { font-size: 13px; color: #93c5fd; }
.profile-card {
    background: rgba(255,255,255,0.95); border-radius: 12px;
    padding: 12px 16px; margin-top: 14px;
    display: flex; justify-content: space-between; align-items: center;
}
.profile-name { font-size: 15px; font-weight: 700; color: #1e293b; }
.profile-desc { font-size: 12px; color: #64748b; margin-top: 2px; }
.status-badge {
    font-size: 11px; font-weight: 700; color: #1d4ed8;
    background: #eff6ff; padding: 4px 12px; border-radius: 99px;
}

/* 지표 카드 */
.metric-row { display: flex; gap: 12px; margin-bottom: 14px; }
.metric-card {
    flex: 1; background: #fff; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 12px 14px;
}
.metric-label { font-size: 12px; color: #64748b; margin-bottom: 4px; }
.metric-value { font-size: 20px; font-weight: 700; }
.meter-bg { height: 6px; background: #f1f5f9; border-radius: 99px; margin-top: 6px; overflow: hidden; }
.meter-fill { height: 100%; border-radius: 99px; }

/* 탭 */
.tab-row { display: flex; gap: 6px; margin-bottom: 14px; }
.tab-btn {
    padding: 6px 18px; border-radius: 99px; border: 1px solid #e2e8f0;
    background: #fff; cursor: pointer; font-size: 13px; font-weight: 600; color: #64748b;
}
.tab-active {
    background: #eff6ff !important; border-color: #bfdbfe !important; color: #1d4ed8 !important;
}

/* 메뉴 버튼 */
.main-btn>button {
    width: 100%; height: 58px; font-size: 13px !important;
    border-radius: 10px; font-weight: 600;
    background-color: #fff !important; border: 1px solid #e2e8f0 !important;
    color: #334155 !important;
}
.main-btn>button:hover {
    background-color: rgba(37,99,235,0.04) !important;
    border-color: #2563eb !important; color: #2563eb !important;
}
.active-btn>button {
    width: 100% !important; height: 58px !important;
    font-size: 13px !important; border-radius: 10px !important; font-weight: 700 !important;
    background-color: #2563eb !important; border: 1px solid #2563eb !important;
    color: #fff !important; box-shadow: 0 4px 12px rgba(37,99,235,0.2) !important;
}
.opd-btn>button {
    width: 100%; height: 46px; font-size: 13px !important;
    border-radius: 10px; font-weight: 700;
    background-color: #fff !important; border: 1px solid #e2e8f0 !important; color: #334155 !important;
}
.sub-btn>button {
    width: 100%; height: 40px; font-size: 12px !important;
    border-radius: 8px; font-weight: 600;
    background-color: #fff !important; border: 1px solid #e2e8f0 !important; color: #334155 !important;
}
.active-sub-btn>button {
    width: 100% !important; height: 40px !important; font-size: 12px !important;
    border-radius: 8px !important; font-weight: 700 !important;
    background-color: #2563eb !important; border: 1px solid #2563eb !important; color: #fff !important;
}

/* OPD 카드 */
.opd-card { padding: 18px; border-radius: 12px; margin-bottom: 12px; border-left: 5px solid #64748b; }
.opd-strong { border-left-color: #2563eb; background: rgba(37,99,235,0.04); }
.opd-warning { border-left-color: #f59e0b; background: rgba(245,158,11,0.04); }
.opd-success { border-left-color: #10b981; background: rgba(16,185,129,0.04); }
.opd-danger  { border-left-color: #ef4444; background: rgba(239,68,68,0.04); }
.opd-title { font-size: 14px; font-weight: 700; margin-bottom: 8px; color: #1e293b; }
.opd-content { font-size: 13px; line-height: 1.7; color: #334155; }

/* 면담일지 로그 */
.log-item { padding: 8px 0; border-bottom: 1px solid #f1f5f9; }
.log-date { font-size: 11px; color: #94a3b8; margin-right: 8px; }
.log-cat { font-size: 11px; padding: 2px 8px; border-radius: 99px; background: #eff6ff; color: #1d4ed8; font-weight: 600; margin-right: 6px; }
.log-content { font-size: 13px; color: #475569; line-height: 1.6; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# ✏️ 설정 구역
# =========================================================================
EMPLOYEE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1iPzvekrGlzxcfaUt6wXY7oCU1KdqH3ZM27Gd8MffZA4/export?format=csv&gid=0"

SPOT_CONFIG_BASE = {
    "kafe5": {
        "label": "사내카페 (kafe5)",
        "password": "kafe5",
        "base_url": "https://docs.google.com/spreadsheets/d/1rRpq9zX7g70hX2uwRwA1enPY83KSK_lNOiJ1MGIOzqY",
    },
}

GEMINI_API_KEY = "여기에_제미나이_API_키_입력"
# =========================================================================

for key, val in [
    ("logged_in_spot", None), ("current_action", None), ("ai_report_data", {}),
    ("selected_sub_view", "요약"), ("expanded_row", None), ("active_tab", "면담일지"),
    ("selected_user", None)
]:
    if key not in st.session_state:
        st.session_state[key] = val

@st.cache_data(ttl=60)
def load_employee_config(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        config = {}
        for _, row in df.iterrows():
            spot = str(row['스팟']).strip()
            name = str(row['호칭']).strip()
            gid  = str(int(float(row['gid']))).strip()
            if spot not in config:
                config[spot] = {}
            config[spot][name] = gid
        return config
    except:
        return {}

employee_config = load_employee_config(EMPLOYEE_SHEET_URL)
SPOT_CONFIG = {}
for spot_key, base in SPOT_CONFIG_BASE.items():
    SPOT_CONFIG[base["label"]] = {
        "base_url": base["base_url"],
        "password": base["password"],
        "employees": employee_config.get(spot_key, {}),
    }

# ── 로그인 ──
if st.session_state["logged_in_spot"] is None:
    st.markdown("<h2 style='text-align:center; margin-bottom:30px;'>🔒 사내 면담 관리 시스템 권한 인증</h2>", unsafe_allow_html=True)
    _, cent, _ = st.columns([1, 1.8, 1])
    with cent:
        with st.container(border=True):
            selected_spot = st.selectbox("접근할 근무 스팟 선택:", list(SPOT_CONFIG.keys()))
            input_pw = st.text_input(f"🔑 [{selected_spot}] 전용 비밀번호:", type="password")
            st.write("")
            if st.button("🚀 대시보드 진입", use_container_width=True):
                if input_pw == SPOT_CONFIG[selected_spot]["password"]:
                    st.session_state["logged_in_spot"] = selected_spot
                    st.session_state["current_action"] = None
                    st.session_state["ai_report_data"] = {}
                    st.session_state["selected_user"] = None
                    st.success("🔓 인증 성공!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ 비밀번호가 올바르지 않습니다.")
        st.markdown("<p style='font-size:12px; color:#94a3b8; text-align:center; margin-top:8px;'>비밀번호 문의: 담당 매니저 세라에게 연락하세요</p>", unsafe_allow_html=True)
    st.stop()

# ── 메인 ──
current_spot = st.session_state["logged_in_spot"]
spot_data = SPOT_CONFIG[current_spot]
employee_list = list(spot_data["employees"].keys())

if st.session_state["selected_user"] is None and employee_list:
    st.session_state["selected_user"] = employee_list[0]

selected_user = st.session_state["selected_user"]

# ── 사이드바 ──
with st.sidebar:
    st.markdown("#### 📋 면담일지 시스템")
    st.markdown(f'<span class="spot-badge">{current_spot.split("(")[0].strip()}</span>', unsafe_allow_html=True)
    
    search_emp = st.text_input("", placeholder="🔍 직원 검색...", label_visibility="collapsed")
    
    # 스팟별로 직원 그룹화
    for spot_key, base in SPOT_CONFIG_BASE.items():
        spot_label = base["label"]
        emp_dict = employee_config.get(spot_key, {})
        if emp_dict:
            st.markdown(f"<p style='font-size:11px; color:#94a3b8; font-weight:600; margin:8px 0 2px; text-transform:uppercase;'>{spot_label}</p>", unsafe_allow_html=True)
            for name in emp_dict.keys():
                if search_emp and search_emp.lower() not in name.lower():
                    continue
                is_active = selected_user == name
                if st.button(f"👤 {name}", key=f"emp_{name}", use_container_width=True):
                    st.session_state["selected_user"] = name
                    st.session_state["current_action"] = None
                    st.session_state["ai_report_data"] = {}
                    st.session_state["active_tab"] = "면담일지"
                    st.rerun()

    st.markdown("---")
    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state["logged_in_spot"] = None
        st.session_state["selected_user"] = None
        st.rerun()

# ── 데이터 로드 ──
@st.cache_data(ttl=5)
def load_data(url):
    try:
        df_raw = pd.read_csv(url, header=None)
        header_idx = None
        for i, row in df_raw.iterrows():
            if any(str(v).strip() in ['일자', '구분', '내용'] for v in row.values):
                header_idx = i
                break
        if header_idx is None:
            return None
        df = pd.read_csv(url, skiprows=header_idx)
        df.columns = df.columns.str.strip()
        for col in ['내용', '구분', '세부 구분']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace('nan', '')
        return df
    except:
        return None

if selected_user and selected_user in spot_data["employees"]:
    raw_url = spot_data["base_url"].strip().split("/edit")[0].split("/export")[0]
    gid = spot_data["employees"][selected_user]
    sheet_url = f"{raw_url}/export?format=csv&gid={gid}"
    final_df = load_data(sheet_url)
else:
    final_df = None

total_count = len(final_df) if final_df is not None else 0

# ── 상단 배너 ──
col_banner, col_logout = st.columns([9, 1])
with col_banner:
    st.markdown(f"""
    <div class="blue-banner">
        <div class="banner-title">안녕하세요, 관리자님 👋</div>
        <div class="banner-sub">{current_spot} 현장 크루들의 케어 상태를 실시간 체크 중입니다.</div>
        <div class="profile-card">
            <div>
                <div class="profile-name">👤 {selected_user} 크루</div>
                <div class="profile-desc">면담 기록 {total_count}건 로드 완료 · Gemini AI 분석 대기 중</div>
            </div>
            <div style="display:flex; gap:8px; align-items:center;">
                <div class="status-badge">정상 근무 중</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_logout:
    st.write("")
    st.write("")

# ── 지표 카드 ──
if final_df is not None and '내용' in final_df.columns:
    recent = final_df.tail(20)
    def calc(kw):
        cnt = recent['내용'].str.contains(kw, na=False, case=False).sum()
        return min(95, max(10, int(cnt / max(len(recent), 1) * 100)))
    def color(s, inv=False):
        good = s < 40 if inv else s > 60
        bad  = s > 60 if inv else s < 40
        return "#16a34a" if good else "#dc2626" if bad else "#d97706"
    def label(s, inv=False):
        good = s < 40 if inv else s > 60
        bad  = s > 60 if inv else s < 40
        return "양호" if good else "주의" if bad else "보통"
    
    anxiety = calc("불안|긴장|힘들|어려움|고충")
    hygiene = calc("위생|청결|손씻기|마스크|앞치마")
    growth  = calc("발전|향상|성장|잘함|성공|개선")
    
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-label">😰 불안도</div>
            <div class="metric-value" style="color:{color(anxiety,True)}">{label(anxiety,True)}</div>
            <div class="meter-bg"><div class="meter-fill" style="width:{anxiety}%;background:{color(anxiety,True)};"></div></div>
            <div style="font-size:11px;color:#94a3b8;margin-top:4px;">최근 기록 기반</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">🧼 위생 상태</div>
            <div class="metric-value" style="color:{color(hygiene)}">{label(hygiene)}</div>
            <div class="meter-bg"><div class="meter-fill" style="width:{hygiene}%;background:{color(hygiene)};"></div></div>
            <div style="font-size:11px;color:#94a3b8;margin-top:4px;">최근 기록 기반</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">📈 업무 발전도</div>
            <div class="metric-value" style="color:{color(growth)}">{label(growth)}</div>
            <div class="meter-bg"><div class="meter-fill" style="width:{growth}%;background:{color(growth)};"></div></div>
            <div style="font-size:11px;color:#94a3b8;margin-top:4px;">최근 기록 기반</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── 탭 카드 ──
with st.container(border=True):
    # 탭 버튼
    t1, t2, t3 = st.columns(3)
    active_tab = st.session_state["active_tab"]
    with t1:
        if st.button("면담일지", key="tab_log", use_container_width=True):
            st.session_state["active_tab"] = "면담일지"
            st.rerun()
    with t2:
        if st.button("AI 분석", key="tab_ai", use_container_width=True):
            st.session_state["active_tab"] = "AI 분석"
            st.rerun()
    with t3:
        if st.button("면담 입력", key="tab_write", use_container_width=True):
            st.session_state["active_tab"] = "면담 입력"
            st.rerun()

    st.markdown(f"""
    <style>
    div[data-testid="column"]:nth-child({"1" if active_tab=="면담일지" else "2" if active_tab=="AI 분석" else "3"}) button {{
        background: #eff6ff !important; border-color: #bfdbfe !important; color: #1d4ed8 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='margin:8px 0 14px;'>", unsafe_allow_html=True)

    # ── 면담일지 탭 ──
    if active_tab == "면담일지":
        col_search, col_filter = st.columns([3, 1])
        with col_search:
            search_q = st.text_input("", placeholder="🔍 키워드 검색 (예: 위생, 불안, 피크타임...)", label_visibility="collapsed")
        with col_filter:
            cats = ["전체 구분"]
            if final_df is not None and '구분' in final_df.columns:
                cats += [c for c in final_df['구분'].dropna().unique().tolist() if c and c != 'nan']
            cat_filter = st.selectbox("", cats, label_visibility="collapsed")

        if final_df is not None and '내용' in final_df.columns:
            filtered = final_df.copy()
            if search_q:
                filtered = filtered[
                    filtered['내용'].str.contains(search_q, na=False, case=False) |
                    filtered['구분'].str.contains(search_q, na=False, case=False)
                ]
            if cat_filter != "전체 구분":
                filtered = filtered[filtered['구분'] == cat_filter]

            st.caption(f"총 {len(filtered)}건 · 클릭하면 내용 펼쳐짐")
            
            for i, (_, row) in enumerate(filtered.iloc[::-1].iterrows()):
                col_meta, col_toggle = st.columns([11, 1])
                with col_meta:
                    preview = str(row.get('내용',''))[:50] + ("..." if len(str(row.get('내용',''))) > 50 else "")
                    st.markdown(
                        f"<div style='padding:5px 0; font-size:13px;'>"
                        f"<span class='log-date'>{row.get('일자','')}</span>"
                        f"<span class='log-cat'>{row.get('구분','')}</span>"
                        f"<span style='font-size:11px;color:#94a3b8;margin-right:8px;'>{row.get('세부 구분','')}</span>"
                        f"<span style='color:#64748b;'>{preview if st.session_state['expanded_row'] != i else ''}</span>"
                        f"</div>", unsafe_allow_html=True
                    )
                with col_toggle:
                    if st.button("▼" if st.session_state["expanded_row"] != i else "▲", key=f"row_{i}"):
                        st.session_state["expanded_row"] = None if st.session_state["expanded_row"] == i else i
                        st.rerun()
                if st.session_state["expanded_row"] == i:
                    st.markdown(
                        f"<div style='background:#f8fafc; border-left:3px solid #2563eb; padding:10px 14px; font-size:13px; color:#334155; line-height:1.7; white-space:pre-wrap; margin-bottom:4px;'>{row.get('내용','')}</div>",
                        unsafe_allow_html=True
                    )
                st.markdown("<hr style='margin:2px 0; border-color:#f8fafc;'>", unsafe_allow_html=True)
        else:
            st.warning("데이터를 불러올 수 없습니다.")

    # ── AI 분석 탭 ──
    elif active_tab == "AI 분석":
        # OPD 버튼
        st.markdown(f"<p style='font-weight:700; margin-bottom:8px;'>📄 {selected_user}의 OPD 가이드라인</p>", unsafe_allow_html=True)
        _, opd_col, _ = st.columns([1, 2, 1])
        with opd_col:
            is_opd = st.session_state["current_action"] == "opd_report"
            st.markdown(f'<div class="{"active-btn" if is_opd else "opd-btn"}">', unsafe_allow_html=True)
            if st.button("📊 한 페이지 요약 보고서 (OPD) 분석", use_container_width=True):
                st.session_state["current_action"] = "opd_report"
                st.session_state["ai_report_data"] = {}
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 근무 메뉴
        st.markdown("<p style='color:#2563eb; font-weight:700; font-size:13px; margin-bottom:8px;'>📱 근무 및 평가 관리</p>", unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)
        for col, key, lbl in [(c1,"move_spot","📍 근무지\n이동"),(c2,"attendance","⏰ 근태\n관리"),(c3,"monthly","📅 월면담"),(c4,"review","📊 근무\n리뷰"),(c5,"growth","📈 업무\n발전")]:
            with col:
                is_active = st.session_state["current_action"] == key
                st.markdown(f'<div class="{"active-btn" if is_active else "main-btn"}">', unsafe_allow_html=True)
                if st.button(lbl, key=f"btn_{key}"):
                    st.session_state["current_action"] = key
                    st.session_state["ai_report_data"] = {}
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br><p style='color:#0f766e; font-weight:700; font-size:13px; margin-bottom:8px;'>🧼 위생 및 행동 수칙</p>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        for col, key, lbl in [(c1,"hygiene","🧼 개인\n위생"),(c2,"manual","☕ 매뉴얼\n준수"),(c3,"etiquette","🤝 직장\n예절"),(c4,"others","🔍 기타\n사항")]:
            with col:
                is_active = st.session_state["current_action"] == key
                st.markdown(f'<div class="{"active-btn" if is_active else "main-btn"}">', unsafe_allow_html=True)
                if st.button(lbl, key=f"btn_{key}"):
                    st.session_state["current_action"] = key
                    st.session_state["ai_report_data"] = {}
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # AI 분석 결과
        action_type = st.session_state["current_action"]
        if action_type and final_df is not None:
            KEYWORD_MAP = {
                "move_spot": "이동|배치|스팟|전환|근무지|파견",
                "attendance": "근태|지각|결근|조퇴|무단|휴가|병가",
                "monthly": "면담|월면담|정기|상담",
                "review": "리뷰|평가|근무|태도|중간|점검",
                "growth": "발전|향상|성장|습득|성취|도전|개선",
                "hygiene": "위생|청결|마스크|손씻기|복장|샤워|단정|양치",
                "manual": "매뉴얼|준수|미준수|제조|순서|레시피|수칙|실수",
                "etiquette": "예절|태도|인사|소통|동료|존중|갈등|경어|존댓말",
                "others": "기타|특이|사항|기록|종합",
            }
            CAT_NAMES = {
                "opd_report": "OPD 종합 보고서", "move_spot": "근무지 이동",
                "attendance": "근태 관리", "monthly": "월면담",
                "review": "근무 리뷰", "growth": "업무 발전",
                "hygiene": "개인 위생", "manual": "매뉴얼 준수",
                "etiquette": "직장 예절", "others": "기타 사항",
            }
            category_name = CAT_NAMES.get(action_type, "")

            if action_type == "opd_report":
                display_df = final_df.copy()
            else:
                kw = KEYWORD_MAP.get(action_type, "")
                display_df = final_df[
                    final_df['내용'].str.contains(kw, na=False, case=False) |
                    final_df['구분'].str.contains(kw, na=False, case=False)
                ] if '내용' in final_df.columns else pd.DataFrame()

            st.markdown("<hr style='margin:16px 0;'>", unsafe_allow_html=True)

            if action_type != "opd_report":
                st.markdown(f"**📋 [{category_name}] 관련 기록 ({len(display_df)}건)**")
                st.dataframe(display_df, use_container_width=True)

            if not display_df.empty:
                if not st.session_state["ai_report_data"]:
                    with st.spinner("Gemini AI가 실시간 데이터를 분석 중입니다..."):
                        context = "\n".join([
                            f"[{r.get('일자','')}] 구분: {r.get('구분','')}, 내용: {r.get('내용','')}"
                            for _, r in display_df.tail(40).iterrows()
                        ])
                        if action_type == "opd_report":
                            prompt = f"""당신은 장애인 표준사업장의 최고 전문 지도원입니다.
제공된 데이터를 깊이 있게 분석하여 {selected_user} 크루의 OPD(One Page Description) 가이드를 작성하세요.
[PART1], [PART2], [PART3], [PART4] 구분선을 반드시 포함하세요.

[PART1] 강점
(이 크루가 가진 성격적/업무적 강점을 상세하게 작성해주세요.)

[PART2] 중요하게 여길 것 (건강과 안전)
(스트레스 관리, 신체 안전을 위해 주의해야 할 점들을 작성해주세요.)

[PART3] 중요하게 여길 것 (좋아하는 것, 소중한 것)
(이 크루가 즐거워하거나 보람을 느끼는 것들을 작성해주세요.)

[PART4] 잘 지원해줄 수 있는 방법
(매니저들이 대화 시 주의해야 할 요령을 작성해주세요.)

[누적 데이터]:
{context}"""
                        else:
                            prompt = f"""당신은 장애인 표준사업장의 지도원입니다.
다음 [{category_name}] 데이터를 분석하여 4개 파트로 나누어 작성하세요.
[PART1], [PART2], [PART3], [PART4] 구분선을 반드시 포함하세요.

[PART1] 현재 상태 요약
[PART2] 보완 및 누락점
[PART3] 교육 지원 방향
[PART4] 칭찬 및 격려 팁

[데이터]:
{context}"""
                        try:
                            client = genai.Client(api_key=GEMINI_API_KEY)
                            response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                            raw = response.text
                            parts = {"p1": "기록이 부족합니다.", "p2": "", "p3": "", "p4": ""}
                            if "[PART1]" in raw and "[PART4]" in raw:
                                parts["p1"] = raw.split("[PART1]")[1].split("[PART2]")[0].strip()
                                parts["p2"] = raw.split("[PART2]")[1].split("[PART3]")[0].strip()
                                parts["p3"] = raw.split("[PART3]")[1].split("[PART4]")[0].strip()
                                parts["p4"] = raw.split("[PART4]")[1].strip()
                            else:
                                parts["p1"] = raw
                            parts["context_data"] = context
                            st.session_state["ai_report_data"] = parts
                        except Exception as e:
                            st.error(f"구글 AI 통신 실패: {e}")

                if st.session_state["ai_report_data"]:
                    report = st.session_state["ai_report_data"]
                    if action_type == "opd_report":
                        st.markdown(f"### 📋 {selected_user} 크루 마스터 One-Page Profile")
                        for cls, icon, title, key in [
                            ("opd-strong",  "💪", f"1. {selected_user} 크루의 강점", "p1"),
                            ("opd-warning", "⚠️", f"2. {selected_user}를 위해 중요한 것 (건강과 안전)", "p2"),
                            ("opd-success", "❤️", f"3. {selected_user}에게 중요한 것 (좋아하는 것)", "p3"),
                            ("opd-danger",  "💡", f"4. {selected_user}를 잘 지원해줄 수 있는 방법", "p4"),
                        ]:
                            st.markdown(f"<div class='opd-card {cls}'><div class='opd-title'>{icon} {title}</div><div class='opd-content'>{report.get(key,'').replace(chr(10),'<br>')}</div></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("##### 🎯 AI 인사이트 탐색")
                        sc1, sc2, sc3, sc4 = st.columns(4)
                        view = st.session_state["selected_sub_view"]
                        for col, v, lbl in [(sc1,"요약","📋 1. 상태 요약"),(sc2,"보완","❌ 2. 누락/보완"),(sc3,"교육","💡 3. 교육 방향"),(sc4,"칭찬","👏 4. 칭찬 팁")]:
                            with col:
                                st.markdown(f'<div class="{"active-sub-btn" if view==v else "sub-btn"}">', unsafe_allow_html=True)
                                if st.button(lbl, key=f"sub_{v}"):
                                    st.session_state["selected_sub_view"] = v
                                    st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)
                        vk = {"요약":"p1","보완":"p2","교육":"p3","칭찬":"p4"}[view]
                        st.markdown(f"<p style='font-size:13px; font-weight:700; color:#2563eb; margin-top:12px;'>🤖 Gemini AI 결과 → {view}</p>", unsafe_allow_html=True)
                        st.info(report.get(vk, "내용을 불러올 수 없습니다."))

                    # 추가 질문
                    st.markdown("<hr style='margin:16px 0;'>", unsafe_allow_html=True)
                    st.markdown(f"**🔍 Gemini AI에게 추가 질문하기**")
                    user_q = st.text_input("", placeholder=f"예: {selected_user} 크루가 돌발 행동을 할 때 어떻게 제지하면 좋나요?", label_visibility="collapsed")
                    if st.button("💬 심층 분석 답변 받기"):
                        if not user_q.strip():
                            st.warning("질문을 입력해주세요!")
                        else:
                            with st.spinner("Gemini AI가 답변을 작성 중입니다..."):
                                try:
                                    client = genai.Client(api_key=GEMINI_API_KEY)
                                    resp = client.models.generate_content(
                                        model='gemini-2.5-flash',
                                        contents=f"장애인 표준사업장 전문 지도원으로서 답변하세요.\n질문: {user_q}\n데이터: {report.get('context_data','')}"
                                    )
                                    st.success(f"💡 [{selected_user}] 크루에 대한 답변")
                                    st.write(resp.text)
                                except Exception as e:
                                    st.error(f"오류: {e}")

    # ── 면담 입력 탭 ──
    elif active_tab == "면담 입력":
        st.markdown(f"**✏️ {selected_user} 크루 면담 내용 입력**")
        st.caption("입력 후 구글 시트 직접 저장 기능은 추후 업데이트 예정입니다.")
        col1, col2 = st.columns(2)
        with col1:
            f_date = st.date_input("날짜")
            f_cat = st.selectbox("구분", ["근무 리뷰", "면담", "이슈 대응", "업무 발전", "위생 점검"])
        with col2:
            f_sub = st.selectbox("세부 구분", ["오전 근무", "오후 근무", "피크타임", "월례면담", "개인면담"])
            f_writer = st.text_input("면담자", value="세라")
        f_content = st.text_area("면담 내용", height=120, placeholder="면담 내용을 입력하세요...")
        if st.button("저장", use_container_width=True):
            st.success("✅ 저장되었습니다! (구글 시트 연동 기능 업데이트 예정)")
