import asyncio
import edge_tts
import os
import streamlit as st
import tempfile as tf

# 임시 폴더 생성
def create_temp_dir():
    # Create a temporary directory
    set_temp_dir = tf.TemporaryDirectory()
    temp_dir = set_temp_dir.name + "/"
    # 디렉터리 접근 권한 설정
    os.chmod(temp_dir, 0o700)
    return temp_dir

def make_filename(filehead):
    temp_dir = create_temp_dir()
    audio_filename = os.path.join(temp_dir + filehead + ".mp3")
    return audio_filename

# 스트리밍 오디오/자막 파일 생성
async def amain(text, voice, rate, volume, audio_filename):
    # Main function
    communicate = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
    submaker = edge_tts.SubMaker()
    os.makedirs(os.path.dirname(audio_filename), exist_ok=True)
    with open(audio_filename, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

def app():
        # 세션 상태 가져오기
    if "audio_file" not in st.session_state:
        st.session_state.audio_file = None
    if "sub_file" not in st.session_state:
        st.session_state.sub_file = None
    st.set_page_config(
    page_title="Simple Text-to-Speech",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Speaker_Icon.svg/1024px-Speaker_Icon.svg.png"
    )
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Speaker_Icon.svg/1024px-Speaker_Icon.svg.png", width=150)
    st.title("simple text-to-speech")
    st.markdown("powered by [edge-tts](https://github.com/rany2/edge-tts)")
    article_text = st.text_area('본문 넣기', height=200, placeholder='읽고자 하는 기사 본문을 넣어주세요')
    filehead = st.text_input('파일명', placeholder='103348')
    tts_button = st.button("오디오 기사 만들기")
    # 목소리 선택
    voice_select = st.radio(
            "목소리를 선택하세요.",
            ('여성', '남성')
        )
    voices = {'여성': 'ko-KR-SunHiNeural', '남성': 'ko-KR-InJoonNeural'}
    voice = voices[voice_select]
    # 읽기 속도
    rate_value = st.slider(
        "읽기 속도",
        0, 30, 10
    )
    rate = '+' + str(rate_value) + '%'
    # 볼륨 조절
    volume_value = st.slider("볼륨 조절", -50, 50, 0)
    volume = str(volume_value) + '%'
    if volume_value >= 0:
        volume = '+' + str(volume_value) + '%'
    
    if tts_button:
        with st.spinner("오디오 기사를 생성하고 있어요... 🧐"):
            try:
                audio_filename = make_filename(filehead)
                asyncio.run(amain(article_text, voice, rate, volume, audio_filename))
                with open(audio_filename, "rb") as f:
                    mp3_file = f.read()
                st.audio(mp3_file, format='audio/mp3')
                st.success("오디오 기사 생성 완료! 🥳")
                # 오디오 파일을 세션 상태에 저장
                st.session_state.audio_file = mp3_file
                # 세션 상태에 저장된 오디오 파일을 사용
                if st.session_state.audio_file is not None:
                    # st.audio(st.session_state.audio_file, format='audio/mp3')
                    st.download_button(
                        label="오디오 파일(MP3) 내려받기",
                        data=st.session_state.audio_file,
                        file_name=filehead + '.mp3',
                        mime='audio/mp3'
                    )
            except Exception as e:
                st.error("오류가 발생했습니다.")
                st.error(e)

if __name__ == "__main__":
    app()
