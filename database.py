import sqlite3
import os


def create():
    db = sqlite3.connect('Resources\\realtest.db')
    c = db.cursor()
    c.execute("""CREATE TABLE realtest(
    numPlate text,
    timeStamp text,
    name text,
    address text,
    errCode integer,
    photo blob,
    platePic blob
    )""")
    db.commit()
    db.close()


def insert(numPlate, name, address, photo, time, errcode, platePic):
    cwd = os.getcwd()
    db = sqlite3.connect(f'{cwd}\\realtest.db')
    c = db.cursor()
    c.execute(
        f"INSERT INTO realtest VALUES ('{numPlate}','{time}','{name}','{address}',{errcode},?,?)",
        (sqlite3.Binary(photo), sqlite3.Binary(platePic)))
    db.commit()
    db.close()


def getDb():
    cwd = os.getcwd()
    db = sqlite3.connect(f'{cwd}\\realtest.db')
    c = db.cursor()
    c.execute("SELECT rowid,* FROM realtest")
    list = c.fetchall()
    db.commit()
    db.close()
    return list


def image_to_bin():
    cwd = os.getcwd()
    with open(f'{cwd}\\Resources\\img.png', 'rb') as file:
        binary0 = file.read()
    with open(f'{cwd}\\Resources\\img_1.png', 'rb') as file:
        binary1 = file.read()
    return binary0, binary1

# deprecated
def bin_to_image(binary):
    cwd = os.getcwd()
    with open(f'{cwd}\\Resources\\tempPhoto.png', 'wb') as file:
        file.write(binary[0])
    with open(f'{cwd}\\Resources\\tempPlate.png', 'wb') as file:
        file.write(binary[1])

    # print(errorCodes.decode(3))


# create()
# b0, b1 = image_to_bin()
# for i in range(20):
#     insert(
#         numPlate='MH14DT2661',
#         name=f'MARUTI SXI GREEN VXI',
#         address='PIMPRI-CHINCHWAD, Maharashtra',
#         photo=b0,
#         time=(datetime.now() + timedelta(days=i, minutes=i)).strftime("%H:%M:%S | %d-%m-%Y"),
#         errcode=i % 8,
#         platePic=b1
#     )

# print(show())

# cwd = os.getcwd()  # Get the current working directory (cwd)
# files = os.listdir(cwd)  # Get all the files in that directory
# print("Files in %r: %s" % (cwd, files))
# par_dir = os.path.dirname(cwd)
# print("Parent directory", par_dir)
