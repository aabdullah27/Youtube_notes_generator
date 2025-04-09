import streamlit as st
from google import genai
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import os
import json
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'custom_styles' not in st.session_state:
    st.session_state.custom_styles = {}
if 'transcript_text' not in st.session_state:
    st.session_state.transcript_text = None
if 'video_title' not in st.session_state:
    st.session_state.video_title = None
if 'video_id' not in st.session_state:
    st.session_state.video_id = None

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
    
    # Built-in and custom note styles
    st.subheader("📊 Note Styles")
    
    # Display custom styles
    if st.session_state.custom_styles:
        st.write("Your custom styles:")
        for style_name in st.session_state.custom_styles.keys():
            st.write(f"- {style_name}")
    
    # Custom style creator
    with st.expander("➕ Create Custom Style"):
        new_style_name = st.text_input("Style Name:", key="new_style_name")
        new_style_description = st.text_area("Style Description:", 
                                            placeholder="Example: Create notes that focus on technical details and include code snippets.", 
                                            key="new_style_description")
        if st.button("Save Custom Style"):
            if new_style_name and new_style_description:
                st.session_state.custom_styles[new_style_name] = new_style_description
                st.success(f"✅ Custom style '{new_style_name}' created!")
                st.rerun()
            else:
                st.error("Please provide both a name and description for your custom style.")
    
    # Layout
    st.divider()
    st.markdown("### 👨‍💻 About")
    st.markdown("This app converts YouTube video transcripts into organized notes using AI.")

# Create combined list of built-in and custom styles
default_styles = ["Detailed", "Concise", "Bullet Points", "Academic", "Mind Map"]
all_style_options = default_styles + list(st.session_state.custom_styles.keys())

