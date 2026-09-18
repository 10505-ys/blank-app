import streamlit as st
import datetime

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="시험 공부 플래너", layout="wide", page_icon="🎯")

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
st.title("🎯 시험 공부 맞춤형 플래너")

# ---------------------------------------------------------
# 기능 1: D-Day / 기간 종료 판별 / 진행률 및 경고 색상 적용
# ---------------------------------------------------------
days_left = (start_date - today).days

# 시험 상태 체크
if today > end_date:
    st.success("🎉 시험 기간이 종료되었습니다! 고생 많으셨습니다.")
    st.stop()  # 시험이 끝나면 플래너 동작 중단
elif today >= start_date and today <= end_date:
    st.warning("🔥 현재 시험이 진행 중입니다! 끝까지 화이팅하세요!")
    progress_val = 100
else:
    # 시험 D-Day 계산
    total_prep_days = (start_date - today).days
    progress_val = max(0, min(100, int((1 - (days_left / 30)) * 100))) # 30일 기준 진행률 예시

# D-Day 카운터 메트릭 및 경고 색상
col_dday, col_prog = st.columns([1, 2])

with col_dday:
    if days_left <= 3 and days_left >= 0:
        # D-3 이하일 때 빨간색 경고
        st.markdown(
            f"<h2 style='color: red; font-weight: bold;'>⚠️ D-Day: D-{days_left} (비상!)</h2>", 
            unsafe_allow_html=True
        )
    elif days_left > 3:
        st.markdown(f"## ⏳ D-Day: D-{days_left}")

with col_prog:
    st.write(f"📊 **시험 대비 준비 진행률 ({progress_val}%)**")
    st.progress(progress_val / 100)

st.divider()

# ---------------------------------------------------------
# 기능 2: 과목/단원 체크리스트 & 실시간 달성률 카드
# ---------------------------------------------------------
st.subheader("✅ 과목별 시험범위 체크리스트")

# 새 과목/단원 추가 폼
with st.expander("➕ 새 과목 및 시험범위 추가하기"):
    with st.form("add_task_form", clear_on_submit=True):
        new_subject = st.text_input("과목명 (예: 국어, 수학)")
        new_unit = st.text_input("시험 범위/단원 (예: 1~3단원)")
        submitted = st.form_submit_button("추가하기")
        if submitted and new_subject and new_unit:
            st.session_state.tasks.append({"subject": new_subject, "unit": new_unit, "done": False})
            st.rerun()

# 달성률 계산 및 시각화 카드
total_tasks = len(st.session_state.tasks)
completed_tasks = sum(1 for t in st.session_state.tasks if t["done"])
achievement_rate = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

# 달성률 카드 출력
st.metric(label="🏆 오늘 공부 달성률", value=f"{achievement_rate}%", delta=f"{completed_tasks}/{total_tasks} 완료")

# 체크리스트 항목 출력
for idx, task in enumerate(st.session_state.tasks):
    col_check, col_text, col_del = st.columns([1, 6, 1])
    
    with col_check:
        # 체크박스 상태 업데이트
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
# 기능 3: 자습 시간 기반 자동 추천 스케줄러
# ---------------------------------------------------------
st.subheader("📅 하루 과목별 자동 추천 시간표")

# 미완료 과목 추출
uncompleted_subjects = list(set([t["subject"] for t in st.session_state.tasks if not t["done"]]))

if uncompleted_subjects:
    num_subjects = len(uncompleted_subjects)
    allocated_time = round(study_hours_per_day / num_subjects, 1)
    
    st.info(f"💡 총 자습 시간 **{study_hours_per_day}시간**을 남은 과목 **{num_subjects}개**에 균등 배분했습니다.")
    
    cols = st.columns(min(num_subjects, 4))
    for i, subj in enumerate(uncompleted_subjects):
        with cols[i % 4]:
            st.success(f"📚 **{subj}**\n\n⏱️ 추천: **{allocated_time}시간**")
else:
    st.balloons()
    st.success("🎉 모든 과목의 공부를 끝마치셨습니다! 시험에서 좋은 결과가 있길 바랍니다!")