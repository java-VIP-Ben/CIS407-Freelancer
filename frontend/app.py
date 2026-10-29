from tkinter import *
import customtkinter
from CTkTable import CTkTable

# matches users theme and all widgets are blue
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

testData = [[1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5],[1,2,3,4,5]]


# buttons
class MyButtonCluster(customtkinter.CTkFrame):
    def __init__(self,master):
        super().__init__(master)

        self.bg_color="#6b606085"

        self.nameLBL = customtkinter.CTkLabel(self,text="Name of Freelancer")
        self.nameLBL.grid(row=0,column=0,padx=10,pady=(10,0))

        # test btn
        self.homeBTN = customtkinter.CTkButton(self, text="Home",command=self.buttonCallback)
        self.homeBTN.grid(row=0,column=1,padx=10,pady=(10,0),sticky=W)

        self.tableTest = CTkTable(master=self, row=4, column=5,values=testData)
        self.tableTest.grid(row=1,column=0,padx=10,pady=(10,0))

    # button command - must be outside __init__ function but in the class
    def buttonCallback(self):
        print("button pressed")
        

    
# main window
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # name of window
        self.title("Freelancer")
        # window size
        self.geometry("1080x720")

        # buttons
        self.loginBTN = MyButtonCluster(self)
        self.loginBTN.grid(row=0,column=0,padx=10,pady=(10,0))

    


        

app = App()
app.mainloop()
