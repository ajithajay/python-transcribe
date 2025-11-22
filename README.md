# Video Transcription Tool

A simple Python tool that transcribes video files locally using OpenAI's Whisper model. Runs entirely on CPU with 24GB RAM.

## Features

-   Extract audio from video files
-   Local transcription using Whisper (no API calls needed)
-   Multiple output formats: text, JSON, SRT, VTT, or all at once
-   Timestamp support for subtitles
-   Auto-detect language or specify manually
-   Multiple model sizes for speed/accuracy tradeoff
-   **Organized folder structure** - automatic input/output management
-   **Per-video output folders** - all files organized by video name

## Project Structure

```
take-audio/
├── input/              # Place your video files here
├── output/             # Transcriptions organized by video name
│   ├── video1/
│   │   ├── video1_transcription.txt
│   │   ├── video1_transcription.json
│   │   ├── video1_transcription.srt
│   │   └── video1_audio.wav (if --keep-audio)
│   └── video2/
│       └── ...
├── transcribe.py       # Main script
├── requirements.txt
└── README.md
```

## Installation

1. Install system dependencies (ffmpeg):

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

1. **Place your video in the `input/` folder:**

```bash
cp your_video.mp4 input/
```

2. **Run transcription:**

```bash
python transcribe.py input/your_video.mp4
```

3. **Find results in `output/your_video/`** - automatically organized!

### Basic Usage

Transcribe a video with default settings (medium model, text output):

```bash
# From input folder (recommended)
python transcribe.py input/video.mp4

# Or from any path
python transcribe.py /path/to/video.mp4
```

Output will be automatically organized in `output/video/` folder.

### Advanced Options

**Specify model size:**

```bash
# Fast but less accurate
python transcribe.py input/video.mp4 -m small

# Best accuracy (slower on CPU)
python transcribe.py input/video.mp4 -m large
```

**Specify output format:**

```bash
# JSON with timestamps
python transcribe.py input/video.mp4 -f json

# SRT subtitle file
python transcribe.py input/video.mp4 -f srt

# Generate ALL formats at once
python transcribe.py input/video.mp4 -f all
```

**Specify language (faster than auto-detect):**

```bash
python transcribe.py input/video.mp4 -l en
```

**Keep extracted audio file:**

```bash
python transcribe.py input/video.mp4 --keep-audio
```

**Custom output path (overrides auto-organization):**

```bash
python transcribe.py input/video.mp4 -o custom/path/transcription.txt
```

### Complete Example

```bash
# Generate all formats, keep audio, use English
python transcribe.py input/my_video.mp4 -m medium -f all -l en --keep-audio
```

This creates:

```
output/my_video/
├── my_video_transcription.txt
├── my_video_transcription.json
├── my_video_transcription.srt
├── my_video_transcription.vtt
└── my_video_audio.wav
```

## Model Sizes

Choose based on your needs:

| Model  | RAM Usage | Speed (CPU) | Accuracy | Recommended For       |
| ------ | --------- | ----------- | -------- | --------------------- |
| tiny   | ~1GB      | Very Fast   | Low      | Quick drafts          |
| base   | ~1GB      | Fast        | Good     | General use           |
| small  | ~2GB      | Medium      | Better   | Good balance          |
| medium | ~5GB      | Slow        | High     | **Best for 24GB RAM** |
| large  | ~10GB     | Very Slow   | Highest  | Maximum accuracy      |

## Performance Expectations

On a CPU-only system with 24GB RAM:

-   **1 minute of video** ≈ 2-5 minutes processing time (medium model)
-   **1 hour of video** ≈ 2-5 hours processing time (medium model)
-   Use smaller models (base/small) for faster results

## Output Formats

### TXT

Plain text transcription without timestamps.

### JSON

Structured format with full text and segmented timestamps:

```json
{
	"text": "Full transcription...",
	"language": "en",
	"segments": [
		{
			"start": 0.0,
			"end": 3.5,
			"text": "Hello world"
		}
	]
}
```

### SRT

Standard subtitle format for video players:

```
1
00:00:00,000 --> 00:00:03,500
Hello world
```

### VTT

WebVTT format for web players.

## Supported Video Formats

Common formats supported by moviepy/ffmpeg:

-   MP4, AVI, MOV, MKV, WMV, FLV, WebM, MPEG, and more

## Troubleshooting

**Error: "ffmpeg not found"**

-   Install ffmpeg using your system package manager

**Out of memory errors:**

-   Use a smaller model (small or base)
-   Process shorter video segments

**Slow processing:**

-   This is expected on CPU. Use smaller models for faster results
-   Consider upgrading to a GPU for 10-100x speedup

## License

MIT License - Feel free to use and modify
