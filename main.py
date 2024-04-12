from utils.args import *
from utils.download import download
from utils.movies import movieLinks

parser = get_parser()
args = parser.parse_args()

if(len(args.url) != 0):
    url = args.url
    download(url)
elif(args.random == True):
    url = av_recommand()
    download(url)
elif(args.all_urls != ""):
    all_urls = args.all_urls
    urls = movieLinks(all_urls)
    for url in urls:
        download(url)
else:
    # 使用者输入视频网址
    url = input('输入视频网址:')
    download(url)
