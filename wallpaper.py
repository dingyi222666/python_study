import json
import random
import time
import typing
from abc import ABC, abstractmethod
import requests
import asyncio
import http3
from lxml import etree

from base import BaseCrawl


def setup_download_dir():
    import os
    basedir = os.path.abspath(os.path.dirname(__file__)) + "/downloader/"
    os.makedirs(basedir, exist_ok=True)
    return basedir


class WallpaperCrawl(BaseCrawl, ABC):
    __page: int = 1
    __format_url: str = "https://wallpaperscraft.com/catalog/anime/page{0}"
    __domain = "https://wallpaperscraft.com"
    __headers: dict[str, str] = {
        # setting ua
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/92.0.4515.159 Safari/537.36 "
    }

    __client = http3.AsyncClient()

    def run(self):
        target_page: int = 5

        while self.__page < target_page:
            print("开始爬取第{0}页".format(self.__page).center(60, "-"))
            response = self.request(self.build_url_form_page())
            print("已经获得请求结果 ", {'code': response.status_code})
            result_dict = self.parse_response(response)
            print("基础爬取结束 开始二次爬取图片地址".center(60, "-"))
            result_dict = self.get_image_url(result_dict)
            print("本页爬取结束 正在下载本页壁纸".center(60, "-"))
            response.close()  # close response
            self.save_parse_result(result_dict)
            self.__page += 1
            print("本页壁纸下载结束，正在下载第{}页".format(self.__page).center(60,"-"))
            random_num = random.randint(0, 10)
            print("随机休眠{}秒".format(random_num).center(60,"-"))
            time.sleep(random_num)  # random sleep 10-100

        asyncio.run(self.close_client()) # 关闭池

    async def close_client(self):
        asyncio.get_event_loop().close()
        await self.__client.close()

    def save_parse_result(self, result: list[dict[str, str]]):
        download_dir = setup_download_dir()

        download_count = 0

        async def downloader(data: dict[str, str]):
            nonlocal download_count

            download_count += 1
            download_url = data['img_url']
            download_name = data['keywords'] + ("_{0}_{1}.jpg".format(self.__page, download_count))

            response = await self.__client.get(url=download_url, verify=False, stream=True, timeout=1000 * 30)

            with open(download_dir + "/" + download_name, "wb+") as stream:
                async for chunk in response.stream():
                    if chunk:
                        stream.write(chunk)

            print('下载完成:{}'.format(download_name).center(60, "-"))
            await response.close()

        download_task = []

        for element in result:
            download_task.append(downloader(element))

        loop = asyncio.get_event_loop()

        loop.run_until_complete(asyncio.wait(download_task))


    def parse_response(self, response: requests.Response) -> list[dict[str, str]]:
        content: str = response.text
        tree: etree.ElementBase = etree.HTML(content)

        li_list: list[etree.ElementBase] = tree.xpath("//ul[@class='wallpapers__list ']/li")

        result = []

        for element in li_list:
            result.append({
                'img_url': self.__domain + element.xpath("./a/@href")[0],
                'keywords': element.xpath("./a/span[3]/text()")[0],
                'score': element.xpath(".//span[@class='wallpapers__info-rating']/text()")[1][1:-8],
                "download_count": element.xpath(".//span[@class='wallpapers__info-downloads']/text()")[1][1:-3]
            })

        print(json.dumps(result, indent=4, ensure_ascii=False))

        return result

    def get_image_url(self, data: list[dict[str, str]]):

        async def request_and_parse_image_url(index: int):
            element = data[index]

            response = await self.__client.get(url=element["img_url"], timeout=1000 * 120)
            content: str = response.text
            tree: etree.ElementBase = etree.HTML(content)
            original_size: list = tree.xpath(
                "//div[@class='wallpaper-info']//span[@class='wallpaper-table__cell']//a/text()")

            if len(original_size) == 0:
                original_size.insert(0, "1280x720")

            original_size = original_size[0]

            element["img_url"] = "https://images.wallpaperscraft.com/image/single/{0}_{1}.jpg".format(
                element['img_url'][element['img_url'].rfind('/') + 1:],
                original_size)
            await response.close()
            print(json.dumps(element, indent=4, ensure_ascii=False))

        tasks = []
        for key, value in enumerate(data):
            tasks.append(request_and_parse_image_url(key))

        loop = asyncio.get_event_loop()

        loop.run_until_complete(asyncio.wait(tasks))
        return data

    # time.sleep(random.randint(1, 5))
    def request(self, url: str) -> requests.Response:
        return requests.get(url=url, headers=self.__headers)

    def build_url_form_page(self) -> str:
        return self.__format_url.format(self.__page)

