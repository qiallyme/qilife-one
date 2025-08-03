# Voice Transcription & Speaker Separation (Windows)

This setup is for transcribing MP4 argument clips with isolated voices and speaker labeling. It is **separate from Qivoice** (phone call module) but can be merged later if needed.

---

## 1. Requirements
- Windows 10/11
- Python 3.10+ (add to PATH during install)
- Git (optional but recommended)
- FFmpeg (auto-installed via pip package `ffmpeg-python`)

---

## 2. Setup Instructions

### Create Project Folder & Virtual Environment
```powershell
mkdir voice_transcripts
cd voice_transcripts
python -m venv venv
.env\Scriptsctivate
```

### Install Required Libraries
```powershell
pip install ffmpeg-python demucs openai-whisper pyannote.audio torch torchaudio
```

---

## 3. Convert MP4 → WAV
```powershell
ffmpeg -i "argument.mp4" "argument.wav"
```

---

## 4. Isolate Vocals (Demucs)
```powershell
demucs "argument.wav"
```
- Output: `separated/htdemucs/argument/vocals.wav`

---

## 5. Transcribe (Whisper)
```powershell
whisper "separated/htdemucs/argument/vocals.wav" --model medium --language en
```
- Outputs `.txt` and `.srt` with timestamps

---

## 6. Speaker Separation (Pyannote)
Run the provided `diarize.py` to create a timestamped speaker file.

```powershell
python diarize.py
```

---

## 7. Output
- `vocals.txt` → transcription
- `vocals.srt` → transcription with timestamps
- `diarization.txt` → speaker-labeled timestamps

Combine manually or extend script to merge.

---

## 8. Future Integration
- Can merge with Qivoice module to handle **both calls & clips** under QiLife.
- Future automation: drag-drop MP4 → full transcript generation.
