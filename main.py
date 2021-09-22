# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import threading

import requests

import gir_img_download
import wallpaper

from base import BaseCrawl


def main():
    crawl: BaseCrawl = gir_img_download.GirlImg()
    crawl.run()



if __name__ == '__main__':
    main()
