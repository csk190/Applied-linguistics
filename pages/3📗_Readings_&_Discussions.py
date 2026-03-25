import streamlit as st
import requests
import re

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="Readings and in-class discussion", layout="wide")

# ---------- [비디오 라이브러리용 헬퍼 함수] ----------
def extract_youtube_id(url: str) -> str | None:
    patterns = [
        r"(?:v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:embed/)([A-Za-z0-9_-]{11})",
        r"(?:shorts/)([A-Za-z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def youtube_embed_url(url: str) -> str:
    vid = extract_youtube_id(url)
    return f"https://www.youtube.com/embed/{vid}?rel=0&modestbranding=1" if vid else ""

def render_player(selected_url: str):
    embed = youtube_embed_url(selected_url)
    if not embed:
        st.error("Invalid YouTube link format.")
        return

    st.markdown(
        f"""
        <style>
        .video-wrap {{
            width: 100%;
            max-width: 1000px;
            margin: 0 auto;
            aspect-ratio: 16 / 9;
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 6px 20px rgba(0,0,0,0.12);
            background: #000;
        }}
        .video-wrap iframe {{
            width: 100%;
            height: 100%;
            border: 0;
        }}
        </style>
        <div class="video-wrap">
          <iframe src="{embed}" allowfullscreen></iframe>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- [비디오 데이터 데이터베이스] ----------
VIDEOS = {
    "SW교육과 AI교육, 왜 배워야 할까요?": {"url": "https://youtu.be/lQ2kAukmWQE", "caption": "AI 시대에 왜 SW·AI 교육이 중요한지 개관하는 입문 영상"},
    "2015-1": {"url": "https://www.youtube.com/watch?v=VIDEO_ID_2", "caption": "임용 대비 핵심 개념 정리(예시 캡션)."},
    "2005-2": {"url": "https://www.youtube.com/watch?v=VIDEO_ID_3", "caption": "기출 유형 분석(예시 캡션)."},
}

CLASS_VIDEOS = {
    "Week 01a · From Teacher to Creator": {"url": "https://youtu.be/ya0trJ6qtOw", "caption": "Becoming a teacher-designer who shapes the learning environment"},
    "Week 01b · Humanistic Horizon": {"url": "https://youtu.be/pKKR7RVBlc0", "caption": "수업에서 사용할 디지털 도구와 활동 흐름 소개"},
    "Week 02a · Digital Mind": {"url": "https://youtu.be/U8CwEvGeU_A", "caption": "디지털 사고에 대한 이해 및 인간의 가치 문제"},
    "Week 02b · Alignment Problem": {"url": "https://youtu.be/JqBV-wug-WQ", "caption": "인간의 지식처리와 인공지능의 데이터처리 방식"},
    "Week 03 · CT and Literacy": {"url": "https://youtu.be/bRVTDYAfj3M", "caption": "인공지능 시대의 새로운 문해력 정의 및 접근방식"},
}

# --- 2. 탭 생성 ---
tab_labels = ["🏠 Reading list", "🌱 Core idea", "💦 In-class presentation", "🖼️ Infographics", "🎬 Video"]
tab1, tab2, tab3, tab4, tab5 = st.tabs(tab_labels)

# --- 3. 탭별 콘텐츠 구성 ---
with tab1:
    st.markdown("### 🔖 Reading list")
    st.caption("To be updated continuously")
    st.markdown("""
      + Reading #1: Translanguaging [Li, Wei (2018)](https://www.researchgate.net/publication/323720294_Translanguaging_as_a_Practical_Theory_of_Language)
      + Reading #2: Alignment issues [Curry et al. (2025)](https://github.com/MK316/Applied-linguistics/raw/main/readings/02_Curry_etal_2025.pdf)
      # ... (중략) ...
      """)

with tab2:
    url = "https://raw.githubusercontent.com/MK316/Applied-linguistics/main/mdfiles/Core-idea.md"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            st.markdown(response.text)
    except Exception as e:
        st.error(f"Error loading Core-idea: {e}")

with tab3:
    st.caption("Github [Collaboration26](https://github.com/MK316/Collaboration26) Documentation.")
    readme_url = "https://raw.githubusercontent.com/MK316/Collaboration26/main/README.md"
    try:
        response = requests.get(readme_url)
        if response.status_code == 200:
            st.markdown(response.text)
    except Exception as e:
        st.error(f"Error loading README: {e}")

with tab4:
    image_options = {
        "Select an image...": None,
        "Supplementary book Chapter 1": "https://raw.githubusercontent.com/MK316/Collaboration26/main/infographic/CH01_infographic.png",
        "Reading #1": "https://raw.githubusercontent.com/MK316/Collaboration26/main/infographic/Reading01_infographic.png",
    }
    selected_image_name = st.selectbox("Choose an image to display:", options=list(image_options.keys()))
    if selected_image_name and image_options[selected_image_name]:
        st.image(image_options[selected_image_name], use_container_width=True)

# 🎬 4. Video 탭 (교수님의 코드를 통합한 부분)
with tab5:
    st.markdown("### 🎬 Class Video Library")
    
    # 상단 메뉴 선택 (segmented_control 사용 시도)
    try:
        view = st.segmented_control(
            "Video Type",
            options=["Video Library", "Class videos"],
            default="Video Library",
            label_visibility="visible"
        )
    except:
        view = st.radio("Select Video Category:", options=["Video Library", "Class videos"], horizontal=True)

    # 선택된 카테고리에 따른 데이터셋 설정
    dataset = VIDEOS if view == "Video Library" else CLASS_VIDEOS
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📋 Playlist")
        selected_label = st.selectbox("Choose a video:", options=list(dataset.keys()), key="video_selector")
        
        target = dataset[selected_label]
        st.info(f"**Description:** {target['caption']}")
        st.caption(f"[Open on YouTube ▶️]({target['url']})")
    
    with col2:
        st.subheader("📺 Now Playing")
        render_player(target['url'])
