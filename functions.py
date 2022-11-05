from imutils import face_utils
import dlib
import cv2
import os
import t
from tkinter import messagebox
import datetime as dt

model = t.Model()

if t.validConfig:
    conn = t.conn
    cursor = t.cursor

if (not os.path.isfile("Model.npz")) and t.isServer:
    print("NoModel")
    cursor.execute("UPDATE PERSON SET istrained = false")
    conn.commit()


######################################## Start Methods Database ########################################

def insertPerson(name, ssn, address, birthdate, job, gender, jtype, arriving, exiting, dataset_Num):
    if checkPersonFoundOrNot(ssn):
        raise Exception("This SSN found")
    else:
        sql = "INSERT INTO person (name, ssn, address, birthdate, job, gender, type, arriving, exiting, dataset_Num) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (name, ssn, address, birthdate, job, gender, jtype, arriving, exiting, dataset_Num)
        cursor.execute(sql, val)
        conn.commit()
        print(cursor.rowcount, "Inserted done")


def insertZone(name, open_time, close_time):
    sql = "INSERT INTO zone (name, open_time, close_time) VALUES (%s, %s, %s)"
    val = (name, open_time, close_time)
    cursor.execute(sql, val)
    conn.commit()
    print(cursor.rowcount, "Inserted done")


def insertCamera(cam: t.Camtype):
    if checkCamera(cam.cm_id, cam.zone):
        if messagebox.askokcancel("Dymmo Asks : ", "Already camera found, do you overwrite?"):
            deleteCamera(cam.camName, cam.zone)
            insertCam(cam)
    else:
        insertCam(cam)


def insertCam(cam: t.Camtype):
    sql = "INSERT INTO camera (CameraOpenNumber, name, entering, date_of_pruchese, zone_id) VALUES (%s, %s, %s, %s, %s)"
    val = (cam.cm_id, cam.camName, cam.is_entering, cam.date, cam.zone)
    cursor.execute(sql, val)
    conn.commit()
    print(cursor.rowcount, "Inserted done")


def insertPersonWorksInZone(person_ssn: int, zones: list):
    if len(zones) != 0:
        for i in range(len(zones)):
            sql = "INSERT INTO person_works_in_zone (person_ssn, zone_id, extraTime) VALUES (%s, %s, 0)"
            val = (person_ssn, zones[i])
            cursor.execute(sql, val)
            conn.commit()
        print(len(zones), "Inserted done")
    else:
        print("Empty zone list")


def insertZoneLocation(idzone_location, location):
    sql = "INSERT INTO zone_location (idzone_location, location) VALUES (%s, %s)"
    val = (idzone_location, location)
    cursor.execute(sql, val)
    conn.commit()
    print(cursor.rowcount, "Inserted done")


def insertUserAndPass(person_ssn, username, password):
    sql = "INSERT INTO userandpass (person_ssn, username, password) VALUES (%s, %s, %s)"
    val = (person_ssn, username, password)
    cursor.execute(sql, val)
    conn.commit()
    print(cursor.rowcount, "Inserted done")


def updateDataset(ssn: int, datasetNumber: int):
    sql = "UPDATE person set dataset_Num = %s where SSN = %s"
    val = (datasetNumber, ssn)
    cursor.execute(sql, val)
    conn.commit()


def updatePerson(ssn, name, address, birthdate, job, gender, type, arriving, exiting):
    sql = "UPDATE person SET name = %s, address = %s, birthdate = %s, job = %s, gender = %s, type = %s, arriving = %s, exiting = %s WHERE SSN = %s"
    val = (name, address, birthdate, job, gender, type, arriving, exiting, ssn)
    cursor.execute(sql, val)
    conn.commit()
    print(cursor.rowcount, "Updated done")


def updatePersonWorksInZone(person_ssn: int, zones: list):
    sql = "DELETE FROM person_works_in_zone WHERE person_ssn = %s"
    val = (person_ssn,)
    cursor.execute(sql, val)
    conn.commit()

    if len(zones) != 0:
        for i in range(len(zones)):
            sql = "INSERT INTO person_works_in_zone (person_ssn, zone_id, extraTime) VALUES (%s, %s, 0)"
            val = (person_ssn, zones[i])
            cursor.execute(sql, val)
            conn.commit()

        print(len(zones), "Inserted done")


