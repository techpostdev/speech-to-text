<div align="center">

# 🎙️ Speech-to-Text Whisper GUI Python

# *Convert MP4 · MP3 · WAV · M4A · FLAC · MOV · AVI · MKV to Text & Subtitles*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

**Turn any video or audio file into text, subtitles, or data — with one click!**

</div>


# 📸 Screenshot

<p align="center">
  <img src="assets/Screenshot_1.png" alt="Whisper GUI Screenshot" width="800"/>
  <br/>
  <em>Main application interface</em>
</p>


# 📥 What can you transcribe?

| If you have... | You can get... |
|----------------|-----------------|
| 🎥 MP4 Video | 📝 Text transcript |
| 🎵 MP3 Audio | 🎬 SRT subtitles |
| 🎶 WAV Recording | 🌐 VTT web subtitles |
| 📀 M4A Podcast | 📊 JSON data |
| 🎼 FLAC Music | 📈 TSV for Excel |
| 🎬 MOV Video | ✅ All formats at once! |
| 🎞️ AVI Video | |
| 🗃️ MKV Video | |


# 🚀 One-click conversions

- **MP4 → TXT** : Extract text from YouTube videos, lectures, movies
- **MP3 → SRT** : Create subtitles for your podcast
- **WAV → JSON** : Get word-by-word timestamps
- **MOV → VTT** : Web-ready subtitles
- **Batch folder → All formats** : Process 100+ files overnight


# ✨ Features

- 🎯 Drag & Drop support
- 🚀 GPU (CUDA) acceleration
- 📁 Batch processing (entire folders)
- 🌍 8 languages support
- 📄 Multiple output formats (TXT, SRT, VTT, JSON, TSV)
- 🎨 Modern dark theme UI
- ⚡ Keyboard shortcuts


# 🎯 Supported Languages

| Language | Code | Language | Code |
|----------|------|----------|------|
| English | en | Spanish | es |
| French | fr | German | de |
| Italian | it | Japanese | ja |
| Chinese | zh | Russian | ru |


# 📦 Installation

# Prerequisites

- Python 3.8 or higher
- FFmpeg

### Step 1: Install FFmpeg

**Windows:**
winget install ffmpeg

**macOS:**
brew install ffmpeg

**Linux (Ubuntu/Debian):**
sudo apt update
sudo apt install ffmpeg

### Step 2: Clone Repository

git clone https://github.com/techpostdev/speech-to-text
cd speech-to-text

### Step 3: Install Python Packages

pip install -r requirements.txt

### Step 4: Run Application

python speech-to-text.py


### 🚀 GPU Acceleration (Optional)

For 10x faster transcription with NVIDIA GPU:

pip uninstall torch torchaudio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

Verify GPU is working:
python -c "import torch; print(torch.cuda.is_available())"


## 🎮 How to Use

### Single File:
1. Click "BROWSE FILE" or Drag & Drop
2. Select Model (Tiny/Base/Small/Medium)
3. Select Language
4. Choose Output Formats
5. Click "START TRANSCRIPTION"

### Batch Processing:
1. Click "SCAN FOLDER"
2. Select folder with files
3. Check "BATCH PROCESS ALL FILES"
4. Click "START TRANSCRIPTION"


## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl + O | Browse File |
| Ctrl + B | Scan Folder |
| Ctrl + Enter | Start Transcription |


## 📁 Project Structure
Whisper-Speech-To-Text-GUI/
│
├── speech_to_text_gui.py    # Main application (run this)
├── requirements.txt         # Python packages list
├── README.md                # This file
├── LICENSE                  # MIT License
├── .gitignore               # Git ignore rules
│
├── assets/                  # Images folder
│   └── Screenshot_1.png     # App screenshot
│
└── docs/                    # Documentation folder
    ├── installation.md
    ├── usage.md
    └── faq.md


<div align="center">
⭐ Star this repository if you find it useful! ⭐

Made with ❤️ for everyone

</div>