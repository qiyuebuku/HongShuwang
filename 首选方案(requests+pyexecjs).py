"""
使用方法
    1. 如果在抓取过程中出现问题，请使用备用方案
    2. 首选方案依赖node环境，所以需要进行安装，安装好后在项目所在目录执行：
                npm i jsdom
"""



import re

import requests
from lxml import etree
import execjs

import spiderTools



class HongShuwang(object):
    def __init__(self):
        self.headers = {
            'User-Agent': spiderTools.getAgent()
        }

    def get_html(self, url):
        """
        :功能 获取小说页的html，并将用伪元素替代的文字补全
        :param url: 需要抓取的网页url
        :return: 完整的html页面
        """
        html = requests.get(url,headers=self.headers).text

        # 由于提取出的js代码中含有对Dom树的操作，
        # 而在execjs中是不支持这些的(好像只有浏览器才支持。。)
        # 最终这里使用了node.js提供的一个解决方案jsdom来解决这个问题
        crypto_js = """ 
                            const jsdom = requir  e("jsdom");
                            const { JSDOM } = jsdom;
                            const dom = new JSDOM(`<!DOCTYPE html><p>Hello world</p>`);
                            window = dom.window;
                            document = window.document;
                            XMLHttpRequest = window.XMLHttpRequest;
                            function start(){
                        """
        # 匹配出所有关于解密的js代码
        crypto_js += re.search(r"(var CryptoJS=CryptoJS[\s\S]*;}})</script>[\s\S]*<!--内容结束-->", html).group(1)
        # 剔除无关的代码
        # crypto_js, n = re.subn(r"var words=new Array\S+\);", "", crypto_js)
        # crypto_js, n = re.subn(r"var n=document\[_\S+,!!\[\]\);", "", crypto_js)
        # crypto_js, n = re.subn(r"var n=document\['createElement'\]\S+!!\[\]\);", "", crypto_js)
        # crypto_js, n = re.subn(r'var _\S+=document.+return null;}', '', crypto_js)
        # crypto_js, n = re.subn(r"else{document\[_.+\(n\);}", "", crypto_js)
        # crypto_js, n = re.subn(r"typeof document===_\S{6}\('\S{4}'\)", "false", crypto_js)
        # crypto_js,n = re.subn(r"document\S+'\\x22'\);","我被替换了4",crypto_js)
        # crypto_js,n = re.subn(r"document\['styleSheets'","我被替换了5",crypto_js)
        # crypto_js, n = re.subn(r"break;}}.*", "break;}} return words;}start();", crypto_js)
        crypto_js += "return words;}"
        # 编译js代码
        ctx = execjs.compile(crypto_js)
        # 获取解密好的字符数组
        beffor_array = [" ", " "] + ctx.call('start')
        # print(len(beffor_array), beffor_array)
        # 将解密出来的字符还原到html文档中
        for context_kw_index in range(len(beffor_array)):
            html, n = re.subn('<span class="context_kw{0}"></span>'.format(context_kw_index),
                              beffor_array[context_kw_index], html)
            print('本次共替换了：{0}处文本，内容为：{1}，'.format(n, beffor_array[context_kw_index]))
        return html


    def get_content(self, url):
        """
        :param url: 需要抓取小说的url
        :return: 小说内容
        """
        html = self.get_html(url)
        text = etree.HTML(html)
        with open('网页.html','w',encoding='utf-8') as f:
            f.write(html)
        content = ""
        for p in text.xpath('//div[@class="rdtext"]//text()'):
            content += p
        return content


if __name__ == '__main__':
    hong_shu = HongShuwang()
    content = hong_shu.get_content('https://g.hongshu.com/content/93416/13877912.html')
    # content = hong_shu.get_content('https://g.hongshu.com/content/93416/13899610.html')
    # content = hong_shu.get_content('https://g.hongshu.com/content/93416/13903039.html')
    with open('小说.txt','w',encoding='utf-8') as f:
        f.write(content)
    print('长度为：',len(content))
    # print(content)

    """
GET https://g.hongshu.com/content/93416/13877912.html HTTP/1.1
Host: g.hongshu.com
Connection: keep-alive
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Language: zh-CN,zh;q=0.9
Cookie: bookfav=%7B%22b97544%22%3A0%2C%22b93416%22%3A0%7D; pgv_pvi=8507540480; pgv_si=s1109681152; yqksid=6cekngmck3mals4duekb2fd2s4
Accept-Encoding: gzip, deflate, br



    """
