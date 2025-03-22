# YT-Transcription-Project

A powerful tool for converting YouTube videos into searchable, readable text content.

![License](https://img.shields.io/badge/License-MIT-green)

## 📋 Project Overview

YT-Transcription automatically converts spoken content from YouTube videos into accurate text transcriptions. Whether you're a researcher, content creator, student, or just someone who prefers reading to watching, this tool makes video content more accessible and useful.

## ✨ Features

- **🎯 Accurate Transcription**: Utilizes state-of-the-art speech recognition technology to provide high-quality transcriptions
- **🌐 Multi-language Support**: Transcribe videos in multiple languages and dialects
- **🔍 Searchable Content**: Easily search through video content without watching the entire video
- **📱 User-friendly Interface**: Simple and intuitive interface designed for users of all technical levels
- **💾 Multiple Export Formats**: Export transcriptions as TXT, PDF, or other common formats
- **⚡ Batch Processing**: Process multiple videos in one go to save time
- **📊 Custom Note Styles**: Generate different styles of notes from transcriptions

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/username/yt-transcription.git
cd yt-transcription
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up API keys:
   - Create a `.env` file in the root directory
   - Add your API keys as follows:
     ```
     GOOGLE_API_KEY=your_google_api_key
     GROQ_API_KEY=your_groq_api_key
     ```

## 🚀 Usage


### Web Interface

1. Start the web server:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Enter a YouTube URL in the input field and click "Generate Notes" or use other features


## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the project's coding standards and includes appropriate tests.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

Abdullah - [Gmail](my.abdullah.nauman@gmail.com)

Project Link: [Streamlit App](https://youtube-notes-generator.streamlit.app/)

## 🙏 Acknowledgements

- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)