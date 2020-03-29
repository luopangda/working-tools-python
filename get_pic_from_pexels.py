# urllib模块提供了读取Web页面数据的接口
import requests
import os
import io
from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver

# data-large-src="https://images.pexels.com/photos/792381/pexels-photo-792381.jpeg"

browser = webdriver.PhantomJS()



def get_html(url):
    # 伪装成浏览器
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
        "cookie": "cfduid=d06140361435067b7f10656966cfbe3b31579481312; locale=en-US; _ga=GA1.2.2053146073.1579481329; _pexels_session=TkZzK09GZDVHOTVXUzBVdkFZWWszVnRlRFZIOFVLRTNzMGU5a0IzNUo4UzlyOHV3T2JsNFhLYWg0OXRFRGZyVEtPdDhtSllVSUgxV2RXWEt6aGlyZlBtdXhxRlhBRFZMMXVVRWE1NUs5RDNsUGdhT2JlSlNaOXJEaFU0UlVKOG9FTkY5QlBPcFpxU3dwbTY0YWRINll3PT0tLTE0YlJXSTZlRVB3UXU3b1VWSitVRXc9PQ%3D%3D--325884aceb0574085b9c54146ee870e3df95ad60; _gaexp=GAX1.2.nX3RY6kqQP2P41NJE6AqsA.18370.0; _fbp=fb.1.1579481331741.44865622; _hjid=1f4145ae-35fe-4953-a057-62300845969f; _gid=GA1.2.1430687399.1579585368; _gat=1",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }
    plain_text = requests.get(url, headers=headers).text
    soup = BeautifulSoup(plain_text)
    return soup


def get_img(soup, folder_path, page, scenario):
    download_links = []
    temp = soup.find_all("img")
    for pic_tag in soup.find_all("img"):
        pic_link = pic_tag.get('data-tiny-src')
        if pic_link:
            download_links.append(pic_link.split('?')[0] + '?auto=compress')
    # 创建文件夹
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # 挨个下载
    for index, item in enumerate(download_links):
        res = requests.get(item)
        # 判断文件宽高
        pic = Image.open(io.BytesIO(res.content))
        width = pic.size[0]
        height = pic.size[1]
        ratio = width / height
        # 如果宽高比大于 1.3 则保存下来
        if ratio > 1.3:
            # P 图加上 LOGO
            # 压缩图片，质量要好的话，Image.ANTIALIAS 得加上，抗锯齿。
            new_pic = pic.resize((666, int(height / width * 666)), Image.ANTIALIAS)
            #  新建底图
            target = Image.new('RGBA', new_pic.size, (0, 0, 0, 0))
            # 先加载原图，把 RGB 格式转换成 RGBA 格式
            new_pic = new_pic.convert("RGBA")
            #  先加载原图，整个图和底图重合
            box1 = (0, 0, 666, int(height / width * 666))
            target.paste(new_pic, box1)
            # 加载透明图（要叠加上去的图），
            tmp_img = Image.open('./' + scenario + '.png')
            # 加载透明图（要叠加上去的图），垂直居中
            box2 = (0, int((height / width * 666) / 2 - 141), 666, int((height / width * 666) / 2 + 142))  # 底图上需要P掉的区域
            region = tmp_img.resize((box2[2] - box2[0], box2[3] - box2[1]))
            target.paste(region, box2, region) # 干嘛要整两个region ？不懂
            # 保存RGBA意思是红色，绿色，蓝色，Alpha的色彩空间，Alpha指透明度。
            # 而JPG不支持透明度，所以要么丢弃Alpha,要么保存为.png文件，
            # PNG 文件直接保存，尺寸大，JPEG的效果一样好，选择保存成jpeg
            # target.save(folder_path + '/' + str(page) + '-' + str(index) + ".png", quality=95)
            target = target.convert('RGB')
            target.save(folder_path + '/' + str(page) + '-' + str(index) + ".jpeg", 'jpeg', quality=100)
            # 原图也保存一下，备用
            with open(folder_path + '/' + str(page) + '-' + str(index) + "-o.jpeg", 'wb') as f:
                f.write(res.content)
            print("——————page" + str(page) + "下蛋啦——————")


# 主题
theme = 'friend'
# 场景
scenario = 'friend'
# 文件夹
folder_path = "./pexels/" + scenario + "/" + theme
for page in range(1, 100):
    print(page)
    html = get_html("https://www.pexels.com/search/" + theme + "?page=" + str(page))
    get_img(html, folder_path, page, scenario)


