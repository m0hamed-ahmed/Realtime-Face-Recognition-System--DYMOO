import mysql.connector
import datetime
import socket
import dlib
import cv2
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import threading as th
import pyttsx3 as robot
import numpy as np
import pickle
from sklearn.preprocessing import Normalizer
from imutils import face_utils
from enum import Enum
import time
import psutil
from tkinter import messagebox

from tensorflow.keras.models import load_model

net = load_model("Modeler.dat")


def checkValidConfig() -> bool:
    if not os.path.isfile("Config.ini"):
        return False

    configs = ["CurrentZone", "Host", "Username", "Password", "isServer", "isMain", "Port", "Clients"]

    file = open("Config.ini", 'r')

    lines = file.readlines()

    if len(lines) != len(configs):
        return False

    for line in lines:
        if not line[0:line.find(':')] in configs:
            return False

    return True

validConfig = checkValidConfig()

def setConfigration():
    myZone = 1
    host = "127.0.0.1"
    user = "root"
    password = ""
    port = 9514
    isServer = False
    isMain = False
    numberOfAllowedClients = 5
    canTalk = True

    if not validConfig:
        return myZone, host, user, password, port, isServer,isMain, numberOfAllowedClients, canTalk, validConfig

    file = open("Config.ini", 'r')

    lines = file.readlines()

    for line in lines:
        item = line[0:line.find(':')]
        value = line[line.find(':') + 1:]

        if item == "CurrentZone":
            myZone = int(value)
        elif item == "Host":
            host = value.replace('\n', '')
        elif item == "Username":
            user = value.replace('\n', '')
        elif item == "Password":
            password = value.replace('\n', '')
        elif item == "Port":
            port = int(value)
        elif item == "isServer":
            isServer = bool(int(value.replace('\n', '')))
        elif item == "Clients":
            numberOfAllowedClients = int(value)
        elif item == "Talk":
            canTalk = bool(value)
        elif item == "isMain":
            isMain = bool(value)

    return myZone, host, user, password, port, isServer,isMain, numberOfAllowedClients, canTalk, validConfig


# Configuration
myZone, host, user, password, port, isServer, isMainZone, numberOfAllowedClients, canTalk, canConnect = setConfigration()
myZoneName = ""
myZoneEnterTime: datetime.datetime
myZoneExitTime: datetime.datetime

numberOfCameras = 0
programTitle = "Dymmo"
zones = []
allPersons = []
notTrainedPeople = []
allCams = []

# Connect to database
if validConfig:
    try:
        #conn = mysql.connector.connect(database="dymmo", host='13.82.30.137', user=user, password=password , auth_plugin='mysql_native_password')
        conn = mysql.connector.connect(database="dymmo", host=host, user=user, password=password)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(e)
        if messagebox.askokcancel("Dymmo Asks : ", "Can't connect to database,You will have to reconfig the system"):
            if os.path.isfile('Config.ini'):
                os.remove('Config.ini')
        exit(321)

engine = robot.init()
engine.setProperty('rate', 150)


def say(text: str):
    if canTalk:
        engine.say(text)
        if engine._inLoop:
            engine.endLoop()
        engine.runAndWait()


# Create socket
mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def connect():
    connected = False
    while not connected:
        try:
            mySocket.connect((host, int(port)))
            connected = True
        except:
            pass


if isServer:
    mySocket.bind((host, int(port)))
    mySocket.listen(numberOfAllowedClients)
elif canConnect:
    try:
        mySocket.connect((host, int(port)))
    except:
        say("Can't Connect To The Server,Do u want me to try again")

        if messagebox.askokcancel("Dymmo Asks : ", "Can't connect to the server\n\nDo you want me to try again ?"):
            connect()
        else:
            exit(1)


class PersonType(Enum):
    Admin = 1
    Supervisor = 2
    Worker = 3
    Agnet = 4
    Unknown = 5


class MessageType(Enum):
    Disconnect = 1  # Client and Server
    Pass = 2  # Client and Server
    Broadcasted = 3  # Client
    AskToBroadcast = 4  # Server
    TrainModel = 5  # Server
    Send = 6  # Server
    StoreDataset = 7  # Server
    StoreProve = 8  # Server
    RemovePerson = 9    # Server
    GetModel = 10   # Server
    GetProf = 11    # Server