# Create custom prompts based on style selection
default_prompts = {
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
                If possible provide a mermaide diagram in markdown format for proper understanding.
                Explain by making connections between ideas and concepts.""",
}

def extract_video_id(video_url):
    """Extract video ID from various YouTube URL formats"""
    try:
        if not video_url:
            return None
            
        # Handle youtu.be format
        if "youtu.be" in video_url:
            return video_url.split("/")[-1].split("?")[0]
            
        # Handle youtube.com format with v parameter
        elif "v=" in video_url:
            return video_url.split("v=")[1].split("&")[0]
            
        # Handle youtube.com/embed format
        elif "youtube.com/embed/" in video_url:
            return video_url.split("embed/")[-1].split("?")[0]
            
        # Handle youtube.com/shorts format
        elif "youtube.com/shorts/" in video_url:
            return video_url.split("shorts/")[-1].split("?")[0]
            
        else:
            # Check if the URL contains just the video ID (11 characters alphanumeric)
            if re.match(r'^[a-zA-Z0-9_-]{11}$', video_url):
                return video_url
            return None
    except Exception:
        return None

def google_text_generation(transcript_text, prompt, conversation_history=None):
    """Generate notes or answer questions using Google Gemini API"""
    try:
        if not user_api_key:
            return "⚠️ Please provide a Google API key in the settings panel."
            
        generator = genai.Client(api_key=user_api_key)
        
        content = f'System Prompt: {prompt}\n\nTranscript: {transcript_text}'
        
        # Include conversation history for Q&A
        if conversation_history:
            content += f"\n\nPrevious conversation: {json.dumps(conversation_history[-3:])}"
        
        response = generator.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=content
        )
        return response.text
    except Exception as e:
        return f"🚫 Error with Google Gemini API: {str(e)}"

def groq_text_generation(transcript_text, prompt, conversation_history=None):
    """Generate notes or answer questions using Groq API"""
    try:
        if not user_api_key:
            return "⚠️ Please provide a Groq API key in the settings panel."
            
        client = Groq(api_key=user_api_key)
        
        messages = [
            {"role": "system", "content": prompt},
        ]
        
        # Include conversation history for Q&A
        if conversation_history:
            # Add the last 3 messages from conversation history
            for msg in conversation_history[-3:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": f"Process this transcript: {transcript_text}"})
        
        response = client.chat.completions.create(
            model="llama3.3-70b-versatile",
            messages=messages,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"🚫 Error with Groq API: {str(e)}"

def get_youtube_transcript(video_url):
    """Get transcript from YouTube video"""
    try:
        video_id = extract_video_id(video_url)
        if not video_id:
            return None, None, "🚫 Could not extract video ID from URL. Please check the URL format."
            
        # Try to get transcript
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([x['text'] for x in transcript])
            
            # Try to get video title (simplified - would need additional library for real implementation)
            video_title = f"Video {video_id}"
            
            return transcript_text, video_id, video_title
        except Exception as transcript_error:
            # Handle specific transcript errors
            error_message = str(transcript_error).lower()
            
            if "no transcript" in error_message:
                return None, video_id, "⚠️ This video doesn't have captions/transcripts available."
            elif "language code" in error_message:
                return None, video_id, "⚠️ The requested language transcript is not available."
            elif "forbidden" in error_message or "403" in error_message:
                return None, video_id, "⚠️ Access to this video's transcript is restricted."
            else:
                return None, video_id, f"⚠️ Transcript error: {transcript_error}"
    except Exception as e:
        return None, None, f"🚫 Error: {str(e)}"

def get_prompt_for_style(selected_style):
    """Get the appropriate prompt for the selected style"""
    if selected_style in default_prompts:
        return default_prompts[selected_style]
    elif selected_style in st.session_state.custom_styles:
        return st.session_state.custom_styles[selected_style]
    else:
        return default_prompts["Detailed"]  # Fallback to detailed

# Main input area
youtube_link = st.text_input("🔗 Enter YouTube Video Link:", placeholder="https://www.youtube.com/watch?v=...")

# Process video when link is provided
if youtube_link and youtube_link != st.session_state.get('last_processed_link', ''):
    # Display loading message
    with st.spinner("📥 Fetching video information..."):
        transcript_text, video_id, message = get_youtube_transcript(youtube_link)
    
    if transcript_text and video_id:
        st.session_state.transcript_text = transcript_text
        st.session_state.video_id = video_id
        st.session_state.last_processed_link = youtube_link
        st.success("✅ Transcript successfully retrieved!")
    else:
        st.error(message)
        st.session_state.video_id = video_id  # May still have a valid video ID even without transcript

# If we have a video ID (even without transcript), show the thumbnail
if st.session_state.video_id:
    # Create two columns for video preview
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display video thumbnail
        st.image(f"http://img.youtube.com/vi/{st.session_state.video_id}/0.jpg", 
                use_container_width=True)
    
    with col2:
        # Show video info
        st.markdown(f"##### 🎬 Video ID: `{st.session_state.video_id}`")
        st.markdown(f"🔗 [Open video on YouTube](https://youtube.com/watch?v={st.session_state.video_id})")
        
        # Show transcript info if available
        if st.session_state.transcript_text:
            st.success("✅ Transcript available")
            with st.expander("📄 View Full Transcript"):
                st.text_area("Transcript", st.session_state.transcript_text, height=200)
        else:
            st.error("❌ No transcript available")

# Create tabs for Notes Generation and Q&A
notes_tab, qa_tab = st.tabs(["📝 Generate Notes", "❓ Ask Questions About Video"])

# Notes Generation Tab
with notes_tab:
    if st.session_state.transcript_text:
        # Note style selection
        note_style = st.selectbox("📊 Select Notes Style:", all_style_options)
        
        # Generate notes button
        if st.button("✨ Generate Notes", type="primary"):
            if not user_api_key:
                st.error("🚫 Please enter your API key in the sidebar")
            else:
                # Generate notes based on selected API and style
                with st.spinner(f"🧠 Generating {note_style} notes with {api_choice}..."):
                    selected_prompt = get_prompt_for_style(note_style)
                    
                    if api_choice == "Google Gemini":
                        notes = google_text_generation(st.session_state.transcript_text, selected_prompt)
                    else:
                        notes = groq_text_generation(st.session_state.transcript_text, selected_prompt)
                
                if not notes.startswith("🚫") and not notes.startswith("⚠️"):
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
                        file_name=f"notes_{st.session_state.video_id}.md",
                        mime="text/markdown"
                    )
                else:
                    st.error(notes)
    elif youtube_link:
        st.warning("⚠️ No transcript available for this video. Notes cannot be generated.")
    else:
        st.info("👆 Enter a YouTube URL above to get started")

# Q&A Tab
with qa_tab:
    if st.session_state.transcript_text:
        st.subheader("💬 Ask questions about this video")
        
        # Display past conversation
        for message in st.session_state.conversation_history:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**AI:** {message['content']}")
        
        # Question input
        user_question = st.text_input("Your question:", key="user_question")
        
        if st.button("🔍 Ask", key="ask_button"):
            if not user_question:
                st.warning("⚠️ Please enter a question")
            elif not user_api_key:
                st.error("🚫 Please enter your API key in the sidebar")
            else:
                # Add question to conversation history
                st.session_state.conversation_history.append({
                    "role": "user",
                    "content": user_question
                })
                
                # Show user question
                st.markdown(f"**You:** {user_question}")
                
                # Prepare Q&A prompt
                qa_prompt = """You are an assistant that answers questions about a YouTube video based on its transcript. 
                            Use the information in the transcript to answer questions. Guide the student in the context of the video.
                            If the question is not related to the video, respond with "I can only answer questions about the video."""
                
                # Generate answer based on selected API
                with st.spinner("🧠 Thinking..."):
                    if api_choice == "Google Gemini":
                        answer = google_text_generation(
                            st.session_state.transcript_text, 
                            qa_prompt, 
                            st.session_state.conversation_history
                        )
                    else:
                        answer = groq_text_generation(
                            st.session_state.transcript_text, 
                            qa_prompt, 
                            st.session_state.conversation_history
                        )
                
                # Add answer to conversation history
                if not answer.startswith("🚫") and not answer.startswith("⚠️"):
                    st.session_state.conversation_history.append({
                        "role": "assistant",
                        "content": answer
                    })
                    
                    # Show answer
                    st.markdown(f"**AI:** {answer}")
                else:
                    st.error(answer)
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation"):
            st.session_state.conversation_history = []
            st.rerun()
    else:
        st.info("⚠️ A video transcript is needed to ask questions. Please enter a YouTube URL above.")

# Footer
st.divider()
st.markdown("#### 💡 Tips")
st.markdown("""
- For best results, use videos with good quality auto-generated captions
- Try different note styles for different types of content
- Create custom styles for specialized content (e.g., programming tutorials, math lessons)
- The Q&A feature works best for specific questions about the video content
- If you encounter errors with a video, try another one - not all videos have available transcripts
""")