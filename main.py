import database
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from msedge.selenium_tools import EdgeOptions
import cv2
import pytesseract
from datetime import datetime
from errorCode import errorCodes
import threading


class Scraper:
    def __init__(self):
        self.LICENSE_NUMBER = 'MH14DT2661'
        self.TESS_PATH = 'D:\Software\Programming\Teserract_OCR\\tesseract.exe'
        self.TESS_CONFIG = "-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ --psm 8"
        self.DRIVER_PATH = "D:\Software\Programming\Edge Webdriver\msedgedriver.exe"
        self.WEBSITE = "https://vahan.nic.in/nrservices/faces/user/citizen/citizenlogin.xhtml"
        self.LOGIN_ID = "9403675041"
        self.PASSWORD = "Shashikant1@"

        isStop = False

        options = EdgeOptions()
        # options.use_chromium = True
        options.add_argument("--headless")
        options.add_argument("disable-gpu")
        options.add_argument("--window-size=1920,1200")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(executable_path=self.DRIVER_PATH, options=options)
        pytesseract.pytesseract.tesseract_cmd = self.TESS_PATH

        while not isStop:
            try:
                self.login()
                self.driver.find_element_by_name("regn_no1_exact").click()
                self.send_discrete_keys(name="regn_no1_exact", str=self.LICENSE_NUMBER)
                self.captchaSolve()
                while True:
                    try:
                        vehicle, address, regDate, insDate, pucDate = self.finalScrape()
                        self.saveInDb(self.LICENSE_NUMBER, vehicle, address, regDate.strip(' '), insDate.strip(' '),
                                      pucDate.strip(' '))
                        break
                    except:
                        wait = WebDriverWait(self.driver, 10)
                        print('waiting')
                        wait.until(EC.element_to_be_clickable((By.NAME, "vahancaptcha:btn_Captchaid")))
                        self.driver.find_element_by_name("vahancaptcha:btn_Captchaid").send_keys(Keys.ENTER)
                        wait.until(EC.element_to_be_clickable((By.NAME, "vahancaptcha:btn_Captchaid")))
                        print('refreshed')
                        self.captchaSolve()
                isStop = True
            except:
                isStop = False

    def login(self):
        self.driver.get(self.WEBSITE)
        self.driver.find_element_by_name("TfMOBILENO").click()
        self.send_discrete_keys(name="TfMOBILENO", str=self.LOGIN_ID)
        self.driver.find_element_by_name("btRtoLogin").click()

        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "tfPASSWORD")))

        self.send_discrete_keys(name="tfPASSWORD", str=self.PASSWORD)
        self.driver.find_element_by_name("btRtoLogin").click()

    def captchaSolve(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "vahancaptcha:ref_captcha")))
        self.driver.find_element_by_name("regn_no1_exact").click()
        self.send_discrete_keys(name="regn_no1_exact", str=self.LICENSE_NUMBER)
        print('ss')
        self.driver.find_element_by_id("vahancaptcha:ref_captcha").screenshot("Resources\\captcha.png")

        captchaText = self.tesseract_captcha_ocr()
        print(captchaText, " ", len(captchaText))
        if len(captchaText) == 5:
            self.driver.find_element_by_id("vahancaptcha:CaptchaID").send_keys(Keys.ENTER)
            self.send_discrete_keys(name="vahancaptcha:CaptchaID", str=captchaText, byType=By.ID)
            self.driver.implicitly_wait(1)
            try:
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[normalize-space()='Vahan Search']")))
                self.driver.find_element_by_xpath("//button[normalize-space()='Vahan Search']").click()
            except:
                print('here')
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[normalize-space()='Vahan Search']")))
                self.driver.find_element_by_xpath("//button[normalize-space()='Vahan Search']").send_keys(
                    Keys.ENTER)
            print('captcha')
        else:
            self.captchaSolve()

    def finalScrape(self):
        WebDriverWait(self.driver, 3).until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id='rcDetailsPanel']/div[1]/table/tbody/tr[4]/td/div/span[1]")))

        vehicle = self.driver.find_element_by_xpath(
            "//*[@id='rcDetailsPanel']/div[1]/table/tbody/tr[4]/td/div/span[1]").text
        address = self.driver.find_element_by_xpath(
            "//*[@id='rcDetailsPanel']/div[1]/table/tbody/tr[4]/td/div/span[3]").text
        regDate = self.driver.find_element_by_css_selector(
            "#rcDetailsPanel > div:nth-child(5) > div:nth-child(2) > span").text
        insDate = self.driver.find_element_by_css_selector(
            "#rcDetailsPanel > div:nth-child(6) > div:nth-child(2) > span").text
        pucDate = self.driver.find_element_by_css_selector(
            "#rcDetailsPanel > div:nth-child(6) > div:nth-child(4) > span").text

        return vehicle, address, regDate, insDate, pucDate

    def send_discrete_keys(self, name, str, byType=By.NAME):
        for character in str:
            self.driver.find_element(byType, name).send_keys(character)

    def saveInDb(self, licenseno, vehicle, address, reg, ins, puc):
        regDT = datetime.strptime(reg.strip(' '), '%d-%b-%Y')
        insDT = datetime.strptime(ins.strip(' '), '%d-%b-%Y')
        pucDT = datetime.strptime(puc.strip(' '), '%d-%b-%Y')
        errcode = errorCodes.encode(regDT, insDT, pucDT)

        photo, plate = database.image_to_bin()

        database.insert(licenseno, vehicle, address, photo, datetime.now().strftime("%H:%M:%S | %d-%m-%Y"), errcode,
                        plate)

    def tesseract_captcha_ocr(self):
        captchaImg = cv2.imread('Resources\captcha.png')
        # captchaImg = captchaImg[4:-3, 4:-3] #43,122
        gray = cv2.cvtColor(captchaImg, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        gray = cv2.medianBlur(gray, 3)
        text = pytesseract.image_to_string(gray, lang='eng', config=self.TESS_CONFIG)
        return text[:5]


t1 = threading.Thread(target=Scraper, args=('MH14DT2662'))
t2 = threading.Thread(target=Scraper, args=('MH14DT2662'))
t3 = threading.Thread(target=Scraper, args=('MH14DT2662'))
t4 = threading.Thread(target=Scraper, args=('MH14DT2662'))
t5 = threading.Thread(target=Scraper, args=('MH14DT2662'))
t6 = threading.Thread(target=Scraper, args=('MH14DT2662'))
t7 = threading.Thread(target=Scraper, args=('MH14DT2662'))
# a = Scraper()
t1.start()
t2.start()