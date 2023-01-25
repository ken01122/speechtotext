import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import shutil


def speed_change(sound, speed=1.0):
    rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * speed)
      })
    return rate.set_frame_rate(sound.frame_rate)


def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = sound.dBFS - target_dBFS
    return sound.apply_gain(change_in_dBFS)


def get_large_audio_transcription(path, filename):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks
    """

    # open the audio file using pydub
    sound = match_target_amplitude(AudioSegment.from_wav(path), -20.0)
    # split audio sound where silence is 700 miliseconds or more and get chunks
    chunks = split_on_silence(sound,
                              # experiment with this value for your target audio file
                              min_silence_len=250,
                              # adjust this per requirement
                              silence_thresh=sound.dBFS - 12,
                              # keep the silence for 1 second, adjustable as well
                              keep_silence=200,
                              seek_step=1
                              )
    folder_name = f"C:\\Users\\Ken\\pythonProject\\audio-chunks"

    r = sr.Recognizer()
    # create a directory to store the audio chunks
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    else:
        shutil.rmtree(folder_name)  # 刪除音檔分割資料夾以刪除分割音檔
        os.mkdir(folder_name)
    f = open(fr'C:\Users\Ken\pythonProject\text\{filename}.txt', "w", encoding='UTF-8')
    # process each chunk
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk = speed_change(audio_chunk, 0.9)  # 更改聲音速度
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened, language="zh-TW") + "\n"
            except sr.UnknownValueError as e:
                print("can not recognize", end="")
                text = ""
            else:
                text = f"{text.capitalize()}"
            f.write(text)
    f.close


for info in os.listdir(r'C:\Users\Ken\pythonProject\wav'):
    domain = os.path.abspath(r'C:\Users\Ken\pythonProject\wav') #獲取資料夾的路徑，此處其實沒必要這麼寫，目的是為了熟悉os的資料夾操作
    path = os.path.join(domain, info) #將路徑與檔名結合起來就是每個檔案的完整路徑
    filename = os.path.splitext(info)[0]
    get_large_audio_transcription(path, filename)