class MessageObject(Enum):
    ProveImage = 1
    ModelFaces = 2
    ModelLabels = 3
    Empty = 4
    TrainingResult = 5
    DataSet = 6
    PersonIdToRemove = 7
    Path = 8


userPer = PersonType.Unknown
userSSN = 0


class Client(object):

    def __init__(self, address: str, clientPort: int, ClientSocket: socket.socket):
        self.address = address
        self.socket = ClientSocket
        self.port = clientPort

    def isEmpty(self):
        if not self.address:
            return True

        return False


class Message(object):
    def __init__(self, messageType: MessageObject, data):
        self.mType = messageType
        self.data = data


class Network(object):

    def __init__(self, allClients: list, messageList: list):
        self.clients = allClients
        self.headerSize = 65
        self.messageList = messageList

    def start(self):
        if isServer:
            listeningOperation = th.Thread(target=self.listen, daemon=True)
            listeningOperation.start()
            print('Server is listening...')
        else:
            connection = th.Thread(target=self.wait, args=(Client(host, port, mySocket),), daemon=True)
            connection.start()
            print('Client is waiting...')

    def listen(self):
        while True:
            try:
                print('Waiting to accept')
                client, addr = mySocket.accept()
                print(addr)
                new = Client(addr[0], addr[1], client)
                self.clients.append(new)
                c = th.Thread(target=self.wait, args=(new,), daemon=True)
                c.start()
            except Exception as e:
                print(e)
                break

    def wait(self, client):
        c = 0
        while True:
            s, mType, message = self.recieveMessage(client.socket)

            if s:
                th.Thread(target=self.applyMessage,args= (mType, message, client)).start()
            elif mType == -1:
                c += 1
                if c >= 10:
                    break
            elif mType == 0:
                c += 1
                if c >= 10:
                    exit(1)

    def searchMessageList(self, message: MessageObject):
        for m in self.messageList:
            if m.mType == message:
                self.messageList.remove(m)
                return m

        return "Not Found"

    def applyMessage(self, messageType: MessageType, message, client: Client):
        # ClientSide and ServerSide

        if messageType == MessageType.Disconnect:
            if client in self.clients:
                self.clients.remove(client)
            client.socket.close()
        elif messageType == MessageType.Pass:

            if isinstance(message, tuple):
                message = message[0]

            self.messageList.append(message)
        elif messageType == MessageType.StoreProve:
            if isinstance(message,tuple):
                message = message[0]
            if isinstance(message, dict):
                if not os.path.isdir(message["dir"]):
                    os.makedirs(message["dir"])

                cv2.imwrite(message["name"], message["img"])
        elif messageType == MessageType.Send:
            reciever = self.getClient(message[1], message[2])
            self.sendMessageToClient(reciever, message[0], (message[3], client))
        elif messageType == MessageType.Broadcasted:
            if message.mType == MessageObject.ModelFaces:
                if os.path.isfile('Model.npz'):
                    m = np.load('Model.npz')

                    faces = message.data
                    labels = m['arr_1']

                    np.savez('Model.npz', faces, labels)
                else:
                    result = self.searchMessageList(MessageObject.ModelLabels)

                    if result == "Not Found":
                        self.messageList.append(message)
                        return
                    else:
                        faces = message.data
                        labels = result.data

                        np.savez_compressed('Model.npz', faces, labels)

            elif message.mType == MessageObject.ModelLabels:
                if os.path.isfile('Model.npz'):
                    m = np.load('Model.npz')

                    faces = m['arr_0']
                    labels = message.data

                    np.savez('Model.npz', faces, labels)

                else:
                    result = self.searchMessageList(MessageObject.ModelFaces)

                    if result == "Not Found":
                        self.messageList.append(message)
                        return
                    else:
                        faces = result.data
                        labels = message.data

                        np.savez_compressed('Model.npz', faces, labels)

            else:
                self.messageList.append(message)
        elif messageType == MessageType.AskToBroadcast:
            self.broadcast(message)
        elif messageType == MessageType.TrainModel:
            model = Model()
            result = model.trainModel(net, message[1])

            self.sendMessageToClient(message[1], MessageType.Pass, Message(MessageObject.TrainingResult, result))

        elif messageType == MessageType.StoreDataset:
            result = self.searchMessageList(MessageObject.DataSet)
            while result != "Not Found":
                result = result.data
                if not os.path.isdir("Dataset/" + str(result["ssn"])):
                    os.makedirs("Dataset/" + str(result["ssn"]))

                cv2.imwrite("Dataset/" + str(result["ssn"]) + "/%s.jpg" % (result["dataNum"]), result["image"])
                result = self.searchMessageList(MessageObject.DataSet)
        elif messageType == MessageType.RemovePerson:
            model = Model()
            model.deletePerson(self.searchMessageList(MessageObject.PersonIdToRemove))
        elif messageType == MessageType.GetModel:

            if os.path.isfile("Model.npz"):
                data = np.load("Model.npz")

                faces = data['arr_0']
                labels = data['arr_1']
            else:
                faces = []

                faces = np.asarray(faces)
                labels = np.asarray(faces)

            self.sendMessageToClient(client,MessageType.Broadcasted,Message(MessageObject.ModelFaces,faces))
            self.sendMessageToClient(client,MessageType.Broadcasted,Message(MessageObject.ModelLabels,labels))
            self.sendMessageToClient(client, MessageType.Pass, Message(MessageObject.TrainingResult, "Done"))
        elif messageType == MessageType.GetProf:
            print(message)
            path = message[0].data

            if os.path.isfile(path):
                img = cv2.imread(path)
                self.sendMessageToClient(client,MessageType.Pass,Message(MessageObject.ProveImage,img))
            else:
                self.sendMessageToClient(client, MessageType.Pass, Message(MessageObject.ProveImage, 'Not Available'))


    def encodeMessage(self, message):

        message = pickle.dumps(message)
        length = str(len(message)).encode('utf-8')

        return length, message

    def decodeMessage(self, message):
        message = pickle.loads(message)
        return message

    def sendMessageToClient(self, client: Client, messageType: MessageType, objectToSend) -> bool:

        if isServer:
            try:

                if client.address == host and client.port == port:
                    self.applyMessage(messageType, objectToSend, objectToSend[1])
                    return True

                typeLen, messageType = self.encodeMessage(messageType)
                length, Message = self.encodeMessage(objectToSend)

                client.socket.send(typeLen)
                time.sleep(0.5)
                client.socket.send(messageType)
                time.sleep(1)
                client.socket.send(length)
                time.sleep(0.5)
                client.socket.send(Message)

                return True
            except Exception as e:
                print(e)
                return False
        else:
            # Send Message To server then ask the server to send it to the required client

            result = self.askServerToSendMessage(client.address, client.port, messageType, objectToSend)
            print(result)

    def recieveMessage(self, client: socket.socket):

        try:

            length = client.recv(self.headerSize).decode('utf-8')

            print(length)

            if length:
                mType = client.recv(int(length))
            else:
                print("Empty Length")
                return False, 0, 0

            length = client.recv(self.headerSize).decode('utf-8')
            print(length)

            if length:
                message = client.recv(int(length))
            else:
                print("Empty Length")
                return False, 0, 0

            mType = self.decodeMessage(mType)
            message = self.decodeMessage(message)
            print(message)

            print(str(message))
            if isinstance(message,Message):
                print('Data : ' + str(message.data))
            else:
                print('Tuple : ' + str(message))
                print('Data : ' + str(message[3].data))

            return True, mType, message

        except Exception as e:
            print(e)
            return False, -1, 0

    def getClient(self, Address: str, Port: int) -> Client:

        if Address == host and Port == port:
            return Client(host, port, mySocket)

        for client in self.clients:
            if client.address == Address and client.port == Port:
                return client

        return Client("", 0, socket.socket())

    def askServerToSendMessage(self, ClientAddress: str, ClientPort: int, messageType: MessageType, message: Message):
        # ClientSide
        client = self.getClient(host, port)

        if client.isEmpty():
            return "Client is NOT Connected"

        try:
            length, message = self.encodeMessage((messageType, ClientAddress, ClientPort, message))
            typeLength, typeMessage = self.encodeMessage(MessageType.Send)

            client.socket.send(typeLength)
            time.sleep(0.5)
            client.socket.send(typeMessage)
            time.sleep(1)
            client.socket.send(length)
            time.sleep(0.5)
            client.socket.send(message)

            return "Message sent"
        except Exception as e:
            print(e)
            exit(12)
            return "Something Wrong"

    def disconnect(self):
        # ClientSide
        if isServer:
            return
        self.sendMessageToClient(Client(host, port, mySocket), MessageType.Disconnect, "Disconnect")
        mySocket.close()

    def disconnectAll(self):
        # ServerSide
        if isServer:
            for client in self.clients:
                self.sendMessageToClient(client, MessageType.Disconnect, Message(MessageObject.Empty, ""))
                client.socket.close()

            mySocket.close()

    def broadcast(self, object: Message):
        if isServer:
            for client in self.clients:
                self.sendMessageToClient(client, MessageType.Broadcasted, object)
        else:
            self.sendMessageToClient(Client(host, port, mySocket), MessageType.AskToBroadcast, object)



