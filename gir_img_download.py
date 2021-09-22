import gc
import re
from typing import Union
import requests
import asyncio
import httpx
from lxml import etree

from base import BaseCrawl


def setup_download_dir():
    import os
    basedir = os.path.abspath(os.path.dirname(__file__)) + "/downloader/"
    os.makedirs(basedir, exist_ok=True)
    return basedir


class GirlImg(BaseCrawl):
    __now_page: int = 1

    __headers: dict[str, str] = {
        # setting ua
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/92.0.4515.159 Safari/537.36"
    }

    __client = httpx.AsyncClient()

    def get_page_url(self) -> str:
        if self.__now_page == 1:
            return "http://m.quantuwang1.com/meinv/taotu/index.html"
        else:
            return "http://m.quantuwang1.com/meinv/taotu/index_{}.html".format(self.__now_page)

    def request(self, url: str) -> requests.Response:
        response: requests.Response = requests.get(url=url, headers=self.__headers)
        response.encoding = "utf-8"
        gc.collect()
        return response

    def parse_response(self, response: requests.Response) -> list[dict[str, Union[str, dict[str, str]]]]:
        tree: etree.ElementBase = etree.HTML(response.text)
        # 可能不是list，这个标注类型只是为了代码补全
        elements: list[etree.ElementBase] = tree.xpath("//div[@class='index_middle_c']//li")

        result: list[dict[str, Union[str, dict[str, str]]]] = []
        for element in elements:
            append_dict: dict[str, str] = {}
            title: str = element.xpath(".//img//@alt")[0]
            target_url: str = element.xpath(".//a//@href")[0]
            append_dict["title"] = title
            print("title:{}".format(title))
            append_dict["target_url"] = "http://m.quantuwang1.com" + target_url
            result.append(append_dict)

        tree.clear()
        gc.collect()
        return result

    async def save_parse_result(self, result: dict[str, Union[str, dict[str, str]]]):
        async def download_img(page: str, url: str):
            img_name = result["title"] + "_" + page + ".jpg"
            download_dir = setup_download_dir()

            img_name = re.sub(r"[\/\\\:\*\?\"\<\>\|]", "_", img_name)  # 替换为下划线
            async with self.__client.stream(method='GET', timeout=1000000, url=url, headers=self.__headers) as response:
                response: httpx.Response = response
                with open(download_dir + "/" + img_name, "wb+") as stream:
                    async for chunk in response.aiter_bytes(1024):
                        if chunk:
                            stream.write(chunk)

        gc.collect()
        self.print_message("开始下载图片链接:{}".format(result["title"]))

        tasks = [download_img(page, url) for page, url in result["img_urls"].items()]

        async_task_num = 6
        size = len(tasks)
        for i in range(0, size, async_task_num):
            print("download:title {0} slice {1}/{2} start".format(result["title"], i, min(size, i + async_task_num)))
            await asyncio.wait(tasks[i:i + async_task_num])
            print("download:title {0} slice {1}/{2} ok".format(result["title"], i, min(size, i + async_task_num)))

        self.print_message("图片链接下载结束:{}".format(result["title"]))
        result.clear()

    def async_crawl_img_url(self, result: list[dict[str, Union[str, dict[str, str]]]]) -> None:

        async def get_img(url: str, data: dict[str, str], deep: int = 0) -> None:
            gc.collect()
            try:
                response = await self.__client.get(url=url, timeout=200, headers=self.__headers)
                response.encoding = "utf-8"
                tree: etree.ElementBase = etree.HTML(response.text)
                now_page: str = tree.xpath("//div[@class=\"index_c_page\"]//span//text()")[0]
                img_url: str = tree.xpath("//div[@class=\"index_c_img\"]//img//@src")[0]
                data[now_page] = img_url
                tree.clear()
                await response.aclose()
            except Exception:
                print('error,now deep:{}'.format(deep))
                if deep > 3:
                    print("max deep stop")
                else:
                    await get_img(url, data, deep + 1)

        async def async_crawl_img(data: dict[str, Union[str, dict[str, str]]]) -> None:
            gc.collect()
            self.print_message("开始爬取图片链接:{}".format(data["title"]))

            data["img_urls"]: dict[str, str] = {}

            all_pages: list[str] = [data["target_url"]]

            crawl_tasks = []

            response = await self.__client.get(url=data["target_url"], headers=self.__headers)
            response.encoding = "utf-8"
            tree: etree.ElementBase = etree.HTML(response.text)

            all_pages_elements: list[str] = tree.xpath("//div[@class=\"index_c_page\"]//a//@href")

            for url in all_pages_elements:
                all_pages.append("http://m.quantuwang1.com" + url)

            for url in all_pages:
                crawl_tasks.append(get_img(url, data["img_urls"]))

            async_num = 12
            size = len(crawl_tasks)
            for i in range(0, size, async_num):
                print("crawl:title {0} slice {1}/{2} start".format(data["title"], i, min(size, i + async_num)))
                await asyncio.wait(crawl_tasks[i:i + async_num], timeout=None)
                print("crawl:title {0} slice {1}/{2} ok".format(data["title"], i, min(size, i + async_num)))
            self.print_message("图片链接爬取结束:{}".format(data["title"]))
            tree.clear()
            await response.aclose()

        loop = asyncio.get_event_loop()

        async_task_num = 5

        for num in range(0, len(result), async_task_num):
            gc.collect()
            target_task = result[num:num + async_task_num]
            loop.run_until_complete(asyncio.wait([async_crawl_img(item) for item in target_task]))
            loop.run_until_complete(asyncio.wait([self.save_parse_result(item) for item in target_task]))
            map(lambda tmp: tmp.clear(), target_task)

    def run(self):

        target_page = 2

        while self.__now_page < target_page:
            self.print_message('开始爬取，当前爬取的是第{}页'.format(self.__now_page))
            response = self.request(self.get_page_url())
            self.print_message('已经获取到请求结果')
            result: list[dict[str, Union[str, dict[str, str]]]] = self.parse_response(response)
            self.print_message("已经爬取第{}页的基本信息，即将开始并发爬取".format(self.__now_page))
            response.close()
            self.async_crawl_img_url(result)
            gc.collect()
            self.print_message("第{}页爬取完成".format(self.__now_page))
            result.clear()
            gc.collect()
            asyncio.run(self.__client.aclose())
            self.__now_page += 1
