import streamlit as st
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()
# google_api_key = os.getenv("GOOGLE_API_KEY")

prompt = """
You are professional notes maker you make helpful, insightful notes from the provided data and information.
You will be provided with a trancript and you will use it to create notes.
Generate in markdown format. Be detailed and insightful.
"""

def google_text_generation(trancript_text, prompt):
    generator = genai.Client(api_key=google_api_key)
    response = generator.models.generate_content(
        model = "gemini-2.0-flash-001",
        contents = f'System Prompt: {prompt}\n\nTranscript: {trancript_text}'
    )
    return response.text

def yt_transcriptions(video_url):
    try:
        video_id = video_url.split("=")[1]
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.get_transcript(video_id)
        trancript_text = " ".join([x['text'] for x in transcript])
        return trancript_text

    except Exception as e:
        st.error(f"Error: {e}")

st.title("YouTube Transcript to Detailed Notes Converter")

with st.sidebar:
    st.markdown('API key:')
    google_api_key = st.text_input("Google API Key", type="password")

youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    print(video_id)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

if st.button("Generate Notes"):
    trancript_text = yt_transcriptions(youtube_link)
    st.markdown("### Transcript")
    st.write(trancript_text)

    if trancript_text:
        notes = google_text_generation(trancript_text, prompt)
        st.markdown(notes)
