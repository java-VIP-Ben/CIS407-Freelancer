from tkinter import messagebox
import customtkinter as ctk

from backend.database import (
    create_freelancer,
    get_freelancers,
    update_freelancer,
    delete_freelancer,
)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Freelancer")
        self.geometry("1080x720")
        self.minsize(780, 540)
        self.selected_freelancer_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

<<<<<<< HEAD
        self.mainContainer = customtkinter.CTkFrame(self, corner_radius=0)
        self.mainContainer.grid(row=1, column=0, sticky="nsew")
        self.mainContainer.grid_rowconfigure(0, weight=1)
        self.mainContainer.grid_columnconfigure(0, weight=1)   

        self.navBar = customtkinter.CTkFrame(self,height=50,corner_radius=0)
        self.navBar.grid(row=0,column=0,sticky="ew")

        self.logoLBL = customtkinter.CTkLabel(self.navBar,text="Freelancer")
        self.logoLBL.pack(side="left",padx=20,pady=20)

        self.homeBTN = customtkinter.CTkButton(self.navBar,text="Home",fg_color="transparent",hover_color=("gray70","gray30"),command=lambda:self.showPage("home"))
        self.homeBTN.pack(side="left",padx=5,pady=10)

        self.dashboardBTN = customtkinter.CTkButton(self.navBar,text="Dashboard",fg_color="transparent",hover_color=("gray70","gray30"),command=lambda:self.showPage("dashboard"))
        self.dashboardBTN.pack(side="left",padx=5,pady=10)

        self.projectBTN = customtkinter.CTkButton(self.navBar,text="Projects",fg_color="transparent",hover_color=("gray70","gray30"),command=lambda:self.showPage("project"))
        self.projectBTN.pack(side="left",padx=5,pady=10)

        self.loginBTN = customtkinter.CTkButton(self.navBar,text="Sign Out",fg_color="transparent",hover_color=("gray70","gray30"),command=lambda:self.showPage("login"))
        self.loginBTN.pack(side="right",padx=5,pady=10)

        self.settingsBTN = customtkinter.CTkButton(self.navBar,text="Settings",fg_color="transparent",hover_color=("gray70","gray30"),command=lambda:self.selectPage("settings"))
        self.settingsBTN.pack(side="right",padx=20,pady=10)
