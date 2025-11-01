"""
Step 2 – GPT API 기반 서술형 채점 + 피드백 (점수 미사용)
───────────────────────────────────────────────
• 기존 Step 1‑2 코드 하단에 그대로 이어 붙이면 됩니다. (별도 파일로도 사용 가능)
• 교사는 GRADING_GUIDELINES 사전에 문항별 ‘채점 기준’을 자유롭게 입력하세요.
• 피드백은 ‘정답/오답 + 200자 이내 설명’ 형식으로 반환됩니다.
• 비용 절감을 위해 temperature=0, max_tokens≈250(≈200자) 사용.
"""

import streamlit as st

# ── 1. 수업 제목 ──
st.title("전류의 흐름")  # ← 교과별 제목으로 자유롭게 수정하세요.

# ── 2. 학번 입력 ──
student_id = st.text_input("학번", help="학생의 학번을 작성하세요. (예: 10130)")

# ── 3‑1. 서술형 문제 1 표시 ──
QUESTION_1 = """
(+)극에 이끌려 움직이는 입자와 그 입자가 띠고 있는 전하에 대해 서술하시오
"""  # ← 교사가 원하는 서술형 문제로 변경
st.markdown("#### 1번(5점)")
st.write(QUESTION_1)
answer_1 = st.text_area("답안을 입력하세요", key="answer1", height=150)

# ── 3‑2. 서술형 문제 2 표시 ──
QUESTION_2 = """
도선과 전지를 연결했을때, 도선 속 입자의 움직임에 대해 서술하시오.
"""
st.markdown("#### 2번(5점)")
st.write(QUESTION_2)
answer_2 = st.text_area("답안을 입력하세요", key="answer2", height=150)

# ── 3‑3. 서술형 문제 3 표시 ──
QUESTION_3 = """
전류의 흐름 방향에 대해 서술하시오.
"""
st.markdown("#### 3번(5번)")
st.write(QUESTION_3)
answer_3 = st.text_area("답안을 입력하세요", key="answer3", height=150)

# 답안을 리스트로 모아 이후 채점 로직에서 재사용하기
answers = [answer_1, answer_2, answer_3]

# ── 4. 전체 제출 버튼 ──
if st.button("제출"):
    if not student_id.strip():
        st.warning("학번을 입력하세요.")
    elif any(ans.strip() == "" for ans in answers):
        st.warning("모든 답안을 작성하세요.")
    else:
        st.success(f"제출 완료! 학번: {student_id}")
        # ⚠️ Step 2에서 GPT 채점 및 DB 저장 로직을 여기에 추가할 예정입니다.
        
from openai import OpenAI, OpenAIError

# ── 0. OpenAI 클라이언트 ──
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("⚠️ secrets.toml 에 OPENAI_API_KEY 를 설정하세요.")
    st.stop()

# ── 1. 문항별 채점 기준 (교사가 수정) ──
GRADING_GUIDELINES = {
    1: "(+)극에 이끌리는 입자는 전자이고, 전자는 (-)전하를 띠고 있음을 언급한다.",
    2: "도선 속 입자 중 전자가 전지의 (+)극과 가까워지고, (-)극과 멀어지는 방향으로 움직임을 언급한다. (+)극과 가까워지거나, (-)극과 멀어지거나 둘 중 하나만 언급해도 정답처리 함.",
    3: "전류는 (+)극에서 (-)극으로 이동한다. 또는 전자의 이동 방향과 반대이다. 둘 중 하나만 언급해도 정답으로 처리함"
}

# ── 2. 제출 버튼 (Step 1‑2의 버튼을 대체/호출) ──
if st.button("GPT 피드백 확인"):

    # answers 리스트는 Step 1‑2 코드에서 정의됨
    try:
        answers
    except NameError:
        st.error("answers 리스트가 정의되지 않았습니다. Step 1‑2 코드와 함께 실행하세요.")
        st.stop()

    feedbacks = []
    for idx, ans in enumerate(answers, start=1):
        # 빈 답안 처리
        if ans.strip() == "":
            feedbacks.append("X: 답안이 제출되지 않았습니다.")
            continue
        criterion = GRADING_GUIDELINES.get(idx, "채점 기준이 없습니다.")

        # 프롬프트 구성
        prompt = (
            f"문항 번호: {idx}\n"
            f"채점 기준: {criterion}\n"
            f"학생 답안: {ans}\n"
            "요구사항: 1) 정답 여부(O/X) 한 글자, 2) 200자 이내 구체적 피드백.\n"
            "형식 예시 → O: (피드백)"
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",            # 필요 시 모델 변경
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=250,
            )
            feedback_text = response.choices[0].message.content.strip()
        except OpenAIError as e:
            feedback_text = f"API 오류: {e}"

        feedbacks.append(feedback_text)

    # ── 3. 결과 표시 ──
    for i, fb in enumerate(feedbacks, start=1):
        st.markdown(f"##### ▶ 서술형 문제 {i} 피드백")
        st.write(fb)

    st.success("모든 피드백이 생성되었습니다. 교사 확인 후 학생에게 전달하세요.")
