
import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime
import random
import csv
import re
import os
import xml.etree.ElementTree as ET
from io import StringIO

# Gemini API 설정
try:
    genai.configure(api_key=os.getenv("AIzaSyCjaXGNzHNhXDa1hmBnj0A6CyOgRG5q1vk"))
except Exception as e:
    st.error(f"Gemini API 키 설정 오류: {e}. Streamlit Cloud의 Secrets 설정에서 GEMINI_API_KEY를 확인하세요.")
    st.stop()

st.set_page_config(page_title="인공지능과 윤리", layout="wide")
st.title("📝 최근 기사로 알아보는 AI의 권리침해")

# 데이터 디렉토리 확인 및 생성
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR)
    except Exception as e:
        st.error(f"데이터 디렉토리 생성 실패: {e}")
        st.stop()

# 요약 함수 정의
def summarize_article(article_text):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        prompt = (
            "다음 기사 내용을 서론, 본론, 결론의 구조로 자연스럽고 간결하게 요약해줘. "
            "각 부분은 소제목으로 구분해줘.\n\n"
            f"{article_text}"
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gemini 요약 실패: {e}"

# 기사 본문 추출 함수 (newspaper 제거 버전)
def fetch_article_text(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text(strip=True) for p in paragraphs])
        return text if len(text.strip()) > 200 else ""
    except Exception as e:
        st.error(f"기사 본문 추출 실패: {e}")
        return ""

# 구글 뉴스에서 기사 링크 가져오기 (50개 중 랜덤 3개)
def get_google_news_links(keyword):
    try:
        query = f"AI+{keyword}"
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(rss_url, headers=headers, timeout=10)
        response.raise_for_status()

        rss_content = StringIO(response.text)
        tree = ET.parse(rss_content)
        root = tree.getroot()

        all_links = []
        for item in root.findall(".//item")[:50]:
            title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            if title and link:
                all_links.append((title, link))

        return random.sample(all_links, k=min(3, len(all_links)))
    except Exception as e:
        st.error(f"구글 뉴스 검색 실패: {e}")
        return []

# 권리 키워드 추정 함수
def infer_rights(text):
    keywords = {
        "노동": "노동권",
        "파업": "노동권",
        "저작권": "저작권",
        "표절": "저작권",
        "차별": "평등권",
        "성별": "평등권",
        "사생활": "프라이버시권",
        "감시": "프라이버시권",
        "얼굴인식": "프라이버시권",
        "개인정보": "개인정보보호권",
        "유출": "개인정보보호권"
    }
    matched = set()
    for k, v in keywords.items():
        if k in text:
            matched.add(v)
    return list(matched)

# 권리별 기사 기록 저장
def save_to_csv(title, link, rights):
    csv_path = os.path.join(DATA_DIR, "data.csv")
    try:
        with open(csv_path, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for right in rights:
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), title, link, right])
    except Exception as e:
        st.error(f"CSV 저장 오류: {e}")

# 키워드 하이라이팅 함수
def highlight_keywords(text):
    for keyword in ["노동", "파업", "저작권", "표절", "차별", "성별", "사생활", "감시", "얼굴인식", "개인정보", "유출"]:
        text = re.sub(f"({keyword})", r"**\1**", text, flags=re.IGNORECASE)
    return text

col_left, col_center, col_right = st.columns([1, 4, 1])

# 왼쪽 col_left: 로그인 및 개념 보기 메뉴
with col_left:
    st.subheader("👥 로그인")
    login_role = st.radio("계정 유형을 선택하세요:", ["학생", "교사"])
    st.session_state["login_role"] = login_role

    st.subheader("📚 권리 개념 보기")
    selected_right = st.selectbox("관심 있는 권리를 선택하세요:", ["노동권", "저작권", "평등권", "프라이버시권", "개인정보보호권"])
    rights_info = {
        "노동권": "노동권은 모든 사람이 인간다운 삶을 위해 일할 권리입니다. AI가 사람을 대체하거나 AI로 인한 감시·평가가 노동환경을 악화시키는 경우 침해될 수 있습니다.\n\n📜 관련 법령: 대한민국 헌법 제32조, 근로기준법 제1조",
        "저작권": "저작권은 창작자가 자신의 창작물에 대해 가지는 권리입니다. 생성형 AI가 무단으로 창작물을 학습·생성하는 경우 침해가 발생할 수 있습니다.\n\n📜 관련 법령: 저작권법 제4조, 제97조의5",
        "평등권": "평등권은 인종, 성별, 나이, 장애 등에 관계없이 동등하게 대우받을 권리입니다. AI 알고리즘이 편향되었을 경우 차별을 초래할 수 있습니다.\n\n📜 관련 법령: 대한민국 헌법 제11조",
        "프라이버시권": "프라이버시권은 사생활의 자유와 인격권을 보호받을 권리입니다. 얼굴인식 기술이나 감시 시스템이 과도하게 활용될 경우 침해될 수 있습니다.\n\n📜 관련 법령: 개인정보 보호법 제4조, 헌법 제17조",
        "개인정보보호권": "개인정보보호권은 이름, 생년월일, 위치 정보, 건강 정보 등 개인 정보를 수집·처리·유출로부터 보호받을 권리입니다. AI 시스템이 정보를 수집하거나 유출할 경우 문제가 됩니다.\n\n📜 관련 법령: 개인정보 보호법 제15조~제17조, 정보통신망법"
    }
    st.info(rights_info[selected_right])

