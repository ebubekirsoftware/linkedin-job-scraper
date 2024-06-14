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
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")

    username_field.send_keys(LINKEDIN_USERNAME)
    password_field.send_keys(LINKEDIN_PASSWORD)

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click()
    time.sleep(5)


def search_posts(driver):
    driver.get(SEARCH_URL)
    time.sleep(5)

    posts = driver.find_elements(By.CLASS_NAME, 'search-result__info')
    links = []
    for post in posts:
        try:
            link = post.find_element(By.TAG_NAME, 'a').get_attribute('href')
            links.append(link)
        except Exception as e:
            print(e)
    return links


def is_valid_link(link):
    return "linkedin.com/jobs" in link

def contains_keywords(driver, link, keywords):
    driver.get(link)
    time.sleep(3)
    page_content = driver.page_source
    return any(keyword.lower() in page_content.lower() for keyword in keywords)

def filter_links(driver, links, keywords):
    job_links = []
    for link in links:
        if is_valid_link(link):
            if contains_keywords(driver, link, keywords):
                job_links.append(link)
    return job_links


def send_email(links):
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


def main():
    driver = webdriver.Chrome()
    login_linkedin(driver)
    links = search_posts(driver)
    job_links = filter_links(driver, links, job_keywords)
    if job_links:
        send_email(job_links)
    driver.quit()

if __name__ == "__main__":
    # Manuel çalıştırma
    main()

    # Schedule job
    schedule.every().day.at("15:00").do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
