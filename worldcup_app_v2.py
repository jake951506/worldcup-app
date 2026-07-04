
import streamlit as st
import random
import json
import os
from datetime import datetime
from collections import Counter

st.set_page_config(page_title="서강대 본부 기피부서 조사", page_icon="🚫", layout="centered")

TEAMS = [
    {"name": "예산팀", "desc": "예산 편성"},
    {"name": "전략기획팀", "desc": "대학 평가, 공간, 통계"},
    {"name": "교육혁신팀", "desc": "대학혁신지원 국고사업"},
    {"name": "발전홍보팀", "desc": "발전기금, 대내외홍보"},
    {"name": "교무팀", "desc": "교원 인사, 급여, 상벌"},
    {"name": "인사총무팀", "desc": "직원 인사, 일반 행정"},
    {"name": "재무팀", "desc": "회계, 자금 집행, 등록금"},
    {"name": "구매팀", "desc": "용역, 장비, 공사, 비품"},
    {"name": "관재팀", "desc": "자산관리(비품/재산)"},
    {"name": "학사지원팀", "desc": "수업, 성적, 학적 관리"},
    {"name": "학생지원팀", "desc": "학생회, 장학금 지원"},
    {"name": "취업지원팀", "desc": "진로 상담, 취업 프로그램"},
    {"name": "입학팀", "desc": "신입생 선발, 입시 홍보"},
    {"name": "국제학생팀", "desc": "외국인 선발, 학생관리"},
    {"name": "국제교류팀", "desc": "교환학생, 하계대학"},
    {"name": "법전원행정팀", "desc": "로스쿨 교수, 학생관리"}
]

ROUND_NAMES = {16: "16강", 8: "8강", 4: "4강", 2: "결승"}
RESULT_FILE = "worldcup_result.json"
ADMIN_PASSWORD = "sogang2026"

def load_results():
    if os.path.exists(RESULT_FILE):
        try:
            with open(RESULT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_result(respondent, champion, runner_up, history):
    result = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "team": respondent["team"],
        "name": respondent["name"],
        "emp_id": respondent["emp_id"],
        "most_avoided": champion["name"],
        "second_avoided": runner_up,
        "history": history
    }
    all_results = load_results()
    all_results.append(result)
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

def init_state():
    if "stage" not in st.session_state:
        st.session_state.stage = "info"
    if "current_round" not in st.session_state:
        teams = TEAMS[:]
        random.shuffle(teams)
        st.session_state.current_round = teams
        st.session_state.next_round = []
        st.session_state.match_idx = 0
        st.session_state.history = []
        st.session_state.finished = False
        st.session_state.champion = None
        st.session_state.runner_up = None

def choose(more_avoided, less_avoided, round_size):
    st.session_state.history.append({
        "round": ROUND_NAMES.get(round_size, f"{round_size}강"),
        "team_a": more_avoided["name"],
        "team_b": less_avoided["name"],
        "more_avoided": more_avoided["name"],
        "less_avoided": less_avoided["name"]
    })
    st.session_state.next_round.append(more_avoided)
    st.session_state.match_idx += 2
    current = st.session_state.current_round
    if st.session_state.match_idx >= len(current):
        if len(st.session_state.next_round) == 1:
            st.session_state.champion = st.session_state.next_round[0]
            st.session_state.runner_up = st.session_state.history[-1]["less_avoided"]
            st.session_state.finished = True
            save_result(st.session_state.respondent, st.session_state.champion, st.session_state.runner_up, st.session_state.history)
        else:
            st.session_state.current_round = st.session_state.next_round
            st.session_state.next_round = []
            st.session_state.match_idx = 0

def restart():
    for key in ["stage", "current_round", "next_round", "match_idx", "history", "finished", "champion", "runner_up", "respondent"]:
        if key in st.session_state:
            del st.session_state[key]

