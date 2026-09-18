import streamlit as st
import datetime

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="스마트 달력 & 시간표 플래너", layout="wide", page_icon="📅")

# 2. 데이터 유지(Session State) 초기화
if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"subject": "국어", "unit": "1~2단원 개념 복습", "done": False},
        {"subject": "수학", "unit": "이차방정식 유형 풀이", "done": False},
        {"subject": "영어", "unit": "1과 본문 암기", "done": False}
    ]

if "selected_date" not in st.session_state:
    st.session_state.selected_date = datetime.date.today()

# 요일별 기본 고정 일정 데이터 초기화 (월:0 ~ 일:6)
days_map = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
if "weekly_schedule" not in st.session_state:
    st.session_state.weekly_schedule = {}
    for i, day in enumerate(days_map):
        if i < 5: # 평일
            st.session_state.weekly_schedule[i] = {
                "school": (8, 16),
                "academy": (18, 21),
                "dinner": (17, 18)
            }
        else: # 주말
            st.session_state.weekly_schedule[i] = {
                "school": (0, 0), # 주말 학교 없음
                "academy": (13, 17) if i == 5 else (0, 0), # 토요일 학원 예시
                "dinner": (18, 19)
            }

# 3. 사이드바: 시험 기간 및 요일별 고정 일정 설정
st.sidebar.header("⚙️ 1. 시험 기간 설정")
today = datetime.date.today()
default_start = today + datetime.timedelta(days=7)
default_end = default_start + datetime.timedelta(days=3)

start_date = st.sidebar.date_input("시험 시작일", default_start)
end_date = st.sidebar.date_input("시험 종료일", default_end)

st.sidebar.divider()
st.sidebar.header("🏫 2. 요일별 고정 일정 (공부 불가 시간)")

# 요일별 탭 생성
day_tabs = st.sidebar.tabs(["월", "화", "수", "목", "금", "토", "일"])
for i, tab in enumerate(day_tabs):
    with tab:
        st.caption(f"📌 {days_map[i]} 일정 설정")
        sch = st.slider(f"학교 시간", 0, 24, st.session_state.weekly_schedule[i]["school"], key=f"sch_{i}")
        aca = st.slider(f"학원 시간", 0, 24, st.session_state.weekly_schedule[i]["academy"], key=f"aca_{i}")
        din = st.slider(f"식사/휴식", 0, 24, st.session_state.weekly_schedule[i]["dinner"], key=f"din_{i}")
        
        # 설정값 저장
        st.session_state.weekly_schedule[i] = {
            "school": sch,
            "academy": aca,
            "dinner": din
        }

# 4. 메인 타이틀
st.title("📅 스마트 달력 & 맞춤 시간표 플래너")

# ---------------------------------------------------------
# 기능 1: D-Day 및 기간 판별
# ---------------------------------------------------------
if today > end_date:
    st.success("🎉 시험 기간이 종료되었습니다! 고생 많으셨습니다.")
    st.stop()

days_left = (start_date - today).days

col_dday, col_info = st.columns([1, 2])
with col_dday:
    if days_left <= 3 and days_left >= 0:
        st.markdown(f"<h2 style='color: red; font-weight: bold;'>⚠️ D-Day: D-{days_left} (비상!)</h2>", unsafe_allow_html=True)
    elif days_left > 3:
        st.markdown(f"## ⏳ D-Day: D-{days_left}")
    else:
        st.markdown("## 🔥 시험 진행 중!")

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
# 기능 3: 달력 클릭형 그리드 (날짜 클릭 시 해당 시간표로 즉시 이동)
# ---------------------------------------------------------
st.subheader("🗓️ 달력 일정표 (날짜를 클릭하면 해당 일시 시간표로 이동합니다)")

# 날짜 이동 상단 버튼
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

# 클릭 가능한 달력 버튼 그리드
total_days = (end_date - today).days + 1
days_list = [today + datetime.timedelta(days=i) for i in range(max(1, total_days))]

