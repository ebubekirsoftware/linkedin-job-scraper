from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import os

# LinkedIn giriş bilgileri
LINKEDIN_USERNAME = os.getenv('LINKEDIN_USERNAME')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

# Gönderilerin kontrol edildiği URL
SEARCH_URL = "https://www.linkedin.com/search/results/content/?keywords=%23hiring%20junior%20data%20scientist"

# İş arama kelimeleri listesi
job_keywords = ["Data Scientist", "Machine Learning", "Artificial Intelligence"]

# E-posta ayarları
SMTP_SERVER = 'smtp.yourserver.com'
SMTP_PORT = 587
SMTP_USERNAME = 'you@example.com'
SMTP_PASSWORD = 'yourpassword'
EMAIL_TO = 'recipient@example.com'


def login_linkedin(driver):
    try:
        driver.get("https://www.linkedin.com/login")
        time.sleep(2)

        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        username_field.send_keys(LINKEDIN_USERNAME)
        password_field.send_keys(LINKEDIN_PASSWORD)

        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        time.sleep(5)
    except Exception as e:
        print(f"Hata LinkedIn girişinde: {e}")


def search_posts(driver, max_posts=10):
    try:
        driver.get(SEARCH_URL)
        time.sleep(5)

        posts = driver.find_elements(By.CLASS_NAME, 'search-result__info')
        links = []
        count = 0
        for post in posts:
            try:
                link = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
                if is_valid_link(link):
                    links.append(link)
                    count += 1
                    if count >= max_posts:
                        break
            except Exception as e:
                print(f"Hata link alma sırasında: {e}")
                continue
        return links
    except Exception as e:
        print(f"Hata arama sayfasında: {e}")
        return []




def is_valid_link(link):
    return "linkedin.com/jobs" in link


def contains_keywords(driver, link, keywords):
    try:
        driver.get(link)
        time.sleep(3)
        page_content = driver.page_source
        return any(keyword.lower() in page_content.lower() for keyword in keywords)
    except Exception as e:
        print(f"Hata sayfa içeriğini kontrol ederken: {e}")
        return False


def get_valid_job_links(driver, links, keywords):
    job_links = []
    for link in links:
        try:
            if is_valid_link(link):
                if contains_keywords(driver, link, keywords):
                    job_links.append(link)
        except Exception as e:
            print(f"Hata link filtreleme sırasında: {e}")
    return job_links


def send_email(links):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = EMAIL_TO
        msg['Subject'] = "New LinkedIn Job Postings"

        body = "\n".join(links)
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, EMAIL_TO, text)
        server.quit()
    except Exception as e:
        print(f"Hata e-posta gönderirken: {e}")



def main():
    try:
        driver = webdriver.Chrome()
        login_linkedin(driver)
        links = search_posts(driver, max_posts=10)
        links
        job_links = get_valid_job_links(driver, links, job_keywords)
        if job_links:
            send_email(job_links)
    except Exception as e:
        print(f"Ana işlevde hata oluştu: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    # Manuel çalıştırma
    main()
