from selenium import webdriver
import spiderTools
import requests
import re
from lxml import etree


class HongShuwang(object):
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'Remote Address': '183.232.215.122:443',
            'Referrer Policy': 'no-referrer-when-downgrade',
            'User-Agent':spiderTools.getAgent()
        }
    def get_html(self,url):
        options = webdriver.ChromeOptions()
        options.set_headless()
        # 创建浏览器对象
        driver = webdriver.Chrome(options=options)
        print('正在获取网页源代码...')
        driver.get(url)
        beffor_array = driver.execute_script('return words;')
        print(len(beffor_array))
        html = driver.page_source
        for context_kw_index in range(len(beffor_array)):
            html,n = re.subn('<span class="context_kw{0}"></span>'.format(context_kw_index),beffor_array[context_kw_index],html )
            print('本次共替换了：{0}处文本，内容为：{1}，'.format(n,beffor_array[context_kw_index]))
        return html


    def get_content(self,url):
        html = self.get_html(url)
        content = etree.HTML(html)
        text = ""
        for p in content.xpath('//div[@class="rdtext"]//text()'):
            text+= p
        return text
''



if __name__ == '__main__':
    hong_shu = HongShuwang()
    # text = hong_shu.get_content('https://g.hongshu.com/content/93416/13877912.html')
    # text = hong_shu.get_content('https://g.hongshu.com/content/93416/13903039.html')
    text = hong_shu.get_content('https://g.hongshu.com/content/93416/13910518.html')
    print('小说内容为：',text)