def getPersonDataNumber(ssn: int) -> int:
    sql = "SELECT dataset_Num FROM person WHERE ssn = %s"
    val = (ssn,)
    cursor.execute(sql, val)
    row = cursor.fetchone()
    return int(row[0])


def getRecordByType(type: str):
    sql = "SELECT date, time, describtion FROM record WHERE type = %s"
    val = (type,)
    cursor.execute(sql, val)
    rows = cursor.fetchall()
    return rows


def updateZone(name, open_time, close_time):
    sql = "UPDATE zone SET open_time = %s, close_time = %s WHERE name = %s"
    val = (open_time, close_time, name)
    cursor.execute(sql, val)
    conn.commit()
    print(cursor.rowcount, "Updated done")


def updateUserAndPass(ssn, username, password):
    sql = "SELECT person_ssn FROM userandpass where person_ssn = (SELECT ssn FROM person WHERE ssn = %s)"
    val = (ssn,)
    cursor.execute(sql, val)

    if cursor.rowcount == 0:
        sql2 = "INSERT userandpass (person_ssn, username, password) VALUES((SELECT ssn FROM person WHERE ssn = %s), %s, %s)"
        val2 = (ssn, username, password)
        cursor.execute(sql2, val2)
        conn.commit()
        print(cursor.rowcount, "Inserted done")
    else:
        sql2 = "UPDATE userandpass set username = %s, password = %s WHERE person_ssn = (SELECT ssn FROM person WHERE ssn = %s)"
        val2 = (username, password, ssn)
        cursor.execute(sql2, val2)
        conn.commit()
        print(cursor.rowcount, "Updated done")


def deletePerson(ssn):
    sql = "DELETE FROM person WHERE ssn = %s"
    val = (ssn,)
    cursor.execute(sql, val)
    conn.commit()
    print(cursor.rowcount, "Deleted done")


def deleteCamera(id, zoneId):
    sql = "DELETE FROM camera WHERE id = %s AND zone_id = %s"
    val = (id, zoneId)
    cursor.execute(sql, val)
    conn.commit()
    print(cursor.rowcount, "Deleted done")


def deleteZone(name):
    sql = "DELETE FROM zone WHERE name = %s"
    val = (name,)
    cursor.execute(sql, val)
    conn.commit()
    print(cursor.rowcount, "Deleted done")


def checkUserAndPass(username: str, password: str) -> tuple:
    if not (username or password):
        return (False, -1)
    sql = "SELECT person_ssn FROM userandpass WHERE username = %s AND password = %s AND BINARY(username) = BINARY(%s) AND BINARY(password) = BINARY(%s)"
    val = (username, password, username, password)
    cursor.execute(sql, val)
    rows = cursor.fetchall()
    if len(rows) > 0:
        return (True, rows[0][0])
    else:
        return (False, -1)


def checkValidUsername(username: str):
    if not username:
        return True
    sql = "SELECT person_ssn FROM userandpass WHERE username = %s AND BINARY(username) = BINARY(%s)"
    val = (username, username)
    cursor.execute(sql, val)
    rows = cursor.fetchall()
    if len(rows) > 0:
        return False
    else:
        return True


def checkCamera(cameraOpenNumber, zoneId) -> bool:
    sql = "SELECT * FROM camera WHERE CameraOpenNumber = %s AND zone_id = %s"
    val = (cameraOpenNumber, zoneId)
    cursor.execute(sql, val)
    rows = cursor.fetchall()
    if len(rows) > 0:
        return True
    else:
        return False


def getUserAndPass(ssn):
    sql = "SELECT username, password FROM userandpass WHERE person_ssn = (SELECT ssn FROM person WHERE ssn = %s)"
    val = (ssn,)
    cursor.execute(sql, val)
    if cursor.rowcount == 0:
        return "", ""

    row = cursor.fetchone()
    return row


def getZoneById(id: int):
    sql = "SELECT name,open_time,close_time FROM zone WHERE id = %s"
    val = (id,)
    cursor.execute(sql, val)
    row = cursor.fetchone()

    now = dt.datetime.now().strftime('%Y:%m:%d')

    if cursor.rowcount > 0:
        t.myZoneName = row[0]
        t.myZoneEnterTime = dt.datetime.strptime(now, '%Y:%m:%d') + row[1]
        t.myZoneExitTime = dt.datetime.strptime(now, '%Y:%m:%d') + row[2]


