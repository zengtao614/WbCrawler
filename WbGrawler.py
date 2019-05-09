"""

"""

import requests
import logging
import threadpool

class WbGrawler():
    def __init__(self,start=1,end=500):
        """
        参数的初始化
        :return:
        """
        self.baseurl = "https://m.weibo.cn/api/container/getIndex?containerid=2304131792328230&"
        self.headers = {
            "Host": "m.weibo.cn",
            "Referer": "https://m.weibo.cn/p/2304131792328230",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
            "X-Requested-with": "XMLHttpRequest"
        }
        self.start_pages = start
        self.end_pages = end
        # 图片保存位置
        self.path = "D:/weibosrc/"
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def getPageJson(self, page):
        """
        获取单个页面的json数据
        :param page:传入的page参数
        :return:返回页面响应的json数据
        """
        url = self.baseurl + "page=%d" % page
        try:
            response = requests.get(url, self.headers)
            if response.status_code == 200:
                return response.json()
        except requests.ConnectionError as e:
            print("error")
            self.logger.error("error",e.args)

    def parserJson(self, json):
        """
        解析json数据得到目标数据
        :param json: 传入的json数据
        :return: 返回目标数据
        """
        items = json.get("data").get("cards")
        for item in items:
            pics = item.get("mblog").get("pics")
            picList = []
            # 有些微博没有配图，所以需要加一个判断，方便后面遍历不会出错
            if pics is not None:
                for pic in pics:
                    pic_dict = {}
                    pic_dict["pid"] = pic.get("pid")
                    pic_dict["url"] = pic.get("large").get("url")
                    picList.append(pic_dict)
            yield picList

    def imgDownload(self,results):
        """
        下载图片
        :param results:
        :return:
        """
        for result in results:
            for img_dict in result:
                img_name = img_dict.get("pid") + ".jpg"
                try:
                    img_data = requests.get(img_dict.get("url")).content
                    with open(self.path+img_name,"wb") as file:
                        file.write(img_data)
                        file.close()
                        print(img_name+"\tdownload successed!")
                except Exception as e:
                    self.logger.error(img_name+"\tdownload failed!",e.args)

    def startCrawler(self,page):
        page_json = self.getPageJson(page)
        results = self.parserJson(page_json)
        self.imgDownload(results)


if __name__ == '__main__':
    wg = WbGrawler(100,200)
    pool = threadpool.ThreadPool(10)
    reqs = threadpool.makeRequests(wg.startCrawler,range(wg.start_pages,wg.end_pages))
    [pool.putRequest(req) for req in reqs]
    pool.wait()
