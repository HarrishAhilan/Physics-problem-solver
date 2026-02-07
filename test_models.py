import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyADaRascUNM4fS-QGYK12ljfaKCp1sBYGo")

print("Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")