def getLocationName(name):
    sql = "SELECT location FROM zone_location where idzone_location = (SELECT id FROM zone where name = %s)"
    val = (name,)
    cursor.execute(sql, val)

    if cursor.rowcount == 0:
        return ""

    return cursor.fetchone()[0]


def getPersonType(ssn: int) -> t.PersonType:
    sql = "SELECT type FROM person WHERE ssn = %s"
    val = (ssn,)
    cursor.execute(sql, val)
    rows = cursor.fetchall()
    rows = str(rows[0][0])

    if rows == "Admin":
        return t.PersonType.Admin
    elif rows == "Supervisor":
        return t.PersonType.Supervisor
    elif rows == "Security Agent":
        return t.PersonType.Agnet
    elif rows == "Worker":
        return t.PersonType.Worker
    else:
        return t.PersonType.Unknown


def getPersonWithSSN(SSN) -> dict:
    sql = "SELECT * FROM person WHERE SSN = %s"
    val = (SSN,)
    cursor.execute(sql, val)

    info = {}
    if cursor.rowcount == 0:
        return info

    row = cursor.fetchone()

    sql2 = "SELECT name FROM person WHERE SSN = (SELECT supervisor_ssn FROM person_subervise_persons WHERE person_ssn = %s)"
    val2 = (SSN,)
    cursor.execute(sql2, val2)
    supervisor = cursor.fetchone()

    if supervisor is None:
        supervisor = ""
    else:
        supervisor = supervisor[0]

    ssn = row[0]
    name = row[1]
    if row[1] != None:
        address = row[2]
    else:
        address = ""

    if row[3] != None:
        birthdate = row[3]
    else:
        birthdate = "0000-00-00"

    job = row[4]
    gender = row[5]
    type = row[6]
    arriving = row[7]
    exiting = row[8]
    dataset_Num = row[9]

    info["ssn"] = ssn
    info["name"] = name
    info["address"] = address
    info["job"] = job
    info["gender"] = gender
    info["type"] = type
    info["dataset_Num"] = dataset_Num
    info["supervisor"] = supervisor
    year = str(birthdate).split("-")[0]
    month = str(birthdate).split("-")[1]
    day = str(birthdate).split("-")[2]
    info["birthdate"] = f"{day}-{month}-{year}"
    if int(str(arriving).split(":")[0]) > 12:
        info["hourin"] = int(str(arriving).split(":")[0]) - 12
    else:
        info["hourin"] = int(str(arriving).split(":")[0])
    info["minutein"] = str(arriving).split(":")[1]
    if int(str(exiting).split(":")[0]) > 12:
        info["hourout"] = int(str(exiting).split(":")[0]) - 12
    else:
        info["hourout"] = int(str(exiting).split(":")[0])
    info["minuteout"] = str(exiting).split(":")[1]
    if int(str(arriving).split(":")[0]) > 12:
        info["edit_in"] = "2"
    else:
        info["edit_in"] = "1"
    if int(str(exiting).split(":")[0]) > 12:
        info["edit_out"] = "2"
    else:
        info["edit_out"] = "1"

    return info


# Delete this
def getLatestPersonSSN():
    cursor.execute("SELECT Max(id) FROM person")
    row = cursor.fetchone()
    return row[0]


def getLatestZoneId():
    cursor.execute("SELECT Max(id) FROM zone")
    row = cursor.fetchone()
    return row[0]


def getTrainingData():
    cursor.execute("SELECT COUNT(ssn), SUM(dataset_Num) FROM person Where istrained = false")
    row = cursor.fetchone()
    return f"You have {row[0]} ones and {row[1]} datasets"


def getNonTrained():
    cursor.execute("SELECT ssn, dataset_num from person where isTrained = false")
    rows = cursor.fetchall()
    return rows


def getAllCamsForZone():
    sql = "SELECT CameraOpenNumber, name, entering, date_of_pruchese FROM camera where zone_id = %s"
    val = (t.myZone,)
    cursor.execute(sql, val)
    rows = cursor.fetchall()

    cams = []

    for row in rows:
        cams.append(t.Camtype(row[0], row[1], str(t.myZone), bool(row[2]), row[3]))

    return cams