=======
        nav_bar = ctk.CTkFrame(self, height=50, corner_radius=0)
        nav_bar.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(nav_bar, text="Freelancer", font=ctk.CTkFont(size=20, weight="bold")).pack(
            side="left", padx=20, pady=14
        )
        self.nav_buttons = {}
        for page_name in ("home", "dashboard", "settings"):
            button = ctk.CTkButton(
                nav_bar,
                text=page_name.title(),
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda name=page_name: self.show_page(name),
                width=110,
            )
            button.pack(side="left" if page_name != "settings" else "right", padx=5, pady=10)
            self.nav_buttons[page_name] = button

        self.main_container = ctk.CTkFrame(self, corner_radius=0)
        self.main_container.grid(row=1, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
>>>>>>> 2971eba (CRUD freelancers)


        self.pages = {
<<<<<<< HEAD
            "home": {
                "frame": self.homePage(self.mainContainer),
                "btn": self.homeBTN
            },
            "dashboard": {
                "frame": self.dashboardPage(self.mainContainer),
                "btn": self.dashboardBTN
            },
            "login": {
                "frame": self.loginPage(self.mainContainer,self.handleLogin),
                "btn": self.loginBTN
            },
            "project": {
                "frame": self.projectPage(self.mainContainer),
                "btn": self.projectBTN
            }
=======
            "home": self.home_page(self.main_container),
            "dashboard": self.dashboard_page(self.main_container),
            "settings": self.settings_page(self.main_container),
>>>>>>> 2971eba (CRUD freelancers)
        }
        self.show_page("home")

<<<<<<< HEAD
        self.showPage("login")

    def loginPage(self,master,onLogin):
        loginPage = customtkinter.CTkFrame(master,corner_radius=0)
        loginPage.grid_rowconfigure(0,weight=1)
        loginPage.grid_columnconfigure(0,weight=1)

        mainArea = customtkinter.CTkFrame(loginPage,width=340,corner_radius=12)
        mainArea.grid(row=0,column=0,padx=20,pady=20)
        mainArea.grid_columnconfigure(0,weight=1)

        signTXT = customtkinter.CTkLabel(mainArea,text="Sign In",font=customtkinter.CTkFont(size=24,weight="bold"))
        signTXT.grid(row=0,column=0,padx=30,pady=(30,15))

        usernameEntry = customtkinter.CTkEntry(mainArea,width=260,placeholder_text="Username")
        usernameEntry.grid(row=1,column=0,padx=30,pady=8)

        passwordEntry = customtkinter.CTkEntry(mainArea,width=260,placeholder_text="Password",show="*")
        passwordEntry.grid(row=2,column=0,padx=30,pady=8)

        error_label = customtkinter.CTkLabel(mainArea, text="", text_color="#ff5555", font=customtkinter.CTkFont(size=12))
        error_label.grid(row=3, column=0, padx=30, pady=(2, 8))

        def attempt_login(event=None):
            user = usernameEntry.get().strip()
            pw = passwordEntry.get()

            if user == "admin" and pw == "admin":
                error_label.configure(text="")
                passwordEntry.delete(0, "end")
                onLogin(user)
            else:
                error_label.configure(text="Invalid username or password")

            passwordEntry.bind("<Return>", attempt_login)

        login_btn = customtkinter.CTkButton(mainArea, text="Login", width=260, command=attempt_login)
        login_btn.grid(row=4, column=0, padx=30, pady=(5, 30))


        return loginPage
    
    def homePage(self,master):
        homePage = customtkinter.CTkFrame(master,corner_radius=0)

        testLBL = customtkinter.CTkLabel(homePage,text="Home")
        testLBL.pack(side="left")

        return homePage
        

    def dashboardPage(self,master):
        dashboardPage = customtkinter.CTkFrame(master,corner_radius=0)
        dashboardPage.grid_rowconfigure(0,weight=1)
        dashboardPage.grid_columnconfigure(0,weight=1)

        self.scrollFrame = customtkinter.CTkScrollableFrame(dashboardPage,fg_color="transparent",label_text="Find Your Freelancer")
        self.scrollFrame.grid(row=0,column=0,padx=10,pady=10,sticky="nsew")
        self.scrollFrame.grid_columnconfigure(0,weight=1)

        itemsData = [
            {"freelanceName": "Mike Hawk", "skill": "flying"},
            {"freelanceName": "Jonah Zoller", "skill": "plumbing"},
            {"freelanceName": "Benjamin Lukens", "skill": "vehicle repair"},
            {"freelanceName": "Joe Piper", "skill": "flying"}
        ]

        for index, data in enumerate(itemsData):
            self.create_freelancer_card(index, data.get("freelanceName"), data.get("skill"))
        
        return dashboardPage

    def projectPage(self,master):
        projectPage = customtkinter.CTkFrame(master,corner_radius=0)
        projectPage.grid_rowconfigure(0,weight=1)
        projectPage.grid_columnconfigure(0,weight=1)

        currentproFrame = customtkinter.CTkScrollableFrame(projectPage,fg_color="transparent",label_text="Current Projects")
        currentproFrame.grid(row=0,column=0,padx=10,pady=10,sticky="nsew")
        currentproFrame.grid_columnconfigure(0,weight=1)

        

        

        return projectPage


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
=======
    def home_page(self, master):
        page = ctk.CTkFrame(master, corner_radius=0)
        page.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(page, text="Find Your Freelancer", font=ctk.CTkFont(size=24, weight="bold")).pack(
            anchor="w", padx=20, pady=(20, 10)
>>>>>>> 2971eba (CRUD freelancers)
        )
        self.scroll_frame = ctk.CTkScrollableFrame(page, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        return page

<<<<<<< HEAD
    def createCurrentProjects(self, index, name, skill):
        print("test")


    def book_freelancer(self, name):
        print(f"Booked {name}!")
=======
    def dashboard_page(self, master):
        page = ctk.CTkScrollableFrame(master, corner_radius=0)
        ctk.CTkLabel(page, text="Freelancer Management", font=ctk.CTkFont(size=24, weight="bold")).pack(
            anchor="w", padx=20, pady=(20, 12)
        )
        form = ctk.CTkFrame(page)
        form.pack(fill="x", padx=20, pady=10)
        form.grid_columnconfigure(1, weight=1)
>>>>>>> 2971eba (CRUD freelancers)

        self.entries = {}
        for row, (key, label) in enumerate((
            ("name", "Name"), ("email", "Email"), ("phone", "Phone")
        )):
            ctk.CTkLabel(form, text=label).grid(row=row, column=0, padx=12, pady=10, sticky="w")
            entry = ctk.CTkEntry(form, placeholder_text=f"Enter {label.lower()}")
            entry.grid(row=row, column=1, padx=12, pady=10, sticky="ew")
            self.entries[key] = entry

<<<<<<< HEAD
    def handleLogin(self, username: str):
        self.current_user = username
        self.showPage("home")


    def showPage(self, target_key: str):
        if target_key == "login":
            self.navBar.grid_remove()
        else:
            self.navBar.grid(row=0, column=0, sticky="ew")

        for key, page in self.pages.items():
            if key == target_key:
                page["frame"].grid(row=0, column=0, sticky="nsew")
                page["btn"].configure(
                    fg_color=("gray75", "gray25"),
                    font=customtkinter.CTkFont(weight="bold"),
                )
            else:
                page["frame"].grid_remove()
                page["btn"].configure(
                    fg_color="transparent",
                    font=customtkinter.CTkFont(weight="normal"),
                )
=======
        actions = ctk.CTkFrame(page, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=10)
        ctk.CTkButton(actions, text="Add Freelancer", command=self.add_freelancer).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Update Selected", command=self.edit_freelancer).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Delete Selected", fg_color="#B23B3B", hover_color="#8F2D2D",
                      command=self.remove_freelancer).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Clear", command=self.clear_form).pack(side="left", padx=4)

        ctk.CTkLabel(page, text="Select a freelancer below to edit", font=ctk.CTkFont(size=15)).pack(
            anchor="w", padx=20, pady=(12, 4)
        )
        self.dashboard_list = ctk.CTkScrollableFrame(page, height=240)
        self.dashboard_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.dashboard_list.grid_columnconfigure(0, weight=1)
        return page

    def settings_page(self, master):
        page = ctk.CTkFrame(master, corner_radius=0)
        ctk.CTkLabel(page, text="Settings", font=ctk.CTkFont(size=24, weight="bold")).pack(
            anchor="w", padx=20, pady=20
        )
        ctk.CTkLabel(page, text="Appearance").pack(anchor="w", padx=20)
        ctk.CTkOptionMenu(page, values=["System", "Light", "Dark"],
                          command=ctk.set_appearance_mode).pack(anchor="w", padx=20, pady=10)
        return page

    def show_page(self, target_page):
        for name, page in self.pages.items():
            if name == target_page:
                page.grid(row=0, column=0, sticky="nsew")
            else:
                page.grid_remove()
            self.nav_buttons[name].configure(
                fg_color=("gray75", "gray25") if name == target_page else "transparent"
            )
        if target_page in ("home", "dashboard"):
            self.refresh_freelancers()
>>>>>>> 2971eba (CRUD freelancers)

    def refresh_freelancers(self):
        try:
            freelancers = get_freelancers()
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))
            return

        for parent in (self.scroll_frame, self.dashboard_list):
            for child in parent.winfo_children():
                child.destroy()

        if not freelancers:
            ctk.CTkLabel(self.scroll_frame, text="No freelancers registered yet.").grid(
                row=0, column=0, padx=20, pady=20
            )
            ctk.CTkLabel(self.dashboard_list, text="No freelancers registered yet.").grid(
                row=0, column=0, padx=20, pady=20
            )
            return

        # freelancers schema: FreelancerID, Name, SkillsListID, Email, Phone, ReviewsID
        for index, record in enumerate(freelancers):
            freelancer_id, name, _, email, phone, _ = record
            self.create_freelancer_card(index, freelancer_id, name, email)
            button = ctk.CTkButton(
                self.dashboard_list,
                text=f"#{freelancer_id}  {name}  |  {email or 'No email'}  |  {phone or 'No phone'}",
                anchor="w", fg_color=("gray80", "gray25"), text_color=("black", "white"),
                command=lambda fid=freelancer_id, n=name, e=email, p=phone:
                    self.select_freelancer(fid, n, e, p),
            )
            button.grid(row=index, column=0, sticky="ew", padx=6, pady=4)

    def create_freelancer_card(self, index, freelancer_id, name, email):
        card = ctk.CTkFrame(self.scroll_frame, corner_radius=8)
        card.grid(row=index, column=0, padx=10, pady=6, sticky="ew")
        card.grid_columnconfigure(0, weight=2)
        card.grid_columnconfigure(1, weight=2)
        ctk.CTkLabel(card, text=name or "Unnamed freelancer",
                     font=ctk.CTkFont(size=14, weight="bold"), anchor="w").grid(
            row=0, column=0, padx=15, pady=12, sticky="w"
        )
        ctk.CTkLabel(card, text=email or "No email", text_color="gray", anchor="w").grid(
            row=0, column=1, padx=10, pady=12, sticky="w"
        )
        ctk.CTkButton(card, text="Book", width=90,
                      command=lambda fid=freelancer_id: self.book_freelancer(fid)).grid(
            row=0, column=2, padx=15, pady=12
        )

    def book_freelancer(self, freelancer_id):
        messagebox.showinfo("Booking", f"Booking for freelancer #{freelancer_id} is coming soon.")

    def select_freelancer(self, freelancer_id, name, email, phone):
        self.selected_freelancer_id = freelancer_id
        for key, value in (("name", name), ("email", email), ("phone", phone)):
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, value or "")

    def clear_form(self):
        self.selected_freelancer_id = None
        for entry in self.entries.values():
            entry.delete(0, "end")

    def form_values(self):
        name = self.entries["name"].get().strip()
        email = self.entries["email"].get().strip()
        phone = self.entries["phone"].get().strip()
        if not name or not email or not phone:
            messagebox.showwarning("Missing Information", "Please fill in name, email, and phone.")
            return None
        if "@" not in email or "." not in email.split("@")[-1]:
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return None
        return name, email, phone

    def add_freelancer(self):
        values = self.form_values()
        if values is None:
            return
        try:
            new_id = create_freelancer(*values)
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))
            return
        self.clear_form()
        self.refresh_freelancers()
        messagebox.showinfo("Success", f"Freelancer #{new_id} added.")

    def edit_freelancer(self):
        if self.selected_freelancer_id is None:
            messagebox.showwarning("No Selection", "Select a freelancer from the list first.")
            return
        values = self.form_values()
        if values is None:
            return
        try:
            count = update_freelancer(self.selected_freelancer_id, *values)
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))
            return
        self.clear_form()
        self.refresh_freelancers()
        messagebox.showinfo("Update", "Freelancer updated." if count else "Freelancer no longer exists.")

    def remove_freelancer(self):
        if self.selected_freelancer_id is None:
            messagebox.showwarning("No Selection", "Select a freelancer from the list first.")
            return
        if not messagebox.askyesno("Confirm Delete", "Delete the selected freelancer?"):
            return
        try:
            count = delete_freelancer(self.selected_freelancer_id)
        except Exception as exc:
            messagebox.showerror("Database Error", str(exc))
            return
        self.clear_form()
        self.refresh_freelancers()
        messagebox.showinfo("Delete", "Freelancer deleted." if count else "Freelancer no longer exists.")
