import datetime
import logging
import os
import random
import time
from dotenv import load_dotenv

load_dotenv('input.txt')

import requests
from selenium.webdriver import ActionChains, Keys
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
import re
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service


def get_browser() -> webdriver:
    options = Options()
    options.page_load_strategy = 'eager'
    options.add_argument("--no-sandbox")
    options.add_argument("window-size=1200,1000")
    options.add_argument('--headless')
    options.add_argument("--disable-blink-features=AutomationControlled")
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0'
    options.add_argument(f'user-agent={user_agent}')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    s = Service(executable_path="chromedriver")
    driver = webdriver.Chrome(service=s, options=options)
    driver.set_page_load_timeout(20)
    return driver

def get_page(text, target, region):
    try:
        count = 0
        result_pos = 0
        for page in range(10):
            with get_browser() as browser:
                url = f'https://yandex.ru/search/?text={text}&lr=237&rstr={region}&p={page}'
                print(url)
                browser.get(url)
                xpath = '//li[@data-fast="1"]'
                # browser.save_screenshot(f'scr.png')
                try:
                    WebDriverWait(browser, 5).until(expected_conditions.visibility_of_element_located((By.XPATH, xpath)))
                except TimeoutException:
                    # browser.save_screenshot(f'scr_capcha.png')
                    print('Капча')
                    capthca_patch = '//input[@class="CheckboxCaptcha-Button"]'
                    capthcha = browser.find_element(By.XPATH, capthca_patch)
                    print('Нашлась капча', capthcha)
                    browser.save_screenshot('scr_capcha.png')
                    actions = ActionChains(browser).move_to_element(capthcha).click().perform()
                try:
                    WebDriverWait(browser, 5).until(expected_conditions.visibility_of_element_located((By.XPATH, xpath)))
                except TimeoutException:
                    print('Чет не получилось')
                page_html = browser.page_source
                with open(f'pages/{page}_{text}.html', 'w', encoding='UTF_8') as file:
                    file.write(str(page_html))

                results_li = browser.find_elements(By.XPATH, xpath)

                for li in results_li:
                    count += 1
                    is_him = target in li.text
                    if is_him:
                        result_pos = count + 1
                        print(count + 1)
                        print(li.text[:50])
                        return (result_pos, page)

                time.sleep(random.random())
        return (result_pos, page)
    except Exception:
        print('-------------------------ОШИБКА-------------------\n')
        page = browser.page_source
        with open('error.html', 'w', encoding='UTF_8') as file:
            file.write(page)
        return 'Error', 'Error'


if __name__ == '__main__':
    import chromedriver_autoinstaller
    target = os.getenv('TARGET')
    texts = os.getenv('TEXT').split(',')
    region =  os.getenv('REGION')
    print(texts)
    delta = datetime.timedelta(hours=7)
    tz = datetime.timezone(delta)
    dt = datetime.datetime.now(tz=tz)
    with open('result.txt', 'a', encoding='UTF-8') as file:
        file.writelines(f'\n{str(dt)[:-7]}\n')
    for text in texts:
        print(f'\n---------------Новый поиск:{text} ----------- \n')
        result = 'Error'
        page = 'Error'
        while result == 'Error' or page == 'Error':
            try:
                result, page = get_page(text, target, region)
                print(text, result)
            except Exception as err:
                print('Ошибка при парсинше')
                print(err)
        with open('result.txt', 'a', encoding='UTF-8') as file2:
            file2.writelines(f'{target} {text}: {result or "-"}. Просмотрено страрниц: {page + 1}\n')
        print(f'-----------------Поиск {text} закончен--------')
