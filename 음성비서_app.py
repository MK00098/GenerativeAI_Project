import streamlit as st
from audiorecorder import audiorecorder
import openai
import os
from datetime import datetime
from gtts import gTTS
import base64

##### 기능 구현 함수 #####

def STT(audio, apikey):
    # 파일 저장
    filename='input.mp3'
    audio.export(filename, format="mp3")
    # 음원 파일 열기
    audio_file = open(filename, "rb")
    # Whisper 모델을 활용해 텍스트 얻기
    client = openai.OpenAI(api_key = apikey)
    response = client.audio.transcriptions.create(model = "whisper-1", file = audio_file)
    audio_file.close()
    # 파일 삭제
    os.remove(filename)
    return response.text

def ask_gpt(prompt, model, apikey):
    client = openai.OpenAI(api_key = apikey)
    response = client.chat.completions.create(
        model=model,
        messages=prompt)
    gptResponse = response.choices[0].message.content
    return gptResponse

def TTS(response):
    # gTTS를 활용하여 음성 파일 생성
    filename = "output.mp3"
    tts = gTTS(text=response, lang="ko")
    tts.save(filename)

    # 음원 파일 자동 재생
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True,)
    os.remove(filename)

##### 메인 함수 #####
def main():
    st.set_page_config(
        page_title="음성 비서 프로그램",
        layout="wide")

    st.header("음성 비서 프로그램")
    st.markdown("---")

    with st.expander("음성비서 프로그램에 관하여", expanded=True):
        st.write(
        """
        - 음성비서 프로그램의 UI는 스트림릿을 활용하여 만들었습니다.
        - STT(Speech-To-Text)는 OpenAI의 Whisper AI를 활용하였습니다.
        - 답변은 OpenAI의 GPT 모델을 활용하였습니다.
        - TTS(Text-To-Speech)는 구글의 Google Translate TTS를 활용하였습니다.
        """
        )

    if "chat" not in st.session_state:
        st.session_state["chat"] = []
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False

    with st.sidebar:
        st.session_state["OPENAI_API"] = st.text_input(label="OPENAI API 키", placeholder="Enter Your API Key", value="", type="password")
        st.markdown("---")
        model = st.radio(label="GPT 모델", options=["gpt-4", "gpt-3.5-turbo"])
        st.markdown("---")
        if st.button(label="초기화"):
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]
            st.session_state["check_reset"] = True

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("질문하기")
        audio = audiorecorder("클릭하여 녹음하기", "녹음 중...")
        # 'audio' 객체가 존재하고, 리셋 버튼이 눌리지 않았을 때만 실행하도록 수정
        if audio and not st.session_state["check_reset"]:
            st.audio(audio.export().read())
            question = STT(audio, st.session_state["OPENAI_API"])

            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"].append(("user", now, question))
            st.session_state["messages"].append({"role": "user", "content": question})

    with col2:
        st.subheader("질문/답변")
        # 'audio' 객체가 존재하고, 리셋 버튼이 눌리지 않았을 때만 실행하도록 수정
        if audio and not st.session_state["check_reset"]:
            response = ask_gpt(st.session_state["messages"], model, st.session_state["OPENAI_API"])
            st.session_state["messages"].append({"role": "system", "content": response})
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"].append(("bot", now, response))

            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display: flex; align-items: center;"><div style="background-color:#007AFF; color:white; border-radius:12px; padding:8px 12px; margin-right:auto;">{message}</div><div style="font-size:0.8rem; color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(f'<div style="display: flex; align-items: center; justify-content: flex-end;"><div style="background-color:lightgray; border-radius:12px; padding:8px 12px; margin-left:auto;">{message}</div><div style="font-size:0.8rem; color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
            TTS(response)

if __name__ == "__main__":
    main()