# 가운데 col_center: 기사 출력, 요약, 제출 기능
with col_center:
    if "news_links" not in st.session_state:
        st.session_state["news_links"] = []

    st.subheader("📌 기사 키워드 입력")
    keyword_input = st.text_input("기사 검색 키워드 (예: 노동권, 저작권 등)", key="keyword_input")

    if st.button("📰 AI 관련기사 출력"):
        if keyword_input.strip():
            st.session_state["news_links"] = get_google_news_links(keyword_input.strip())
        else:
            st.warning("키워드를 입력해주세요.")

    if st.session_state["news_links"]:
        st.markdown("### 📌 최근 AI 논란 관련 기사 (출처: Google News)")
        for idx, (title, link) in enumerate(st.session_state["news_links"], 1):
            text = fetch_article_text(link)
            inferred_rights = infer_rights(text)
            highlighted_title = highlight_keywords(title)

            st.markdown(f"**기사 {idx}:** {highlighted_title}")
            st.markdown(f"🔗 URL: {link}")

            if inferred_rights:
                st.markdown(f"🔐 추정 권리 침해: {', '.join(set(inferred_rights))}")
                save_to_csv(title, link, inferred_rights)
            else:
                st.markdown("🔍 관련 권리 탐색 필요")

    st.subheader("📌 기사 링크 입력")
    url_input = st.text_input("기사 링크를 입력하세요:", key="url_input")

    if st.button("🧠 요약하기", key="summarize_button"):
        if not url_input.strip():
            st.warning("URL을 입력해주세요.")
        else:
            st.markdown(f"### 🔗 기사 링크: [{url_input}]({url_input})")
            text = fetch_article_text(url_input)
            if text:
                with st.spinner("요약 중입니다..."):
                    summary = summarize_article(text)
                st.markdown(f"#### 📋 요약 결과")
                st.write(summary)
            else:
                st.error("❌ 기사 본문을 가져오지 못했습니다. 링크가 유효한 뉴스 기사인지 확인해주세요.")

    st.markdown("#### ✍️ 기사에 대한 AI와 인간의 권리에 대한 생각을 적어보세요.")
    user_name = st.text_input("이름(팀명)을 입력하세요", key="name_input")
    user_thought = st.text_area("생각을 작성하세요", key="thought_input")

    if st.button("제출하기", key="submit_thought"):
        if user_name.strip() == "" or user_thought.strip() == "":
            st.warning("⚠️ 이름과 생각을 모두 입력해주세요.")
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            txt_path = os.path.join(DATA_DIR, "data.txt")
            try:
                with open(txt_path, "a", encoding="utf-8") as f:
                    f.write( f,"[{timestamp}] {user_name}:\n{user_thought}\n\n")
                st.success("✅ 생각이 성공적으로 제출되었습니다!")
            except Exception as e:
                st.error(f"파일 저장 중 오류: {e}")

    if st.session_state.get("login_role") == "교사":
        st.markdown("---")
        st.subheader("📋 학생 제출 내용 열람")
        txt_path = os.path.join(DATA_DIR, "data.txt")
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                st.text(f.read())
        else:
            st.info("아직 제출된 학생의 생각이 없습니다.")

# 오른쪽 col_right: 원래의 Tips
with col_right:
    st.subheader("Tips...")
    st.info("""
    👀 이 앱은 최근 기사로 침해되는 다양한 권리를 탐색하기 위한 앱입니다
    📌 기사를 검색하고 url을 복사, 붙여넣기로 요약하고 참고하세요
    🧭 AI에 의해 침해되는 권리를 더 찾아주세요
    """)
