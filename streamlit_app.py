import streamlit as st
import datetime
import calendar

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="달력형 시험 공부 플래너", layout="wide", page_icon="📅")

# 2. 데이터 유지(Session State) 초기화
if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"subject": "국어", "unit": "1~2단원 개념 복습", "done": False},
        {"subject": "수학", "unit": "이차방정식 유형 풀이", "done": False},
        {"subject": "영어", "unit": "1과 본문 암기", "done": False}
    ]

# 3. 사이드바: 시험 기간 및 자습 시간 입력
st.sidebar.header("⚙️ 시험 및 공부 설정")

today = datetime.date.today()
default_start = today + datetime.timedelta(days=7)
default_end = default_start + datetime.timedelta(days=3)

# 시험 시작일과 종료일 입력
start_date = st.sidebar.date_input("시험 시작일", default_start)
end_date = st.sidebar.date_input("시험 종료일", default_end)
study_hours_per_day = st.sidebar.number_input("하루 자습 가능 시간 (시간)", min_value=1, max_value=16, value=4)

# 4. 메인 타이틀
st.title("📅 달력 기반 시험 맞춤형 공부 플래너")

# ---------------------------------------------------------
# 기능 1: 시험 기간 검증 및 D-Day 카운터
# ---------------------------------------------------------
if today > end_date:
    st.success("🎉 시험 기간이 완료되었습니다! 고생 많으셨습니다.")
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
# 기능 2: 과목/단원 체크리스트 및 달성률
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

# 체크리스트 관리
total_tasks = len(st.session_state.tasks)
completed_tasks = sum(1 for t in st.session_state.tasks if t["done"])
achievement_rate = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

st.metric(label="🏆 전체 달성률", value=f"{achievement_rate}%", delta=f"{completed_tasks}/{total_tasks} 완료")

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
# 기능 3: 오늘부터 시험 종료일까지의 달력(Calendar) 그리드
# ---------------------------------------------------------
st.subheader("🗓️ 시험 준비 달력 일정표")

# 달력에 표시할 일수 계산
total_days = (end_date - today).days + 1
selected_date = st.date_input("시간표를 조회할 날짜 선택", today, min_value=today, max_value=end_date)

# 달력 카드 그리드 배치 (7일씩 한 줄)
cols_per_row = 7
days_list = [today + datetime.timedelta(days=i) for i in range(total_days)]

for i in range(0, len(days_list), cols_per_row):
    row_days = days_list[i:i+cols_per_row]
    cols = st.columns(len(row_days))
    
    for idx, day in enumerate(row_days):
        with cols[idx]:
            # 날짜에 따른 스타일링
            if day == today:
                box_color = "background-color: #E3F2FD; border: 2px solid #2196F3;"
                day_title = "오늘 🎯"
            elif start_date <= day <= end_date:
                box_color = "background-color: #FFEBEE; border: 1px solid #FF5252;"
                day_title = "시험 D-Day 📝"
            else:
                box_color = "background-color: #F5F5F5; border: 1px solid #DDD;"
                day_title = f"D-{(start_date - day).days}"
                
            st.markdown(
                f"""
                <div style="{box_color} padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 10px;">
                    <div style="font-size: 12px; color: #666;">{day.strftime('%m/%d (%a)')}</div>
                    <div style="font-weight: bold; font-size: 14px; margin-top: 5px;">{day_title}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

st.divider()

# ---------------------------------------------------------
# 기능 4: 선택한 날짜의 시간표(Timetable) 자동 배분
# ---------------------------------------------------------
st.subheader(f"⏰ {selected_date.strftime('%Y년 %m월 %d일')} 과목별 맞춤 시간표")

uncompleted = [t for t in st.session_state.tasks if not t["done"]]

if uncompleted:
    num_subj = len(uncompleted)
    time_per_subj = round(study_hours_per_day / num_subj, 1)
    
    start_hour = 18  # 오후 6시 기준 자동 배분 예시
    
    st.info(f"💡 하루 **{study_hours_per_day}시간**을 **{num_subj}개 미완료 과목**에 균등 배치한 시간표입니다.")
    
    current_time = datetime.datetime.combine(selected_date, datetime.time(start_hour, 0))
    
    for task in uncompleted:
        end_time = current_time + datetime.timedelta(hours=time_per_subj)
        
        col_time, col_detail = st.columns([1, 3])
        with col_time:
            st.warning(f"⏱️ **{current_time.strftime('%H:%M')} ~ {end_time.strftime('%H:%M')}**")
        with col_detail:
            st.success(f"📚 **[{task['subject']}]** {task['unit']} ({time_per_subj}시간 권장)")
            
        current_time = end_time
else:
    st.balloons()
    st.success("🎉 목표한 모든 과목 공부를 마쳤습니다!")