import functions as f
import t

if t.validConfig and t.myZone != 0:
    f.getAllPersonsInMyZone()
    f.getZoneById(t.myZone)

from os.path import isfile
from os import remove
from tkinter import messagebox

if not isfile("Modeler.dat"):
    t.say("Modeler.dat is missing, I can't run without it")
    messagebox.showerror("Dymmo Says : ", "Modeler.dat is missing\n\nDymmo can't run without it")
    exit(1)
elif not isfile("DYMMO.png"):
    messagebox.showerror("Dymmo Says : ", "DYMMO.png is missing\n\nDymmo can't run without it")
    exit(1)
elif not isfile("DYMMO1.png"):
    messagebox.showerror("Dymmo Says : ", "DYMMO1.png is missing\n\nDymmo can't run without it")
    exit(1)
elif not isfile("dymmo2.png"):
    messagebox.showerror("Dymmo Says : ", "dymmo2.png is missing\n\nDymmo can't run without it")
    exit(1)
elif not isfile("dymoo3.png"):
    messagebox.showerror("Dymmo Says : ", "dymoo3.png is missing\n\nDymmo can't run without it")
    exit(1)
elif not isfile('dymmo.ico'):
    t.say('dymmo.ico is NOT found')
    messagebox.showerror('dymmo.ico is NOT found')
    exit(1)

import threading as th
from tkinter import *
import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog
import babel.numbers
from tkcalendar import DateEntry
from PIL import ImageTk
from tkinter import ttk
from cv2 import destroyWindow
import datetime as dt

t.numberOfCameras = f.cameraCount()

names = set()

t.myNetwork.start()

if not t.isServer and t.checkValidConfig():
    t.Model().getModel(t.Client(t.host,t.port,t.mySocket))

t.say("Welcome to Dimmo")


def refresh():
    f.getAllPersonsInMyZone()
    # Ask all clients to update all person
    Zones = f.getAllZones()
    for item in Zones:
        t.zones.append(item[1])

    t.allCams = f.getAllCamsForZone()
    t.notTrainedPeople = f.getNonTrained()

if t.validConfig:
    refresh()

processList = []


class MainUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title_font = tkfont.Font(family='Helvetica', size=16, weight="bold")
        self.title("DYmMO")
        self.resizable(False, False)
        self.geometry("1200x700")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.active_name = None
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        if t.validConfig and t.myZone != 0:
            for F in (
                    StartPage, PageOne, Options, InsertMember, train, Edit, cameraControl, zoneControl, zoneEdit,
                    cameracreate, DirectRecord,
                    OptionsEdit, TestEditMember, TestEditZone, Configure, SReport):
                page_name = F.__name__
                frame = F(container, self)
                self.frames[page_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")
            self.show_frame("StartPage")
        else:
            for F in (Configure,):
                page_name = F.__name__
                frame = F(container, self)
                self.frames[page_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")
            self.show_frame("Configure")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure that you want to close the program?"):
            global names
            f = open("nameslist.txt", "a+")
            for i in names:
                f.write(i + " ")
            self.destroy()


class StartPage(tk.Frame):

    def check(self):
        user = user_var.get()
        password = pass_var.get()
        permission, ssn = f.checkUserAndPass(user, password)
        if permission:
            type = f.getPersonType(int(ssn))
            t.userSSN = ssn
            if type == t.PersonType.Admin:
                t.userPer = t.PersonType.Admin
                self.controller.show_frame("PageOne")
                user_var.set("")
                pass_var.set("")
            elif type == t.PersonType.Agnet:
                t.userPer = t.PersonType.Agnet
                self.controller.show_frame("cameraControl")
                user_var.set("")
                pass_var.set("")
            elif type == t.PersonType.Supervisor:
                t.userPer = t.PersonType.Supervisor
                self.controller.show_frame("DirectRecord")
                user_var.set("")
                pass_var.set("")
            else:
                t.say("You don't have permission to enter here...")
                messagebox.showerror("Dymmo Says : ", "You don't have permission to enter here...")
        else:
            t.say("You are NOT allowed to access me...")
            messagebox.showinfo("Dymmo Says : ", "You are NOT allowed to access me...")

    def __init__(self, parent, controller):

        global user_var
        user_var = StringVar()
        global pass_var
        pass_var = StringVar()
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bg = ImageTk.PhotoImage(file="DYMMO.png")
        self.bg_image = tk.Label(self, image=self.bg).place(x=0, y=0, relwidth=1, relheight=1)
        LoginFrame = tk.Frame(self, bg="black")
        LoginFrame.place(x=35, y=120, height=450, width=500)
        LoginTitle = tk.Label(LoginFrame, text="Login :  ", font=("Comic Sans MS", 30, "bold"), fg="white",
                              bg="black")
        LoginTitle.place(x=30, y=30)
        usernamelable = tk.Label(LoginFrame, text="Username :  ", font=("Comic Sans MS", 15, "bold"), fg="white",
                                 bg="black").place(x=70, y=110)
        UserEntry = tk.Entry(LoginFrame, font=(20), textvariable=user_var).place(x=75, y=150, width=300, height=30)
        Passwordlable = tk.Label(LoginFrame, text="Password :  ", font=("Comic Sans MS", 15, "bold"), fg="white",
                                 bg="black").place(x=70, y=200)
        passwordEntry = tk.Entry(LoginFrame, font=(20), show="*", textvariable=pass_var).place(x=75, y=240,
                                                                                               width=300, height=30)
        login = tk.Button(LoginFrame, text="   Login  ", font=("Comic Sans MS", 17, "bold"), fg="black",
                          bg="#d7dde6", command=self.check)
        Exit = tk.Button(LoginFrame, text="Quit", font=("Comic Sans MS", 17, "bold"), fg="black", bg="#d7dde6",
                         command=self.on_closing)
        login.place(x=75, y=300, width=300, height=40)
        Exit.place(x=75, y=350, width=300, height=40)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure that you want to close the programm?"):
            global names
            with open("nameslist.txt", "w") as f:
                for i in names:
                    f.write(i + " ")
            self.controller.destroy()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bg = ImageTk.PhotoImage(file="dymmo2.png")
        self.bg_image = tk.Label(self, image=self.bg).place(x=0, y=0, relwidth=1, relheight=1)

        OpotionsFrame = tk.Frame(self, bg="black")
        OpotionsFrame.place(x=35, y=120, height=600, width=500)
        addmember = tk.Button(OpotionsFrame, text="   Add Member   ", font=("Comic Sans MS", 15, "bold"),
                              fg="black", bg="#d7dde6",
                              command=lambda: controller.show_frame("InsertMember"))
        train = tk.Button(OpotionsFrame, text="   Train  ", font=("Comic Sans MS", 15, "bold"), fg="black",
                          bg="#d7dde6",
                          command=lambda: controller.show_frame("train"))
        camcontrol = tk.Button(OpotionsFrame, text="   Camera Control  ", font=("Comic Sans MS", 15, "bold"),
                               fg="black", bg="#d7dde6",
                               command=lambda: controller.show_frame("cameraControl"))
        Optionbtn = tk.Button(OpotionsFrame, text="   More Options  ", font=("Comic Sans MS", 15, "bold"),
                              fg="black", bg="#d7dde6",
                              command=lambda: controller.show_frame("Options"))

        cncelbt = tk.Button(OpotionsFrame, text="Quit", font=("Comic Sans MS", 15, "bold"), fg="black",
                            bg="#d7dde6",
                            command=self.on_closing)

        blackbt = tk.Button(OpotionsFrame, text=" Back ", font=("Comic Sans MS", 15, "bold"), fg="black",
                            bg="#d7dde6",
                            command=lambda: controller.show_frame("StartPage"))

        Option = tk.Button(OpotionsFrame, text="Configuration", font=("Comic Sans MS", 17, "bold"), fg="black",
                           bg="#d7dde6",
                           command=lambda: controller.show_frame("Configure"))

        addmember.place(x=75, y=100, width=300, height=40)
        train.place(x=75, y=150, width=300, height=40)
        camcontrol.place(x=75, y=200, width=300, height=40)
        Optionbtn.place(x=75, y=250, width=300, height=40)
        Option.place(x=75, y=300, width=300, height=40)
        blackbt.place(x=75, y=350, width=300, height=40)
        cncelbt.place(x=75, y=400, width=300, height=40)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure that you want to close the program?"):
            global names
            with open("nameslist.txt", "w") as f:
                for i in names:
                    f.write(i + " ")
            self.controller.destroy()


class Options(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bg = ImageTk.PhotoImage(file="dymmo2.png")
        self.bg_image = tk.Label(self, image=self.bg).place(x=0, y=0, relwidth=1, relheight=1)

        OpotionsFrame = tk.Frame(self, bg="black")
        OpotionsFrame.place(x=35, y=120, height=600, width=500)
        Editbtn = tk.Button(OpotionsFrame, text="   Edit Data   ", font=("Comic Sans MS", 15, "bold"), fg="black",
                            bg="#d7dde6",
                            command=lambda: controller.show_frame("OptionsEdit"))
        zone = tk.Button(OpotionsFrame, text="   Add Zone   ", font=("Comic Sans MS", 15, "bold"), fg="black",
                         bg="#d7dde6",
                         command=lambda: controller.show_frame("zoneControl"))
        cam = tk.Button(OpotionsFrame, text="   Creat Camera   ", font=("Comic Sans MS", 15, "bold"), fg="black",
                        bg="#d7dde6",
                        command=lambda: controller.show_frame("cameracreate"))
        cncelbt = tk.Button(OpotionsFrame, text="Quit", font=("Comic Sans MS", 15, "bold"), fg="black",
                            bg="#d7dde6",
                            command=self.on_closing)

        blackbt = tk.Button(OpotionsFrame, text=" Back ", font=("Comic Sans MS", 15, "bold"), fg="black",
                            bg="#d7dde6",
                            command=lambda: controller.show_frame("PageOne"))

        securitybt = tk.Button(OpotionsFrame, text=" Security Report ", font=("Comic Sans MS", 15, "bold"),
                               fg="black",
                               bg="#d7dde6",
                               command=lambda: controller.show_frame("SReport"))

        directrecords = tk.Button(OpotionsFrame, text="    Supervisor Record   ",
                                  font=("Comic Sans MS", 15, "bold"),
                                  fg="black",
                                  bg="#d7dde6",
                                  command=lambda: controller.show_frame("DirectRecord"))

        Editbtn.place(x=75, y=100, width=300, height=40)
        zone.place(x=75, y=150, width=300, height=40)
        cam.place(x=75, y=200, width=300, height=40)
        securitybt.place(x=75, y=250, width=300, height=40)
        directrecords.place(x=75, y=300, width=300, height=40)
        blackbt.place(x=75, y=350, width=300, height=40)
        cncelbt.place(x=75, y=400, width=300, height=40)

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Are you sure that you want to close the program?"):
            global names
            with open("nameslist.txt", "w") as f:
                for i in names:
                    f.write(i + " ")
            self.controller.destroy()


class OptionsEdit(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bg = ImageTk.PhotoImage(file="DYMMO.png")
        self.bg_image = tk.Label(self, image=self.bg).place(x=0, y=0, relwidth=1, relheight=1)

        OptionsEditFrame = tk.Frame(self, bg="black")
        OptionsEditFrame.place(x=35, y=120, height=450, width=500)
        TestinsertTitle = tk.Label(OptionsEditFrame, text="Choose Edit :  ", font=("Comic Sans MS", 30, "bold"),
                                   fg="white", bg="black")
        TestinsertTitle.place(x=30, y=50)
        EditMemberbtn = tk.Button(OptionsEditFrame, text="   Edit Member    ", font=("Comic Sans MS", 15, "bold"),
                                  fg="black", bg="#d7dde6",
                                  command=lambda: controller.show_frame("TestEditMember"))
        EditZonebtn = tk.Button(OptionsEditFrame, text="   Edit Zone   ", font=("Comic Sans MS", 15, "bold"),
                                fg="black", bg="#d7dde6",
                                command=lambda: controller.show_frame("TestEditZone"))
        blackbt = tk.Button(OptionsEditFrame, text=" Back ", font=("Comic Sans MS", 15, "bold"), fg="black",
                            bg="#d7dde6",
                            command=lambda: controller.show_frame("Options"))

        EditMemberbtn.place(x=75, y=200, width=300, height=40)
        EditZonebtn.place(x=75, y=250, width=300, height=40)
        blackbt.place(x=75, y=300, width=300, height=40)


class TestEditZone(tk.Frame):

    def passValues(self):
        name = zoneNameGet.get()
        info = f.getZoneInfo(name)
        if info == {}:
            t.say("There is no zone called " + name)
            messagebox.showinfo("Dymmo Says : ", "There is no zone called " + name)
            return
        namezone.set(name)
        locationzone.set(f.getLocationName(name))
        inhourzone.set(info["hour_open_time"])
        outhourzone.set(info["hour_close_time"])
        inminutezone.set(info["minute_open_time"])
        outminutezone.set(info["minute_close_time"])
        Inzone.set(info["am_or_pm_open_time"])
        outzone.set(info["am_or_pm_close_time"])
        zoneNameGet.set("")
        self.controller.show_frame("zoneEdit")

    def Back(self):
        zoneNameGet.set("")
        self.controller.show_frame("OptionsEdit")

    def __init__(self, parent, controller):
        global zoneNameGet
        zoneNameGet = StringVar()
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bg = ImageTk.PhotoImage(file="DYMMO.png")
        self.bg_image = tk.Label(self, image=self.bg).place(x=0, y=0, relwidth=1, relheight=1)

        TestEditFrame = tk.Frame(self, bg="black")
        TestEditFrame.place(x=35, y=120, height=450, width=500)
        TestinsertTitle = tk.Label(TestEditFrame, text="Check For Edit :  ", font=("Comic Sans MS", 30, "bold"),
                                   fg="white", bg="black")
        TestinsertTitle.place(x=30, y=50)
        nameLable = tk.Label(TestEditFrame, text="Enter Zone Name :  ", font=("Comic Sans MS", 15, "bold"),
                             fg="white", bg="black").place(x=70, y=200)
        nameEntry = tk.Entry(TestEditFrame, font=(12), textvariable=zoneNameGet).place(x=75, y=240, width=300,
                                                                                       height=30)

        nextbt = tk.Button(TestEditFrame, text="   Search  ", font=("Comic Sans MS", 17, "bold"), fg="black",
                           bg="#d7dde6", command=self.passValues)
        backbt = tk.Button(TestEditFrame, text="  Back  ", font=("Comic Sans MS", 17, "bold"), fg="black",
                           bg="#d7dde6", command=self.Back)

        nextbt.place(x=75, y=300, width=300, height=40)
        backbt.place(x=75, y=350, width=300, height=40)


datanumEdit = 0


class TestEditMember(tk.Frame):

    def passValues(self):
        ssnValue = ssnValueTest.get()
        info = f.getPersonWithSSN(ssnValue)
        if info == {}:
            t.say("This social security number is not inserted")
            messagebox.showinfo("Dymmo Says : ", "This social security number is not inserted")
            return
        editssn.set(info["ssn"])
        genderMenu.set(info["gender"])
        editentry_name.set(info["name"])
        editentry_add.set(info["address"])
        editentry_job.set(info["job"])
        ptypeMenu.set(info["type"])
        editentry_birth.set(info["birthdate"])
        editinhour.set(info["hourin"])
        editinminute.set(info["minutein"])
        editouthour.set(info["hourout"])
        editoutminute.set(info["minuteout"])
        editIn.set(info["edit_in"])
        editout.set(info["edit_out"])
        supervisorName.set(info['supervisor'])
        username, password = f.getUserAndPass(info["ssn"])
        editentry_username.set(username)
        editentry_password.set(password)
        datanumEdit = info["dataset_Num"]
        ssnValueTest.set("")
        self.controller.show_frame("Edit")

    def Back(self):
        ssnValueTest.set("")
        self.controller.show_frame("OptionsEdit")

    def __init__(self, parent, controller):
        global ssnValueTest
        ssnValueTest = StringVar()

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bg = ImageTk.PhotoImage(file="DYMMO.png")
        self.bg_image = tk.Label(self, image=self.bg).place(x=0, y=0, relwidth=1, relheight=1)

        TestEditFrame = tk.Frame(self, bg="black")
        TestEditFrame.place(x=35, y=120, height=450, width=500)
        TestinsertTitle = tk.Label(TestEditFrame, text="Check For Edit :  ", font=("Comic Sans MS", 30, "bold"),
                                   fg="white", bg="black")
        TestinsertTitle.place(x=30, y=50)
        SSNlable = tk.Label(TestEditFrame, text="Enter your SSN :  ", font=("Comic Sans MS", 15, "bold"),
                            fg="white", bg="black").place(x=70, y=200)
        SSNEntry = tk.Entry(TestEditFrame, font=(12), textvariable=ssnValueTest).place(x=75, y=240, width=300,
                                                                                       height=30)

        nextbt = tk.Button(TestEditFrame, text="   Next  ", font=("Comic Sans MS", 17, "bold"), fg="black",
                           bg="#d7dde6", command=self.passValues)
        backbt = tk.Button(TestEditFrame, text="  Back  ", font=("Comic Sans MS", 17, "bold"), fg="black",
                           bg="#d7dde6", command=self.Back)

        nextbt.place(x=75, y=300, width=300, height=40)
        backbt.place(x=75, y=350, width=300, height=40)


class InsertMember(tk.Frame):

    def Insert(self):
        ready = False
        name = entry_nameinsert.get()
        username = entry_usernameinsert.get()  # Optional
        method = vinsert.get()
        arg = xinsert.get()
        socialNum = ssninsert.get()
        if Ininsert.get() == 1:
            atime = dt.timedelta(0, int(inhourinsert.get()) * 3600 + int(inminuteinsert.get()))
        else:
            atime = dt.timedelta(0, int(inhourinsert.get()) * 3600 + int(inminuteinsert.get())) + dt.timedelta(0,
                                                                                                               43200)
        if outinsert.get() == 1:
            etime = dt.timedelta(0, int(outhourinsert.get()) * 3600 + int(outminuteinsert.get()))
        else:
            etime = dt.timedelta(0, int(outhourinsert.get()) * 3600 + int(outminuteinsert.get())) + dt.timedelta(0,
                                                                                                                 43200)
        password = entry_passwordinsert.get()  # Optional
        birth = entry_birthinsert.get()  # Optional
        address = entry_addinsert.get()  # Optional
        gender = combogenderinsert.get()
        subervisor = combosubervisor.get()
        job = entry_jobinsert.get()
        ptype = combojobinsert.get()
        if not name:
            messagebox.showerror("Dymmo Says : ", "You forgot to enter name : ")
            return
        elif len(name.split()) < 4:
            messagebox.showerror("Dymmo Says : ", "Please write your name 4 names or more ")
            return
        elif not socialNum:
            messagebox.showerror("Dymmo Says : ", "You have to enter Social Security Number")
        elif not (inhour and inminute):
            messagebox.showerror("Dymmo Says : ", "You forgot to enter the entering time")
            return
        elif not (outhour and outminute):
            messagebox.showerror("Dymmo Says : ", "You forgot to enter the exiting time")
            return
        elif not gender:
            messagebox.showerror("Dymmo Says : ", "You forgot to enter the gender")
            return
        elif not job:
            messagebox.showerror("Dymmo Says : ", "You forgot to enter the job")
            return

        elif ptype == "Select Type":
            messagebox.showerror("Dymmo Says : ", "You forgot to select the type")
            return
        elif not f.checkValidUsername(username):
            messagebox.showerror("Dymmo Says : ", "Username has been used before")
            return
        else:
            ready = True
        if ready:

            birth = dt.datetime.strptime(birth, '%d-%m-%Y')

            new = t.Person(int(socialNum), name, address, birth, job, gender, ptype, atime, etime)

            try:
                f.insertPerson(new.name, new.ssn, new.address, new.birth, new.job, new.gender, new.type, new.atime,
                               new.etime, new.dataNum)
                x = f.getSubervisorSsn(subervisor)
                if x != 0:
                    f.insertPersonSubervisePersons(x,int(socialNum))

            except Exception as e:
                print(e)
                messagebox.showerror("Dymmo Says : ", "Error Happened : " + str(e))
                return

            if not arg:
                messagebox.showerror("Dymmo Says : ", "You Haven't Entered The Camera Number Or The Video Path")
            else:
                if method == 1 and ready:
                    cam = t.allCams[int(arg)]
                    for p in processList:

                        if not p.is_alive():
                            processList.remove(p)

                        if p.name == cam.camName:
                            p.terminate()
                            processList.remove(p)
                            t.say("Closing " + p.name)
                    new.dataNum = f.createDatasetFromCamera(int(arg), new)
                elif method == 2 and ready:
                    new.dataNum = f.createDatasetFromVideo(arg, new)
                else:
                    messagebox.showerror("Dymmo cries : ", "Something went wrong")
                    return
            f.updateDataset(new.ssn, new.dataNum)
            if username:
                if not password:
                    messagebox.showinfo("Dymmo Says : ", "Enter Password to be able to create the permission")
                else:
                    f.insertUserAndPass(int(socialNum), username, password)

            f.insertPersonWorksInZone(int(socialNum), self.zonesToWork)

            t.say("Welcome " + name + " , Nice to meet you")
            messagebox.showinfo("Dymmo Says : ", "Welcome " + name + ", Nice to meet you")

            t.notTrainedPeople = f.getNonTrained()
            var.set(f.getTrainingData())
            refresh()

            entry_nameinsert.set("")
            entry_usernameinsert.set("")  # Optional
            vinsert.set("1")
            xinsert.set("")
            ssninsert.set("")
            entry_passwordinsert.set("")  # Optional
            entry_addinsert.set("")  # Optional
            combogenderinsert.set("Male")
            entry_jobinsert.set("")
            combojobinsert.set("")
            combosubervisor.set("")
            self.reslist = []

    def Back(self):
        entry_nameinsert.set("")
        entry_usernameinsert.set("")  # Optional
        vinsert.set("1")
        xinsert.set("")
        ssninsert.set("")
        entry_passwordinsert.set("")  # Optional
        entry_addinsert.set("")  # Optional
        combogenderinsert.set("Male")
        entry_jobinsert.set("")
        combojobinsert.set("")
        combosubervisor.set("")
        self.controller.show_frame("PageOne")

    def openNewWindow(self):
        # Toplevel object which will
        # be treated as a new window
        newWindow = Toplevel(self)

        # sets the title of the
        # Toplevel widget
        newWindow.title("Select Zone")

        # sets the geometry of toplevel
        newWindow.geometry("200x200")

        zones = f.getAllZones()
        zonesNames = ""

        for zone in zones:
            zonesNames += " " + zone[1]

        valores = StringVar()
        valores.set(zonesNames)

        lstbox = Listbox(newWindow, listvariable=valores, selectmode=MULTIPLE, width=20, height=10)
        lstbox.grid(column=0, row=0, columnspan=2)

        self.zonesToWork = []

        def select():
            self.reslist = []
            seleccion = lstbox.curselection()
            for i in seleccion:
                entrada = lstbox.get(i)
                self.reslist.append(entrada)

            for zone in self.reslist:
                for zone2 in zones:
                    if zone == zone2[1]:
                        self.zonesToWork.append(zone2[0])

            print(self.zonesToWork)

        btn = Button(newWindow, text="Choices", command=select)
        btn.grid(column=1, row=1)

    def __init__(self, parent, controller):
        self.zonesToWork = []
        self.reslist = []

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self['background'] = '#d7dde6'
        # able to store any value
        global vinsert
        vinsert = IntVar()
        vinsert.set("1")
        global xinsert
        xinsert = StringVar()
        global Ininsert
        Ininsert = IntVar()
        Ininsert.set("1")
        global outinsert
        outinsert = IntVar()
        outinsert.set("1")
        global entry_nameinsert
        entry_nameinsert = StringVar()
        global entry_usernameinsert
        entry_usernameinsert = StringVar()
        global entry_passwordinsert
        entry_passwordinsert = StringVar()
        global entry_addinsert
        entry_addinsert = StringVar()
        global entry_jobinsert
        entry_jobinsert = StringVar()
        global entry_birthinsert
        entry_birthinsert = StringVar()
        global inhourinsert
        inhourinsert = StringVar()
        global inminuteinsert
        inminuteinsert = StringVar()
        global outhourinsert
        outhourinsert = StringVar()
        global outminuteinsert
        outminuteinsert = StringVar()
        global combogenderinsert
        global combojobinsert
        global combosubervisor
        global ssninsert
        ssninsert = StringVar()

        self.left = ImageTk.PhotoImage(file="dymoo3.png")
        left = tk.Label(self, image=self.left).place(x=0, y=0, height=700, width=400)
        AddMemberTitle = tk.Label(self, text="Add Member : ", font=("Comic Sans MS", 30, "bold"), fg="black",
                                  bg="#d7dde6")
        AddMemberTitle.place(x=425, y=0)

        Select_zon = tk.Button(self, text="  select zone  ", font=("Comic Sans MS", 17, "bold"), fg="black",
                               bg="#d7dde6",
                               command=self.openNewWindow)

        # row 0
        tk.Radiobutton(self, text="from camera ", variable=vinsert, font=("Comic Sans MS", 15, "bold"),
                       fg="black",
                       bg="#d7dde6", value=1, command=lambda: self.dett()).place(x=475, y=55)
        tk.Radiobutton(self, text="from video ", variable=vinsert, font=("Comic Sans MS", 15, "bold"),
                       fg="black",
                       bg="#d7dde6", value=2, command=lambda: self.dett()).place(x=635, y=55)
        # row
        lableSSN = tk.Label(self, text="Enter Your SSN : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                            bg="#d7dde6")
        lableSSN.place(x=475, y=105)
        entrySSN = tk.Entry(self, bd=1, font=(12), textvariable=ssninsert)
        entrySSN.place(x=480, y=140, width=300, height=30)
        lableType = tk.Label(self, text="Enter Your Gender : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                             bg="#d7dde6")
        lableType.place(x=835, y=105)

        combogenderinsert = comboExample = ttk.Combobox(self, values=["Male", "Female"], state="readonly")

        comboExample.place(x=50, y=20)
        combogenderinsert.config(width=47)
        combogenderinsert.place(x=840, y=140, height=30)

        # row 1
        lableName = tk.Label(self, text="Enter Your Name : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                             bg="#d7dde6")
        lableName.place(x=475, y=170)
        entryName = tk.Entry(self, bd=1, font=(12), textvariable=entry_nameinsert)
        entryName.place(x=480, y=210, width=300, height=30)

        lable3 = tk.Label(self, text="Enter Camera Number: ", font=("Comic Sans MS", 15, "bold"), fg="black",
                          bg="#d7dde6")
        lable3.place(x=835, y=170)
        entry2 = tk.Entry(self, bd=1, font=(12), textvariable=xinsert)
        entry2.place(x=840, y=210, width=300, height=30)

        # row 2
        lableUsername = tk.Label(self, text="Enter Your Username : ", font=("Comic Sans MS", 15, "bold"),
                                 fg="black", bg="#d7dde6")
        lableUsername.place(x=475, y=240)
        entryName = tk.Entry(self, bd=1, font=(12), textvariable=entry_usernameinsert)
        entryName.place(x=480, y=280, width=300, height=30)

        lableUsername = tk.Label(self, text="Enter Your Password : ", font=("Comic Sans MS", 15, "bold"),
                                 fg="black", bg="#d7dde6")
        lableUsername.place(x=835, y=240)
        entryName = tk.Entry(self, bd=1, font=(12), textvariable=entry_passwordinsert)
        entryName.place(x=840, y=280, width=300, height=30)

        # row 3
        lableAddress = tk.Label(self, text="Enter Your Address : ", font=("Comic Sans MS", 15, "bold"),
                                fg="black",
                                bg="#d7dde6")
        lableAddress.place(x=475, y=310)
        entryAdderss = tk.Entry(self, bd=1, font=(12), textvariable=entry_addinsert)
        entryAdderss.place(x=480, y=350, width=300, height=30)

        lableJob = tk.Label(self, text="Enter Your Job : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                            bg="#d7dde6")
        lableJob.place(x=835, y=310)
        entryJob = tk.Entry(self, textvariable=entry_jobinsert, bd=1, font=(12))
        entryJob.place(x=840, y=350, width=300, height=30)

        # row 4
        lableBirth = tk.Label(self, text="Enter Your Birthday: ", font=("Comic Sans MS", 15, "bold"),
                              fg="black",
                              bg="#d7dde6")
        lableBirth.place(x=475, y=380)
        entryBirth = DateEntry(self, width=12, background='darkblue', bd=1, font=(12), foreground='white',
                               borderwidth=2, textvariable=entry_birthinsert, date_pattern='dd-mm-y')

        entryBirth.place(x=480, y=420, width=300, height=30)

        lableType = tk.Label(self, text="Enter Your Type : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                             bg="#d7dde6")
        lableType.place(x=835, y=380)
        combojobinsert = ttk.Combobox(self, values=["Worker", "Admin", "Security Agent", "Supervisor"],
                                      state="readonly")
        combojobinsert.place(x=50, y=20)
        combojobinsert.config(width=47)
        combojobinsert.place(x=835, y=420, height=30)
        # row 5
        lableSubervisor = tk.Label(self, text="Enter Your Subervisor Name : ",
                                   font=("Comic Sans MS", 15, "bold"), fg="black",
                                   bg="#d7dde6")
        lableSubervisor.place(x=475, y=450)

        types = f.getSubervisorName()
        if types is None:
            types = []
        else:
            types = list(types)
        types.append(' ')
        types.reverse()

        combosubervisor = ttk.Combobox(self, values=types, state="readonly")

        combosubervisor.place(x=50, y=20)
        combosubervisor.config(width=46)
        combosubervisor.place(x=480, y=490, height=30)

        Select_zon.place(x=835, y=475, width=300, height=40)

        # row 6
        lableInTime = tk.Label(self, text="Enter Your Arrive Time: ", font=("Comic Sans MS", 15, "bold"),
                               fg="black", bg="#d7dde6")
        lableInTime.place(x=475, y=540)
        spinInHour = tk.Spinbox(self, from_=1, to=12, font=("Comic Sans MS", 12), textvariable=inhourinsert)
        spinInHour.place(x=735, y=540, width=150, height=30)
        tk.Label(self, text=":", font=("Comic Sans MS", 15, "bold"), fg="black", bg="#d7dde6").place(x=900,
                                                                                                     y=540)
        spinInminute = tk.Spinbox(self, from_=0, to=60, font=("Comic Sans MS", 12), textvariable=inminuteinsert)
        spinInminute.place(x=925, y=540, width=150, height=30)
        tk.Radiobutton(self, text="AM ", variable=Ininsert, value=1, font=("Comic Sans MS", 15, "bold"),
                       fg="black",
                       bg="#d7dde6").place(x=1090, y=525)
        tk.Radiobutton(self, text="PM", variable=Ininsert, value=2, font=("Comic Sans MS", 15, "bold"),
                       fg="black",
                       bg="#d7dde6").place(x=1090, y=555)

        # row 6
        lableOutTime = tk.Label(self, text="Enter Your Exiting Time: ", font=("Comic Sans MS", 15, "bold"),
                                fg="black", bg="#d7dde6")
        lableOutTime.place(x=475, y=605)
        spinOutHour = tk.Spinbox(self, from_=1, to=12, font=("Comic Sans MS", 12), textvariable=outhourinsert)
        spinOutHour.place(x=735, y=605, width=150, height=30)
        lab = tk.Label(self, text=":", font=("Comic Sans MS", 15, "bold"), fg="black", bg="#d7dde6").place(
            x=900,
            y=605)
        spinOutminute = tk.Spinbox(self, from_=0, to=60, font=("Comic Sans MS", 12),
                                   textvariable=outminuteinsert)
        spinOutminute.place(x=925, y=605, width=150, height=30)
        tk.Radiobutton(self, text="AM ", variable=outinsert, value=1, font=("Comic Sans MS", 15, "bold"),
                       fg="black", bg="#d7dde6").place(x=1090, y=590)
        tk.Radiobutton(self, text="PM", variable=outinsert, value=2, font=("Comic Sans MS", 15, "bold"),
                       fg="black",
                       bg="#d7dde6").place(x=1090, y=620)

        # buttons
        insertbt = tk.Button(self, text="  Insert  ", font=("Comic Sans MS", 17, "bold"), fg="black",
                             bg="#d7dde6",
                             command=self.Insert)
        backbt = tk.Button(self, text="  Back  ", font=("Comic Sans MS", 17, "bold"), fg="black", bg="#d7dde6",
                           command=self.Back)

        insertbt.place(x=30, y=555, width=150, height=60)
        backbt.place(x=200, y=555, width=150, height=60)

    def dett(self):
        label3 = tk.Label(self)
        if (vinsert.get() == 1):
            lable3 = tk.Label(self, text="Enter Camera Number: ", font=("Comic Sans MS", 15, "bold"), fg="black",
                              bg="#d7dde6")
            lable3.place(x=835, y=170)
            self.entry2 = tk.Entry(self, bd=1, font=(12), textvariable=xinsert)
            self.entry2.place(x=840, y=210, width=300, height=30)
        elif (vinsert.get() == 2):
            lable3 = tk.Label(self, text="Enter File Name :             ", font=("Comic Sans MS", 15, "bold"),
                              fg="black", bg="#d7dde6")
            lable3.place(x=835, y=170)
            self.entry2 = tk.Entry(self, bd=1, font=(12), textvariable=xinsert)
            self.entry2.place(x=840, y=210, width=300, height=30)
            self.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                       filetypes=(("mp4 files", ".mp4"), ("all files", ".*")))
            self.entry2.insert(0, self.filename)


class train(tk.Frame):

    def TrainModel(self):
        if not t.isServer:
            r.set(f.model.trainModel(t.net, t.Client(t.host, t.port, t.mySocket)).data)
        else:
            r.set(f.model.trainModel(t.net, t.Client(t.host, t.port, t.mySocket)))
        var.set(f.getTrainingData())

    def __init__(self, parent, controller):
        global var
        global r
        var = StringVar()
        var.set(f.getTrainingData())
        r = StringVar()
        r.set("")

        if (not t.isServer) and (not isfile("Model.npz")):
            var.set("You Don't have model, please ask for one")

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bg = ImageTk.PhotoImage(file="DYMMO.png")
        self.bg_image = tk.Label(self, image=self.bg).place(x=0, y=0, relwidth=1, relheight=1)
        TrainFrame = tk.Frame(self, bg="black")
        TrainFrame.place(x=35, y=120, height=450, width=500)
        TrainTitle = tk.Label(TrainFrame, text="Train Model :  ", font=("Comic Sans MS", 30, "bold"), fg="white",
                              bg="black")
        TrainTitle.place(x=30, y=70)
        message = tk.Label(TrainFrame, textvariable=r, font=("Comic Sans MS", 15), bg="black", fg="white").place(
            x=75, y=200)
        result = tk.Label(TrainFrame, textvariable=var, font=("Comic Sans MS", 15), fg="black", bg="white").place(
            x=75, y=250, width=380, height=30)
        button1 = tk.Button(TrainFrame, text="Train Model", font=("Comic Sans MS", 17, "bold"), fg="black",
                            bg="#d7dde6", command=self.TrainModel).place(x=75, y=300, width=380, height=40)

        cncelbt = tk.Button(TrainFrame, text="Back", font=("Comic Sans MS", 17, "bold"), fg="black", bg="#d7dde6",
                            command=lambda: controller.show_frame("PageOne")).place(x=75, y=350, width=380,
                                                                                    height=40)


class Edit(tk.Frame):

    def openNewWindow(self):
        # Toplevel object which will
        # be treated as a new window
        newWindow = Toplevel(self)

        # sets the title of the
        # Toplevel widget
        newWindow.title("Select Zone")

        # sets the geometry of toplevel
        newWindow.geometry("200x200")

        zones = f.getAllZones()
        zonesNames = ""

        for zone in zones:
            zonesNames += " " + zone[1]

        valores = StringVar()
        valores.set(zonesNames)

        lstbox = Listbox(newWindow, listvariable=valores, selectmode=MULTIPLE, width=20, height=10)
        lstbox.grid(column=0, row=0, columnspan=2)

        self.zonesToWork = []

        def select():
            self.reslist = list()
            seleccion = lstbox.curselection()
            for i in seleccion:
                entrada = lstbox.get(i)
                self.reslist.append(entrada)

            for zone in self.reslist:
                for zone2 in zones:
                    if zone == zone2[1]:
                        self.zonesToWork.append(zone2[0])

            print(self.zonesToWork)

        btn = Button(newWindow, text="Choices", command=select)
        btn.grid(column=1, row=1)

    def updatePerson(self):
        ssn = editssn.get()
        name = editentry_name.get()
        address = editentry_add.get()
        x = editentry_birth.get()
        print(x)
        birth = dt.datetime.strptime(x, '%d-%m-%Y')
        job = editentry_job.get()
        gender = genderMenu.get()
        ptype = ptypeMenu.get()
        hourin = editinhour.get()
        minutein = editinminute.get()
        hourout = editouthour.get()
        minuteout = editoutminute.get()
        username = editentry_username.get()
        password = editentry_password.get()
        edit_In = editIn.get()
        edit_Out = editout.get()
        method = editv.get()
        arg = editx.get()
        supervisorEdit = subervisorMenu.get()

        if edit_In == 1:
            atime = dt.timedelta(0, int(hourin) * 3600 + int(minutein) * 60)
        else:
            atime = dt.timedelta(0, int(hourin) * 3600 + int(minutein) * 60) + dt.timedelta(0, 43200)
        if edit_Out == 1:
            etime = dt.timedelta(0, int(hourout) * 3600 + int(minuteout) * 60)
        else:
            etime = dt.timedelta(0, int(hourout) * 3600 + int(minuteout) * 60) + dt.timedelta(0, 43200)

        f.updatePerson(ssn, name, address, birth, job, gender, ptype, atime,
                       etime)
        f.updateInPersonSubervisePersons(ssn, f.getSubervisorSsn(supervisorEdit))
        if username:
            if not password:
                t.say("Enter Password to be able to create the permission")
                messagebox.showinfo("Dymmo Says : ", "Enter Password to be able to create the permission")
            else:
                f.updateUserAndPass(ssn, username, password)

        new = t.Person(int(ssn), name, address, birth, job, gender, ptype, atime,
                       etime)
        new.dataNum = f.getPersonDataNumber(int(ssn))

        if arg:
            if method == 1:
                new.dataNum = f.createDatasetFromCamera(int(arg), new)
            elif method == 2:
                new.dataNum = f.createDatasetFromVideo(arg, new)
            else:
                messagebox.showerror("Dymmo cries : ", "Something went wrong")
                return

            f.updateDataset(int(ssn), new.dataNum)

        f.updatePersonWorksInZone(int(ssn), self.zonesToWork)

        t.allPersons = f.getAllCamsForZone()

        messagebox.showinfo("Dymmo Says : ", new.name + " updated")

        # Ask all clients to Update person

        editentry_name.set("")
        editentry_username.set("")  # Optional
        editv.set("1")
        editx.set("")
        editssn.set("")
        editentry_password.set("")  # Optional
        editentry_add.set("")  # Optional
        genderMenu.set("Male")
        editentry_job.set("")
        ptypeMenu.set("")
        subervisorMenu.set("")

        self.reslist = []
        self.zonesToWork = []

        self.controller.show_frame("TestEditMember")

    def delPerson(self):
        ssn = editssn.get()
        name = editentry_name.get()

        if not messagebox.askokcancel("Dymmo asks : ",
                                      "If you deleted " + name + "This will require to retrain the model"):
            return

        try:
            if isfile("Model.npz"):
                remove("Model.npz")

            f.model.deletePerson(ssn)

            f.deletePerson(ssn)
            f.deletePersonSubervisePersons(ssn)
            t.say("Bye " + name)
            messagebox.showinfo("Dymmo Says : ", "Bye " + name)
            self.controller.show_frame("TestEditMember")

            editentry_name.set("")
            editentry_username.set("")  # Optional
            editv.set("1")
            editx.set("")
            editssn.set("")
            editentry_password.set("")  # Optional
            editentry_add.set("")  # Optional
            genderMenu.set("Male")
            editentry_job.set("")
            ptypeMenu.set("")
            subervisorMenu.set("")


        except Exception as e:
            print(e)
            messagebox.showinfo("Dymmo Says : ", "Can't delete him because :" + str(e))

    def Back(self):

        editentry_name.set("")
        editentry_username.set("")  # Optional
        editv.set("1")
        editx.set("")
        editssn.set("")
        editentry_password.set("")  # Optional
        editentry_add.set("")  # Optional
        genderMenu.set("Male")
        editentry_job.set("")
        ptypeMenu.set("")
        self.controller.show_frame("OptionsEdit")

    def __init__(self, parent, controller):
        self.reslist = []
        self.zonesToWork = []

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self['background'] = '#d7dde6'
        # able to store any value
        global editv
        editv = IntVar()
        editv.set("1")
        global editx
        editx = StringVar()
        global editIn
        editIn = IntVar()
        editIn.set("1")
        global editout
        editout = IntVar()
        editout.set("1")
        global editentry_name
        editentry_name = StringVar()
        global editentry_username
        editentry_username = StringVar()
        global editentry_password
        editentry_password = StringVar()
        global editentry_add
        editentry_add = StringVar()
        global editentry_job
        editentry_job = StringVar()
        global editentry_birth
        editentry_birth = StringVar()
        global editinhour
        editinhour = StringVar()
        global editinminute
        editinminute = StringVar()
        global editouthour
        editouthour = StringVar()
        global editoutminute
        editoutminute = StringVar()
        global editssn
        editssn = StringVar()
        global ptypeMenu
        global genderMenu
        global subervisorMenu
        global supervisorName
        supervisorName = StringVar()

        self.left = ImageTk.PhotoImage(file="dymoo3.png")
        tk.Label(self, image=self.left).place(x=0, y=0, height=700, width=400)
        tk.Label(self, text="Edit Member : ", font=("Comic Sans MS", 30, "bold"), fg="black",
                 bg="#d7dde6").place(x=425, y=0)

        Select_zon = tk.Button(self, text="  select zone  ", font=("Comic Sans MS", 17, "bold"), fg="black",
                               bg="#d7dde6",
                               command=self.openNewWindow)
        Select_zon.place(x=835, y=475, width=300, height=40)

        # row 0
        tk.Radiobutton(self, text="from camera ", variable=editv, font=("Comic Sans MS", 15, "bold"),
                       fg="black",
                       bg="#d7dde6", value=1,
                       command=lambda: self.dett()).place(x=475, y=55)
        tk.Radiobutton(self, text="from video ", variable=editv, font=("Comic Sans MS", 15, "bold"), fg="black",
                       bg="#d7dde6", value=2,
                       command=lambda: self.dett()).place(x=635, y=55)
        # row
        lableSSN = tk.Label(self, text="Your SSN : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                            bg="#d7dde6")
        lableSSN.place(x=475, y=105)
        entrySSN = tk.Label(self, font=("Comic Sans MS", 12, "bold"), fg="black", bg="#d7dde6",
                            textvariable=editssn)
        entrySSN.place(x=480, y=140, width=300, height=30)
        lableType = tk.Label(self, text="Enter Your Gender : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                             bg="#d7dde6")
        lableType.place(x=835, y=105)

        genderMenu = ttk.Combobox(self, values=["Male", "Female"], state="readonly")

        genderMenu.config(width=47)
        genderMenu.place(x=840, y=140, height=30)

        # row 1
        lableName = tk.Label(self, text="Your Name : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                             bg="#d7dde6")
        lableName.place(x=475, y=170)
        entryName = tk.Entry(self, bd=1, textvariable=editentry_name, font=(12))
        entryName.place(x=480, y=210, width=300, height=30)

        lable3 = tk.Label(self, text="Camera Number: ", font=("Comic Sans MS", 15, "bold"), fg="black",
                          bg="#d7dde6")
        lable3.place(x=835, y=170)
        entry2 = tk.Entry(self, bd=1, textvariable=editx, font=(12))
        entry2.place(x=840, y=210, width=300, height=30)

        # row 2
        lableUsername = tk.Label(self, text="Your Username : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                                 bg="#d7dde6")
        lableUsername.place(x=475, y=240)
        entryName = tk.Entry(self, bd=1, textvariable=editentry_username, font=(12))
        entryName.place(x=480, y=280, width=300, height=30)

        lablePassword = tk.Label(self, text="Your Password : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                                 bg="#d7dde6")
        lablePassword.place(x=835, y=240)
        entryName = tk.Entry(self, bd=1, textvariable=editentry_password, font=(12))
        entryName.place(x=840, y=280, width=300, height=30)

        # row 3
        lableAddress = tk.Label(self, text="Your Address : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                                bg="#d7dde6")
        lableAddress.place(x=475, y=310)
        entryAdderss = tk.Entry(self, bd=1, textvariable=editentry_add, font=(12))
        entryAdderss.place(x=480, y=350, width=300, height=30)

        lableJob = tk.Label(self, text="Your Job : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                            bg="#d7dde6")
        lableJob.place(x=835, y=310)
        entryJob = tk.Entry(self, bd=1, textvariable=editentry_job, font=(12))
        entryJob.place(x=840, y=350, width=300, height=30)

        # row 4
        lableBirth = tk.Label(self, text="Your Birthday: ", font=("Comic Sans MS", 15, "bold"), fg="black",
                              bg="#d7dde6")
        lableBirth.place(x=475, y=380)
        entryBirth = DateEntry(self, width=12, background='darkblue', bd=1, font=(12), foreground='white',
                               borderwidth=2, textvariable=editentry_birth, date_pattern='dd-mm-y')

        entryBirth.place(x=480, y=420, width=300, height=30)

        lableType = tk.Label(self, text="Your Type : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                             bg="#d7dde6")
        lableType.place(x=835, y=380)
        ptypeMenu = ttk.Combobox(self, values=["Worker", "Admin", "Security Agent", "Supervisor"],
                                 state="readonly")

        ptypeMenu.config(width=47)
        ptypeMenu.place(x=835, y=420, height=30)

        # row 5
        lableSubervisor = tk.Label(self, text="Enter Your Subervisor Name : ",
                                   font=("Comic Sans MS", 15, "bold"), fg="black",
                                   bg="#d7dde6")
        lableSubervisor.place(x=475, y=450)
        types = f.getSubervisorName()
        if types is None:
            types = []
        else:
            types = list(types)
        types.append(' ')
        types.reverse()

        subervisorMenu = ttk.Combobox(self, textvariable=supervisorName, values=types, state="readonly")

        subervisorMenu.place(x=50, y=20)
        subervisorMenu.config(width=46)
        subervisorMenu.place(x=480, y=490, height=30)

        # row 6
        lableInTime = tk.Label(self, text="Your Arrive Time: ", font=("Comic Sans MS", 15, "bold"), fg="black",
                               bg="#d7dde6")
        lableInTime.place(x=475, y=540)
        spinInHour = tk.Spinbox(self, from_=1, to=12, textvariable=editinhour, font=("Comic Sans MS", 12))
        spinInHour.place(x=735, y=540, width=150, height=30)
        tk.Label(self, text=":", font=("Comic Sans MS", 15, "bold"), fg="black", bg="#d7dde6").place(x=900,
                                                                                                     y=540)
        spinInminute = tk.Spinbox(self, from_=0, to=60, textvariable=editinminute, font=("Comic Sans MS", 12))
        spinInminute.place(x=925, y=540, width=150, height=30)
        tk.Radiobutton(self, text="AM ", variable=editIn, value=1, font=("Comic Sans MS", 15, "bold"),
                       fg="black",
                       bg="#d7dde6").place(x=1090, y=525)
        tk.Radiobutton(self, text="PM", variable=editIn, value=2, font=("Comic Sans MS", 15, "bold"),
                       fg="black",
                       bg="#d7dde6").place(x=1090, y=555)

        # row 6
        lableOutTime = tk.Label(self, text="Your Exiting Time: ", font=("Comic Sans MS", 15, "bold"),
                                fg="black",
                                bg="#d7dde6")
        lableOutTime.place(x=475, y=605)
        spinOutHour = tk.Spinbox(self, from_=1, to=12, textvariable=editouthour, font=("Comic Sans MS", 12))
        spinOutHour.place(x=735, y=605, width=150, height=30)
        lab = tk.Label(self, text=":", font=("Comic Sans MS", 15, "bold"), fg="black", bg="#d7dde6").place(
            x=900,
            y=605)
        spinOutminute = tk.Spinbox(self, from_=0, to=60, textvariable=editoutminute, font=("Comic Sans MS", 12))
        spinOutminute.place(x=925, y=605, width=150, height=30)
        tk.Radiobutton(self, text="AM ", variable=editout, value=1, font=("Comic Sans MS", 15, "bold"),
                       fg="black",
                       bg="#d7dde6").place(x=1090, y=590)
        tk.Radiobutton(self, text="PM", variable=editout, value=2, font=("Comic Sans MS", 15, "bold"),
                       fg="black",
                       bg="#d7dde6").place(x=1090, y=620)

        # buttons
        Edittbt = tk.Button(self, text="  Edit  ", font=("Comic Sans MS", 17, "bold"), fg="black", bg="#d7dde6",
                            command=self.updatePerson)
        backbt = tk.Button(self, text="  Back  ", font=("Comic Sans MS", 17, "bold"), fg="black", bg="#d7dde6",
                           command=self.Back)
        btdleat = tk.Button(self, text="  Delete  ", font=("Comic Sans MS", 17, "bold"), fg="black",
                            bg="#d7dde6",
                            command=self.delPerson)
        btdleat.place(x=30, y=620, width=320, height=60)

        Edittbt.place(x=30, y=555, width=150, height=60)
        backbt.place(x=200, y=555, width=150, height=60)

    def dett(self):
        label3 = tk.Label(self)
        if (editv.get() == 1):
            lable3 = tk.Label(self, text=" Camera Number: ", font=("Comic Sans MS", 15, "bold"), fg="black",
                              bg="#d7dde6")
            lable3.place(x=835, y=170)
            self.entry2 = tk.Entry(self, bd=1, textvariable=editx)
            self.entry2.place(x=840, y=210, width=300, height=30)
        elif (editv.get() == 2):
            lable3 = tk.Label(self, text=" Fill Name :             ", font=("Comic Sans MS", 15, "bold"),
                              fg="black", bg="#d7dde6")
            lable3.place(x=835, y=170)
            self.entry2 = tk.Entry(self, bd=1, textvariable=editx)
            self.entry2.place(x=840, y=210, width=300, height=30)
            self.filename = filedialog.askopenfilename(initialdir="/", title="Select file",
                                                       filetypes=(("mp4 files", ".mp4"), ("all files", ".*")))
            self.entry2.insert(0, self.filename)


class cameraControl(tk.Frame):
    def openCam(self, id: int):
        cam = 0
        for camera in t.allCams:
            if id == camera.cm_id:
                cam = camera
                break
        if cam == 0:
            print("Camera Not Found")
            return

        for p in processList:
            if not p.is_alive():
                processList.remove(p)

            if p.name == cam.camName:
                cam.working = False
                destroyWindow(cam.camName)
                t.say("Closing " + p.name)
                return

        cam.working = True
        process = th.Thread(target=cam.recognize, args=(t.net,), daemon=True)
        process.name = cam.camName
        t.say("Opening " + process.name)
        process.start()
        processList.append(process)

    def displayCam(self, id: int):
        cam = 0
        for camera in t.allCams:
            if id == camera.cm_id:
                cam = camera
                break
        if cam == 0:
            print("Camera Not Found")
            return

        camFound = False
        for p in processList:

            if not p.is_alive():
                processList.remove(p)

            if p.name == cam.camName:
                camFound = True

        if camFound:
            cam.displayCam()
            t.say("Displaying " + cam.camName)
        else:
            t.say("Camera " + cam.camName + " is NOT Working Please Lunch it")
            messagebox.showinfo("Dymmo Says : ", "Camera " + cam.camName + " is NOT working, Please lunch it first")

    def close(self):
        if t.userPer == t.PersonType.Admin:
            self.controller.show_frame("PageOne")
        elif t.userPer == t.PersonType.Agnet:
            self.controller.show_frame("StartPage")

    def refresh(self):
        if self.CameraControlFrame is not None:
            self.CameraControlFrame.destroy()
            self.camlist = t.allCams

            self.CameraControlFrame = tk.LabelFrame(self, bg="black", bd=0)

            TestinsertTitle = tk.Label(self.CameraControlFrame, text="Camera Control :  ",
                                       font=("Comic Sans MS", 30, "bold"), fg="white", bg="black")
            TestinsertTitle.place(x=30, y=10)
            SmallFrame = tk.LabelFrame(self.CameraControlFrame, bg="black")
            SmallFrame.place(x=35, y=80, width=450, height=400)
            backbt = tk.Button(self.CameraControlFrame, text="  Back  ", font=("Comic Sans MS", 17, "bold"),
                               fg="black",
                               bg="#d7dde6", command=self.close)

            backbt.place(x=25, y=500, width=150, height=50)
            canvas = tk.Canvas(SmallFrame, bg="black")
            scroll_y = tk.Scrollbar(SmallFrame, orient="vertical", command=canvas.yview)

            frame = tk.Frame(canvas, bg="black")
            for cam in self.camlist:
                button1 = tk.Button(frame, text=cam.camName, font=("Comic Sans MS", 15, "bold"), width=12,
                                    fg="black",
                                    bg="#d7dde6", command=lambda id=cam.cm_id: self.openCam(id))

                openbt = tk.Button(frame, text="  Open  ", font=("Comic Sans MS", 15, "bold"), width=12, fg="black",
                                   bg="#d7dde6", command=lambda id=cam.cm_id: self.displayCam(id))

                button1.grid(row=cam.cm_id, column=1, pady=5, padx=30)
                openbt.grid(row=cam.cm_id, column=3)

                frame.after(500)

            canvas.create_window(0, 0, width=500, height=400, anchor='nw', window=frame)

            canvas.update_idletasks()

            canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scroll_y.set)

            canvas.place(x=0, y=0, relwidth=1, relheight=1)
            scroll_y.pack(fill='y', side='right')

            button1 = tk.Button(self.CameraControlFrame, text="Refresh", font=("Comic Sans MS", 15, "bold"),
                                width=12, fg="black",
                                bg="#d7dde6", command=self.refresh)
            button1.place(x=200, y=500, width=150, height=50)
        self.CameraControlFrame.place(x=35, y=100, width=500, height=550)

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bg = ImageTk.PhotoImage(file="DYMMO.png")
        self.bg_image = tk.Label(self, image=self.bg).place(x=0, y=0, relwidth=1, relheight=1)
        x = IntVar()
        self.camlist = t.allCams
        # Zone of current cam
        self.zone = "Zone 1"
        self.CameraControlFrame = tk.LabelFrame(self, bg="black", bd=0)
        self.CameraControlFrame.place(x=35, y=100, width=500, height=550)
        TestinsertTitle = tk.Label(self.CameraControlFrame, text="Camera Control :  ",
                                   font=("Comic Sans MS", 30, "bold"), fg="white", bg="black")
        TestinsertTitle.place(x=30, y=10)
        SmallFrame = tk.LabelFrame(self.CameraControlFrame, bg="black")
        SmallFrame.place(x=35, y=80, width=450, height=400)
        backbt = tk.Button(self.CameraControlFrame, text="  Back  ", font=("Comic Sans MS", 17, "bold"), fg="black",
                           bg="#d7dde6", command=self.close)

        backbt.place(x=25, y=500, width=150, height=50)
        canvas = tk.Canvas(SmallFrame, bg="black")
        scroll_y = tk.Scrollbar(SmallFrame, orient="vertical", command=canvas.yview)

        frame = tk.Frame(canvas, bg="black")
        for cam in self.camlist:
            button1 = tk.Button(frame, text=cam.camName, font=("Comic Sans MS", 15, "bold"), width=12, fg="black",
                                bg="#d7dde6", command=lambda id=cam.cm_id: self.openCam(id))

            openbt = tk.Button(frame, text="  Open  ", font=("Comic Sans MS", 15, "bold"), width=12, fg="black",
                               bg="#d7dde6", command=lambda id=cam.cm_id: self.displayCam(id))

            button1.grid(row=cam.cm_id, column=1, pady=5, padx=30)
            openbt.grid(row=cam.cm_id, column=3)

            frame.after(500)

        canvas.create_window(0, 0, width=500, height=400, anchor='nw', window=frame)

        canvas.update_idletasks()

        canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scroll_y.set)

        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        scroll_y.pack(fill='y', side='right')

        button1 = tk.Button(self.CameraControlFrame, text="Refresh", font=("Comic Sans MS", 15, "bold"), width=12,
                            fg="black",
                            bg="#d7dde6", command=self.refresh)
        button1.place(x=200, y=500, width=150, height=50)


class zoneControl(tk.Frame):

    def insert(self):
        zoneName = zName.get()
        zoneLocation = location.get()

        if In.get() == 1:
            atime = inhour.get() + ":" + inminute.get()
        else:
            atime = str(int(inhour.get()) + 12) + ":" + inminute.get()
        if out.get() == 1:
            etime = outhour.get() + ":" + outminute.get()
        else:
            etime = str(int(outhour.get()) + 12) + ":" + outminute.get()
        if not zoneName:
            messagebox.showerror("Dymmo says : ", "You forgot to enter zone name")
        elif not inhour.get() or not inminute.get():
            messagebox.showerror("Dymmo says : ", "You forgot to enter arriving time or there's something wrong")
        elif not outhour.get() or not outminute.get():
            messagebox.showerror("Dymmo says : ", "You forgot to enter exiting time or there's something wrong")
        else:
            f.insertZone(zoneName, atime, etime)
            if zoneLocation:
                f.insertZoneLocation(f.getLatestZoneId(), zoneLocation)
            messagebox.showinfo("Dymmo Says : ", "Zone " + zoneName + " inserted Successfully")
            zName.set('')
            location.set('')

        refresh()


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self['background'] = '#d7dde6'
        global zName
        zName = StringVar()
        global location
        location = StringVar()
        global inhour
        inhour = StringVar()
        global inminute
        inminute = StringVar()
        global outhour
        outhour = StringVar()
        global outminute
        outminute = StringVar()
        global In
        In = IntVar()
        In.set(1)
        global out
        out = IntVar()
        out.set(1)
        # row 0
        self.left = ImageTk.PhotoImage(file="dymoo3.png")
        left = tk.Label(self, image=self.left).place(x=0, y=0, height=700, width=400)
        AddZoneTitle = tk.Label(self, text="Add Zone : ", font=("Comic Sans MS", 30, "bold"), fg="black",
                                bg="#d7dde6").place(x=425, y=50)

        # row 1
        Label(self, text="Enter Zone Name : ", font=("Comic Sans MS", 15, "bold"), fg="black", bg="#d7dde6").place(
            x=475, y=170)
        Entry(self, textvariable=zName, bd=1, font=("Comic Sans MS", 12)).place(x=480, y=210, width=600, height=30)

        # row 2
        Label(self, text="Enter Zone Location : ", font=("Comic Sans MS", 15, "bold"), fg="black",
              bg="#d7dde6").place(x=475, y=270)
        Entry(self, textvariable=location, bd=1, font=("Comic Sans MS", 12)).place(x=480, y=310, width=600,
                                                                                   height=30)

        # row 3
        lableInTime = tk.Label(self, text="Enter Zone Arrive Time : ", font=("Comic Sans MS", 15, "bold"),
                               fg="black", bg="#d7dde6")
        lableInTime.place(x=475, y=370)
        spinInHour = tk.Spinbox(self, from_=1, to=12, textvariable=inhour, font=("Comic Sans MS", 12))
        spinInHour.place(x=735, y=370, width=150, height=30)
        tk.Label(self, text=":", font=("Comic Sans MS", 15, "bold"), fg="black", bg="#d7dde6").place(x=900, y=370)
        spinInminute = tk.Spinbox(self, from_=0, to=59, textvariable=inminute, font=("Comic Sans MS", 12))
        spinInminute.place(x=925, y=370, width=150, height=30)
        tk.Radiobutton(self, text="AM ", variable=In, value=1, font=("Comic Sans MS", 15, "bold"), fg="black",
                       bg="#d7dde6").place(x=1090, y=355)
        tk.Radiobutton(self, text="PM", variable=In, value=2, font=("Comic Sans MS", 15, "bold"), fg="black",
                       bg="#d7dde6").place(x=1090, y=385)

        # row 5
        lableInTime = tk.Label(self, text="Enter Zone Exit Time : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                               bg="#d7dde6")
        lableInTime.place(x=475, y=440)
        spinInHour = tk.Spinbox(self, from_=1, to=12, textvariable=outhour, font=("Comic Sans MS", 12))
        spinInHour.place(x=735, y=440, width=150, height=30)
        tk.Label(self, text=":", font=("Comic Sans MS", 15, "bold"), fg="black", bg="#d7dde6").place(x=900, y=440)
        spinInminute = tk.Spinbox(self, from_=0, to=59, textvariable=outminute, font=("Comic Sans MS", 12))
        spinInminute.place(x=925, y=440, width=150, height=30)
        tk.Radiobutton(self, text="AM ", variable=out, value=1, font=("Comic Sans MS", 15, "bold"), fg="black",
                       bg="#d7dde6").place(x=1090, y=425)
        tk.Radiobutton(self, text="PM", variable=out, value=2, font=("Comic Sans MS", 15, "bold"), fg="black",
                       bg="#d7dde6").place(x=1090, y=455)

        # row 7
        Button(self, text="Insert", font=("Comic Sans MS", 17, "bold"), fg="black", bg="#d7dde6",
               command=self.insert).place(x=30, y=555, width=150, height=60)
        Button(self, text="Back", font=("Comic Sans MS", 17, "bold"), fg="black", bg="#d7dde6",
               command=lambda: controller.show_frame("Options")).place(x=200, y=555, width=150, height=60)


class zoneEdit(tk.Frame):

    def edit(self):
        zname = namezone.get()
        ihour = inhourzone.get()
        ohour = outhourzone.get()
        imin = inminutezone.get()
        omin = outminutezone.get()
        inMesuarse = Inzone.get()
        outMesuasre = outzone.get()
        if not zname:
            messagebox.showinfo("Dymmo Says : ", "You should enter name")
            return
        if inMesuarse == 2:
            ihour = str(int(ihour) + 12)
        if outMesuasre == 2:
            ohour = str(int(ohour) + 12)
        try:
            f.updateZone(zname, ihour + ":" + imin, ohour + ":" + omin)
        except Exception as e:
            print(e)
            return

        messagebox.showinfo("Dymmo Says : ", zname + " updated successfully")

        namezone.set("")
        self.controller.show_frame("TestEditZone")

        f.getZoneById(t.myZone)
        refresh()

    def delZone(self):
        zname = namezone.get()

        if not messagebox.askokcancel("Dymmo Says : ",
                                      "Are you sure you want to delete " + zname + "\n\nThis may harm employees data"):
            return

        try:
            f.deleteZone(zname)
            t.say(zname + " has been deleted")
            messagebox.showinfo("Dymmo Says : ", zname + " has been deleted")
            namezone.set("")
            self.controller.show_frame("TestEditZone")
            refresh()
        except Exception as e:
            print(e)
            messagebox.showinfo("Dymmo Says : ", "Can't delete it because : " + str(e))

    def Back(self):
        namezone.set("")
        self.controller.show_frame("OptionsEdit")

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self['background'] = '#d7dde6'
        global namezone
        namezone = StringVar()

        global locationzone
        locationzone = StringVar()

        global inhourzone
        inhourzone = StringVar()

        global inminutezone
        inminutezone = StringVar()

        global outhourzone
        outhourzone = StringVar()

        global outminutezone
        outminutezone = StringVar()

        global Inzone
        Inzone = IntVar()
        Inzone.set(1)

        global outzone
        outzone = IntVar()
        outzone.set(1)

        self.left = ImageTk.PhotoImage(file="dymoo3.png")
        left = tk.Label(self, image=self.left).place(x=0, y=0, height=700, width=400)
        AddZoneTitle = tk.Label(self, text="Edit Zone : ", font=("Comic Sans MS", 30, "bold"), fg="black",
                                bg="#d7dde6").place(x=425, y=50)

        # row 1
        Label(self, text="Zone Name : ", font=("Comic Sans MS", 15, "bold"), fg="black",
              bg="#d7dde6").place(x=475, y=170)
        Entry(self, textvariable=namezone, bd=1, font=("Comic Sans MS", 12)).place(x=480, y=210, width=600,
                                                                                   height=30)

        # row 2
        Label(self, text="Zone Location : ", font=("Comic Sans MS", 15, "bold"), fg="black",
              bg="#d7dde6").place(x=475, y=270)
        Entry(self, textvariable=locationzone, bd=1, font=("Comic Sans MS", 12)).place(x=480, y=310, width=600,
                                                                                       height=30)

        # row 3
        lableInTime = tk.Label(self, text="Zone Arrive Time : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                               bg="#d7dde6")
        lableInTime.place(x=475, y=370)
        spinInHour = tk.Spinbox(self, from_=1, to=12, textvariable=inhourzone, font=("Comic Sans MS", 12))
        spinInHour.place(x=735, y=370, width=150, height=30)
        tk.Label(self, text=":", font=("Comic Sans MS", 15, "bold"), fg="black",
                 bg="#d7dde6").place(x=900, y=370)
        spinInminute = tk.Spinbox(self, from_=0, to=59, textvariable=inminutezone, font=("Comic Sans MS", 12))
        spinInminute.place(x=925, y=370, width=150, height=30)
        tk.Radiobutton(self, text="AM ", variable=Inzone, value=1, font=("Comic Sans MS", 15, "bold"), fg="black",
                       bg="#d7dde6").place(x=1090, y=355)
        tk.Radiobutton(self, text="PM", variable=Inzone, value=2, font=("Comic Sans MS", 15, "bold"), fg="black",
                       bg="#d7dde6").place(x=1090, y=385)

        # row 5
        lableInTime = tk.Label(self, text="Zone Exit Time : ", font=("Comic Sans MS", 15, "bold"), fg="black",
                               bg="#d7dde6")
        lableInTime.place(x=475, y=440)
        spinInHour = tk.Spinbox(self, from_=1, to=12, textvariable=outhourzone, font=("Comic Sans MS", 12))
        spinInHour.place(x=735, y=440, width=150, height=30)
        tk.Label(self, text=":", font=("Comic Sans MS", 15, "bold"), fg="black",
                 bg="#d7dde6").place(x=900, y=440)
        spinInminute = tk.Spinbox(self, from_=0, to=59, textvariable=outminutezone, font=("Comic Sans MS", 12))
        spinInminute.place(x=925, y=440, width=150, height=30)
        tk.Radiobutton(self, text="AM ", variable=outzone, value=1, font=("Comic Sans MS", 15, "bold"), fg="black",
                       bg="#d7dde6").place(x=1090, y=425)
        tk.Radiobutton(self, text="PM", variable=outzone, value=2, font=("Comic Sans MS", 15, "bold"), fg="black",
                       bg="#d7dde6").place(x=1090, y=455)

        # row 7
        Button(self, text="Edit", font=("Comic Sans MS", 17, "bold"), fg="black",
               bg="#d7dde6", command=self.edit).place(x=30, y=555, width=150, height=60)
        Button(self, text="Back", font=("Comic Sans MS", 17, "bold"), fg="black",
               bg="#d7dde6", command=self.Back).place(x=200, y=555, width=150, height=60)
        btdleat = tk.Button(self, text="  Delete  ", font=("Comic Sans MS", 17, "bold"), fg="black",
                            bg="#d7dde6",
                            command=self.delZone)
        btdleat.place(x=30, y=620, width=320, height=60)


class cameracreate(tk.Frame):
    def openCam(self):

        if self.process.is_alive():
            messagebox.showinfo('Dymmo Says : ', 'Another camera is opened')
            return

        if combovalue.get() == "Select Camera":
            messagebox.showinfo("Dymmo Says : ", "Select camera first")
            return

        x = int(combovalue.get().split(' ')[1])
        camera = t.Camtype(x, "Camera " + str(x), "", True)
        self.process = th.Thread(target=camera.open)
        self.process.name = "TestCamera"
        self.process.start()

    def insertCamera(self):
        if combovalue.get() == "Select Camera":
            messagebox.showinfo("Dymmo Says : ", "You should select camera first :)")
            return

        Id = int(combovalue.get().split(" ")[1])
        Zone = t.myZone
        status = bool(v.get())
        Name = name.get()

        if not Name:
            messagebox.showinfo("Dymmo Says : ", "You have to enter camera name ")
            return

        dat = dt.datetime.strptime(date.get(), '%d-%m-%Y')

        c = t.Camtype(cam_id=Id, cam_name=Name, zone=str(Zone), is_entering=status, date=dat)

        f.insertCamera(c)
        messagebox.showinfo("Dymmo Says : ", "Camera " + Name + " Inserted To Database")

        name.set("")
        v.set("1")
        refresh()

    def Back(self):
        name.set("")
        v.set("1")
        self.controller.show_frame("Options")

    def __init__(self, parent, controller):
        self.process = th.Thread()

        global name
        name = StringVar()

        global v
        v = IntVar()
        v.set("1")

        global date
        date = StringVar()

        global CameraZone
        CameraZone = StringVar()
        CameraZone.set("You are in " + t.myZoneName)

        global combovalue

        cams = ["Select Camera"]

        for i in range(t.numberOfCameras):
            cams.append("Camera " + str(i))

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self['background'] = '#d7dde6'
        # row0
        self.left = ImageTk.PhotoImage(file="dymoo3.png")
        left = tk.Label(self, image=self.left).place(x=0, y=0, height=700, width=400)
        Addcameratitle = tk.Label(self, text="Add Camera : ", font=("Comic Sans MS", 30, "bold"), fg="black",
                                  bg="#d7dde6").place(x=425, y=60)
        combovalue = ttk.Combobox(self, values=cams, state="readonly")
        combovalue.current(0)

        combovalue.place(x=475, y=170, width=600, height=30)
        buton1 = tk.Button(self, text="Open", bd=1, font=("Comic Sans MS", 15, "bold"), fg="white",
                           bg="#272626", command=self.openCam).place(x=475, y=230, width=600, height=40)
        camerneme = tk.Label(self, text='Enter Camera Name :', font=("Comic Sans MS", 15, "bold"), fg="black",
                             bg="#d7dde6").place(x=475, y=290)
        enteryname = tk.Entry(self, bd=1, font=("Comic Sans MS", 12), textvariable=name).place(x=480, y=340,
                                                                                               width=600, height=30)
        camerdate = tk.Label(self, text='Enter Camera Date Recorded :', font=("Comic Sans MS", 15, "bold"),
                             fg="black",
                             bg="#d7dde6").place(x=475, y=400)
        entryCamDate = DateEntry(self, width=12, background='darkblue', bd=1, font=(12), foreground='white',
                                 borderwidth=2, textvariable=date, date_pattern='dd-mm-y')
        entryCamDate.place(x=475, y=450, width=600, height=35)
        tk.Radiobutton(self, text="Entry Camera ", variable=v, value=1, font=("Comic Sans MS", 15, "bold"),
                       fg="black",
                       bg="#d7dde6").place(x=475, y=510)
        tk.Radiobutton(self, text="Exiting Camera", variable=v, value=0, font=("Comic Sans MS", 15, "bold"),
                       fg="black",
                       bg="#d7dde6").place(x=775, y=510)
        camerzone = tk.Label(self, textvariable=CameraZone, font=("Comic Sans MS", 15, "bold"), fg="black",
                             bg="#d7dde6").place(x=475, y=570, width=600, height=30)
        buton1 = tk.Button(self, text="Insert", font=("Comic Sans MS", 17, "bold"), fg="black", bg="#d7dde6",
                           command=self.insertCamera)
        buton1.place(x=30, y=555, width=150, height=60)
        buton2 = tk.Button(self, text="Back", font=("Comic Sans MS", 17, "bold"), fg="black",
                           bg="#d7dde6", command=self.Back)
        buton2.place(x=200, y=555, width=150, height=60)


class Configure(tk.Frame):

    def setNewConfig(self):

        x = self.CurrentZone.get()
        newZone = 0
        for pos, zone in enumerate(self.ZonesName):
            if zone == x:
                newZone = pos
                break

        if messagebox.askokcancel("Dymmo Says : ",
                                  "This will close the program\n\nYou will have to open the program again"):
            file = open('Config.ini', 'w')

            if not file.writable:
                messagebox.showerror("Dymmo Says : ", "Config.ini is NOT writable...")
                return

            file.write("CurrentZone:" + str(self.ZonesIds[newZone]) + '\n')
            file.write("Host:" + Hostname.get() + '\n')
            file.write("Username:" + HostUsername.get() + '\n')
            file.write("Password:" + Hostpass.get() + '\n')
            file.write("isServer:" + str(Server_ch.get()) + '\n')
            file.write("isMain:" + str(isAMainZone.get()) + '\n')
            file.write("Port:" + str(Port_N.get()) + '\n')
            file.write("Clients:" + str(Cliant_N.get()) + '\n')

            t.programExit()

            exit(0)

    def back(self):
        Hostname.set(t.host)
        Hostpass.set(t.password)
        HostUsername.set(t.user)
        Port_N.set(str(t.port))
        Cliant_N.set(str(t.numberOfAllowedClients))

        if t.isServer:
            Server_ch.set(1)
        else:
            Server_ch.set(0)

        if t.checkValidConfig():
            self.controller.show_frame("StartPage")
        else:
            messagebox.showerror("Dymmo Says : ", "Config.ini is inValid")


    def clic(self):
        self.CurrentZone.destroy()
        if t.validConfig:
            allZones = f.getAllZones()
        else:
            allZones = [(0,'Nozone')]

        self.ZonesName = [x[1] for x in allZones]
        self.ZonesIds = [x[0] for x in allZones]
        zoneNumber = 0
        for pos, zone in enumerate(self.ZonesName):
            if zone == t.myZoneName:
                zoneNumber = pos
                break
        self.CurrentZone = ttk.Combobox(CNfuFrame,
                                   values=self.ZonesName,
                                   state="readonly", font=("Comic Sans MS", 12))
        self.CurrentZone.current(zoneNumber)
        self.CurrentZone.place(x=75, y=80, width=300, height=30)


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        global HostUsername
        HostUsername = StringVar()
        global Hostname
        Hostname = StringVar()
        global Hostpass
        Hostpass = StringVar()
        global Port_N
        Port_N = IntVar()
        global Cliant_N
        Cliant_N = IntVar()
        global Server_ch
        Server_ch = IntVar()
        global CurrentZone
        global CNfuFrame
        global isAMainZone
        isAMainZone = IntVar()


        Hostname.set(t.host)
        Hostpass.set(t.password)
        HostUsername.set(t.user)
        Port_N.set(str(t.port))
        Cliant_N.set(str(t.numberOfAllowedClients))

        if t.isServer:
            Server_ch.set(1)
        else:
            Server_ch.set(0)

        if t.isMainZone:
            isAMainZone.set(1)
        else:
            isAMainZone.set(0)

        if t.validConfig:
            allZones = f.getAllZones()
        else:
            allZones = [(0,'Nozone')]

        self.ZonesName = [x[1] for x in allZones]
        self.ZonesIds = [x[0] for x in allZones]

        zoneNumber= 0
        for pos, zone in enumerate(self.ZonesName):
            if zone == t.myZoneName:
                zoneNumber = pos
                break
        # row0
        self.bg = ImageTk.PhotoImage(file="dymmo2.png")
        self.bg_image = tk.Label(self, image=self.bg).place(x=0, y=0, relwidth=1, relheight=1)
        CNfuFrame = tk.Frame(self, bg="black")
        CNfuFrame.place(x=35, y=120, height=600, width=500)
        # row1
        zone_cr = tk.Label(CNfuFrame, text="Select current zoon : ", font=("Comic Sans MS", 15, "bold"), fg="white",
                           bg="black")
        self.CurrentZone = ttk.Combobox(CNfuFrame,
                                   values=self.ZonesName,
                                   state="readonly", font=("Comic Sans MS", 12))
        self.CurrentZone.current(zoneNumber)
        # row2
        Host_name = tk.Label(CNfuFrame, text="Host name : ", font=("Comic Sans MS", 15, "bold"), fg="white",
                             bg="black")
        Host_nameE = tk.Entry(CNfuFrame, textvariable=Hostname, bd=1, font=("Comic Sans MS", 12))

        user_name = tk.Label(CNfuFrame, text="user name : ", font=("Comic Sans MS", 15, "bold"), fg="white", bg="black")
        user_nameE = tk.Entry(CNfuFrame, textvariable=HostUsername, bd=1, font=("Comic Sans MS", 12))

        # row3
        Host_password = tk.Label(CNfuFrame, text="Host password", font=("Comic Sans MS", 14, "bold"), fg="white",
                                 bg="black")
        Host_paswordE = tk.Entry(CNfuFrame, textvariable=Hostpass, bd=1, font=("Comic Sans MS", 12))
        # row4
        Port_lable = tk.Label(CNfuFrame, text="Enter port : ", font=("Comic Sans MS", 15, "bold"), fg="white",
                              bg="black")
        PortE = tk.Entry(CNfuFrame, textvariable=Port_N, bd=1, font=("Comic Sans MS", 12))
        # row5
        Numperof_cl = tk.Label(CNfuFrame, text="Number Of Clients : ", font=("Comic Sans MS", 15, "bold"),
                               fg="white", bg="black")
        Numperof_clE = tk.Entry(CNfuFrame, textvariable=Cliant_N, bd=1, font=("Comic Sans MS", 12))
        # row6
        IS_Server = tk.Checkbutton(CNfuFrame, text='Is server', font=("Comic Sans MS", 13, "bold"),
                                   foreground="red", bg="black",
                                   variable=Server_ch, onvalue=1, offvalue=0, )

        IS_main_zone = tk.Checkbutton(CNfuFrame, text='Is main zoon', font=("Comic Sans MS", 13, "bold"),
                                      foreground="red",
                                      bg="black", variable=isAMainZone, onvalue=1, offvalue=0)

        Apply_Btn = tk.Button(CNfuFrame, text="Apply", font=("Comic Sans MS", 17, "bold"), fg="black",
                              bg="#d7dde6", command=self.setNewConfig)
        BACK_Btn = tk.Button(CNfuFrame, text="Back", font=("Comic Sans MS", 17, "bold"), fg="black",
                             bg="#d7dde6", command=self.back)
        buton_refresh = tk.Button(CNfuFrame, text="Refresh", font=("Comic Sans MS", 17, "bold"), fg="black",
                             bg="#d7dde6", command=self.clic)
        zone_cr.place(x=75, y=50)
        self.CurrentZone.place(x=75, y=80, width=300, height=30)

        Host_name.place(x=75, y=110)
        Host_nameE.place(x=75, y=140, width=300, height=30)

        user_name.place(x=75, y=170, width=140)
        Host_password.place(x=235, y=170, width=150)
        user_nameE.place(x=75, y=200, width=140, height=30)
        Host_paswordE.place(x=235, y=200, width=140, height=30)
        Port_lable.place(x=75, y=230)
        PortE.place(x=75, y=260, width=300, height=30)
        Numperof_cl.place(x=75, y=290)
        Numperof_clE.place(x=75, y=320, width=300, height=30)
        IS_Server.place(x=75, y=365)
        Apply_Btn.place(x=75, y=420, width=300, height=40)
        BACK_Btn.place(x=75, y=480, width=140, height=40)
        buton_refresh.place(x=235, y=480, width=140, height=40)
        IS_main_zone.place(x=235, y=365, width=140)



class DirectRecord(tk.Frame):
    def close(self):
        if t.userPer == t.PersonType.Admin:
            self.controller.show_frame("PageOne")
        elif t.userPer == t.PersonType.Supervisor:
            self.controller.show_frame("StartPage")

    def update(self):

        tv = ttk.Treeview(self, columns=(1, 2, 3), show="headings", height=100)
        tv.place(x=430, y=60, width=730, height=600)
        tv['columns'] = ("Date", "Time", "Describtion")
        tv.column("Date", anchor=CENTER, width=20)
        tv.column("Time", anchor=CENTER, width=20)
        tv.column("Describtion", anchor=W, width=500)
        tv.heading("Date", text="Date")
        tv.heading("Time", text="Time")
        tv.heading("Describtion", text="Describtion")
        tv.tag_configure('odd', background="lightblue")
        tv.tag_configure('even', background="white")
        rows = f.getRecordDescribtion()
        count = 0
        for i in rows[0:50]:
            if count % 2 == 0:
                tv.insert('', 'end', values=i, tags=('even',))
            else:
                tv.insert('', 'end', values=i, tags=('odd',))
            count += 1

        self.after(3000, self.update)

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self['background'] = '#d7dde6'
        self.left = ImageTk.PhotoImage(file="dymoo3.png")

        style = ttk.Style(self)
        style.configure('Treeview', rowheight=50)
        tk.Label(self, image=self.left).place(x=0, y=0, height=700, width=400)
        tk.Label(self, text="Direct Records : ", font=("Comic Sans MS", 25, "bold"), fg="black",
                 bg="#d7dde6").place(x=425, y=3)

        tv = ttk.Treeview(self, columns=(1, 2, 3), show="headings", height="10")
        tv.place(x=430, y=60, width=730, height=600)
        tv['columns'] = ("Date", "Time", "Describtion")
        tv.column("Date", anchor=CENTER, width=20)
        tv.column("Time", anchor=CENTER, width=20)
        tv.column("Describtion", anchor=W, width=500)
        tv.heading("Date", text="Date")
        tv.heading("Time", text="Time")
        tv.heading("Describtion", text="Describtion")

        rows = f.getRecordDescribtion()
        tv.tag_configure('odd', background="lightblue")
        tv.tag_configure('even', background="white")
        global count
        count = 0
        for i in rows[0:50]:
            if count % 2 == 0:
                tv.insert('', 'end', values=i, tags=('even',))
            else:
                tv.insert('', 'end', values=i, tags=('odd',))
            count += 1
        tk.Button(self, text="Close", font=("Comic Sans MS", 20, "bold"), fg="black",
                  bg="#d7dde6", command=self.close).place(x=50, y=570, width=300, height=60)

        self.update()


class SReport(tk.Frame):

    def onclick(self):

        day = reportDay.get()
        month = reportMonth.get()
        year = reportYear.get()

        stime, etime = '', ''

        if reportSTime.get():
            stime = int(reportSTime.get())
        if reportETime.get():
            etime = int(reportETime.get())

        if stime:
            if not reportSTime.get().isdigit():
                messagebox.showerror('Dymmo Says : ', "Start time can't have letter")
                return

        if etime:
            if not reportETime.get().isdigit():
                messagebox.showerror('Dymmo Says : ', "End time can't have letter")
                return

        rType = self.types[self.reportTypes.index(reportType.get())]

        inTime = InReport.get()
        outTime = outReport.get()

        if inTime == 1 and stime == 12:
            stime = 0
        elif inTime == 2:
            stime += 12

        if outTime == 1 and etime == 12:
            etime = 0
        if outTime == 2:
            etime += 12

        nefram.pack()
        for i in tvOmar.get_children(): tvOmar.delete(i)
        for i in f.getRecordsForSecurity(year, month, day, str(stime), str(etime), rType): tvOmar.insert('', 'end',
                                                                                                         values=i)

        nefram.place(x=450, y=100, height=550, width=700)

    def showProf(self):
        rID = recordNumber.get()

        if not rID:
            messagebox.showinfo('Dymmo Says : ', 'You should enter record id...')
            return

        path = f.getProfPath(rID)

        if path is None or path == '':
            messagebox.showinfo('Dymmo Says : ', 'No path available for this record')
            return

        f.getProfWithPath(path)

    def __init__(self, parent, controller):

        global nefram
        global tvOmar

        global reportDay
        global reportMonth
        global reportYear
        global reportPName
        reportPName = StringVar()
        reportDay = StringVar()
        reportYear = StringVar()
        reportMonth = StringVar()

        global reportSTime
        global reportETime

        reportSTime = StringVar()
        reportETime = StringVar()

        global reportType
        reportType = StringVar()

        global InReport
        InReport = IntVar()

        global outReport
        outReport = IntVar()

        global recordNumber
        recordNumber = StringVar()

        self.reportTypes = ['Select All', 'Security Report', 'Entering in time', 'Entering Early', 'Entering Late',
                            'Invalid Enter', 'Exiting Early', 'Exiting in time', 'Exiting Late']
        self.types = ['', 'Security', 'Entering', 'EarlyEnter', 'LateEnter', 'InvalidEnter', 'EarlyExit', 'Exiting',
                      'LateExit']

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.bg = ImageTk.PhotoImage(file="dymmo2.png")
        self.bg_image = tk.Label(self, image=self.bg).place(x=0, y=0, relwidth=1, relheight=1)
        frm = tk.Frame(self, bg="black")
        # row0
        personlabl = tk.Label(frm, text='Search with name :', font=("Comic Sans MS", 15, "bold"), fg="white",
                              bg="black")
        ent = tk.Entry(frm, textvariable=reportPName, bg="#d7dde6")
        # row1
        Dlabl = tk.Label(frm, text='D:', font=("Comic Sans MS", 15, "bold"), fg="white", bg="black")
        Mlabl = tk.Label(frm, text='M:', font=("Comic Sans MS", 15, "bold"), fg="white", bg="black")
        Ylabl = tk.Label(frm, text='Y:', font=("Comic Sans MS", 15, "bold"), fg="white", bg="black")
        Dayent = tk.Entry(frm, textvariable=reportDay, bg="#d7dde6")
        Ment = tk.Entry(frm, textvariable=reportMonth, bg="#d7dde6")
        Yent = tk.Entry(frm, textvariable=reportYear, bg="#d7dde6")
        # row3
        Ent_labl = tk.Label(frm, text='Enter:', font=("Comic Sans MS", 15, "bold"), fg="white", bg="black")
        Out_labl = tk.Label(frm, text='Exit:', font=("Comic Sans MS", 15, "bold"), fg="white", bg="black")
        Ent_ent = tk.Entry(frm, textvariable=reportSTime, bg="#d7dde6")
        Out_ent = tk.Entry(frm, textvariable=reportETime, bg="#d7dde6")

        tk.Radiobutton(frm, text="AM ", variable=InReport, value=1, font=("Comic Sans MS", 15, "bold"),
                       foreground="red",
                       bg="black").place(x=145, y=300)
        tk.Radiobutton(frm, text="PM", variable=InReport, value=2, font=("Comic Sans MS", 15, "bold"),
                       foreground="red",
                       bg="black").place(x=145, y=340)
        tk.Radiobutton(frm, text="AM ", variable=outReport, value=1, font=("Comic Sans MS", 15, "bold"),
                       foreground="red",
                       bg="black").place(x=295, y=300)
        tk.Radiobutton(frm, text="PM", variable=outReport, value=2, font=("Comic Sans MS", 15, "bold"),
                       foreground="red",
                       bg="black").place(x=295, y=340)
        # row 4
        Tyabl = tk.Label(frm, text='Type:', font=("Comic Sans M S", 15, "bold"), fg="white", bg="black")
        TYb_select = ttk.Combobox(frm, textvariable=reportType,
                                  values=self.reportTypes,
                                  state="readonly", font=("Comic Sans MS", 12))
        TYb_select.current(0)
        searchbtn = tk.Button(frm, text="Show", font=("Comic Sans MS", 17, "bold"), fg="black", bg="#d7dde6",
                              command=self.onclick)
        buton_back = tk.Button(frm, text="Back", font=("Comic Sans MS", 17, "bold"), fg="black",
                               bg="#d7dde6", command=lambda: controller.show_frame("Options"))
        nefram = tk.Frame(self, bg="black")
        # nfrow1
        tvOmar = ttk.Treeview(nefram, columns=(1, 2, 3, 4, 5), show="headings")

        tvOmar['columns'] = ("Id", "Date", "Time", "Description", "Arg")
        tvOmar.column("Id", anchor=CENTER, width=30)
        tvOmar.column("Date", anchor=CENTER, width=30)
        tvOmar.column("Time", anchor=CENTER, width=30)
        tvOmar.column("Arg", anchor=CENTER, width=30)
        tvOmar.column("Description", anchor=W, width=300)
        tvOmar.heading("Date", text="Date")
        tvOmar.heading("Time", text="Time")
        tvOmar.heading("Arg", text="Argument")
        tvOmar.heading("Id", text="#")
        tvOmar.heading("Description", text="Description")
        tvOmar.insert('', 'end', values=("00-00-0000", "00:00", "0", "None", "0"))
        # nfrow2
        R_id_lable = tk.Label(nefram, text='Get Report Prof :', font=("Comic Sans MS", 15, "bold"), fg="white", bg="black")
        R_id_ent = tk.Entry(nefram, textvariable=recordNumber, bg="#d7dde6")
        Show_image_btn = tk.Button(nefram, text="Show", font=("Comic Sans MS", 17, "bold"), fg="black",
                                   bg="#d7dde6",command=self.showProf)
        scroll_show = tk.Label(nefram, text='Use mouse to scroll', font=("Comic Sans MS", 15, "bold"), fg="red",
                               bg="black")

        tvOmar.place(x=5, y=5, width=690, height=480)
        R_id_lable.place(x=5, y=500, width=150)
        R_id_ent.place(x=170, y=500, width=150, height=30)
        Show_image_btn.place(x=335, y=500, width=150, height=30)
        scroll_show.place(x=500, y=500)

        frm.place(x=35, y=100, height=600, width=400)
        personlabl.place(x=75, y=140)
        ent.place(x=75, y=180, height=30, width=300)
        Dlabl.place(x=75, y=220, height=30, width=90)
        Mlabl.place(x=180, y=220, height=30, width=90)
        Ylabl.place(x=285, y=220, height=30, width=90)
        Dayent.place(x=75, y=260, height=30, width=90)
        Ment.place(x=180, y=260, height=30, width=90)
        Yent.place(x=285, y=260, height=30, width=90)

        Ent_labl.place(x=75, y=300, height=30, width=60)
        Out_labl.place(x=225, y=300, height=30, width=60)
        Ent_ent.place(x=75, y=340, height=30, width=60)
        Out_ent.place(x=225, y=340, height=30, width=60)
        Tyabl.place(x=75, y=380)
        TYb_select.place(x=75, y=420, width=300, height=30)

        searchbtn.place(x=75, y=460, width=300, height=40)
        buton_back.place(x=75, y=510, width=300, height=40)


app = MainUI()

if not t.checkValidConfig():
    app.show_frame("Configure")
app.wm_iconbitmap('dymmo.ico')
app.mainloop()

t.programExit()
