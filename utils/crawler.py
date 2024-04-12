import os
import requests
from config import headers
from functools import partial
import concurrent.futures
import time
import copy


def scrape(ci, folderPath, downloadList, urls):
    os.path.split(urls)
    fileName = urls.split('/')[-1][0:-3]
    saveName = os.path.join(folderPath, fileName + ".mp4")
    if os.path.exists(saveName):
        # 跳过已下載
        print('当前目标: {0} 已下載, 故跳过...剩余 {1} 個'.format(
            urls.split('/')[-1], len(downloadList)))
        downloadList.remove(urls)
    else:
        response = requests.get(urls, headers=headers, timeout=10)
        if response.status_code == 200:
            content_ts = response.content
            if ci:
                content_ts = ci.decrypt(content_ts)  # 解码
            with open(saveName, 'ab') as f:
                f.write(content_ts)
                # 输出进度
            downloadList.remove(urls)
        print('\r当前下载: {0} , 剩余 {1} 个, status code: {2}'.format(
            urls.split('/')[-1], len(downloadList), response.status_code), end='', flush=True)


def prepareCrawl(ci, folderPath, tsList):
    downloadList = copy.deepcopy(tsList)
    # 开始时间
    start_time = time.time()
    print('开始下载 ' + str(len(downloadList)) + ' 个档案..', end='')
    print('预计等待时间: {0:.2f} 分钟 视影片长度与网络速度而定)'.format(len(downloadList) / 150))

    # 开始爬取
    startCrawl(ci, folderPath, downloadList)

    end_time = time.time()
    print('\n花费 {0:.2f} 分钟 爬取完成 !'.format((end_time - start_time) / 60))


def startCrawl(ci, folderPath, downloadList):
    # 同時建立及启用 20 个执行者
    round = 0
    while(downloadList != []):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(partial(scrape, ci, folderPath,
                                 downloadList), downloadList)
        round += 1
        print(f', round {round}')
