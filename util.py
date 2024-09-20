# coding=utf-8
import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
#import edge_tts
from pydub import AudioSegment
import subprocess
import os
 

from pydub.utils import which


import dashscope
from dashscope.audio.tts_v2 import *
# 配置dashscope 
# https://help.aliyun.com/zh/dashscope/developer-reference/cosyvoice-api-details?spm=a2c4g.11186623.0.0.3f2744b7PqGY8W
dashscope.api_key = 'sk-xxx'
model = "cosyvoice-v1"
def get_silcon_client():
    # 配置硅基流动模型
    #https://docs.siliconflow.cn/docs/4-api%E8%B0%83%E7%94%A8
    client = OpenAI(api_key="sk-xxx", 
                    base_url="https://api.siliconflow.cn/v1")
    return client
 
def get_gpt_client():
    # 配置gpt 或其他模型openai 格式
    # https://api.xi-ai.cn/about
    client = OpenAI(
        api_key= 'sk-xxxx',
        base_url="https://api.xi-ai.cn/v1",
    )
    return client


def build_tts(voice,text,output):
    #阿里巴巴api
    print(voice,text,output)
    synthesizer = SpeechSynthesizer(model=model, voice=voice,speech_rate=1)

    audio = synthesizer.call(text)
    print('requestId: ', synthesizer.get_last_request_id())
    with open(output, 'wb') as f:
        f.write(audio)
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffmpeg = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")
def scrape_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()


def generate_podcast_dialogue2(text):
    #暂时不能跑通，需要提示词优化
    client = get_silcon_client()
    model = 'alibaba/Qwen1.5-110B-Chat'# gpt-4o-mini
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "生成一段播客形式的对话，必须要中文,以JSON格式返回。格式为: {\"dialogue\": [{\"speaker\": \"A\", \"text\": \"...\"}, {\"speaker\": \"B\", \"text\": \"...\"}]}"},
            {"role": "user", "content": text}
        ]
    )
    return json.loads(response.choices[0].message.content)

def generate_podcast_dialogue(text):
    client = get_gpt_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "生成一段播客形式的对话，必须要中文,以JSON格式返回。格式为: {\"dialogue\": [{\"speaker\": \"A\", \"text\": \"...\"}, {\"speaker\": \"B\", \"text\": \"...\"}]}"},
            {"role": "user", "content": text}
        ]
    )
    return json.loads(response.choices[0].message.content)

def text_to_speech(text, speaker, output_file):
    # edge tts ，但是不知道为什么运行不了
    voice = 'zh-CN-XiaoxiaoNeural' if speaker == 'A' else 'zh-CN-YunxiNeural'
    command = f'edge-tts --voice {voice} --text "{text}" --write-media {output_file}'
    subprocess.run(command, shell=True, check=True)

def concatenate_audio(audio_files, output_file):
    # 拼接audio
    combined = AudioSegment.empty()
    for file in audio_files:
        if os.path.exists(file):

            print('read',file)
            sound = AudioSegment.from_file(file)
            combined += sound
        else:
            print('not found ',file)
    combined.export(output_file, format="mp3")

def main(url):
    # 1. 爬取网页文本
    text = scrape_text(url)
    
    # 2. 使用自定义客户端生成播客对话
    dialogue_json = generate_podcast_dialogue(text)
    print(dialogue_json)
    
    # 3. 生成语音并拼接
    audio_files = []
    import time
    t = str(time.time())
    for i, entry in enumerate(dialogue_json['dialogue']):
        output_file = f"temp_{t}_{i}.mp3"
        speaker = entry['speaker']
        voice = 'longmiao' if speaker == 'A' else 'longfei'
        build_tts( voice,entry['text'], output_file)
        #text_to_speech(entry['text'], entry['speaker'], output_file)
        audio_files.append(os.path.abspath(output_file))
 
    concatenate_audio(audio_files, f"final_podcast_{t}.mp3")
    
    # 清理临时文件
    for file in audio_files:
        os.remove(file)

# 使用示例
main("https://mp.weixin.qq.com/s/33owTCQkHtdFQRPQgHcC6A")
