import speech_recognition as sr
import streamlit as st

def transcribe_audio(audio_file):
    """
    Транскрибирует аудиофайл (WAV) в текст.
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='ru-RU')
            return text
        except sr.UnknownValueError:
            return "Не удалось распознать речь."
        except sr.RequestError:
            return "Ошибка сервиса распознавания."
