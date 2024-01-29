import requests
import json
from yt_dlp import YoutubeDL
import random
import time
import subprocess
import os
t = time.time()

def section(info_dict, ydl):
    length = info_dict.get("duration")
    if length and length > 60:
        t = random.randint(30, length - 30)
        return [{"start_time": t, "end_time": t+1/30}]

def hook(filename):
    subprocess.call(["ffmpeg", "-i", filename, "-vframes", "1", f"{os.path.basename(filename).split('.')[0]}.jpg"])
    os.remove(filename)

baseUrl = "https://www.thebluealliance.com/api/v3"
year = 2023
headers = {"X-TBA-Auth-Key": "am2fYi8tOjApSkLeOsoHzDeftBra8wp6NzB9pekgpJ18MMqi61zkrtUOvbjstT2Z"}
num_videos = 4

events = json.loads(requests.get(baseUrl + f"/events/{year}/keys", headers=headers).content)
a =1
keys = []
for event in events:
    a+=1
    try:
        matches = json.loads(requests.get(f"{baseUrl}/event/{event}/matches", headers=headers).text)
        for i in range(num_videos):
            videos = random.choice(matches)["videos"]
            if len(videos) > 0:
                for video in videos:
                    if video["type"] == "youtube":
                        keys.append(video["key"])
                        break
    except Exception as e:
         print(e)

with YoutubeDL({"force_keyframes_at_cuts": True, "download_ranges": section, "format_sort": ["res"], "post_hooks": [hook]}) as ydl:
    for key in keys:
        t = time.time()
        ydl.download(f"https://www.youtube.com/watch?v={key}")
        print(time.time() - t)