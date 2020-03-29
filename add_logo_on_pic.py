import requests
import os
import io
from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver


def get_html(url):
    # 伪装成浏览器
    browser = webdriver.Chrome()
    # 加载网页地址
    browser.get(url)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    return soup


def get_img(soup, folder_path, page, scenario):
    # 获取一个页面下的所有图片的链接，保存在download_links内
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
            #  新建底图，因为贴图是PNG格式的，所以需要 RGBA 格式的底图
            target = Image.new('RGBA', new_pic.size, (0, 0, 0, 0))
            # 把 RGB 格式转换成 RGBA 格式
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

            # PNG 文件直接保存，但尺寸大，JPEG的效果一样好，选择保存成jpeg，转换之前需要把视觉通道换成RGB
            # PNG 默认视觉通道是 RGBA，意思是红色，绿色，蓝色，Alpha的色彩空间，Alpha指透明度。
            # 而JPG不支持透明度，所以要么丢弃Alpha（选择保存成jpeg）, 要么保存为.png文件，

            # target.save(folder_path + '/' + str(page) + '-' + str(index) + ".png", quality=95)
            target = target.convert('RGB')
            target.save(folder_path + '/' + str(page) + '-' + str(index) + ".jpeg", 'jpeg', quality=100)
            # 原图也保存一下，备用
            with open(folder_path + '/' + str(page) + '-' + str(index) + "-o.jpeg", 'wb') as f:
                f.write(res.content)
            print("——————page" + str(page) + "下第" + index + "个" + "蛋啦——————")


# 主题：下载什么样的主题
theme = 'love'
# 场景：用在什么图文情景
scenario = 'money'
# 文件夹
folder_path = "./pexels/" + scenario + "/" + theme
for page in range(3, 100):
    print(page)
    html = get_html("https://www.pexels.com/search/" + theme + "?page=" + str(page))
    get_img(html, folder_path, page, scenario)