def show_survey():
    st.title("🚫 서강대학교 본부 기피부서 조사")
    st.caption("두 팀 중 상대적으로 더 근무하고 싶지 않은(기피하는) 팀을 선택해 주세요. 최종적으로 가장 기피하는 팀 1위를 도출합니다.")

    init_state()

    if st.session_state.stage == "info":
        st.subheader("응답자 정보 입력")
        with st.form("info_form"):
            team = st.text_input("현재 소속 팀명")
            name = st.text_input("본인 성명")
            emp_id = st.text_input("사번")
            submitted = st.form_submit_button("설문 시작하기")
            if submitted:
                if not team or not name or not emp_id:
                    st.error("소속 팀명, 성명, 사번을 모두 입력해 주세요.")
                else:
                    st.session_state.respondent = {"team": team, "name": name, "emp_id": emp_id}
                    st.session_state.stage = "tournament"
                    st.rerun()
        return

    if st.session_state.finished:
        champ = st.session_state.champion
        st.warning(f"🚫 최종 기피 1위: **{champ['name']}** ({champ['desc']})")
        st.info(f"🥈 기피 2위: **{st.session_state.runner_up}**")
        st.subheader("대진 요약")
        for h in st.session_state.history:
            st.write(f"[{h['round']}] {h['team_a']} vs {h['team_b']} → 더 기피: **{h['more_avoided']}**")
        st.success("응답이 저장되었습니다. 참여해 주셔서 감사합니다.")
        st.button("새로운 응답 입력하기", on_click=restart)
        return

    current = st.session_state.current_round
    idx = st.session_state.match_idx
    round_size = len(current)
    a, b = current[idx], current[idx + 1]

    st.subheader(f"{ROUND_NAMES.get(round_size, str(round_size)+'강')} — {idx // 2 + 1} / {round_size // 2} 경기")
    st.progress(idx / round_size)
    st.write("아래 두 팀 중 **더 기피하는 팀**을 선택하세요.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### {a['name']}")
        st.write(a["desc"])
        st.button(f"{a['name']} 더 기피", key=f"a_{idx}_{round_size}", on_click=choose, args=(a, b, round_size))
    with col2:
        st.markdown(f"### {b['name']}")
        st.write(b["desc"])
        st.button(f"{b['name']} 더 기피", key=f"b_{idx}_{round_size}", on_click=choose, args=(b, a, round_size))

def show_admin():
    st.title("📊 관리자 통계 화면")
    pw = st.text_input("관리자 비밀번호", type="password")
    if pw != ADMIN_PASSWORD:
        if pw:
            st.error("비밀번호가 올바르지 않습니다.")
        return

    results = load_results()
    if not results:
        st.info("아직 저장된 응답이 없습니다.")
        return

    st.success(f"총 응답 수: {len(results)}건")

    df_rows = []
    for r in results:
        df_rows.append({
            "응답시각": r["timestamp"],
            "소속팀": r["team"],
            "성명": r["name"],
            "사번": r["emp_id"],
            "기피1위": r["most_avoided"],
            "기피2위": r["second_avoided"]
        })

    import pandas as pd
    df = pd.DataFrame(df_rows)
    st.subheader("전체 응답 목록")
    st.dataframe(df, use_container_width=True)

    st.subheader("팀별 '최종 기피 1위' 득표 수")
    counter = Counter(r["most_avoided"] for r in results)
    rank_df = pd.DataFrame(counter.most_common(), columns=["팀명", "기피1위 득표수"])
    st.dataframe(rank_df, use_container_width=True)
    st.bar_chart(rank_df.set_index("팀명"))

    st.subheader("팀별 '결승 진출(기피 2위 이상)' 횟수")
    finalist_counter = Counter()
    for r in results:
        finalist_counter[r["most_avoided"]] += 1
        finalist_counter[r["second_avoided"]] += 1
    fin_df = pd.DataFrame(finalist_counter.most_common(), columns=["팀명", "결승진출 횟수"])
    st.dataframe(fin_df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("전체 응답 CSV 다운로드", data=csv, file_name="worldcup_result.csv", mime="text/csv")

mode = st.sidebar.radio("화면 선택", ["설문 응답", "관리자 통계"])
if mode == "설문 응답":
    show_survey()
else:
    show_admin()