if not isServer:
    myNetwork = Network([Client(host, port, mySocket)], [])
else:
    myNetwork = Network([], [])


class Model(object):

    def pic_norm(self, pic, required_size=(160, 160)):
        image = cv2.imread(pic, 0)
        # contrast limited adaptive histogram equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(image)
        image = cv2.resize(image, required_size)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        face_array = np.asarray(image)
        return face_array

    def load_faces(self, directory, dataNum: int):
        faces = list()
        for filename in range(dataNum):
            path = directory + str(filename) + ".jpg"
            face = self.pic_norm(path)
            faces.append(face)
        return faces

    def load_dataset(self):
        x = []
        y = []

        for per in notTrainedPeople:
            path = "Dataset\\" + str(per[0]) + "\\"
            faces = self.load_faces(directory=path, dataNum=per[1])
            labels = [per[0] for i in range(per[1])]

            x.extend(faces)
            y.extend(labels)

        return np.asarray(x), np.asarray(y)

    def get_embedding(self, model, image):
        face_pixels = image.astype('float32')
        mean, std = face_pixels.mean(), face_pixels.std()
        face_pixels = (face_pixels - mean) / std
        # transform face into one sample
        samples = np.expand_dims(face_pixels, axis=0)
        # make prediction to get embedding
        pre = model.predict(samples)
        return pre[0]

    def train(self, net):
        faces, labels = self.load_dataset()

        x = []

        for face in faces:
            emb = self.get_embedding(net, face)
            x.append(emb)

        x = np.asarray(x)

        if not os.path.isfile("Model.npz"):
            np.savez_compressed("Model", x, labels)
        else:
            data = np.load("Model.npz")

            faces = np.concatenate([data['arr_0'], x])
            labels = np.concatenate([data['arr_1'], labels])

            np.savez("Model.npz", faces, labels)

    def predict(self, face, faces, labels, netObj):

        if face.size == 0:
            return -1

        face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        face = clahe.apply(face)
        face = cv2.resize(face, (160, 160))
        face = np.asarray(face)
        face = cv2.cvtColor(face, cv2.COLOR_GRAY2RGB)
        face = self.get_embedding(netObj, face)
        face = np.asarray(face)
        face = face.reshape(1, -1)

        encoder = Normalizer(norm='l2')
        try:
            faces = encoder.transform(faces)
        except Exception as e:
            print(e)

        try:
            face = encoder.transform(face)
        except Exception as e:
            print(e)

        distance = np.linalg.norm(faces - face, axis=1)
        i = np.argmin(distance)

        if distance[i] > 0.9:
            return -1

        return labels[i]

    def deletePerson(self, label):

        if isServer:

            if not os.path.isfile('Model.npz'):
                return

            data = np.load('Model.npz')
            x = data['arr_0']
            y = data['arr_1']

            label = int(label)

            result = [x for x, z in enumerate(y) if z == label]

            x = np.delete(x, result)
            y = np.delete(y, result)

            np.savez('Model.npz', x, y)

            myNetwork.broadcast(Message(MessageObject.ModelFaces, x))
            time.sleep(5)
            myNetwork.broadcast(Message(MessageObject.ModelLabels, y))

        else:
            myNetwork.askServerToSendMessage(host,port,MessageType.RemovePerson,Message(MessageObject.PersonIdToRemove, label))

    def updateTrainningData(self, ids: list):
        sql = "UPDATE person SET isTrained = 1 WHERE ssn = %s"

        for p in ids:
            val = (p,)
            cursor.execute(sql, val)
            conn.commit()

    def trainModel(self, net, client: Client):
        if isServer:
            if notTrainedPeople == []:

                if client.socket != mySocket:
                    m = np.load('Model.npz')

                    faces = m['arr_0']
                    labels = m['arr_1']

                    myNetwork.sendMessageToClient(client, MessageType.Broadcasted,
                                                  Message(MessageObject.ModelFaces, faces))

                    time.sleep(5)

                    myNetwork.sendMessageToClient(client, MessageType.Broadcasted,
                                                  Message(MessageObject.ModelLabels, labels))

                    return "Model with you"

                return "No new data"

            start = time.time()

            ids = []

            try:
                self.train(net)

                for per in notTrainedPeople:
                    ids.append(per[0])

                self.updateTrainningData(ids)

                m = np.load('Model.npz')

                faces = m['arr_0']
                labels = m['arr_1']

                myNetwork.broadcast(Message(MessageObject.ModelFaces, faces))
                time.sleep(5)
                myNetwork.broadcast(Message(MessageObject.ModelLabels, labels))

                end = time.time()

                return "Model Created Succussfully in %5.2f s" % (end - start)
            except Exception as e:

                if os.path.isfile("Model.npz"):
                    for i in ids:
                        self.deletePerson(i)

                print(e)
                return "can't create model : " + str(e)
        else:
            myNetwork.sendMessageToClient(Client(host, port, mySocket), MessageType.TrainModel,
                                          Message(MessageObject.Empty, ""))

            result = myNetwork.searchMessageList(MessageObject.TrainingResult)

            while result == "Not Found":
                result = myNetwork.searchMessageList(MessageObject.TrainingResult)

            return result

    def getModel(self, client: Client):
        if isServer:
            return
        else:
            myNetwork.sendMessageToClient(Client(host, port, mySocket), MessageType.GetModel,
                                          Message(MessageObject.Empty, ""))

            result = myNetwork.searchMessageList(MessageObject.TrainingResult)

            c = 0

            while result == "Not Found":
                result = myNetwork.searchMessageList(MessageObject.TrainingResult)
                time.sleep(1)
                c += 1

                if c > 100:
                    say("Connection To Server Ran Out")
                    messagebox.showerror("Dymmo Says : ","Connection to server time ran out")
                    exit(456)


