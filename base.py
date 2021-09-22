import typing
from abc import ABC, abstractmethod
import requests


class BaseCrawl(ABC):

    def print_message(self, message: any):
        print(message.center(100, "-"))

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def request(self, url: str) -> requests.Response:
        pass

    @abstractmethod
    def save_parse_result(self, result):
        pass

    @abstractmethod
    def parse_response(self, response: requests.Response) -> typing.Any:
        pass
