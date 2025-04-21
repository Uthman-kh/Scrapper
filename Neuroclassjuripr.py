import os
import csv
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

# Supprimer les logs TensorFlow Lite
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

URL = "https://juriscassation.cspj.ma/ArretAppels/SearchArretAppel"
OUTPUT_CSV = "resultats_table.csv"


def wait_for_table(driver):
    wait = WebDriverWait(driver, 30)
    table_xpath = '/html/body/div[2]/div[2]/div/section/div/div/div[2]/div/table'
    wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
    table = driver.find_element(By.XPATH, table_xpath)
    wait.until(lambda d: len(table.find_elements(By.CSS_SELECTOR, 'tbody tr')) > 0)
    return table


def extract_table_data(table):
    # Extrait en-têtes et lignes
    headers = [th.text.strip() for th in table.find_elements(By.CSS_SELECTOR, 'thead th')]
    rows = []
    for tr in table.find_elements(By.CSS_SELECTOR, 'tbody tr'):
        cells = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, 'td')]
        if cells:
            rows.append(cells)
    return headers, rows


def fetch_all_pages(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 30)

    # Étape 1 : Filtre initial (optionnel)
    try:
        btn_xpath = '/html/body/div[2]/div[1]/section/div/div[2]/div[2]/form/div[4]/div[1]/div/button[1]'
        btn = driver.find_element(By.XPATH, btn_xpath)
        driver.execute_script("arguments[0].click();", btn)
        print("✅ Filtre initial cliqué.")
    except Exception:
        print("⚠️ Filtre initial non cliqué (optionnel).")

    # Étape 2 : Clic sur "بحث"
    try:
        search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'بحث')]") ))
        driver.execute_script("arguments[0].click();", search_btn)
        print("✅ Bouton 'بحث' cliqué.")
    except Exception:
        raise RuntimeError("❌ Impossible de cliquer sur 'بحث'.")

    # Scraper page 1
    print("📄 Scraping page 1...")
    table = wait_for_table(driver)
    headers, all_rows = extract_table_data(table)

    # Pagination par clic sur la flèche "suivant"
    page = 2
    while True:
        try:
            # Trouver le bouton '>' de pagination
            next_btn = driver.find_element(By.CSS_SELECTOR, 'li.PagedList-skipToNext a[rel="next"]')
            driver.execute_script("arguments[0].click();", next_btn)
            print(f"➡️ Passage à la page {page}...")
            time.sleep(1)  # pause pour l'AJAX
            # Gérer stale elements
            try:
                table = wait_for_table(driver)
            except StaleElementReferenceException:
                time.sleep(1)
                table = wait_for_table(driver)
            _, rows = extract_table_data(table)
            all_rows.extend(rows)
            page += 1
        except NoSuchElementException:
            print("✅ Toutes les pages ont été scrappées.")
            break

    return headers, all_rows


def write_csv(filename, headers, rows):
    with open(filename, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


if __name__ == '__main__':
    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()

    try:
        headers, rows = fetch_all_pages(driver, URL)
        if not rows:
            raise ValueError("❌ Aucune donnée récupérée.")
        write_csv(OUTPUT_CSV, headers, rows)
        print(f"✅ {len(rows)} lignes enregistrées dans '{OUTPUT_CSV}'")
    except Exception:
        traceback.print_exc()
    finally:
        driver.quit()