def programExit():
    if isServer:
        myNetwork.disconnectAll()
    else:
        myNetwork.disconnect()

    mySocket.close()

    currentProcess = psutil.Process()
    children = currentProcess.children(recursive=True)
    for child in children:
        child.terminate()


class Person(object):

    def __init__(self, ssn: int = -1, name: str = "Noone", address: str = "",
                 birth: datetime.date = datetime.datetime.now().date(),
                 job: str = "No job", gender: str = "Male", ptype: str = "No type",
                 atime: datetime.datetime = datetime.timedelta(0),
                 etime: datetime.datetime = datetime.timedelta(0), zones: list = []):
        self.ssn = ssn
        self.name = name
        self.address = address
        self.birth = birth
        self.job = job
        self.gender = gender
        self.type = ptype
        self.atime = atime
        self.etime = etime
        self.zones = zones
        self.dataNum = 0

    def increasedataNum(self):
        self.dataNum += 1

    def __str__(self):
        return f"Name: {self.name}" + "\t" + \
               f"SSN: {str(self.ssn)}" + "\t" + \
               f"Type: {str(self.type)}"

    def updateExtraTime(self, amount: int, zoneNumber: int):
        sql = "UPDATE person_works_in_zone Set extraTime = (SELECT extraTime FROM person_works_in_zone WHERE " \
              "person_ssn = %s and zone_id = %s) + %s WHERE person_ssn = %s and zone_id = %s "
        val = (self.ssn, zoneNumber, amount, self.ssn, zoneNumber)
        cursor.execute(sql, val)


