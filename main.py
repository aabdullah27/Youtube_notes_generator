import streamlit as st
from google import genai
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="YouTube Notes Generator",
    page_icon="📝",
    layout="wide"
)

# Title and description
st.title("📝 YouTube Transcript to Detailed Notes Converter")
st.markdown("#### 🎯 Convert any YouTube video into comprehensive notes with AI")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Selection
    api_choice = st.radio("🤖 Select AI Provider:", ["Google Gemini", "Groq"])
    
    # API Key inputs
    if api_choice == "Google Gemini":
        user_api_key = st.text_input("🔑 Enter your Google API Key:", type="password", 
                                     value=os.getenv("GOOGLE_API_KEY", ""))
    else:
        user_api_key = st.text_input("🔑 Enter your Groq API Key:", type="password", 
                                    value=os.getenv("GROQ_API_KEY", ""))
    
    # Note style options
    note_style = st.selectbox("📊 Notes Style:", 
                            ["Detailed", "Concise", "Bullet Points", "Academic", "Mind Map"])
    
    # Layout
    st.divider()
    st.markdown("### 👨‍💻 About")
    st.markdown("This app converts YouTube video transcripts into organized notes using AI.")

# Create custom prompts based on style selection
prompts = {
    "Detailed": """You are professional notes maker. Create helpful, insightful, and DETAILED notes from the provided transcript. 
                Include all important concepts, examples, and explanations. Generate in markdown format with proper headings, 
                subheadings, and formatting.""",
    
    "Concise": """You are professional notes maker. Create CONCISE yet comprehensive notes from the provided transcript. 
                Focus only on the key points and main ideas. Generate in markdown format with clear structure.""",
    
    "Bullet Points": """You are professional notes maker. Create BULLET POINT notes from the provided transcript. 
                     Organize information hierarchically with main points and sub-points. Use markdown bullet formatting.""",
    
    "Academic": """You are professional notes maker. Create ACADEMIC-STYLE notes from the provided transcript. 
                Include citations where relevant, define technical terms, and organize by concepts. Use markdown format with proper headings.""",
    
    "Mind Map": """You are professional notes maker. Create a MIND MAP style set of notes from the provided transcript. 
                Use markdown to create a hierarchical structure showing relationships between concepts.
                Use ## for main concepts and nested lists for related ideas."""
}

def extract_video_id(video_url):
    """Extract video ID from various YouTube URL formats"""
    if "youtu.be" in video_url:
        return video_url.split("/")[-1].split("?")[0]
    elif "v=" in video_url:
        return video_url.split("v=")[1].split("&")[0]
    else:
        return None

def google_text_generation(transcript_text, prompt):
    """Generate notes using Google Gemini API"""
    try:
        generator = genai.Client(api_key=user_api_key)
        response = generator.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=f'System Prompt: {prompt}\n\nTranscript: {transcript_text}'
        )
        return response.text
    except Exception as e:
        st.error(f"🚫 Error with Google Gemini API: {e}")
        return None

def groq_text_generation(transcript_text, prompt):
    """Generate notes using Groq API"""
    try:
        client = Groq(api_key=user_api_key)
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Generate notes for this transcript: {transcript_text}"}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"🚫 Error with Groq API: {e}")
        return None

def get_youtube_transcript(video_url):
    """Get transcript from YouTube video"""
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            st.error("🚫 Could not extract video ID from URL. Please check the URL format.")
            return None
            
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([x['text'] for x in transcript])
        return transcript_text, video_id
    except Exception as e:
        st.error(f"🚫 Error retrieving transcript: {e}")
        return None, None

# Main input area
youtube_link = st.text_input("🔗 Enter YouTube Video Link:", 
                            placeholder="https://www.youtube.com/watch?v=...")

# Process video when link is provided
if youtube_link:
    # Display loading message
    with st.spinner("📥 Fetching video information..."):
        transcript_text, video_id = get_youtube_transcript(youtube_link)
    
    if video_id:
        # Create two columns for video preview
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display video thumbnail
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", 
                    use_container_width=True)
        
        with col2:
            # Get video metadata if possible
            st.markdown(f"##### 🎬 Video ID: `{video_id}`")
            st.markdown(f"🔗 [Open video on YouTube]({youtube_link})")
    
    # Create button to generate notes
    if st.button("✨ Generate Notes", type="primary"):
        if not user_api_key:
            st.error("🚫 Please enter your API key in the sidebar")
        elif not transcript_text:
            st.error("🚫 Could not retrieve transcript. The video might not have captions.")
        else:
            # Display transcript in expander
            with st.expander("📄 View Full Transcript"):
                st.text_area("Transcript", transcript_text, height=200)
            
            # Generate notes based on selected API
            with st.spinner(f"🧠 Generating {note_style} notes with {api_choice}..."):
                selected_prompt = prompts[note_style]
                
                if api_choice == "Google Gemini":
                    notes = google_text_generation(transcript_text, selected_prompt)
                else:
                    notes = groq_text_generation(transcript_text, selected_prompt)
            
            if notes:
                # Display the generated notes with download option
                st.success(f"✅ Successfully generated {note_style} notes!")
                
                # Create tabs for different views
                tab1, tab2 = st.tabs(["📝 Rendered Notes", "📋 Markdown Source"])
                
                with tab1:
                    st.markdown(notes)
                
                with tab2:
                    st.text_area("Markdown Source", notes, height=400)
                
                # Download option
                st.download_button(
                    label="📥 Download Notes as Markdown",
                    data=notes,
                    file_name=f"notes_{video_id}.md",
                    mime="text/markdown"
                )

# Footer
st.divider()
st.markdown("#### 💡 Tips")
st.markdown("""
- For best results, use videos with good quality auto-generated captions
- Try different note styles for different types of content
- Academic style works well for educational content
- Mind Map style is great for conceptual videos
""")