
import requests
import os
import re
import urllib.request
import m3u8
from Crypto.Cipher import AES
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# import自写函数
from utils.args import *
from utils.config import headers
from utils.crawler import prepareCrawl
from utils.merge import mergeMp4
from utils.delete import deleteM3u8, deleteMp4
from utils.cover import getCover
from utils.encode import ffmpegEncode

def download(url):
    encode = 0 #不转档
    action = input('要转档吗?[y/n]')
    if action.lower() == 'y':
        action = input('选择转档方案[1:仅转换格式(默认，推荐) 2:NVIDIA GPU 转档 3:CPU 转档]')
        if action == '2':
            encode = 2 #GPU转档
        elif action == '3':
            encode = 3 #CPU转档
        else:
            encode = 1 #快速无损转档

    print('正在下载影片: ' + url)
    # 建立video资料夹
    urlSplit = url.split('/')
    # save_dir = input("请输入视频保存的地址：") or os.getcwd()
    save_dir = './Video'
    dirName = urlSplit[-2]
    video_save_dir = save_dir + '/' + dirName
    if os.path.exists(f'{video_save_dir}/{dirName}.mp4'):
        print('video资料夹已存在, 跳过...')
        return
    if not os.path.exists(video_save_dir):
        os.makedirs(video_save_dir)
    folderPath = os.path.join(save_dir, dirName) # os.getcwd()会获取当前文件夹
  
    #配置Selenium参数
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")
    dr = webdriver.Chrome(options=options)
    dr.get(url)
    result = re.search("https://.+m3u8", dr.page_source)
    print(f'result: {result}')
    m3u8url = result[0]
    print(f'm3u8url: {m3u8url}')

    # 得到 m3u8 网址
    m3u8urlList = m3u8url.split('/')
    m3u8urlList.pop(-1)
    downloadurl = '/'.join(m3u8urlList)

    # 储存 m3u8 file 至资料夹
    m3u8file = os.path.join(folderPath, dirName + '.m3u8')
    urllib.request.urlretrieve(m3u8url, m3u8file)

    # 得到 m3u8 file里的 URI和 IV
    m3u8obj = m3u8.load(m3u8file)
    m3u8uri = ''
    m3u8iv = ''

    for key in m3u8obj.keys:
        if key:
            m3u8uri = key.uri
            m3u8iv = key.iv

    # 储存 ts网址 in tsList
    tsList = []
    for seg in m3u8obj.segments:
        tsUrl = downloadurl + '/' + seg.uri
        tsList.append(tsUrl)

    # 有加密
    if m3u8uri:
        m3u8keyurl = downloadurl + '/' + m3u8uri  # 得到 key 的网址
        # 得到 key的內容
        response = requests.get(m3u8keyurl, headers=headers, timeout=10)
        contentKey = response.content

        vt = m3u8iv.replace("0x", "")[:16].encode()  # IV取前16位

        ci = AES.new(contentKey, AES.MODE_CBC, vt)  # 构建解码器
    else:
        ci = ''

    # 刪除m3u8 file
    deleteM3u8(folderPath)

    # 开始爬虫并下载mp4片段至资料夹
    prepareCrawl(ci, folderPath, tsList)

    # 合成mp4
    mergeMp4(folderPath, tsList)

    # 刪除子mp4
    deleteMp4(folderPath)

    # 取得封面
    getCover(html_file=dr.page_source, folder_path=folderPath)

    # 转档
    ffmpegEncode(folderPath, dirName, encode)

# url = 'https://jable.tv/videos/rki-665/'
# download(url)