class Record(object):

    def __init__(self, person: int, cam: int, date: datetime, des, zone: int, img: str = "", rec_type: str = "",
                 arg: str = ""):
        self.person = person
        self.camera = cam
        self.date = date
        self.descirbtion = des
        self.img = img
        self.zone = zone
        self.rec_type = rec_type
        self.arg = arg

    def __str__(self):
        return self.descirbtion

    def insertRecord(self):

        year = self.date.year
        month = self.date.month
        day = self.date.day
        hour = self.date.hour
        minute = self.date.minute
        second = self.date.second

        date = f"{year}-{month}-{day}"
        time = f"{hour}:{minute}:{second}"

        sql1 = "INSERT INTO record (date, time, describtion, image, type, arg) VALUES (%s, %s, %s, %s, %s, %s)"
        val1 = (date, time, self.descirbtion, self.img, self.rec_type, self.arg)

        try:
            cursor.execute(sql1, val1)
        except Exception as e:
            print(e)

        sql3 = "SELECT id FROM camera WHERE CameraOpenNumber = %s AND zone_id = %s"
        val3 = (self.camera, self.zone)
        cursor.execute(sql3, val3)
        camera_id = cursor.fetchone()[0]

        sql4 = "SELECT MAX(id) FROM record"
        cursor.execute(sql4)
        record_id = cursor.fetchone()[0]

        sql2 = "INSERT INTO person_has_record_by_cam (person_ssn, cam_id, record_id) VALUES (%s, %s, %s)"
        val2 = (self.person, camera_id, record_id)

        try:
            cursor.execute(sql2, val2)
        except Exception as e:
            print(e)

        conn.commit()

        print(cursor.rowcount, "Inserted done")


