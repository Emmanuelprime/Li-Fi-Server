from flask import Flask, request
import speech_recognition as sr
from pydub import AudioSegment
import io

app = Flask(__name__)
application = app

# Global buffer to store chunks
audio_chunks = []

@app.route("/stt", methods=["POST"])
def stt():
    global audio_chunks

    # Stop signal
    if request.is_json:
        data = request.get_json()
        if data.get("stop"):
            if not audio_chunks:
                return "No audio received", 400

            # Combine all chunks in memory
            full_audio = AudioSegment.empty()
            for chunk in audio_chunks:
                seg = AudioSegment.from_raw(
                    io.BytesIO(chunk),
                    sample_width=2,
                    frame_rate=16000,
                    channels=1
                )
                full_audio += seg

            # Export to an in-memory BytesIO buffer instead of a file
            audio_buffer = io.BytesIO()
            full_audio.export(audio_buffer, format="wav")
            audio_buffer.seek(0)  # Reset pointer to start

            audio_chunks = []  # Clear buffer

            # Run STT
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_buffer) as source:
                audio_data = recognizer.record(source)
                try:
                    text = recognizer.recognize_google(audio_data)
                    return text
                except sr.UnknownValueError:
                    return "Could not understand audio"
                except sr.RequestError:
                    return "Error connecting to Google Speech API"

    # Regular audio chunk
    audio_bytes = request.data
    if audio_bytes:
        audio_chunks.append(audio_bytes)
        return f"🗣️ chunk received ({len(audio_bytes)} bytes)"
    else:
        return "No audio data received", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