def checkPersonFoundOrNot(ssn):
    sql = "SELECT ssn FROM person WHERE SSN = %s"
    val = (ssn,)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    if len(result) > 0:
        return True
    return False


def getAllPersonsInMyZone():
    """
    This Function Get All Persons With Zone From Database
    And Load Them Into allPerson In T
    """

    sql = "SELECT P.*\
           FROM person_works_in_zone PZ, person P\
           WHERE PZ.person_ssn = P.ssn\
           AND PZ.zone_id = %s"

    now = dt.datetime.now().strftime('%Y:%m:%d')

    val = (t.myZone,)
    cursor.execute(sql, val)
    t.allPersons.clear()
    for row in cursor.fetchall():
        sql2 = "SELECT zone_id FROM person_works_in_zone where person_ssn = %s"
        val2 = (row[0],)
        cursor.execute(sql2, val2)
        zones = []
        for z in cursor.fetchall():
            zones.append(z[0])
        t.allPersons.append(t.Person(row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                                     dt.datetime.strptime(now, '%Y:%m:%d') + row[7],
                                     dt.datetime.strptime(now, '%Y:%m:%d') + row[8], zones))


def getAllZones() -> list:
    sql = "SELECT id, name FROM zone"
    cursor.execute(sql)
    rows = cursor.fetchall()
    zones = []
    for x in rows:
        zones.append((x[0], x[1]))
    return zones


def getZoneInfo(name: str) -> dict:
    sql = "SELECT open_time, close_time FROM zone WHERE name = %s"
    val = (name,)
    cursor.execute(sql, val)

    info = {}

    if cursor.rowcount == 0:
        return info

    row = cursor.fetchone()

    open_time = row[0]
    close_time = row[1]

    info["hour_open_time"] = str(open_time).split(":")[0]
    info["minute_open_time"] = str(open_time).split(":")[1]
    info["second_open_time"] = str(open_time).split(":")[2]
    if int(str(open_time).split(":")[0]) > 12:
        info["hour_open_time"] = str(int(str(open_time).split(":")[0]) - 12)
        info["am_or_pm_open_time"] = 2
    else:
        info["am_or_pm_open_time"] = 1
    info["hour_close_time"] = str(close_time).split(":")[0]
    info["minute_close_time"] = str(close_time).split(":")[1]
    info["second_close_time"] = str(close_time).split(":")[2]
    if int(str(close_time).split(":")[0]) > 12:
        info["hour_close_time"] = str(int(str(close_time).split(":")[0]) - 12)
        info["am_or_pm_close_time"] = 2
    else:
        info["am_or_pm_close_time"] = 1

    return info


def checkPersonSubervisePersons(SupervisorSSN, Personssn):
    sql = "SELECT * FROM person_subervise_persons WHERE supervisor_ssn = %s AND person_ssn = %s"
    val = (SupervisorSSN, Personssn)
    cursor.execute(sql, val)
    result = cursor.fetchall()
    if len(result) > 0:
        return True
    return False


def updateInPersonSubervisePersons(Personssn, SupervisorSSN):
    if SupervisorSSN == 0:
        return

    if checkPersonSubervisePersons(SupervisorSSN, Personssn):
        private_updateInPersonSubervisePersons(SupervisorSSN, Personssn)
    else:
        insertPersonSubervisePersons(SupervisorSSN, Personssn)


def insertPersonSubervisePersons(SupervisorSSN, Personssn):
    if SupervisorSSN is None:
        return
    sql = "INSERT INTO person_subervise_persons VALUES (%s, %s);"
    val = (SupervisorSSN, Personssn)
    cursor.execute(sql, val)
    conn.commit()
    print(cursor.rowcount, "Inserted done")


def private_updateInPersonSubervisePersons(SupervisorSSN, Personssn:int):
    sql = "UPDATE person_subervise_persons SET supervisor_ssn = %s, person_ssn = %s"
    val = (int(SupervisorSSN), int(Personssn))
    print(sql)
    print(val)
    cursor.execute(sql, val)
    conn.commit()
    print(cursor.rowcount, "Updated done")


def deletePersonSubervisePersons(ssn):
    sql = "DELETE FROM person_subervise_persons WHERE person_ssn = %s"
    val = (ssn,)
    cursor.execute(sql, val)
    conn.commit()
    print(cursor.rowcount, "Deleted done")

