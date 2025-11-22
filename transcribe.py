#!/usr/bin/env python3
"""
Video Transcription Tool
Extracts audio from video and transcribes it using Whisper (runs locally on CPU)
Organized with input/output folder structure
"""

import whisper
import os
import sys
import argparse
from datetime import timedelta
from pathlib import Path
import json
import shutil
import re


def setup_directories():
    """Create input and output directories if they don't exist"""
    input_dir = Path("input")
    output_dir = Path("output")
    
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    
    return input_dir, output_dir


def is_youtube_url(url):
    """Check if the input is a valid YouTube URL"""
    youtube_pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
    return re.search(youtube_pattern, url) is not None


def download_youtube_video(url, output_dir):
    """
    Download YouTube video using yt-dlp
    
    Args:
        url: YouTube URL
        output_dir: Directory to save the downloaded video
    
    Returns:
        Path to the downloaded video file
    """
    try:
        import yt_dlp
        
        print(f"Downloading video from YouTube: {url}")
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Get the actual downloaded filename
            if 'requested_downloads' in info and info['requested_downloads']:
                filename = info['requested_downloads'][0].get('filepath')
            else:
                filename = ydl.prepare_filename(info)
            
        print(f"Video downloaded to: {filename}")
        return Path(filename)
        
    except ImportError:
        print("Error: yt-dlp not installed. Install with: pip install yt-dlp")
        return None
    except Exception as e:
        print(f"Error downloading YouTube video: {e}")
        return None


def extract_audio(video_path, audio_path):
    """Extract audio from video file using moviepy"""
    try:
        import moviepy
        print(f"Extracting audio from {video_path}...")
        
        video = moviepy.VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path, logger=None)
        video.close()
        
        print(f"Audio extracted to {audio_path}")
        return True
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return False


def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format"""
    return str(timedelta(seconds=int(seconds)))


def transcribe_audio(audio_path, model_size="medium", language=None, output_format="txt"):
    """
    Transcribe audio using Whisper
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: Language code (e.g., 'en', 'es') or None for auto-detect
        output_format: Output format (txt, json, srt, vtt)
    """
    import time
    
    print(f"Loading Whisper {model_size} model...")
    model = whisper.load_model(model_size)
    
    print(f"Transcribing audio (this may take a while on CPU)...")
    start_time = time.time()
    
    # Transcribe with options
    options = {
        "verbose": True,
        "language": language,
    }
    
    result = model.transcribe(audio_path, **options)
    
    elapsed_time = time.time() - start_time
    result['_transcription_time'] = elapsed_time
    
    return result


def save_transcription(result, output_path, format_type="txt"):
    """Save transcription in specified format"""
    
    if format_type == "txt":
        # Simple text format
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result["text"])
        print(f"Transcription saved to {output_path}")
    
    elif format_type == "json":
        # JSON format with timestamps
        output_data = {
            "text": result["text"],
            "language": result["language"],
            "segments": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }
                for seg in result["segments"]
            ]
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"Transcription with timestamps saved to {output_path}")
    
    elif format_type == "srt":
        # SRT subtitle format
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(result["segments"], start=1):
                start_time = format_srt_timestamp(segment["start"])
                end_time = format_srt_timestamp(segment["end"])
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text'].strip()}\n\n")
        print(f"SRT subtitle file saved to {output_path}")
    
    elif format_type == "vtt":
        # WebVTT subtitle format
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
            for segment in result["segments"]:
                start_time = format_srt_timestamp(segment["start"])
                end_time = format_srt_timestamp(segment["end"])
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{segment['text'].strip()}\n\n")
        print(f"VTT subtitle file saved to {output_path}")


def format_srt_timestamp(seconds):
    """Format timestamp for SRT/VTT format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe video files using Whisper (local CPU processing)"
    )
    parser.add_argument(
        "video_path",
        help="Path to the video file or YouTube URL (can be in input/ folder or specify full path)"
    )
    parser.add_argument(
        "-m", "--model",
        choices=["tiny", "base", "small", "medium", "large"],
        default="medium",
        help="Whisper model size (default: medium). Larger = more accurate but slower."
    )
    parser.add_argument(
        "-l", "--language",
        help="Language code (e.g., 'en', 'es', 'fr'). Auto-detect if not specified."
    )
    parser.add_argument(
        "-f", "--format",
        choices=["txt", "json", "srt", "vtt", "all"],
        default="txt",
        help="Output format (default: txt). Use 'all' to generate all formats."
    )
    parser.add_argument(
        "-o", "--output",
        help="Custom output file path. By default, creates organized output in output/<video_name>/"
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep extracted audio file in the output folder"
    )
    
    args = parser.parse_args()
    
    # Setup directories
    input_dir, output_dir = setup_directories()
    
    # Check if input is a YouTube URL
    if is_youtube_url(args.video_path):
        print("YouTube URL detected. Downloading video...")
        video_path = download_youtube_video(args.video_path, input_dir)
        if video_path is None:
            print("Failed to download YouTube video.")
            sys.exit(1)
    else:
        # Validate input video exists - check both relative path and input folder
        video_path = Path(args.video_path)
        if not video_path.exists():
            # Try looking in input folder
            alt_path = input_dir / args.video_path
            if alt_path.exists():
                video_path = alt_path
            else:
                print(f"Error: Video file '{args.video_path}' not found!")
                print(f"Tip: Place videos in the 'input/' folder for automatic organization.")
                sys.exit(1)
    
    # Create output folder for this video
    video_stem = video_path.stem
    video_output_dir = output_dir / video_stem
    video_output_dir.mkdir(exist_ok=True)
    
    # Audio path in the output folder
    audio_path = video_output_dir / f"{video_stem}_audio.wav"
    
    print(f"\n{'='*60}")
    print(f"Video: {video_path.name}")
    print(f"Output folder: {video_output_dir}")
    print(f"{'='*60}\n")
    
    # Extract audio
    if not extract_audio(str(video_path), str(audio_path)):
        sys.exit(1)
    
    try:
        # Transcribe
        result = transcribe_audio(
            str(audio_path),
            model_size=args.model,
            language=args.language,
            output_format=args.format
        )
        
        # Determine formats to generate
        if args.format == "all":
            formats = ["txt", "json", "srt", "vtt"]
        else:
            formats = [args.format]
        
        # Save transcription in requested format(s)
        for fmt in formats:
            if args.output and len(formats) == 1:
                output_path = Path(args.output)
            else:
                extension = fmt
                output_path = video_output_dir / f"{video_stem}_transcription.{extension}"
            
            save_transcription(result, str(output_path), fmt)
        
        # Format elapsed time
        elapsed = result.get('_transcription_time', 0)
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
        
        print(f"\n{'='*60}")
        print(f"✓ Transcription complete!")
        print(f"  Model: {args.model}")
        print(f"  Detected language: {result['language']}")
        print(f"  Processing time: {time_str}")
        print(f"  Output location: {video_output_dir}")
        if args.keep_audio:
            print(f"  Audio saved: {audio_path.name}")
        print(f"{'='*60}")
        
    finally:
        # Cleanup audio file unless requested to keep it
        if not args.keep_audio and audio_path.exists():
            os.remove(audio_path)
            print(f"\nTemporary audio file removed.")


if __name__ == "__main__":
    main()
