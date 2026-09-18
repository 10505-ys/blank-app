import streamlit as st
import datetime
import random
import json
import re
from PIL import Image
import pytesseract

# 1. 페이지 설정 및 폰트 충돌 해결 CSS
st.set_page_config(page_title="STUDY DASHBOARD", layout="wide", page_icon="✨")

st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    html, body, [class*="css"], div, p, span, h1, h2, h3, h4, button, input {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }
    
    .st-emotion-cache-1e5ec1a, [data-testid="stExpanderToggleIcon"] i, .material-symbols-outlined {
        font-family: 'Material Symbols Outlined', 'Material Icons' !important;
    }
    
    .stApp {
        background-color: #F8F9FA;
        color: #212529;
    }
    
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E9ECEF;
        padding-top: 1rem;
    }
    
    .hero-header {
        background: linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%);
        color: white;
        padding: 28px 32px;
        border-radius: 16px;
        box-shadow: 0 10px 20px rgba(108, 92, 231, 0.15);
        margin-bottom: 24px;
    }
    
    .hero-title {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .hero-subtitle {
        font-size: 0.95rem;
        opacity: 0.9;
        margin-top: 6px;
    }
    
    .cheer-card {
        background: #FFFFFF;
        border: 1px solid #E9ECEF;
        border-left: 5px solid #6C5CE7;
        padding: 16px 20px;
        border-radius: 12px;
        font-weight: 600;
        color: #495057;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-bottom: 24px;
    }
    
    .blocked-summary {
        background-color: #F1F3F5;
        border: 1px solid #E9ECEF;
        padding: 12px 18px;
        border-radius: 10px;
        color: #868E96;
        margin-bottom: 8px;
        font-size: 0.92rem;
    }
    
    .study-summary {
        background: linear-gradient(90deg, #E8F5E9 0%, #C8E6C9 100%);
        border-left: 4px solid #4CAF50;
        padding: 12px 18px;
        border-radius: 10px;
        color: #2E7D32;
        margin-bottom: 8px;
        font-weight: 700;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .stButton>button {
        border-radius: 10px !important;
        border: 1px solid #CED4DA !important;
        font-weight: 600 !important;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        border-color: #6C5CE7 !important;
        color: #6C5CE7 !important;
    }
    </style>
""", unsafe_allow_html=True)

CHEERING_MESSAGES = [
    "🍀 지금까지 열심히 준비한 만큼, 시험에서 최고의 실력을 발휘할 수 있을 거예요!",
    "🔥 포기하지 않고 한 걸음씩 나아가는 당신을 응원합니다. 파이팅!",
    "☕ 중간에 따뜻한 음료 한 잔 마시며 쉬어가는 것도 잊지 마세요!",
    "💡 노력을 쏟아부은 시간은 절대 배신하지 않습니다. 자신감을 가지세요!",
    "🎯 시험 당일, 아는 문제는 확실하게! 찍는 문제도 정답으로 이어지는 행운이 함께하길!"
]

DEFAULT_SCHEDULE = {
    str(i): {
        "sleep": [2, 8] if i < 5 else [3, 10],
        "school": [8, 16] if i < 5 else [0, 0],
        "academy": [18, 21] if i < 5 else ([13, 17] if i == 5 else [0, 0]),
        "dinner": [17, 18] if i < 5 else [18, 19]
    } for i in range(7)
}

DEFAULT_TASKS = [
    {"subject": "국어", "publisher": "미래엔", "unit": "1~2단원 개념 복습", "done": False},
    {"subject": "수학", "publisher": "비상교육", "unit": "이차방정식 유형 풀이", "done": False},
    {"subject": "영어", "publisher": "천재(이)", "unit": "1과 본문 암기", "done": False}
]

params = st.query_params
today = datetime.date.today()

if "start_date" in params:
    try:
        init_start = datetime.datetime.strptime(params["start_date"], "%Y-%m-%d").date()
    except:
        init_start = today + datetime.timedelta(days=7)
else:
    init_start = today + datetime.timedelta(days=7)

if "end_date" in params:
    try:
        init_end = datetime.datetime.strptime(params["end_date"], "%Y-%m-%d").date()
    except:
        init_end = init_start + datetime.timedelta(days=3)
else:
    init_end = init_start + datetime.timedelta(days=3)

if "tasks" not in st.session_state:
    if "saved_tasks" in params:
        try:
            st.session_state.tasks = json.loads(params["saved_tasks"])
        except:
            st.session_state.tasks = DEFAULT_TASKS
    else:
        st.session_state.tasks = DEFAULT_TASKS

if "weekly_schedule" not in st.session_state:
    if "saved_schedule" in params:
        try:
            loaded = json.loads(params["saved_schedule"])
            st.session_state.weekly_schedule = {int(k): v for k, v in loaded.items()}
        except:
            st.session_state.weekly_schedule = {i: DEFAULT_SCHEDULE[str(i)] for i in range(7)}
    else:
        st.session_state.weekly_schedule = {i: DEFAULT_SCHEDULE[str(i)] for i in range(7)}

if "selected_date" not in st.session_state:
    st.session_state.selected_date = today

def sync_storage():
    st.query_params["saved_tasks"] = json.dumps(st.session_state.tasks, ensure_ascii=False)
    st.query_params["saved_schedule"] = json.dumps(st.session_state.weekly_schedule)
    st.query_params["start_date"] = st.session_state.start_date_picker.strftime("%Y-%m-%d")
    st.query_params["end_date"] = st.session_state.end_date_picker.strftime("%Y-%m-%d")

def update_schedule_callback(day_idx, key_type):
    val = st.session_state[f"{key_type}_{day_idx}"]
    st.session_state.weekly_schedule[day_idx][key_type] = list(val)
    sync_storage()

days_map = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

# 사이드바
st.sidebar.header("⚙️ 시험 기간 설정")
start_date = st.sidebar.date_input("시험 시작일", init_start, key="start_date_picker", on_change=sync_storage)
end_date = st.sidebar.date_input("시험 종료일", init_end, key="end_date_picker", on_change=sync_storage)

st.sidebar.divider()
st.sidebar.header("🏫 요일별 일과 & 수면 설정")

day_tabs = st.sidebar.tabs(["월", "화", "수", "목", "금", "토", "일"])
for i, tab in enumerate(day_tabs):
    with tab:
        st.caption(f"📌 {days_map[i]} 일정 설정")
        sch_data = st.session_state.weekly_schedule[i]
        
        st.slider("🌙 취침 ~ 기상", 0, 24, tuple(sch_data["sleep"]), key=f"sleep_{i}", on_change=update_schedule_callback, args=(i, "sleep"))
        st.slider("🏫 학교 시간", 0, 24, tuple(sch_data["school"]), key=f"school_{i}", on_change=update_schedule_callback, args=(i, "school"))
        st.slider("✏️ 학원 시간", 0, 24, tuple(sch_data["academy"]), key=f"academy_{i}", on_change=update_schedule_callback, args=(i, "academy"))
        st.slider("🍽️ 식사/휴식", 0, 24, tuple(sch_data["dinner"]), key=f"dinner_{i}", on_change=update_schedule_callback, args=(i, "dinner"))

# 메인 헤더
st.markdown("""
    <div class="hero-header">
        <div class="hero-title">✨ Study Planner Dashboard</div>
        <div class="hero-subtitle">사진 인식(OCR) & 출판사 맞춤형 시험 공부 플래너</div>
    </div>
""", unsafe_allow_html=True)

st.markdown(f'<div class="cheer-card">{random.choice(CHEERING_MESSAGES)}</div>', unsafe_allow_html=True)

if today > end_date:
    st.success("🎉 시험 기간이 종료되었습니다! 정말 고생 많으셨습니다.")
    st.stop()

days_left = (start_date - today).days

col_dday, col_info = st.columns([1, 2])
with col_dday:
    if days_left <= 3 and days_left >= 0:
        st.markdown(f"<h3 style='color: #E74C3C; margin:0;'>⚠️ D-Day : D-{days_left} (최종 스퍼트!)</h3>", unsafe_allow_html=True)
    elif days_left > 3:
        st.markdown(f"<h3 style='margin:0;'>⏳ D-Day : D-{days_left}</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='color: #27AE60; margin:0;'>🔥 시험 진행 중!</h3>", unsafe_allow_html=True)

with col_info:
    st.info(f"📌 시험 기간 : **{start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}**")

st.divider()

# 과목목록 및 체크리스트
st.subheader("✅ 과목별 시험범위 및 교재 등록")

# 1. 📷 사진으로 시험범위 자동 등록 (OCR 연동)
with st.expander("📷 사진(가정통신문/시험범위표) 첨부해서 한 번에 자동 등록하기"):
    st.caption("시험범위 프린트나 가정통신문 사진을 올리시면 AI OCR이 글자를 자동으로 분석해 등록합니다.")
    uploaded_file = st.file_uploader("시험범위 이미지 파일 업로드 (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        st.image(img, caption="업로드된 시험범위 이미지", use_container_width=True)
        
        if st.button("✨ 사진에서 시험범위 자동 추출하기"):
            with st.spinner("사진 속 글자를 읽는 중입니다..."):
                try:
                    # 한국어 + 영어 OCR 수행
                    extracted_text = pytesseract.image_to_string(img, lang="kor+eng")
                    
                    lines = [line.strip() for line in extracted_text.split("\n") if line.strip()]
                    
                    added_count = 0
                    for line in lines:
                        # 과목 구분자 (콜론, 바, 탭 등)가 있거나 주요 과목명이 포함된 줄 파싱
                        match = re.search(r'(국어|수학|영어|사회|과학|역사|기타)[:\-\s]+(.+)', line)
                        if match:
                            subj = match.group(1)
                            content = match.group(2)
                            st.session_state.tasks.append({
                                "subject": subj,
                                "publisher": "사진인식",
                                "unit": content,
                                "done": False
                            })
                            added_count += 1
                        elif len(line) > 3:
                            # 특정 과목으로 분리되지 않은 경우 일반 항목으로 추가
                            st.session_state.tasks.append({
                                "subject": "기타과목",
                                "publisher": "사진인식",
                                "unit": line,
                                "done": False
                            })
                            added_count += 1
                            
                    sync_storage()
                    st.success(f"🎉 총 {added_count}개의 시험범위를 사진에서 추출하여 등록했습니다!")
                    st.rerun()
                except Exception as e:
                    st.error("OCR 처리 중 오류가 발생했습니다. Tesseract 패키지 설치 여부를 확인해주세요.")

# 2. ➕ 직접 입력 등록
with st.expander("➕ 직접 입력으로 과목/출판사/시험범위 추가하기"):
    with st.form("add_task_form", clear_on_submit=True):
        col_in1, col_in2 = st.columns([2, 2])
        with col_in1:
            new_subject = st.text_input("과목명 (예: 국어, 수학)")
        with col_in2:
            new_publisher = st.text_input("출판사 / 교재명 (예: 미래엔, 비상, 학교 프린트)")
            
        new_unit = st.text_input("시험 범위 / 학습 목표 (예: 1~3단원 본문 및 문제풀이)")
        submitted = st.form_submit_button("등록하기")
        
        if submitted and new_subject and new_unit:
            pub_text = new_publisher.strip() if new_publisher.strip() else "자체 교재"
            st.session_state.tasks.append({
                "subject": new_subject,
                "publisher": pub_text,
                "unit": new_unit,
                "done": False
            })
            sync_storage()
            st.rerun()

total_tasks = len(st.session_state.tasks)
completed_tasks = sum(1 for t in st.session_state.tasks if t["done"])
achievement_rate = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

st.metric(label="🏆 전체 달성률", value=f"{achievement_rate}%", delta=f"{completed_tasks}/{total_tasks} 완료")

for idx, task in enumerate(st.session_state.tasks):
    col_check, col_text, col_del = st.columns([1, 6, 1])
    pub_info = f"({task.get('publisher', '자체교재')})" if task.get('publisher') else ""
    
    with col_check:
        is_done = st.checkbox("", value=task["done"], key=f"check_{idx}")
        if is_done != st.session_state.tasks[idx]["done"]:
            st.session_state.tasks[idx]["done"] = is_done
            sync_storage()
            
    with col_text:
        if task["done"]:
            st.markdown(f"~~**[{task['subject']} {pub_info}]** {task['unit']}~~ ✅")
        else:
            st.write(f"**[{task['subject']} {pub_info}]** {task['unit']}")
            
    with col_del:
        if st.button("삭제", key=f"del_{idx}"):
            st.session_state.tasks.pop(idx)
            sync_storage()
            st.rerun()

st.divider()

# 달력 일정표
st.subheader("🗓️ 달력 일정표")

btn_col1, btn_col2, btn_col3, date_col = st.columns([1, 1, 1, 3])
with btn_col1:
    if st.button("◀ 이전 날"):
        st.session_state.selected_date -= datetime.timedelta(days=1)
        st.rerun()
with btn_col2:
    if st.button("📍 오늘"):
        st.session_state.selected_date = datetime.date.today()
        st.rerun()
with btn_col3:
    if st.button("다음 날 ▶"):
        st.session_state.selected_date += datetime.timedelta(days=1)
        st.rerun()
with date_col:
    st.session_state.selected_date = st.date_input("날짜 선택", value=st.session_state.selected_date, key="date_picker_widget")

total_days = (end_date - today).days + 1
days_list = [today + datetime.timedelta(days=i) for i in range(max(1, total_days))]

cols_per_row = 7
for i in range(0, len(days_list), cols_per_row):
    row_days = days_list[i:i+cols_per_row]
    cols = st.columns(len(row_days))
    
    for idx, day in enumerate(row_days):
        with cols[idx]:
            is_selected = (day == st.session_state.selected_date)
            
            if day == today:
                label_str = f"🎯 {day.strftime('%m/%d')}\n오늘"
            elif start_date <= day <= end_date:
                label_str = f"📝 {day.strftime('%m/%d')}\nD-Day"
            else:
                label_str = f"{day.strftime('%m/%d(%a)')}\nD-{(start_date - day).days}"
                
            btn_type = "primary" if is_selected else "secondary"
            
            if st.button(label_str, key=f"cal_btn_{day.strftime('%Y%m%d')}", use_container_width=True, type=btn_type):
                st.session_state.selected_date = day
                st.rerun()

st.divider()

# 시간표
target_date = st.session_state.selected_date
day_weekday = target_date.weekday()
selected_day_schedule = st.session_state.weekly_schedule[day_weekday]

st.subheader(f"⏰ {target_date.strftime('%Y년 %m월 %d일')} ({days_map[day_weekday]}) 맞춤 시간표")

slp_range = selected_day_schedule["sleep"]
sch_range = selected_day_schedule["school"]
aca_range = selected_day_schedule["academy"]
din_range = selected_day_schedule["dinner"]

available_hours = []
blocked_reasons = {}

def is_in_range(hour, start_h, end_h):
    if start_h == end_h:
        return False
    if start_h < end_h:
        return start_h <= hour < end_h
    else:
        return hour >= start_h or hour < end_h

for hour in range(24):
    if is_in_range(hour, slp_range[0], slp_range[1]):
        blocked_reasons[hour] = "🔒 🌙 수면 시간"
    elif is_in_range(hour, sch_range[0], sch_range[1]):
        blocked_reasons[hour] = "🔒 🏫 학교 수업"
    elif is_in_range(hour, aca_range[0], aca_range[1]):
        blocked_reasons[hour] = "🔒 ✏️ 학원 수업"
    elif is_in_range(hour, din_range[0], din_range[1]):
        blocked_reasons[hour] = "🔒 🍽️ 식사 및 휴식"
    else:
        available_hours.append(hour)

uncompleted_tasks = [t for t in st.session_state.tasks if not t["done"]]

st.info(f"💡 **{days_map[day_weekday]}** 수면/일정을 제외한 순수 자습 시간 : **총 {len(available_hours)}시간**")

assigned_schedule = {}
if uncompleted_tasks and available_hours:
    subj_index = 0
    num_subj = len(uncompleted_tasks)
    hours_per_subj = max(1, len(available_hours) // num_subj)
    current_hour_count = 0
    
    for h in available_hours:
        current_task = uncompleted_tasks[subj_index % num_subj]
        pub_str = f"({current_task.get('publisher', '')})" if current_task.get('publisher') else ""
        assigned_schedule[h] = f"📚 [{current_task['subject']} {pub_str}] {current_task['unit']}"
        current_hour_count += 1
        if current_hour_count >= hours_per_subj and (subj_index + 1) < num_subj:
            subj_index += 1
            current_hour_count = 0

schedule_blocks = []
start_h = 0

while start_h < 24:
    if start_h in blocked_reasons:
        reason = blocked_reasons[start_h]
        end_h = start_h + 1
        while end_h < 24 and end_h in blocked_reasons and blocked_reasons[end_h] == reason:
            end_h += 1
        schedule_blocks.append({"start": start_h, "end": end_h, "type": "blocked", "desc": reason})
        start_h = end_h
    elif start_h in assigned_schedule:
        task_desc = assigned_schedule[start_h]
        end_h = start_h + 1
        while end_h < 24 and end_h in assigned_schedule and assigned_schedule[end_h] == task_desc:
            end_h += 1
        schedule_blocks.append({"start": start_h, "end": end_h, "type": "study", "desc": task_desc})
        start_h = end_h
    else:
        end_h = start_h + 1
        while end_h < 24 and (end_h not in blocked_reasons) and (end_h not in assigned_schedule):
            end_h += 1
        schedule_blocks.append({"start": start_h, "end": end_h, "type": "free", "desc": "☕ 자율 학습 및 개인 정비"})
        start_h = end_h

for block in schedule_blocks:
    time_str = f"{block['start']:02d}:00 ~ {block['end']:02d}:00"
    
    if block["type"] == "blocked":
        st.markdown(
            f'<div class="blocked-summary"><b>{time_str}</b> &nbsp;&nbsp;|&nbsp;&nbsp; {block["desc"]}</div>',
            unsafe_allow_html=True
        )
    elif block["type"] == "study":
        st.markdown(
            f'<div class="study-summary"><b>{time_str}</b> &nbsp;&nbsp;|&nbsp;&nbsp; {block["desc"]}</div>',
            unsafe_allow_html=True
        )
    else:
        col_t, col_desc = st.columns([1, 4])
        with col_t:
            st.write(f"**{time_str}**")
        with col_desc:
            st.info(block["desc"])