cols_per_row = 7
for i in range(0, len(days_list), cols_per_row):
    row_days = days_list[i:i+cols_per_row]
    cols = st.columns(len(row_days))
    
    for idx, day in enumerate(row_days):
        with cols[idx]:
            is_selected = (day == st.session_state.selected_date)
            
            # 날짜 레이블 생성
            if day == today:
                label_str = f"🎯 {day.strftime('%m/%d')}\n오늘"
            elif start_date <= day <= end_date:
                label_str = f"📝 {day.strftime('%m/%d')}\n시험 D-Day"
            else:
                label_str = f"{day.strftime('%m/%d(%a)')}\nD-{(start_date - day).days}"
                
            # 선택 여부에 따른 버튼 타입 지정
            btn_type = "primary" if is_selected else "secondary"
            
            if st.button(label_str, key=f"cal_btn_{day.strftime('%Y%m%d')}", use_container_width=True, type=btn_type):
                st.session_state.selected_date = day
                st.rerun()

st.divider()

# ---------------------------------------------------------
# 기능 4: 선택한 요일 맞춤 일일 타임테이블
# ---------------------------------------------------------
target_date = st.session_state.selected_date
day_weekday = target_date.weekday() # 0(월) ~ 6(일)
selected_day_schedule = st.session_state.weekly_schedule[day_weekday]

st.subheader(f"⏰ {target_date.strftime('%Y년 %m월 %d일')} ({days_map[day_weekday]}) 일일 정밀 시간표")

# 해당 요일의 고정 일정 불러오기
sch_range = selected_day_schedule["school"]
aca_range = selected_day_schedule["academy"]
din_range = selected_day_schedule["dinner"]

available_hours = []
blocked_reasons = {}

for hour in range(24):
    if sch_range[0] != sch_range[1] and sch_range[0] <= hour < sch_range[1]:
        blocked_reasons[hour] = "🏫 학교 수업"
    elif aca_range[0] != aca_range[1] and aca_range[0] <= hour < aca_range[1]:
        blocked_reasons[hour] = "✏️ 학원 수업"
    elif din_range[0] != din_range[1] and din_range[0] <= hour < din_range[1]:
        blocked_reasons[hour] = "🍽️ 저녁 식사 및 휴식"
    elif hour < 6: # 새벽 수면 시간 (00:00 ~ 06:00)
        blocked_reasons[hour] = "🌙 취침 시간"
    else:
        available_hours.append(hour)

uncompleted_tasks = [t for t in st.session_state.tasks if not t["done"]]

st.info(f"💡 **{days_map[day_weekday]}** 고정 일정을 제외하고 **실제 자습 가능한 시간은 총 {len(available_hours)}시간**입니다.")

# 시간표 구성 및 출력
if uncompleted_tasks and available_hours:
    subj_index = 0
    num_subj = len(uncompleted_tasks)
    hours_per_subj = max(1, len(available_hours) // num_subj)
    
    assigned_schedule = {}
    current_hour_count = 0
    
    for h in available_hours:
        current_task = uncompleted_tasks[subj_index % num_subj]
        assigned_schedule[h] = f"📚 [{current_task['subject']}] {current_task['unit']}"
        current_hour_count += 1
        if current_hour_count >= hours_per_subj and (subj_index + 1) < num_subj:
            subj_index += 1
            current_hour_count = 0

    for hour in range(7, 24):
        time_str = f"{hour:02d}:00 ~ {hour+1:02d}:00"
        
        col_t, col_desc = st.columns([1, 4])
        with col_t:
            st.write(f"**{time_str}**")
            
        with col_desc:
            if hour in blocked_reasons:
                st.caption(f"🔒 {blocked_reasons[hour]}")
            elif hour in assigned_schedule:
                st.success(assigned_schedule[hour])
            else:
                st.info("☕ 자율 학습 및 복습")

elif not uncompleted_tasks:
    st.balloons()
    st.success("🎉 모든 시험 공부를 끝마치셨습니다!")
else:
    st.warning("⚠️ 해당 요일에 공부 가능한 남은 시간 슬롯이 없습니다. 사이드바에서 고정 일정을 조정해 보세요.")