def getProfPath(recID:int):
    sql = "SELECT image FROM record WHERE id = %s"
    val = (recID,)
    cursor.execute(sql,val)

    if cursor.rowcount <= 0:
        return None

    return cursor.fetchone()[0]

######################################## End Methods Database ########################################

def cameraCount():
    '''
    This Function Gets The All Active Cameras Pluged In
    '''

    i = 0
    cam = cv2.VideoCapture(i)

    while cam.isOpened():
        i += 1
        cam.open(i)

    os.system('cls')
    return i


def getRecordDescribtion():
    sql1 = "SELECT person_ssn from person_subervise_persons WHERE supervisor_ssn = %s"
    val1 = (t.userSSN,)
    cursor.execute(sql1, val1)
    rows1 = []
    for r1 in cursor.fetchall(): rows1.append(r1[0])
    rows1 = ', '.join([str(element) for element in rows1])

    if len(rows1) > 0:
        sql2 = f"SELECT record_id from person_has_record_by_cam WHERE person_ssn IN ({rows1})"
        cursor.execute(sql2)
        rows2 = []
        for r2 in cursor.fetchall(): rows2.append(r2[0])
        rows2 = ', '.join([str(element) for element in rows2])

        if len(rows2) > 0:
            sql3 = f"SELECT date, time, describtion FROM record WHERE id IN ({rows2})"
            cursor.execute(sql3)
            l = cursor.fetchall()
            l.reverse()
            return l
        else:
            return [('None', 'None', 'None')]
    else:
        return [('None', 'None', 'None')]


def createDatasetFromCamera(camNum, person: t.Person):
    '''
    This function takes Camera Number and Person
    and build a dataset for him using this camera
    '''

    # Error
    if camNum < 0 or camNum > t.numberOfCameras:
        # Out Error On GUI
        print("This camera is NOT available")
        return person.dataNum

    cam = cv2.VideoCapture(camNum)
    detector = dlib.get_frontal_face_detector()

    allImgs = []

    try:
        if t.isServer:
            if not os.path.isdir("Dataset/" + str(person.ssn)):
                os.makedirs("Dataset/" + str(person.ssn))
            else:
                print("Dir Exists...")

        z = 0
        while True:
            s, img = cam.read()

            temp = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            faces = detector(temp, 1)

            for rect in faces:
                (x, y, w, h) = face_utils.rect_to_bb(rect)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 1)

                if z > 30:
                    temp = img[y: y + w, x: x + h]

                    if t.isServer:
                        cv2.imwrite("Dataset/" + str(person.ssn) + "/%s.jpg" % (person.dataNum), temp)
                    else:
                        t.myNetwork.sendMessageToClient(t.Client(t.host, t.port, t.mySocket), t.MessageType.Pass,
                                                        t.Message(t.MessageObject.DataSet,
                                                                  {"ssn": person.ssn, "dataNum": person.dataNum,
                                                                   "image": temp}))

                    person.increasedataNum()
                    z = 0

            z += 1
            cv2.imshow("Cam " + str(camNum), img)
            key = cv2.waitKey(1)

            if key == ord('q'):
                break
        cv2.destroyAllWindows()

        if not t.isServer:
            # Share all the dataset with the server
            t.myNetwork.sendMessageToClient(t.Client(t.host, t.port, t.mySocket), t.MessageType.StoreDataset,
                                            t.Message(t.MessageObject.Empty, ""))


    except OSError:
        print("Error Can't create Dataset")
    else:
        print("Dataset Created Successfuly")
        return person.dataNum


def getSubervisorName() -> list:
    sql = "SELECT name FROM person WHERE type = 'Supervisor' or type = 'Admin' and name != 'admin'"
    cursor.execute(sql)
    rows = cursor.fetchone()
    return rows


def getSubervisorSsn(name) -> int:
    if not name or name is None or name == ' ':
        return 0
    sql = "SELECT ssn FROM person WHERE name = %s and type = 'Supervisor' ond type = 'Admin' "
    val = (name,)
    cursor.execute(sql, val)
    row = cursor.fetchone()
    return int(row[0])


