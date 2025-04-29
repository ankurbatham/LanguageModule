#run perfectly

# import speech_recognition as sr
# import pyttsx3
# import librosa
# import numpy as np
# from deep_translator import GoogleTranslator
# from apscheduler.schedulers.background import BackgroundScheduler
# import time

# # Supported languages
# SUPPORTED_LANGUAGES = {
#     "English": "en",
#     "Spanish": "es",
#     "French": "fr",
#     "German": "de",
#     "Hindi": "hi",
#     "Japanese": "ja"
# }

# def recognize_speech():
#     """Capture audio and convert it to text."""
#     recognizer = sr.Recognizer()
#     with sr.Microphone() as source:
#         print("Speak now...")
#         recognizer.adjust_for_ambient_noise(source)
#         audio = recognizer.listen(source)
#         try:
#             text = recognizer.recognize_google(audio)
#             print(f"Recognized text: {text}")
#             return text
#         except sr.UnknownValueError:
#             return "Could not understand audio"
#         except sr.RequestError as e:
#             return f"Error with recognition service: {e}"

# def extract_pitch(audio_file):
#     """Estimate gender based on fundamental frequency."""
#     try:
#         y, sr = librosa.load(audio_file, sr=16000)
#         f0, _, _ = librosa.pyin(y, fmin=80, fmax=400)
#         f0 = f0[np.nonzero(f0)]  # Remove unvoiced frames

#         if len(f0) == 0:
#             return "Unknown"

#         avg_f0 = np.mean(f0)
#         return "Male" if avg_f0 < 165 else "Female"
#     except Exception as e:
#         return f"Error processing audio: {e}"

# def translate_text(text, target_language):
#     """Translate text to the target language."""
#     try:
#         return GoogleTranslator(source="auto", target=target_language).translate(text)
#     except Exception as e:
#         return f"Translation error: {e}"

# def text_to_speech(text):
#     """Convert text to speech with explicit voice selection."""
#     engine = pyttsx3.init()
#     voices = engine.getProperty('voices')

#     if voices:  # Ensure voices exist
#         engine.setProperty('voice', voices[0].id)  # Set default voice

#     engine.setProperty('rate', 150)  # Adjust speech speed

#     if text:
#         print("Speaking translated text...")
#         engine.say(text)
#         engine.runAndWait()
#     else:
#         print("No text to speak.")

# def save_text_as_audio(text, output_file="speech.wav"):
#     """Save text as audio for further analysis."""
#     engine = pyttsx3.init()
#     engine.save_to_file(text, output_file)
#     engine.runAndWait()

# def process_speech():
#     """Scheduled function to execute speech recognition pipeline."""
#     print("\nAvailable languages:", ", ".join(SUPPORTED_LANGUAGES.keys()))
#     chosen_language = input("Enter target language (e.g., Spanish, French, Hindi): ").strip()
    
#     if chosen_language not in SUPPORTED_LANGUAGES:
#         print("Invalid selection. Please choose from the supported options.")
#         return
    
#     target_lang_code = SUPPORTED_LANGUAGES[chosen_language]

#     print("\nStep 1: Speech-to-Text")
#     spoken_text = recognize_speech()
    
#     if not spoken_text or "Could not understand" in spoken_text:
#         print(spoken_text)
#         return
    
#     print(f"Recognized Text: {spoken_text}")

#     # Gender detection using saved audio
#     save_text_as_audio(spoken_text)
#     gender = extract_pitch("speech.wav")
#     print(f"Detected Speaker Gender: {gender}")

#     print("\nStep 2: Translation")
#     translated_text = translate_text(spoken_text, target_lang_code)
#     print(f"Translated Text ({chosen_language}): {translated_text}")

#     print("\nStep 3: Text-to-Speech")
#     text_to_speech(translated_text)

# # Set up scheduler
# scheduler = BackgroundScheduler()
# scheduler.add_job(process_speech, 'interval', seconds=20)  # Run every 20 seconds
# scheduler.start()

# # Keep the script running
# print("Scheduler is running. Press Ctrl+C to exit.")
# try:
#     while True:
#         time.sleep(1)  # Keeps the process alive
# except KeyboardInterrupt:
#     scheduler.shutdown()
#     print("Scheduler stopped.")








#  with api
from flask import Flask, request, jsonify
import speech_recognition as sr
import pyttsx3
import librosa
import numpy as np
from deep_translator import GoogleTranslator
import os

app = Flask(__name__)

SUPPORTED_LANGUAGES = {
    "English": "en", "Spanish": "es", "French": "fr",
    "German": "de", "Hindi": "hi", "Japanese": "ja"
}

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Error: {e}"

@app.route("/speech-to-text", methods=["POST"])
def speech_to_text():
    """Speech recognition API endpoint"""
    text = recognize_speech()
    return jsonify({"recognized_text": text})

@app.route("/translate", methods=["POST"])
def translate():
    """Translation API endpoint"""
    data = request.json
    text = data.get("text")
    target_lang = data.get("target_language")

    if target_lang not in SUPPORTED_LANGUAGES.values():
        return jsonify({"error": "Unsupported language"}), 400

    translated_text = GoogleTranslator(source="auto", target=target_lang).translate(text)
    return jsonify({"translated_text": translated_text})

@app.route("/gender-detection", methods=["POST"])
def gender_detection():
    """Gender detection API endpoint"""
    file = request.files.get("audio")
    if not file:
        return jsonify({"error": "No audio file provided"}), 400

    file.save("speech.wav")
    y, sr = librosa.load("speech.wav", sr=16000)
    f0, _, _ = librosa.pyin(y, fmin=80, fmax=400)
    f0 = f0[np.nonzero(f0)]

    gender = "Unknown" if len(f0) == 0 else ("Male" if np.mean(f0) < 165 else "Female")
    return jsonify({"detected_gender": gender})

@app.route("/text-to-speech", methods=["POST"])
def text_to_speech_api():
    """Text-to-Speech API endpoint"""
    data = request.json
    text = data.get("text")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    engine = pyttsx3.init()
    engine.save_to_file(text, "output_speech.wav")
    engine.runAndWait()

    return jsonify({"message": "Speech generated", "file": "output_speech.wav"})

if __name__ == "__main__":
    app.run(debug=True)