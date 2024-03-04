import pyaudio
import os
import threading
import json
import wave
from openai import OpenAI
from opencc import OpenCC
from pydub import AudioSegment
from pydub.playback import play
from server.instructions import black_cat_instructions
from server.functions import exit_app, switch_output_mode, set_volume
from server.assistant import create_assistant, create_thread, get_completion
from server.mp3_test import create_threading, conctrl_music
import pygame

pygame.init()
pygame.mixer.init()

os.environ["http_proxy"] = "http://localhost:15732"
os.environ["https_proxy"] = "http://localhost:15732"

# 替换为您的实际 OpenAI API 密钥
api_key = "你的API"

# 创建 OpenAI 客户端
client = OpenAI(api_key=api_key)

# 标志位，表示是否停止录音
stop_recording = False

# 录制音频并返回录音状态
def record_audio(filename):
    global stop_recording

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始录音，按回车键结束...")

    frames = []

    while not stop_recording:
        try:
            data = stream.read(CHUNK)
            frames.append(data)
        except Exception as e:
            print("录音失败:", str(e))
            break

    print("录音结束.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print("录音已保存为:", filename)
    print("请稍等...")

# 提供录音文件的路径
audio_file_path = "recorded_audio.wav"

# 创建 Assistant
assistant_id = create_assistant(
    name="智能终端升级版本1.0",
    instructions=black_cat_instructions,
    model="gpt-4-1106-preview",
    tools=[
        {
            "type": "retrieval"  # 知识检索
        },
        {
            "type": "code_interpreter"  # 代码解释器
        },
        {
            "type": "function",  # 用于获取当前日期所在城市的函数
            "function": {
                "name": "switch_output_mode",
                "description": "根据当前输出模式切换输出模式",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "date_str": {
                            "type": "string",
                            "description": "切换后的output_mode输出模式"
                        },
                    },
                    "required": ["date_str"]
                }
            }
        },

    ],
    files=["knowledge.txt"]
)

# 创建函数调用列表
funcs = [exit_app, switch_output_mode, set_volume, conctrl_music]

# 创建 Thread
thread_id = create_thread()
# 全局配置变量
output_mode = ""
volume = 0.0
input_mode = ""
voice = ""
tone = ""
# 读取配置文件
def read_config():
    with open('config.json', encoding='utf-8') as f:
        config = json.load(f)
    return config

# 重新加载配置文件
def reload_config():
    global output_mode, volume, input_mode, voice, tone
    config = read_config()
    output_mode = config["output_mode"]
    volume = config["volume"]
    input_mode = config["input_mode"]
    voice = config["voice"]  # 默认音色为 "alloy"  alloy、echo、fable、onyx、nova和shimmer
    print("重新加载配置文件成功。")

# 读取初始配置
reload_config()
# 文本转语音  pydub
def text_to_speech(text, output_file):
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text
    )
    response.stream_to_file(output_file)
    # 播放音频流
    audio = AudioSegment.from_file(output_file)
    play(audio)

# 根据需求打印或播报助手回答
def text_to_speech_and_play(response):
    print("Bot:", response)
    print(output_mode)
    if output_mode == "audio":
        text_to_speech(response, "response_audio.mp3")

# Assistant聊天函数
def main(input_text):
    message = get_completion(assistant_id, thread_id, input_text, funcs)
    return message

# 开始对话
while True:
    if input_mode == "record":
        input("按下回车键开始录音...")
        # 开始录音
        stop_recording = False
        recording_thread = threading.Thread(target=record_audio, args=(audio_file_path,))
        recording_thread.start()

        # 等待用户按下回车键结束录音
        input("按下回车键结束录音...")
        stop_recording = True
        recording_thread.join()

        # 如果录音成功，则进行转录和聊天API调用
        if os.path.exists(audio_file_path):
            with open(audio_file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    timeout=60
                )
            # 使用 opencc 将繁体中文转换为简体中文
            cc = OpenCC('t2s')  # 't2s' 表示繁体到简体
            transcript_simplified = cc.convert(transcript.text)

            # 输出转录结果
            print("转录结果:", transcript_simplified)
            response = main(transcript_simplified)
            print("已获取响应文字，正在转录音，请稍等")

            # 检查是否包含结束循环的关键词
            if "再见" in transcript_simplified:
                print("结束循环，再见！")
                text_to_speech_and_play("再见！")
                conctrl_music("e")
                exit_app()
                break

                # 其他功能的实现，例如切换输出模式、设置音量等
            elif "切换输出模式" in transcript_simplified:
                output_mode = switch_output_mode(output_mode)
            elif "设置音量" in transcript_simplified:
                volume = set_volume(volume)
            elif "播放音乐" in transcript_simplified:
                create_threading()
            elif "暂停" in transcript_simplified:
                conctrl_music("p")
            elif "恢复播放" in transcript_simplified:
                conctrl_music("u")
            elif "上一首" in transcript_simplified:
                conctrl_music("n")
            elif "下一首" in transcript_simplified:
                conctrl_music("b")
            elif "停止播放" in transcript_simplified:
                conctrl_music("q")
            # 聊天功能
            text_to_speech_and_play(response)
        else:
            print("录音文件不存在！")
    elif input_mode == "write":
        user_input = input("User: ")
        response = main(user_input)

        if user_input.lower() == "exit":
            print("Goodbye!")
            break
            # 其他功能的实现，例如切换输出模式、设置音量等
        elif "再见" in user_input:
            conctrl_music("e")
            exit_app()
        elif "切换输出模式" in user_input:
            output_mode = switch_output_mode(output_mode)
        elif "设置音量" in user_input:
            volume = set_volume(volume)
        elif "轻松的音乐" in user_input:
            create_threading()
        elif "暂停" in user_input:
            conctrl_music("p")
        elif "恢复播放" in user_input:
            conctrl_music("u")
        elif "上一首" in user_input:
            conctrl_music("n")
        elif "下一首" in user_input:
            conctrl_music("b")
        elif "停止播放" in user_input:
            conctrl_music("q")

        text_to_speech_and_play(response)