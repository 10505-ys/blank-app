import streamlit as st
import datetime
import random

# 1. 페이지 기본 설정 및 브라운 테마 CSS 스타일 적용
st.set_page_config(page_title="스마트 달력 & 맞춤 시간표 플래너", layout="wide", page_icon="📅")

st.markdown("""
    <style>
    /* 전체 배경 및 기본 글꼴 색상 */
    .stApp {
        background-color: #FAF6F0;
        color: #4A3E3D;
    }
    
    /* 메인 타이틀 색상 */
    h1 {
        color: #5C3D2E !important;
        font-family: 'Malgun Gothic', sans-serif;
    }
    h2, h3 {
        color: #68422A !important;
    }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #F0E5D8;
        border-right: 1px solid #D9C5B2;
    }
    
    /* 응원 박스 스타일 */
    .cheer-box {
        background-color: #E8D8C8;
        border-left: 5px solid #8C5A3C;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #4A3E3D;
        font-weight: bold;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
    }
    
    /* 통합된 불가 시간대 블록 스타일 */
    .blocked-summary {
        background-color: #EFE6DD;
        border: 1px solid #D1C2B4;
        padding: 10px 15px;
        border-radius: 6px;
        color: #7A685A;
        margin-bottom: 6px;
        font-size: 0.95rem;
    }
    
    /* 공부 시간 블록 스타일 */
    .study-summary {
        background-color: #D5E5D5;
        border-left: 5px solid #4A7C59;
        padding: 10px 15px;
        border-radius: 6px;
        color: #2D4A34;
        margin-bottom: 6px;
        font-weight: bold;
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        border-radius: 6px;
        border: 1px solid #B59A85;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 응원 메시지 리스트
CHEERING_MESSAGES = [
    "🍀 지금까지 열심히 준비한 만큼, 시험에서 최고의 실력을 발휘할 수 있을 거예요!",
    "🔥 할 수 있다! 포기하지 않고 한 걸음씩 나아가는 당신을 응원합니다.",
    "☕ 중간에 따뜻한 차 한 잔 마시며 쉬어가는 것도 잊지 마세요. 파이팅!",
    "💡 노력을 쏟아부은 시간은 절대 배신하지 않습니다. 자신감을 가지세요!",
    "🎯 시험 당일, 아는 문제는 확실하게! 찍는 문제도 정답으로 이어지는 행운이 함께하길!"
]

# 3. Session State 초기화
if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"subject": "국어", "unit": "1~2단원 개념 복습", "done": False},
        {"subject": "수학", "unit": "이차방정식 유형 풀이", "done": False},
        {"subject": "영어", "unit": "1과 본문 암기", "done": False}
    ]

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date.today()

days_map = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
if "weekly_schedule" not in st.session_state:
    st.session_state.weekly_schedule = {}
    for i in range(7):
        if i < 5: # 평일
            st.session_state.weekly_schedule[i] = {
                "sleep": (2, 8),
                "school": (8, 16),
                "academy": (18, 21),
                "dinner": (17, 18)
            }
        else: # 주말
            st.session_state.weekly_schedule[i] = {
                "sleep": (3, 10),
                "school": (0, 0),
                "academy": (13, 17) if i == 5 else (0, 0),
                "dinner": (18, 19)
            }

# 4. 사이드바 설정
st.sidebar.header("⚙️ 1. 시험 기간 설정")
today = datetime.date.today()
default_start = today + datetime.timedelta(days=7)
default_end = default_start + datetime.timedelta(days=3)

start_date = st.sidebar.date_input("시험 시작일", default_start)
end_date = st.sidebar.date_input("시험 종료일", default_end)

st.sidebar.divider()
st.sidebar.header("🏫 2. 요일별 일과 & 수면 시간 설정")

day_tabs = st.sidebar.tabs(["월", "화", "수", "목", "금", "토", "일"])
for i, tab in enumerate(day_tabs):
    with tab:
        st.caption(f"📌 {days_map[i]} 일정 설정")
        slp = st.slider(f"🌙 취침 ~ 기상 시간", 0, 24, st.session_state.weekly_schedule[i]["sleep"], key=f"slp_{i}")
        sch = st.slider(f"🏫 학교 시간", 0, 24, st.session_state.weekly_schedule[i]["school"], key=f"sch_{i}")
        aca = st.slider(f"✏️ 학원 시간", 0, 24, st.session_state.weekly_schedule[i]["academy"], key=f"aca_{i}")
        din = st.slider(f"🍽️ 식사/휴식", 0, 24, st.session_state.weekly_schedule[i]["dinner"], key=f"din_{i}")
        
        st.session_state.weekly_schedule[i] = {
            "sleep": slp,
            "school": sch,
            "academy": aca,
            "dinner": din
        }

st.sidebar.divider()
st.sidebar.markdown("💌 **오늘의 응원 한마디**")
st.sidebar.info(random.choice(CHEERING_MESSAGES))

# 5. 메인 타이틀 및 응원 카드
st.title("📅 스마트 달력 & 맞춤 시간표 플래너")

cheer_msg = random.choice(CHEERING_MESSAGES)
st.markdown(f'<div class="cheer-box">{cheer_msg}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 기능 1: D-Day 및 기간 판별
# ---------------------------------------------------------
if today > end_date:
    st.success("🎉 시험 기간이 종료되었습니다! 정말 고생 많으셨습니다.")
    st.stop()

days_left = (start_date - today).days

col_dday, col_info = st.columns([1, 2])
with col_dday:
    if days_left <= 3 and days_left >= 0:
        st.markdown(f"<h2 style='color: #B23B23; font-weight: bold;'>⚠️ D-Day: D-{days_left} (끝까지 힘내세요!)</h2>", unsafe_allow_html=True)
    elif days_left > 3:
        st.markdown(f"## ⏳ D-Day: D-{days_left}")
    else:
        st.markdown("## 🔥 시험 진행 중! 마지막까지 정성을 모아봐요!")

with col_info:
    st.info(f"📌 시험 기간: **{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}**")

st.divider()

# ---------------------------------------------------------
# 기능 2: 과목별 시험범위 등록 및 체크리스트
# ---------------------------------------------------------
st.subheader("✅ 과목별 공부 목표 등록")

with st.expander("➕ 새 과목/시험범위 추가하기"):
    with st.form("add_task_form", clear_on_submit=True):
        new_subject = st.text_input("과목명 (예: 국어, 수학)")
        new_unit = st.text_input("시험 범위/단원 (예: 1~3단원)")
        submitted = st.form_submit_button("추가하기")
        if submitted and new_subject and new_unit:
            st.session_state.tasks.append({"subject": new_subject, "unit": new_unit, "done": False})
            st.rerun()

total_tasks = len(st.session_state.tasks)
completed_tasks = sum(1 for t in st.session_state.tasks if t["done"])
achievement_rate = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

st.metric(label="🏆 전체 공부 달성률", value=f"{achievement_rate}%", delta=f"{completed_tasks}/{total_tasks} 완료")

for idx, task in enumerate(st.session_state.tasks):
    col_check, col_text, col_del = st.columns([1, 6, 1])
    with col_check:
        is_done = st.checkbox("", value=task["done"], key=f"check_{idx}")
        st.session_state.tasks[idx]["done"] = is_done
    with col_text:
        if is_done:
            st.markdown(f"~~**[{task['subject']}]** {task['unit']}~~ ✅")
        else:
            st.write(f"**[{task['subject']}]** {task['unit']}")
    with col_del:
        if st.button("삭제", key=f"del_{idx}"):
            st.session_state.tasks.pop(idx)
            st.rerun()

st.divider()

# ---------------------------------------------------------
# 기능 3: 달력 일정표
# ---------------------------------------------------------
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
    st.session_state.selected_date = st.date_input(
        "직접 날짜 선택", 
        value=st.session_state.selected_date,
        key="date_picker_widget"
    )

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
                label_str = f"📝 {day.strftime('%m/%d')}\n시험 D-Day"
            else:
                label_str = f"{day.strftime('%m/%d(%a)')}\nD-{(start_date - day).days}"
                
            btn_type = "primary" if is_selected else "secondary"
            
            if st.button(label_str, key=f"cal_btn_{day.strftime('%Y%m%d')}", use_container_width=True, type=btn_type):
                st.session_state.selected_date = day
                st.rerun()

st.divider()

# ---------------------------------------------------------
# 기능 4: 연속된 불가 시간대를 하나로 병합한 간결한 시간표
# ---------------------------------------------------------
target_date = st.session_state.selected_date
day_weekday = target_date.weekday()
selected_day_schedule = st.session_state.weekly_schedule[day_weekday]

st.subheader(f"⏰ {target_date.strftime('%Y년 %m월 %d일')} ({days_map[day_weekday]}) 맞춤 타임테이블")

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
        blocked_reasons[hour] = "🔒 🌙 취침 및 수면 시간"
    elif is_in_range(hour, sch_range[0], sch_range[1]):
        blocked_reasons[hour] = "🔒 🏫 학교 수업"
    elif is_in_range(hour, aca_range[0], aca_range[1]):
        blocked_reasons[hour] = "🔒 ✏️ 학원 수업"
    elif is_in_range(hour, din_range[0], din_range[1]):
        blocked_reasons[hour] = "🔒 🍽️ 식사 및 휴식"
    else:
        available_hours.append(hour)

uncompleted_tasks = [t for t in st.session_state.tasks if not t["done"]]

st.info(f"💡 **{days_map[day_weekday]}** 수면/학교/학원 시간을 제외하고 **실제 자습할 수 있는 시간은 총 {len(available_hours)}시간**입니다.")

# 공부시간 배정
assigned_schedule = {}
if uncompleted_tasks and available_hours:
    subj_index = 0
    num_subj = len(uncompleted_tasks)
    hours_per_subj = max(1, len(available_hours) // num_subj)
    current_hour_count = 0
    
    for h in available_hours:
        current_task = uncompleted_tasks[subj_index % num_subj]
        assigned_schedule[h] = f"📚 [{current_task['subject']}] {current_task['unit']}"
        current_hour_count += 1
        if current_hour_count >= hours_per_subj and (subj_index + 1) < num_subj:
            subj_index += 1
            current_hour_count = 0

# 시간대 묶기 알고리즘 (연속된 동일 타입의 시간대를 하나로 통합)
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

# 병합된 시간표 출력
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