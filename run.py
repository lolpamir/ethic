import streamlit as st
url = 'https://www.youtube.com/watch?v=XyEOEBsa8I4'
# 페이지 설정
st.set_page_config(layout='wide', page_title='EthicApp')

# 앱 타이틀
st.title('Ethic is good for us')

# # 사이드바 메뉴
# # (사이드바 버튼 추가): "학생데이터 가져오기" 버튼을 추가하고, 클릭했을 때, CONTENT영역에 저장된 학생 데이터(data.txt)를 불러와서 제시합니다.
# st.sidebar.subheader('Menu...')
# st.sidebar.markdown("""
# - 홈  
# - AI 윤리 개요  
# - 사례 분석  
# - 참고 자료
# """)  # 기존 사이드바 유지

# 사이드바 메뉴
st.sidebar.subheader('Menu...')
st.sidebar.markdown("""
- 홈  
- AI 윤리 개요  
- 사례 분석  
- 참고 자료
""")  # 기존 사이드바 유지

# "학생데이터 가져오기" 버튼 추가
if st.sidebar.button("학생데이터(더블클릭)"):
    # data.txt 파일에서 데이터 읽기
    try:
        with open("data.txt", "r", encoding="utf-8") as f:
            student_data = f.read()  # 전체 파일 내용 읽기
        # 콘텐츠 영역에 학생 데이터 표시
        st.subheader("학생 데이터")
        st.text_area("저장된 학생 데이터", student_data, height=300)
    except FileNotFoundError:
        st.error("data.txt 파일을 찾을 수 없습니다.")

# 내용 제시 영역 및 화면 분할
content_col, tips_col = st.columns([4, 1])  # 컬럼 비율 (4,1)

# 왼쪽 넓은 content 영역
with content_col:
    st.subheader("AI Ethics and Responsibility")
    st.video(url)  # YouTube 영상

    st.write("""
        인공지능(AI)은 현대 사회를 변화시키는 핵심 기술입니다.  
        그러나 AI의 사용에는 윤리적 고려가 반드시 따라야 하며, 우리는 다음과 같은 원칙을 따라야 합니다:
        
        - **공정성 (Fairness)**: 알고리즘은 누구에게도 불공정한 결과를 내지 않아야 합니다.  
        - **책임성 (Accountability)**: AI 시스템으로 인한 결과에 대해 책임 소재가 분명해야 합니다.  
        - **투명성 (Transparency)**: 의사결정 과정이 이해 가능하고 설명 가능해야 합니다.  
        - **프라이버시 보호 (Privacy)**: 개인 정보는 철저히 보호되어야 합니다.
    """)

    # 🔽 사용자 입력 영역 (추가된 부분)
    st.markdown("#### ✍️ 당신의 생각을 공유해주세요")
    user_input = st.text_area("인공지능 윤리에 대한 의견 또는 질문을 작성해주세요:", height=100)
    if st.button("제출하기"):
        if user_input.strip():  # 빈 문자열은 저장하지 않음
            with open("data.txt", "a", encoding="utf-8") as f:
                f.write(user_input + "\n---\n")  # 구분선 포함하여 저장
            st.success("의견이 성공적으로 저장되었습니다.")
        else:
            st.warning("내용을 입력해주세요.")

# 오른쪽 좁은 tips 영역
with tips_col:
    st.subheader("Tips...")
    st.markdown("""
    ✅ **AI 윤리 체크리스트**  
    - [ ] 데이터 편향 점검  
    - [ ] 결과 설명 가능성 확보  
    - [ ] 사용자 동의 확보  
    - [ ] 지속적 모니터링 체계  

    📌 **참고 링크**  
    - [OECD AI 원칙](https://oecd.ai/en/dashboards)  
    - [AI 윤리 가이드라인 (EU)](https://digital-strategy.ec.europa.eu/en/policies/european-approach-artificial-intelligence)
    """)
