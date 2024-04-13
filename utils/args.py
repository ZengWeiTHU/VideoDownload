import argparse
from bs4 import BeautifulSoup
import random
from urllib.request import Request, urlopen
from utils.config import headers
import re


def get_parser():
    parser = argparse.ArgumentParser(description="Video Downloader")
    parser.add_argument("--random", type=bool, default=False,
                        help="Enter True for download random ")
    parser.add_argument("--url", type=str, default="",
                        help="Video URL to download")
    parser.add_argument("--all-urls", type=str, default="",
                        help="Video URL contains multiple videos")
    
    return parser


def av_recommand():
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = 'https://jable.tv/'
    request = Request(url, headers=headers)             # 这个返回的连接是随机的，但有时候会报错，headers是个特殊参数
    web_content = urlopen(request).read()               # 获取网页的内容
    # 得到绕过地址的 html
    soup = BeautifulSoup(web_content, 'html.parser')    # 几乎返回的是HTML的内容
    h6_tags = soup.find_all('h6', class_='title')       # 这个应该是根据HTML标签找视频标题                   
    av_list = re.findall(r'https[^"]+', str(h6_tags))   # 这个会返回找到的视频地址list
    print('av_list:',av_list)
    return random.choice(av_list)                       # 随机挑选一个


# print(av_recommand())