class Camtype:

    def __init__(self, cam_id: int, cam_name: str, zone: str, is_entering: bool, date: datetime.datetime = datetime.datetime.now()):
        self.cm_id = cam_id  # Camera id
        self.camName = cam_name  # Camera name
        self.zone = zone  # Camera zone name
        self.is_entering = is_entering  # Is the camera entering or exiting
        self.date = date  # Date of prochese of the camera
        self.img = np.zeros((250, 250))  # Current camera image
        self.displaying = False  # Switch the camera to display or not
        self.working = False
        self.model = Model()  # Instance of class model
        self.here: list = [datetime.datetime.strptime('00','%M') for i in range(len(allPersons))]  # Get all people in front of the camera
        self.warring = th.Thread(target=self.timingAlarm, args=("",), daemon=True)
        self.proves = []    # List to store all prof images for sending them to the server

    def __str__(self):
        string = {'id': self.cm_id, 'Name': self.camName, 'zone': self.zone, 'entering': self.is_entering,
                  'date': self.date}
        return str(string)

    def getPersonInfo(self, pid):
        '''
        Take list of all persons and an id and return the name of this person
        '''

        for i, p in enumerate(allPersons):
            if p.ssn == int(pid):
                return True, p, i

        return False, 0, -1

    def displayCam(self):
        '''
        This function displays what the camera sees
        '''
        self.displaying = True

    def open(self):
        '''
        Open the camera and display it but no recognition allowed
        '''

        cam = cv2.VideoCapture(self.cm_id)

        while cv2.waitKey(1) != ord('q'):

            s, self.img = cam.read()

            # Error
            if not s:
                cv2.destroyWindow(self.camName)
                return

            cv2.imshow(self.camName, self.img)

        cv2.destroyWindow(self.camName)
        return

    def sendProf(self, dir: str, name: str, img):
        myNetwork.sendMessageToClient(Client(host, port, mySocket), MessageType.StoreProve,
                                      {"dir": dir, "name": name, "img": img})

    def profSender(self):
        for data in self.proves:
            self.sendProf(data[0],data[1],data[2])

    def unKnownAlarm(self):
        alarm1 = robot.init()
        alarm1.setProperty('rate', 150)
        if alarm1._inLoop:
            alarm1.endLoop()
        alarm1.say("Someone strange trying to access " + myZoneName + " in Camera " + self.camName)
        alarm1.runAndWait()

    def strangeWorkerAlarm(self):
        alarm2 = robot.init()
        alarm2.setProperty('rate', 150)
        if alarm2._inLoop:
            alarm2.endLoop()
        alarm2.say("Look! This Worker is trying to enter " + myZoneName + " in Camera " + self.camName)
        alarm2.runAndWait()

    def timingAlarm(self, text: str):
        alarm3 = robot.init()
        alarm3.setProperty('rate', 150)
        if alarm3._inLoop:
            alarm3.endLoop()
        alarm3.say(text)
        alarm3.runAndWait()

    def sendWarrning(self, text: str):
        if not self.warring.is_alive():
            self.warring = th.Thread(target=self.timingAlarm, args=(text,), daemon=True)
            self.warring.start()

    def recognize(self, netObj):
        '''
        This function recognizes anyone in front of the camera
        '''

        try:
            model = np.load("Model.npz")
        except Exception as e:
            print("Can't Load Model : " + str(e))
            return
        else:
            self.alarm = th.Thread(target=self.unKnownAlarm, daemon=True)
            self.profer = th.Thread()

            datafaces = model['arr_0']
            labels = model['arr_1']

            datafaces = np.asarray(datafaces)

            cam = cv2.VideoCapture(self.cm_id)
            detector = dlib.get_frontal_face_detector()

            inFront = []

            while self.working:
                s, self.img = cam.read()
                # Error
                if not s:
                    exit(1)

                faces = detector(self.img, 1)

                for rect in faces:
                    x, y, w, h = face_utils.rect_to_bb(rect)

                    face = self.img[y:y + w, x:x + h]

                    try:
                        i = self.model.predict(face, datafaces, labels, netObj)
                    except Exception as e:
                        print(e)
                        return

                    agree, per, pos = self.getPersonInfo(pid=i)

                    if agree and i != -1:

                        if self.displaying:
                            cv2.rectangle(self.img, (x, y), (x + w, y + h), (0, 255, 0), 1)
                            cv2.putText(self.img, "Worker : " + str(per.name), (x + 10, y + 25),
                                        cv2.FONT_HERSHEY_COMPLEX,
                                        0.5, (0, 255, 0))

                        now = datetime.datetime.now()

                        if now >= self.here[pos]+datetime.timedelta(0,30):

                            arg = ""
                            recType = ""
                            des = ""

                            if self.is_entering:

                                # Zone is NOT open yet
                                if now < myZoneEnterTime:
                                    des = per.name + " entered " + myZoneName + " before it opens\n\nThis has been " \
                                                                                "taken by " + self.camName
                                    recType = "Security"

                                    self.sendWarrning(
                                        "Worker " + per.name + " is entering " + myZoneName + " before it opens")
                                elif myZoneExitTime > now >= myZoneEnterTime:
                                    if isMainZone:
                                        if per.atime + datetime.timedelta(0,
                                                                          600) > now > per.atime - datetime.timedelta(0,
                                                                                                                      600):
                                            des = per.name + " has entered " + myZoneName + " on time\n\nThis has been taken by " + self.camName
                                            recType = "Entering"
                                        elif now < per.atime - datetime.timedelta(0, 600):
                                            recType = "EarlyEnter"
                                            arg = str((per.atime - now).total_seconds())
                                            des = per.name + " has entered " + myZoneName + " before his/her time" \
                                                                                            "\n\nThis has been taken by " \
                                                  + self.camName + "\n\nHe/She is early by " + str(
                                                int(arg) / (60 * 60)) + " hours"
                                        else:
                                            recType = "LateEnter"
                                            arg = str((now - per.atime).total_seconds())
                                            des = per.name + " has entered " + myZoneName + " after his/her time" \
                                                                                            "\n\nThis has been taken by " \
                                                  + self.camName + "\n\nHe/She is late by " + str(
                                                int(arg) / (60 * 60)) + " hours"
                                    elif now > per.etime + datetime.timedelta(0, 600):
                                        recType = "InvalidEnter"
                                        des = per.name + " has entered " + myZoneName + " after his/her exiting time" \
                                                                                        "\n\nThis has been taken by " \
                                              + self.camName
                                        self.sendWarrning(
                                            "Worker " + per.name + " is entering " + myZoneName + " but he finished working")
                                    else:
                                        des = per.name + " has entered " + myZoneName + "\n\nThis has been taken by " + self.camName
                                        recType = "Entering"
                                elif now > myZoneExitTime:
                                    des = per.name + " entered " + myZoneName + " after it closed\n\nThis has been " \
                                                                                "taken by " + self.camName
                                    recType = "Security"

                                    self.sendWarrning(
                                        "Worker " + per.name + " is entering " + myZoneName + " after it closed")
                            else:

                                if now > myZoneExitTime:
                                    des = per.name + " exited " + myZoneName + " after it closed\n\nThis has been " \
                                                                               "taken by " + self.camName
                                    recType = "Security"

                                    self.sendWarrning(
                                        "Worker " + per.name + " is exiting " + myZoneName + " after it closed")
                                else:

                                    if isMainZone:
                                        if now < per.etime:
                                            recType = "EarlyExit"
                                            arg = str((per.etime - now).total_seconds())
                                            des = per.name + " has exited " + myZoneName + " before his/her time" \
                                                                                           "\n\nThis has been taken by " \
                                                  + self.camName + "\n\nHe/She is early by " + str(
                                                int(arg) / (60 * 60)) + " hours"

                                        elif now > per.etime + datetime.timedelta(0, 600):
                                            recType = "Exiting"
                                            des = per.name + " has gone from " + myZoneName + " on time\n\nThis has been taken by " + self.camName
                                        else:
                                            recType = "LateExit"
                                            arg = str((now - per.etime).total_seconds())
                                            des = per.name + " has exited " + myZoneName + " after his/her time" \
                                                                                           "\n\nThis has been taken by " \
                                                  + self.camName + "\n\nHe/She is late by " + str(
                                                int(arg) / (60 * 60)) + " hours"

                                            # Update Extra Work Hours
                                            per.updateExtraTime(arg, myZone)

                                    else:
                                        recType = "Exiting"
                                        des = per.name + " has gone from " + myZoneName + "\n\nThis has been taken by " + self.camName

                            prove = "Proves\\" + now.strftime("%B") + "\\" + now.strftime("%B") + now.strftime(
                                "%A") + now.strftime("%X") + ".jpg"
                            prove = prove.replace(':', ' ')

                            if not isServer:
                                # Send the prove img (self.img) to the server

                                self.proves.append(("Proves\\" + now.strftime("%B"), prove, self.img))

                                if not self.profer.is_alive():

                                    self.profer = th.Thread(target=self.profSender)
                                    self.profer.start()
                                else:
                                    print('Profer status : ' + str(self.profer.is_alive()))
                                    print(self.proves)

                            else:
                                # Prove Must be writen on the server
                                if not os.path.isdir("Proves\\" + now.strftime("%B")):
                                    if not os.path.isdir("Proves"):
                                        os.mkdir("Proves")

                                    os.mkdir("Proves\\" + now.strftime("%B"))

                                cv2.imwrite(prove, self.img)

                            newRec = Record(person=per.ssn, cam=self.cm_id, date=now, des=des, img=prove, zone=myZone,
                                            rec_type=recType, arg=arg)

                            self.here[pos] = now

                            print(newRec)

                            newRec.insertRecord()

                        inFront.append(pos)

                    elif not agree and i != -1:
                        if not self.alarm.is_alive():
                            self.alarm = th.Thread(target=self.strangeWorkerAlarm, daemon=True)
                            self.alarm.start()

                        if self.displaying:
                            cv2.rectangle(self.img, (x, y), (x + w, y + h), (0, 255, 255), 1)
                            cv2.putText(self.img, "Worker In Another Region", (x + 10, y + 25),
                                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 255))

                    else:
                        if not self.alarm.is_alive():
                            self.alarm = th.Thread(target=self.unKnownAlarm, daemon=True)
                            self.alarm.start()

                        if self.displaying:
                            cv2.rectangle(self.img, (x, y), (x + w, y + h), (0, 0, 255), 1)
                            cv2.putText(self.img, "Unknown", (x + 10, y + 15), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                        (0, 0, 255))

                inFront = []

                if self.displaying:
                    cv2.imshow(self.camName, self.img)
                    if cv2.waitKey(1) == ord('q'):
                        self.displaying = False
                        cv2.destroyWindow(self.camName)

            if not self.working and not isServer and self.profer.is_alive():
                self.profer.join()

                if len(self.proves) > 0:
                    th.Thread(target=self.profSender).start()
