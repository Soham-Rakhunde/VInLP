from datetime import datetime


class DataClass:
    def __init__(self):
        self.numPlate = str('')
        self.timeStamp = datetime.now().strftime("%H:%M:%S | %d-%m-%Y")
        self.vehicleName = str('')
        self.address = str('')
        self.errCode = int(0)
        self.photo = None  # Store cv2 image
        self.plateImage = None  # Store cv2 image
