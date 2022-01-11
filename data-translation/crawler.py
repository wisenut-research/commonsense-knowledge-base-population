import time
import clipboard
import random as rd
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def set_options(headless=True):
    window_sizes = [(1280, 1024), (1600, 1200), (1920, 1440), (1920, 1080), (2560, 1600), (3840, 2400)]
    options = webdriver.ChromeOptions()
    mobile_emulation = {"deviceName": "Nexus 5"}
    # options.add_experimental_option("mobileEmulation", mobile_emulation)
    if headless:
        options.add_argument('headless')  # 웹을 보이지 않게 실행(headless)
    options.add_argument('window-size={}x{}'.format(*window_sizes[rd.randint(0, len(window_sizes) - 1)]))  # 창 크기 설정
    options.add_argument("disable-gpu")  # gpu설정
    options.add_argument("lang=ko_KR")  # 언어 설정
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return options


class BasicCrawler(object):
    def __init__(self, engine='chromedriver', headless=True):
        self.driver = webdriver.Chrome(engine, options=set_options(headless=headless))

    def get_page(self, url):
        self.driver.get(url)
        self.driver.implicitly_wait(10)

    def page_down(self):
        ActionChains(self.driver).send_keys(Keys.END).perform()
        self.driver.implicitly_wait(10)

    def press_enter(self):
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        self.driver.implicitly_wait(10)

    def close(self):
        self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()


class GoogleTranslator(BasicCrawler):
    def translate(self, text):
        self.get_page(f'https://www.google.com/search?q=%EA%B5%AC%EA%B8%80+%EB%B2%88%EC%97%AD&oq=%EA%B5%AC%EA%B8%80+%EB%B2%88%EC%97%AD&aqs=chrome.0.69i59j0i131i433i512j0i512l8.1472j0j9&sourceid=chrome&ie=UTF-8')
        textarea = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'textarea')))
        textarea.send_keys(text)
        ActionChains(self.driver).send_keys(text).perform()
        element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[class="tw-menu-btn-image z1asCe wm4nBd"]')))
        element.click()
        return clipboard.paste()