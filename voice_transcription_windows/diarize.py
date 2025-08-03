from pyannote.audio import Pipeline

# Initialize pipeline (requires HuggingFace auth token if model is gated)
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

# Process isolated vocal track
diarization = pipeline("separated/htdemucs/argument/vocals.wav")

# Save speaker timestamps
with open("diarization.txt", "w") as f:
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        f.write(f"{turn.start:.1f}-{turn.end:.1f} {speaker}\n")