def getRecordsForSecurity(year="", month="", day="", startTime="", endTime="", recType="") -> list:
    sql = "SELECT id,date,time,describtion,arg FROM record "

    values = []

    if year != "" or month != "" or day != "" or startTime != "" or endTime != "" or recType != "":
        sql += "WHERE "

        if recType != "":
            sql += "type = %s "
            values.append(recType)
            if year != "" or month != "" or day != "" or startTime != "" or endTime != "":
                sql += "OR "

        if year != "" or month != "" or day != "":
            if len(month) == 1:
                month = "0" + month
            if len(day) == 1:
                day = "0" + day

            sql += "date LIKE '%%s%-%s%-%s%' "

            if year:
                values.append(int(year))
            else:
                values.append(0)
            if month:
                values.append(int(month))
            else:
                values.append(0)
            if day:
                values.append(int(day))
            else:
                values.append(0)

            if startTime != "" or endTime != "":
                sql += "OR "

        if startTime != "" or endTime != "":
            sql += f"time >= '%s' OR time <= '%s'"
            if startTime:
                values.append(int(startTime))
            if endTime:
                values.append(int(endTime))
            else:
                values.append(0)

    print(sql)
    print(tuple(values))

    cursor.execute(sql, tuple(values))
    row = cursor.fetchall()
    row.reverse()
    return row


def createDatasetFromVideo(fileName: str, person):
    '''
    This function takes Video and Person and Build a dataset for this Video
    '''

    try:
        cam = cv2.VideoCapture(fileName)
    except Exception as e:
        print(str(e))
        return person.dataNum

    detector = dlib.get_frontal_face_detector()

    try:
        if t.isServer:
            if not os.path.isdir("Dataset/" + str(person.ssn)):
                os.makedirs("Dataset/" + str(person.ssn))
            else:
                print("Dir Exists...")

        while True:
            s, img = cam.read()

            if not s:
                break

            temp = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            faces = detector(temp, 1)

            for rect in faces:
                (x, y, w, h) = face_utils.rect_to_bb(rect)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 1)
                temp = img[y: y + w, x: x + h]

                if t.isServer:
                    cv2.imwrite("Dataset/" + str(person.ssn) + "/%s.jpg" % (person.dataNum), temp)
                else:
                    t.myNetwork.sendMessageToClient(t.Client(t.host, t.port, t.mySocket), t.MessageType.Pass,
                                                    t.Message(t.MessageObject.DataSet,
                                                              {"ssn": person.ssn, "dataNum": person.dataNum,
                                                               "image": temp}))

                person.increasedataNum()

            cv2.imshow("Video", img)
            cv2.waitKey(1)

        cv2.destroyAllWindows()

        if not t.isServer:
            # Share all the dataset with the server
            t.myNetwork.sendMessageToClient(t.Client(t.host, t.port, t.mySocket), t.MessageType.StoreDataset,
                                            t.Message(t.MessageObject.Empty, ""))

    except OSError:
        print("Error Can't create Dataset")
    else:
        print("Dataset Created Successfuly")
        return person.dataNum


def getProfWithPath(path: str):
    if t.isServer:

        if os.path.isfile(path):
            prof = cv2.imread(path)

            cv2.imshow('Report Prof', prof)
            cv2.waitKey(0)
            cv2.destroyWindow('Report Prof')
        else:
            t.say('Sorry, This report photo is unavailable for some reason')
            messagebox.showinfo('Dymmo Says : ', 'Sorry\n\nThis report photo is unavailable for some reason')
    else:
        t.myNetwork.sendMessageToClient(t.Client(t.host, t.port, t.mySocket), t.MessageType.GetProf,
                                        t.Message(t.MessageObject.Path, path))

        prof = t.myNetwork.searchMessageList(t.MessageObject.ProveImage)

        c = 0

        while prof == "Not Found":
            prof = t.myNetwork.searchMessageList(t.MessageObject.ProveImage)
            t.time.sleep(1)
            c += 1

            if c >= 30:
                break

        if prof == 'Not Found':
            t.say('Connection ran out of time')
            messagebox.showinfo('Dymmo Says : ', 'Connection time ran out')
            return

        if prof.data == 'Not Available':
            t.say('Sorry, This report photo is unavailable for some reason')
            messagebox.showinfo('Dymmo Says : ', 'Sorry\n\nThis report photo is unavailable for some reason')
            return
        else:

            cv2.imshow('Report Prof', prof.data)
            cv2.waitKey(0)
            cv2.destroyWindow('Report Prof')
