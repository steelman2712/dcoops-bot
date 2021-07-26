from gtts import gTTS


async def tts_to_file(text):
    tts = gTTS(text=text, lang="en", tld="co.in")
    tts.save("tts.mp3")
