import streamlit as st
from openai import OpenAI
import json
import urllib.parse

st.set_page_config(
    page_title="🎵 음악 추천 서비스",
    page_icon="🎵",
    layout="centered"
)

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background-color: #0a0a0a !important;
    color: #e8e8e8 !important;
}
[data-testid="stMain"] { background-color: #0a0a0a !important; }
[data-testid="block-container"] { padding-top: 2.5rem; }

/* ── expander (API Key) ── */
[data-testid="stExpander"] {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 12px !important;
    margin-bottom: 1.2rem;
}
[data-testid="stExpander"] summary {
    color: #aaaaaa !important;
    font-size: 0.9rem !important;
}

h1 {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
    margin-bottom: 0.2rem !important;
}
h2, h3 { color: #e8e8e8 !important; font-weight: 700 !important; }

p, label, .stMarkdown p { color: #aaaaaa !important; }

[data-testid="stForm"] {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 2rem 2rem 1.5rem !important;
}

input, textarea, select,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="select"] div {
    background-color: #1e1e1e !important;
    color: #e8e8e8 !important;
    border-color: #333333 !important;
    border-radius: 8px !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="select"]:focus-within {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 2px rgba(167,139,250,0.2) !important;
}

[data-baseweb="popover"] {
    background-color: #1e1e1e !important;
    border: 1px solid #333 !important;
    border-radius: 10px !important;
}
[data-baseweb="menu"] li {
    color: #e8e8e8 !important;
    background-color: #1e1e1e !important;
}
[data-baseweb="menu"] li:hover { background-color: #2a2a2a !important; }

[data-baseweb="tag"] {
    background-color: #2d2060 !important;
    border-color: #a78bfa !important;
    border-radius: 6px !important;
}
[data-baseweb="tag"] span { color: #d4bbff !important; }

[data-testid="stRadio"] label { color: #cccccc !important; }

[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.65rem 1.5rem !important;
    transition: opacity 0.2s ease;
}
[data-testid="stFormSubmitButton"] button:hover { opacity: 0.88 !important; }

[data-testid="stButton"] button {
    background: #1a1a2e !important;
    color: #a78bfa !important;
    border: 1px solid #3a2a5a !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    transition: background 0.2s;
}
[data-testid="stButton"] button:hover {
    background: #2a1a4a !important;
    border-color: #a78bfa !important;
}

[data-testid="stLinkButton"] a {
    background: #1a1a1a !important;
    color: #ff4e4e !important;
    border: 1px solid #3a1a1a !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: background 0.2s;
}
[data-testid="stLinkButton"] a:hover {
    background: #2a1a1a !important;
    border-color: #ff4e4e !important;
}

.song-card {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-radius: 14px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s;
}
.song-card:hover { border-color: #a78bfa55; }
.song-number {
    font-size: 0.75rem;
    color: #a78bfa;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
}
.song-title { font-size: 1.05rem; font-weight: 700; color: #f0f0f0; }
.song-artist { font-size: 0.88rem; color: #888888; margin-top: 0.1rem; }
.song-reason { font-size: 0.83rem; color: #777777; margin-top: 0.55rem; line-height: 1.5; }

.summary-box {
    background: linear-gradient(135deg, #1a1030, #0f1e30);
    border: 1px solid #3a2a5a;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-top: 1rem;
    font-size: 0.92rem;
}

[data-testid="stAlert"] { border-radius: 10px !important; border: none !important; }
hr { border-color: #222222 !important; }
[data-testid="stSpinner"] p { color: #a78bfa !important; }
[data-testid="stWidgetLabel"] p {
    color: #cccccc !important;
    font-weight: 500 !important;
    font-size: 0.92rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── 세션 초기화 ───────────────────────────────────────────────
for _k in ["songs", "summary", "api_key", "selected_artist"]:
    if _k not in st.session_state:
        st.session_state[_k] = None

# ── 헤더 ──────────────────────────────────────────────────────
st.title("♫ Music Recommend")
st.markdown("<p style='color:#666;margin-top:-0.5rem;margin-bottom:1.5rem;font-size:0.95rem;'>설문에 답하면 AI가 당신만을 위한 플레이리스트를 만들어 드립니다.</p>", unsafe_allow_html=True)

# ── API Key 입력 ──────────────────────────────────────────────
with st.expander("⚙️ OpenAI API Key 설정", expanded=not bool(st.session_state.get("api_key"))):
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="sk-...",
        help="OpenAI API 키를 입력하세요. 키는 저장되지 않습니다.",
        label_visibility="collapsed",
    )
    if api_key:
        st.success("API 키 입력 완료")
    else:
        st.caption("OpenAI API 키를 입력해야 음악을 추천받을 수 있습니다.")

# ── 설문 ─────────────────────────────────────────────────────
st.markdown("#### 📋 취향 설문")

with st.form("survey_form"):
    mood = st.select_slider(
        "1. 지금 기분이 어떤가요?",
        options=["매우 우울해요", "조금 처져요", "보통이에요", "기분 좋아요", "매우 신나요"],
        value="보통이에요"
    )
    situation = st.selectbox(
        "2. 지금 어떤 상황인가요?",
        ["혼자 공부/집중 중", "드라이브 중", "운동 중", "친구들과 파티",
         "연인과 함께", "잠들기 전 휴식", "출퇴근 이동 중", "감정 정리가 필요해요"]
    )
    genre = st.multiselect(
        "3. 좋아하는 장르 (복수 선택 가능)",
        ["K-POP", "팝(Pop)", "R&B / 소울", "힙합", "재즈", "클래식", "인디", "록", "EDM / 댄스", "발라드"],
        default=["K-POP"]
    )
    language = st.radio(
        "4. 선호하는 언어",
        ["한국어", "영어", "상관없어요"],
        horizontal=True
    )
    era = st.selectbox(
        "5. 선호하는 연대",
        ["상관없어요", "2020년대", "2010년대", "2000년대", "90년대", "80년대 이전"]
    )
    extra = st.text_input(
        "6. 추가 키워드 (선택)",
        placeholder="예: 비 오는 날, 설레는 느낌, 가사가 좋은 노래..."
    )
    submitted = st.form_submit_button("✦ 플레이리스트 생성하기", use_container_width=True)

# ── 플레이리스트 생성 ──────────────────────────────────────────
if submitted:
    if not api_key:
        st.error("사이드바에서 OpenAI API 키를 먼저 입력해 주세요.")
        st.stop()
    if not genre:
        st.error("장르를 하나 이상 선택해 주세요.")
        st.stop()

    genre_str = ", ".join(genre)
    prompt = f"""당신은 음악 전문가입니다. 아래 설문 결과를 바탕으로 사용자에게 딱 맞는 노래 5곡을 추천해 주세요.

설문 결과:
- 현재 기분: {mood}
- 현재 상황: {situation}
- 선호 장르: {genre_str}
- 선호 언어: {language}
- 선호 연대: {era}
- 추가 키워드: {extra if extra else '없음'}

반드시 아래 JSON 형식으로만 응답하세요.

{{
  "playlist_summary": "전체 플레이리스트 분위기 한 줄 요약",
  "songs": [
    {{
      "title": "곡명",
      "artist": "아티스트명",
      "reason": "추천 이유 2~3문장",
      "youtube_query": "유튜브 검색에 최적화된 검색어 (예: BTS Dynamite official MV)"
    }}
  ]
}}"""

    with st.spinner("AI가 플레이리스트를 구성하는 중..."):
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                response_format={"type": "json_object"},
            )
            data = json.loads(response.choices[0].message.content)
            st.session_state["songs"] = data.get("songs", [])
            st.session_state["summary"] = data.get("playlist_summary", "")
            st.session_state["api_key"] = api_key
            st.session_state["selected_artist"] = None
        except Exception as e:
            err = str(e)
            if "api_key" in err.lower() or "authentication" in err.lower() or "401" in err:
                st.error("API 키가 올바르지 않습니다. 다시 확인해 주세요.")
            else:
                st.error(f"오류가 발생했습니다: {err}")

# ── 결과 렌더링 ───────────────────────────────────────────────
if st.session_state.get("songs"):
    songs  = st.session_state["songs"]
    summary = st.session_state.get("summary", "")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🎼 Your Playlist")

    for i, song in enumerate(songs, 1):
        title    = song.get("title", "")
        artist   = song.get("artist", "")
        reason   = song.get("reason", "")
        yt_query = song.get("youtube_query", f"{title} {artist}")
        yt_url   = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(yt_query)

        col1, col2, col3 = st.columns([0.68, 0.17, 0.15])
        with col1:
            st.markdown(f"""
            <div class="song-card">
                <div class="song-number">TRACK {i:02d}</div>
                <div class="song-title">{title}</div>
                <div class="song-artist">{artist}</div>
                <div class="song-reason">{reason}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
            if st.button(f"🎤 {artist}", key=f"artist_{i}", use_container_width=True,
                         help=f"{artist}의 다른 노래 보기"):
                st.session_state["selected_artist"] = artist
                st.rerun()
        with col3:
            st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
            st.link_button("▶ YouTube", yt_url, use_container_width=True)

    if summary:
        st.markdown(f"""
        <div class="summary-box">
            🎧 &nbsp;<strong>플레이리스트 분위기</strong><br>
            <span style="color:#b8a4e8">{summary}</span>
        </div>
        """, unsafe_allow_html=True)

# ── 아티스트 추가 추천 ─────────────────────────────────────────
selected_artist = st.session_state.get("selected_artist")
if selected_artist:
    saved_key = st.session_state.get("api_key") or api_key
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"#### 🎤 {selected_artist} 의 다른 추천곡")

    artist_prompt = f"""음악 전문가로서 아티스트 '{selected_artist}'의 대표곡 또는 추천곡 5곡을 알려주세요.
이미 추천된 곡과 겹치지 않도록 다양하게 선정해 주세요.

반드시 아래 JSON 형식으로만 응답하세요.

{{
  "songs": [
    {{
      "title": "곡명",
      "year": "발매연도 (예: 2021)",
      "description": "곡 소개 한 문장",
      "youtube_query": "유튜브 검색어 (예: IU Palette official MV)"
    }}
  ]
}}"""

    with st.spinner(f"{selected_artist}의 곡을 찾는 중..."):
        try:
            client2 = OpenAI(api_key=saved_key)
            res2 = client2.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": artist_prompt}],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            data2 = json.loads(res2.choices[0].message.content)
            artist_songs = data2.get("songs", [])

            for j, asong in enumerate(artist_songs, 1):
                atitle    = asong.get("title", "")
                ayear     = asong.get("year", "")
                adesc     = asong.get("description", "")
                ayt_query = asong.get("youtube_query", f"{selected_artist} {atitle}")
                ayt_url   = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(ayt_query)

                col_a, col_b = st.columns([0.82, 0.18])
                with col_a:
                    st.markdown(f"""
                    <div class="song-card">
                        <div class="song-number">{ayear}</div>
                        <div class="song-title">{atitle}</div>
                        <div class="song-artist">{selected_artist}</div>
                        <div class="song-reason">{adesc}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_b:
                    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
                    st.link_button("▶ YouTube", ayt_url, key=f"ayt_{j}", use_container_width=True)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

    if st.button("✕ 닫기", key="close_artist"):
        st.session_state["selected_artist"] = None
        st.rerun()
