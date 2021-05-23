import threading

import cv2
import concurrent.futures
from dataClass import DataClass
from webScraper import Scraper
import numpy as np


class VideoProcessor:
    def __init__(self, vidPath):
        self.capture = cv2.VideoCapture(vidPath.name)
        FPS = self.capture.get(cv2.CAP_PROP_FPS)
        self.FRAME_SKIP = int(FPS / 5)

        self.frame = np.zeros((532, 945, 3), np.uint8)
        self.plateImage = np.zeros((25, 100, 3), np.uint8)
        self.frame[:] = (250, 250, 255)
        self.plateImage[:] = (250, 250, 255)
        self.isFrameAvailable = True

        thread = threading.Thread(target=self.processFrameWise)
        thread.start()

    def processFrameWise(self):
        self.isFrameAvailable, self.frame = self.capture.read()
        count = 1250
        with concurrent.futures.ProcessPoolExecutor() as multiProcessExecutor:
            while self.isFrameAvailable:
                self.isFrameAvailable, self.frame = self.capture.read()
                if self.isFrameAvailable:
                    h = self.frame.shape[0]
                    w = self.frame.shape[1]
                    imgcrop = self.frame[390:590, 0:w]
                    gray = cv2.cvtColor(imgcrop, cv2.COLOR_BGR2GRAY)
                    gray = cv2.bilateralFilter(gray, 13, 17, 17)
                    edged = cv2.Canny(gray, 150, 200)
                    contours, new = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                    img1 = imgcrop.copy()

                    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
                    cv2.drawContours(img1, contours, -1, (255, 0, 0), 2)
                    img3 = imgcrop.copy()

                    for c in contours:
                        peri = cv2.arcLength(c, True)
                        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                        x, y, w, h = cv2.boundingRect(c)
                        area = cv2.contourArea(c)
                        if len(approx) == 4 and w > 2 * h and area >= 500 and y >= 80:
                            dataObj = DataClass()
                            cv2.drawContours(img3, c, -1, (0, 255, 0), 2)
                            self.plateImage = imgcrop[y:y + h, x:x + w]
                            dataObj.plateImage = imgcrop[y:y + h, x:x + w]
                            dataObj.photo = cv2.rectangle(self.frame, (x - 3, 390 + y - 3), (x + w + 3, 393 + y + h),
                                                          (0, 0, 255), 2)

                            multiProcessExecutor.submit(Scraper, dataObj)
                            break
                    # cv2.imshow("hii", img3)
                    # cv2.imshow("hey", imgcrop)
                    # cv2.imshow("edg", edged)
                    #
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #     break

                count += self.FRAME_SKIP  # i.e. at 5 fps, this advances one second
                self.capture.set(1, count)
