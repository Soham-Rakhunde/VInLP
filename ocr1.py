import cv2
import numpy as np
import pytesseract


class Rekognition:
    def __init__(self, data):
        self.dataObj = data
        pytesseract.pytesseract.tesseract_cmd = "D:\Software\Programming\Teserract_OCR\\tesseract.exe"
        path = "C:\\Users\\soham\\PycharmProjects\\pythonProject\\Resources\\indimg6.jpeg"
        self.dataObj.plateImage = cv2.imread(path)
        self.dataObj.numPlate = self.detectLicense()
        print(self.dataObj.numPlate)

    def showOriginal(self):
        cv2.imshow("Original", self.dataObj.plateImage)
        cv2.waitKey(0)

    def show(self, img, name=""):
        cv2.imshow(name, img)
        cv2.waitKey(0)

    def process_Image(self):
        img = cv2.resize(self.dataObj.plateImage, (440, 160))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        # self.show(thresh,"Threshold")
        output = cv2.connectedComponentsWithStats(thresh, 4, cv2.CV_32S)
        (numLabels, labels, stats, centroids) = output
        for i in range(0, numLabels):
            if i == 0:
                text = "examining component {}/{}".format(i + 1, numLabels)
            else:
                text = "examining component {}/{}".format(i + 1, numLabels)
            print("[INFO] {}".format(text))
            x = stats[i, cv2.CC_STAT_LEFT]
            y = stats[i, cv2.CC_STAT_TOP]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]
            area = stats[i, cv2.CC_STAT_AREA]
            print("width = ", w, " height = ", h)
            (cX, cY) = centroids[i]
            output = img.copy()
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 3)
            cv2.circle(output, (int(cX), int(cY)), 4, (0, 0, 255), -1)
            componentMask = (labels == i).astype("uint8") * 255
            # show our output image and connected component mask
            # cv2.imshow("Output", output)
            # cv2.imshow("Connected Component", componentMask)
            # cv2.waitKey(0)
        mask = np.zeros(gray.shape, dtype="uint8")
        for i in range(1, numLabels):
            x = stats[i, cv2.CC_STAT_LEFT]
            y = stats[i, cv2.CC_STAT_TOP]
            w = stats[i, cv2.CC_STAT_WIDTH]
            h = stats[i, cv2.CC_STAT_HEIGHT]
            area = stats[i, cv2.CC_STAT_AREA]
            kw = w > 15 and w < 100
            kh = h > 50 and h < 160
            # ka = area>2000 and area<16000
            if all((kw, kh)):
                print("[INFO] keeping connected component '{}'".format(i))
                componentMask = (labels == i).astype("uint8") * 255
                mask = cv2.bitwise_or(mask, componentMask)
        return mask

    def detectLicense(self):
        res = self.process_Image()
        # self.show(res,"Masked-Characters")
        return pytesseract.image_to_string(res).replace(" ", "")
