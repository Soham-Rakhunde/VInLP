from datetime import datetime

import cv2
import pytesseract
from msedge.selenium_tools import EdgeOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import database
from errorCode import errorCodes
from ocr1 import Rekognition


class Scraper(Rekognition):
    def __init__(self):
        Rekognition.__init__(self)

        self.TESS_PATH = 'D:\Software\Programming\Teserract_OCR\\tesseract.exe'
        self.TESS_CONFIG = "-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyz --psm 8"
        self.DRIVER_PATH = "D:\Software\Programming\Edge Webdriver\msedgedriver.exe"
        self.WEBSITE = "https://vahan.nic.in/nrservices/faces/user/citizen/citizenlogin.xhtml"
        self.LOGIN_ID = "9403675041"
        self.PASSWORD = "Shashikant1@"

        isStop = False

        options = EdgeOptions()
        options.use_chromium = True
        # options.add_argument("--headless")
        options.add_argument("disable-gpu")
        options.add_argument("--window-size=1920,1200")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--disable-browser-side-navigation')
        self.driver = webdriver.Chrome(executable_path=self.DRIVER_PATH, options=options)
        pytesseract.pytesseract.tesseract_cmd = self.TESS_PATH

        self.license_plate_parser()

        if self.is_license_format():
            while not isStop:
                try:
                    self.login()
                    self.driver.find_element_by_name("regn_no1_exact").click()
                    self.send_discrete_keys(name="regn_no1_exact", string=self.dataObj.numPlate)
                    self.captchaSolve()
                    while True:
                        try:
                            regDate, insDate, pucDate = self.finalScrape()
                            self.saveInDb(regDate.strip(' '), insDate.strip(' '), pucDate.strip(' '))
                            break
                        except Exception as e:
                            # print(1, e)
                            WebDriverWait(self.driver, 2).until(EC.presence_of_element_located(
                                (By.XPATH, "//*[@id='userMessages']/div/ul/li/span")))
                            try:
                                text = self.driver.find_element_by_xpath("//*[@id='userMessages']/div/ul/li/span").text
                                if text == 'Vehicle Detail not found':
                                    print('broke')
                                    break
                            except Exception as e:
                                print(4, 'nothibng found')
                            wait = WebDriverWait(self.driver, 10)
                            print('waiting')
                            wait.until(EC.element_to_be_clickable((By.NAME, "vahancaptcha:btn_Captchaid")))
                            self.driver.find_element_by_name("vahancaptcha:btn_Captchaid").send_keys(Keys.ENTER)
                            wait.until(EC.element_to_be_clickable((By.NAME, "vahancaptcha:btn_Captchaid")))
                            print('refreshed')
                            self.captchaSolve()
                    isStop = True
                except Exception as e:
                    # print(2, e)
                    isStop = False

    def login(self):
        self.driver.get(self.WEBSITE)
        self.driver.find_element_by_name("TfMOBILENO").click()
        self.send_discrete_keys(name="TfMOBILENO", string=self.LOGIN_ID)
        self.driver.find_element_by_name("btRtoLogin").click()

        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, "tfPASSWORD")))

        self.send_discrete_keys(name="tfPASSWORD", string=self.PASSWORD)
        self.driver.find_element_by_name("btRtoLogin").click()

    def captchaSolve(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "vahancaptcha:ref_captcha")))
        self.driver.find_element_by_name("regn_no1_exact").click()
        self.send_discrete_keys(name="regn_no1_exact", string=self.dataObj.numPlate)
        print('in captcha')
        self.driver.find_element_by_id("vahancaptcha:ref_captcha").screenshot("Resources\\captcha.png")

        captchaText = self.tesseract_captcha_ocr()
        print(captchaText, " ", len(captchaText))
        if len(captchaText) == 5:
            self.driver.find_element_by_id("vahancaptcha:CaptchaID").send_keys(Keys.ENTER)
            self.send_discrete_keys(name="vahancaptcha:CaptchaID", string=captchaText, byType=By.ID)
            self.driver.implicitly_wait(1)
            try:
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[normalize-space()='Vahan Search']")))
                self.driver.find_element_by_xpath("//button[normalize-space()='Vahan Search']").click()
            except Exception as e:
                print(3, e)
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[normalize-space()='Vahan Search']")))
                self.driver.find_element_by_xpath("//button[normalize-space()='Vahan Search']").send_keys(
                    Keys.ENTER)
            print('captcha')
        else:
            self.captchaSolve()

    def finalScrape(self):
        WebDriverWait(self.driver, 4).until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id='rcDetailsPanel']/div[1]/table/tbody/tr[4]/td/div/span[1]")))

        self.dataObj.vehicleName = self.driver.find_element_by_xpath(
            "//*[@id='rcDetailsPanel']/div[1]/table/tbody/tr[4]/td/div/span[1]").text
        self.dataObj.address = self.driver.find_element_by_xpath(
            "//*[@id='rcDetailsPanel']/div[1]/table/tbody/tr[4]/td/div/span[3]").text
        regDate = self.driver.find_element_by_css_selector(
            "#rcDetailsPanel > div:nth-child(5) > div:nth-child(2) > span").text
        insDate = self.driver.find_element_by_css_selector(
            "#rcDetailsPanel > div:nth-child(6) > div:nth-child(2) > span").text
        pucDate = self.driver.find_element_by_css_selector(
            "#rcDetailsPanel > div:nth-child(6) > div:nth-child(4) > span").text
        print('got it')
        return regDate, insDate, pucDate

    def send_discrete_keys(self, name, string, byType=By.NAME):
        self.driver.find_element(byType, name).clear()
        for character in string:
            self.driver.find_element(byType, name).send_keys(character)

    def saveInDb(self, reg, ins, puc):
        errcode = errorCodes.encode(reg, ins, puc)

        photoBin, plateBin = database.image_to_bin()

        database.insert(self.dataObj.numPlate, self.dataObj.vehicleName, self.dataObj.address, photoBin,
                        datetime.now().strftime("%H:%M:%S | %d-%m-%Y"), errcode,
                        plateBin)

    def tesseract_captcha_ocr(self):
        captchaImg = cv2.imread('Resources\captcha.png')
        # captchaImg = captchaImg[4:-3, 4:-3] #43,122
        gray = cv2.cvtColor(captchaImg, cv2.COLOR_BGR2GRAY)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        gray = cv2.medianBlur(gray, 3)
        text = pytesseract.image_to_string(gray, lang='eng', config=self.TESS_CONFIG)
        return text[:5]

    def is_license_format(self):
        if self.dataObj.numPlate.isalnum() and self.dataObj.numPlate[0].isalpha() and self.dataObj.numPlate[
            1].isalpha():
            if self.dataObj.numPlate[2].isdigit():
                pass
            elif self.dataObj.numPlate[2] == "O" or self.dataObj.numPlate[2] == "o":
                self.dataObj.numPlate = self.dataObj.numPlate[:2] + '0' + self.dataObj.numPlate[3:]
                print(self.dataObj.numPlate, " this shit")
            else:
                return False

            if self.dataObj.numPlate[-1].isdigit():
                pass
            elif self.dataObj.numPlate[-1] == "O" or self.dataObj.numPlate[-1] == "o":
                self.dataObj.numPlate = self.dataObj.numPlate[:-1] + '0'
                print(self.dataObj.numPlate, " this shit")
            return True

        print('f3', self.dataObj.numPlate[2], self.dataObj.numPlate[-1])
        print('fals')
        return False

    # def license_num_corrector(self):
    #     state = self.dataObj.numPlate[0:2]
    #     char_segment = ''
    #     end_num = ''
    #
    #     if self.dataObj.numPlate[3].isdigit():
    #         district = self.dataObj.numPlate[2:4]
    #         index = 4
    #     else:
    #         district = self.dataObj.numPlate[2]
    #         index = 3
    #
    #     while self.dataObj.numPlate[index].isalpha() and len(char_segment) < 3:
    #         char_segment += self.dataObj.numPlate[index]
    #         index += 1
    #
    #     end_num = self.dataObj.numPlate[index:]
    #
    #     if len(end_num) > 4:
    #         extras = end_num[:-4]
    #         temp = ''
    #
    #         if not end_num[-4:].isdigit():
    #             for char in
    #
    #
    #         for char in extras:
    #             if char.isalpha():
    #                 char_segment += char
    #             elif char == "0":
    #                 char_segment += 'O'

    # while self.dataObj.numPlate[index] and len(end_num) < 4:
    #     if self.dataObj.numPlate[index].isdigit():
    #         end_num += self.dataObj.numPlate[index]
    #     else:
    #
    #     index += 1

    def license_plate_parser(self):
        temp = ''
        for char in self.dataObj.numPlate:
            if char.isalnum():
                temp += char
                print(char, temp)
        self.dataObj.numPlate = temp
