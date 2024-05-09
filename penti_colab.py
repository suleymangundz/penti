

import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from openpyxl import Workbook

# WebDriver'ı başlatma
driver_path = "C:\\Users\\YPN-1067\\Documents\\PYTHONss\\ChromeDriver\\chromedriver-win64\\chromedriver.exe"
data_profile = "C:\\Users\\YPN-1067\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1\\"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("user-data-dir=" + data_profile)
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Base URL ve sayfa aralığını tanımlama
base_url = "https://www.trendyol.com/sr?q=penti&qt=penti&st=penti&os=1"
start_page = 1
end_page = 1

# Boş bir DataFrame oluşturma
data = []

# Her bir sayfa için işlem yapma
for page_number in range(start_page, end_page + 1):
    url = base_url + str(page_number)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser", from_encoding="utf-8")
    products = soup.find_all("div", attrs={"class": "p-card-wrppr with-campaign-view"})
    for product in products:
        product_links = product.find_all("div", attrs={"class": "card-border"})
        product_name = product.find("div", attrs={"class": "prdct-desc-cntnr"})
        product_name_1 = product_name.find("span", attrs={"class": "prdct-desc-cntnr-name hasRatings"})
        product_name_clear = product_name.text.strip()[:5] if product_name else None
        product_name_1_clear = product_name_1.text.strip() if product_name_1 else None
        product_price = product.find("div", attrs={"class": "prc-box-dscntd"})
        original_price = product_price.text.strip() if product_price else None
        
        for link in product_links:
            link_continue = link.find("a")
            if link_continue:
                link_continue = link_continue.get("href")
                link_all = f"https://www.trendyol.com{link_continue}"

                driver.get(link_all)
                driver.implicitly_wait(5)

                try:
                    rating_element = driver.find_element(By.CLASS_NAME, "rating-line-count")
                    rating = rating_element.text
                except NoSuchElementException:
                    rating = None

                try:
                    degerleme_element = driver.find_element(By.CLASS_NAME, 'total-review-count')
                    degerleme = degerleme_element.text
                except NoSuchElementException:
                    degerleme = None

                try:
                    favorite_element = driver.find_element(By.CLASS_NAME, 'favorite-count')
                    favorite = favorite_element.text
                except NoSuchElementException:
                    favorite = None

                try:
                    Soru_Cevap_Element = driver.find_element(By.CLASS_NAME, "answered-questions-count")
                    Soru_Cevap = Soru_Cevap_Element.text
                except NoSuchElementException:
                    Soru_Cevap = None

                # Ürün detaylarındaki bilgileri çekme
                detail = requests.get(link_all)
                detail_soup = BeautifulSoup(detail.content, "html.parser")
                supplier_info = detail_soup.find('div', class_='supplier-info')
                if supplier_info:
                    spans = supplier_info.find_all('span')  # Tüm span etiketlerini bul
                    seller_name, seller_unvan, Satici_Sehir = None, None, None
                    for span in spans:
                        if 'Satıcı:' in span.text:
                            seller_name = span.find_next('b').get_text(strip=True)
                        elif 'Satıcı Ünvanı:' in span.text:
                            seller_unvan = span.find_next('b').get_text(strip=True)
                        elif 'Şehir:' in span.text:
                            Satici_Sehir = span.find_next('b').get_text(strip=True)

                # Breadcrumb bilgilerini çekme
                breadcrumbs = detail_soup.find('div', class_='product-detail-breadcrumb').find_all('a')
                breadcrumb_data = [breadcrumb.get('title', breadcrumb.text) for breadcrumb in breadcrumbs]

                # Ürün bilgilerini products_data'ya ekleme
                products_data = {
                    "Link": link_all,
                    "Brand": product_name_clear,
                    "Product": product_name_1_clear,
                    "Original Price": original_price,
                    "Satici İsim": seller_name,
                    "satici Unvan": seller_unvan,
                    "Satici Sehir": Satici_Sehir,
                    "Rating": rating,
                    "Degerleme": degerleme,
                    "Favorite": favorite,
                    "Soru Cevap": Soru_Cevap,
                    # Breadcrumb bilgilerini ekleyin
                    **{f"Ürün Detayları {i+1}": breadcrumb_data[i] for i in range(len(breadcrumb_data))}
                }
                data.append(products_data)

# DataFrame oluşturma
df = pd.DataFrame(data)
print(df)

# CSV'ye yazma
df.to_csv('11Penti_all_data.csv', encoding="utf-8")

# %%
