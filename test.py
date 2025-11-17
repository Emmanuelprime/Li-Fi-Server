import requests

# Path to your audio file
audio_file = 'new.wav'

with open(audio_file, 'rb') as f:
    audio_data = f.read()

response = requests.post('http://127.0.0.1:5000/stt', data=audio_data)
print('Recognized text:', response.text)