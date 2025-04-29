# python version 3.12.2
# works properly


import speech_recognition as sr
import pyttsx3
import librosa
import numpy as np
from deep_translator import GoogleTranslator

# Supported languages
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Japanese": "ja"
}

def recognize_speech():
    """Capture audio and convert it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"Recognized text: {text}")
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Error with recognition service: {e}"

def extract_pitch(audio_file):
    """Estimate gender based on fundamental frequency."""
    try:
        y, sr = librosa.load(audio_file, sr=16000)
        f0, _, _ = librosa.pyin(y, fmin=80, fmax=400)
        f0 = f0[np.nonzero(f0)]  # Remove unvoiced frames

        if len(f0) == 0:
            return "Unknown"

        avg_f0 = np.mean(f0)
        return "Male" if avg_f0 < 165 else "Female"
    except Exception as e:
        return f"Error processing audio: {e}"

def translate_text(text, target_language):
    """Translate text to the target language."""
    try:
        return GoogleTranslator(source="auto", target=target_language).translate(text)
    except Exception as e:
        return f"Translation error: {e}"

# def text_to_speech(text):
#     """Convert text to speech with improved handling."""
#     engine = pyttsx3.init()

#     # Fix: Explicitly list available voices and set a default one
#     voices = engine.getProperty('voices')
#     engine.setProperty('voice', voices[0].id)  # Selecting a default voice
#     engine.setProperty('rate', 150)  # Adjust speech speed

#     if text:
#         print("Speaking translated text...")
#         engine.say(text)
#         engine.runAndWait()
#     else:
#         print("No text to speak.")
def text_to_speech(text):
    """Convert text to speech with explicit voice selection."""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    if voices:  # Ensure voices exist
        engine.setProperty('voice', voices[0].id)  # Set default voice

    engine.setProperty('rate', 150)  # Adjust speech speed

    if text:
        print("Speaking translated text...")
        engine.say(text)
        engine.runAndWait()
    else:
        print("No text to speak.")

def main():
    """Main function orchestrating speech processing, gender detection, translation, and TTS."""
    print("Available languages:", ", ".join(SUPPORTED_LANGUAGES.keys()))
    chosen_language = input("Enter target language (e.g., Spanish, French, Hindi): ").strip()
    
    if chosen_language not in SUPPORTED_LANGUAGES:
        print("Invalid selection. Please choose from the supported options.")
        return
    
    target_lang_code = SUPPORTED_LANGUAGES[chosen_language]
    
    print("\nStep 1: Speech-to-Text")
    spoken_text = recognize_speech()
    
    if not spoken_text or "Could not understand" in spoken_text:
        print(spoken_text)
        return
    
    print(f"Recognized Text: {spoken_text}")

    # Gender detection using saved audio
    save_text_as_audio(spoken_text)
    gender = extract_pitch("speech.wav")  # Using saved speech file
    print(f"Detected Speaker Gender: {gender}")

    print("\nStep 2: Translation")
    translated_text = translate_text(spoken_text, target_lang_code)
    print(f"Translated Text ({chosen_language}): {translated_text}")

    print("\nStep 3: Text-to-Speech")
    text_to_speech(translated_text)

def save_text_as_audio(text, output_file="speech.wav"):
    """Save text as audio for further analysis."""
    engine = pyttsx3.init()
    engine.save_to_file(text, output_file)
    engine.runAndWait()

if __name__ == "__main__":
    main()
