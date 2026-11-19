from tkinter import *
import customtkinter

# matches users theme and all widgets are blue
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")
    
# main window
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # name of window
        self.title("Freelancer")

        # window size
        self.geometry("1080x720")

        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(1,weight=1)


        self.mainContainer = customtkinter.CTkFrame(self,corner_radius=0)
        self.mainContainer.grid(row=1,column=0,sticky="nsew")


        self.scrollFrame = customtkinter.CTkScrollableFrame(self,fg_color="transparent",label_text="Find Your Freelancer")
        self.scrollFrame.grid(row=1,column=0,padx=10,pady=10,sticky="nsew")
        self.scrollFrame.grid_columnconfigure(0,weight=1)

        

        itemsData = [
            {"freelanceName": "Mike Hawk", "skill": "flying"},
            {"freelanceName": "Jonah Zoller", "skill": "plumbing"},
            {"freelanceName": "Benjamin Lukens", "skill": "vehicle repair"},
            {"freelanceName": "Joe Piper", "skill": "flying"}
        ]
        
    
        for index, data in enumerate(itemsData):
            self.create_freelancer_card(index, data.get("freelanceName"), data.get("skill"))

        navBar = customtkinter.CTkFrame(self,height=50,corner_radius=0)
        navBar.grid(row=0,column=0,sticky="ew")

        self.logoLBL = customtkinter.CTkLabel(navBar,text="Freelancer")
        self.logoLBL.pack(side="left",padx=20,pady=20)

        self.homeBTN = customtkinter.CTkButton(navBar,text="Home",fg_color="transparent",hover_color=("gray70","gray30"),command=lambda:self.showPage("home"))
        self.homeBTN.pack(side="left",padx=5,pady=10)

        self.dashboardBTN = customtkinter.CTkButton(navBar,text="Dashboard",fg_color="transparent",hover_color=("gray70","gray30"),command=lambda:self.showPage("dashboard"))
        self.dashboardBTN.pack(side="left",padx=5,pady=10)

        self.settingsBTN = customtkinter.CTkButton(navBar,text="Settings",fg_color="transparent",hover_color=("gray70","gray30"),command=lambda:self.selectPage("settings"))
        self.settingsBTN.pack(side="right",padx=20,pady=10)

        self.pages = {
            "home": {
                "frame": self.homePage(self.mainContainer),
                "btn": self.homeBTN
            },
            "dashboard": {
                "frame": self.dashboardPage(self.mainContainer),
                "btn": self.dashboardBTN
            }
        }

    def homePage(self,master):
        homePage = customtkinter.CTkFrame(master,corner_radius=0)
        homePage.grid(row=0,column=0,padx=10,pady=10,sticky="nsew")

        testLBL = customtkinter.CTkLabel(homePage,text="Home")
        testLBL.pack(side="left")

    def dashboardPage(self,master):
        dashboardPage = customtkinter.CTkFrame(master,corner_radius=0)
        dashboardPage.grid(row=0,column=0,padx=10,pady=10,sticky="nsew")

        testLBL = customtkinter.CTkLabel(dashboardPage,text="dashboard")
        testLBL.pack(side="left")

    def create_freelancer_card(self, index, name, skill):
        # Individual card frame for each item
        card = customtkinter.CTkFrame(self.scrollFrame, corner_radius=8)
        card.grid(row=index, column=0, padx=10, pady=6, sticky="ew")

        card.grid_columnconfigure(0, weight=2) # Name column
        card.grid_columnconfigure(1, weight=2) # Skill column
        card.grid_columnconfigure(2, weight=1) # Button column

        # Freelancer Name Label
        name_label = customtkinter.CTkLabel(card, text=name, font=customtkinter.CTkFont(size=14, weight="bold"), anchor="w")
        name_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")

        # Skill Label
        skill_label = customtkinter.CTkLabel(card, text=skill, text_color="gray", font=customtkinter.CTkFont(size=13), anchor="w")
        skill_label.grid(row=0, column=1, padx=10, pady=12, sticky="w")

        # book button
        book_btn = customtkinter.CTkButton(
            card, 
            text="Book", 
            width=90, 
            height=28,
            corner_radius=6,
            command=lambda: self.book_freelancer(name)
        )
        book_btn.grid(row=0, column=2, padx=15, pady=12, sticky="e")

    def book_freelancer(self, name):
        print(f"Booked {name}!")

    def selectPage(self, page):
        print(f"Switch to {page}")


    def showPage(self,targetPage):
        for key, page in self.pages.items():
            if key == targetPage:
                page["frame"].pack(fill="both", expand=True)
                page["btn"].configure(
                    fg_color=("gray75", "gray25"),
                    font=customtkinter.CTkFont(weight="bold"),
                )
            else:
                page["frame"].pack_forget()
                page["btn"].configure(
                    fg_color="transparent", font=customtkinter.CTkFont(weight="normal")
                )


app = App()
app.mainloop()
