from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
from selenium_stealth import stealth

import polars as pl
import time
import os

def maindriver(url):
    useragent_rotate = generate_user_agent(navigator='chrome')

    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--incognito')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disk-cache-size=0')
    options.add_argument('user-agent='+useragent_rotate)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument('--disable-notification')
    options.add_argument('--disable-geolocation')

    driver = webdriver.Chrome(
        options=options,
        service=ChromeService(ChromeDriverManager().install())
    )

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win64",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    driver.get(url)
    return driver

def run_bot(url_base, total_level=5):
    if not os.path.exists('./datasets'):
        os.makedirs('./datasets', exist_ok=True)

    if not os.path.exists('./datasets/skipped.json'):
        with open('./datasets/skipped.json', 'w') as file_path:
            pass

    url_driver = url_base.format(level=1, i=1)

    for x in range(0, 15):
        str_error = None
        try:
            driver = maindriver(url_driver)
        except Exception as e:
            str_error = e
            pass

        if str_error:
            print('Connecting Bot Fail, Try again....')
            time.sleep(2)
        else:
            break

    time.sleep(2.5)
    driver.refresh()
    time.sleep(2)
    print('Bot Connected')

    skipped_page_dict = {}

    for level in range(1, total_level+1):
        if driver.current_url != url_base.format(level=level, i=1):
            driver.get(url_base.format(level=level, i=1))
            time.sleep(0.5)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"#full-page > section.table-body > div > nav > ul.pagination.pagination-desktop > li:nth-last-child(2)"))
        )
        total_page = driver.find_element(By.CSS_SELECTOR, f"#full-page > section.table-body > div > nav > ul.pagination.pagination-desktop > li:nth-last-child(2)").text
        total_page = int(total_page)
        print(f"Total Page for Risk Level {level}: {total_page}")

        schema_column = {
            'title': pl.String,
            'link': pl.String,
        }
        df_risk_level = pl.DataFrame(schema=schema_column)
        list_skipped_page = []

        for page in range(1, total_page+1):
            for _ in range(10):
                if driver.current_url == url_base.format(level=level, i=page):
                    time.sleep(0.5)
                    break
                else:
                    driver.get(url_base.format(level=level, i=page))
                    time.sleep(0.5)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f"#full-page > section.table-body > div.container"))
                )
            except TimeoutException as e:
                list_skipped_page.append(page)
                continue

            page_dict = {
                'title': [],
                'link': [],
            }

            articles = driver.find_elements(By.CSS_SELECTOR, f"#full-page > section.table-body > div > div.row")
            for article in articles:
                page_dict['title'].append(article.find_element(By.CSS_SELECTOR, f"div.col-lg > b").text)
                link = article.get_attribute('onclick')
                link = "www.fortiguard.com" + link.split()[-1][1:-1]
                page_dict['link'].append(link)
            time.sleep(0.25)

            df_page = pl.from_dict(page_dict)
            df_risk_level = df_risk_level.vstack(df_page)

        df_risk_level.write_csv(f'./datasets/forti_lists_{level}.csv')
        skipped_page_dict[level] = tuple(list_skipped_page)

        print(f"Total data gathered: {df_risk_level.n_unique()}")
        print(f"List of skipped page: {tuple(list_skipped_page)}")
        time.sleep(0.5)

if __name__ == "__main__":
    url_base = "https://www.fortiguard.com/encyclopedia?type=ips&risk={level:n}&page={i:n}"
    run_bot(url_base)
