import sys
from pathlib import Path
from tkinter import messagebox

# Support both importing App from main.py and running this file directly.
if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from frontend.admin_page import AdminPage

from frontend.listings_page import ListingsHome, ListingsPage

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Freelancer")
        self.geometry("1080x720")
        self.minsize(860, 600)
        self.current_user = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        nav_bar = self.nav_bar = ctk.CTkFrame(self, height=50, corner_radius=0)
        nav_bar.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(nav_bar, text="Freelancer", font=ctk.CTkFont(size=20, weight="bold")).pack(
            side="left", padx=20, pady=14
        )
        self.nav_buttons = {}
        for page_name in ("home", "listings", "projects", "admin", "settings"):
            button = ctk.CTkButton(
                nav_bar,
                text=page_name.title(),
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda name=page_name: self.show_page(name),
                width=90,
            )
            button.pack(side="left" if page_name != "settings" else "right", padx=5, pady=10)
            self.nav_buttons[page_name] = button

        self.sign_out_button = ctk.CTkButton(
            nav_bar, text="Sign Out", width=90,
            fg_color="transparent", hover_color=("gray70", "gray30"),
            command=self.sign_out,
        )
        self.sign_out_button.pack(side="right", padx=5, pady=10)

        self.main_container = ctk.CTkFrame(self, corner_radius=0)
        self.main_container.grid(row=1, column=0, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.pages = {
            "login": self.login_page(self.main_container),
            "home": ListingsHome(self.main_container, self.book_listing),
            "listings": ListingsPage(self.main_container),
            "projects": self.project_page(self.main_container),
            "admin": AdminPage(self.main_container),
            "settings": self.settings_page(self.main_container),
        }
        self.show_page("login")

    def login_page(self, master):
        page = ctk.CTkFrame(master, corner_radius=0)
        page.grid_rowconfigure(0, weight=1)
        page.grid_columnconfigure(0, weight=1)

        form = ctk.CTkFrame(page, width=340, corner_radius=12)
        form.grid(row=0, column=0, padx=20, pady=20)
        form.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(form, text="Sign In", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, padx=30, pady=(30, 15)
        )
        self.username_entry = ctk.CTkEntry(form, width=260, placeholder_text="Username")
        self.username_entry.grid(row=1, column=0, padx=30, pady=8)
        self.password_entry = ctk.CTkEntry(form, width=260, placeholder_text="Password", show="*")
        self.password_entry.grid(row=2, column=0, padx=30, pady=8)
        self.login_error = ctk.CTkLabel(form, text="", text_color=("#B23B3B", "#ff7777"))
        self.login_error.grid(row=3, column=0, padx=30, pady=(2, 8))
        ctk.CTkButton(form, text="Login", width=260, command=self.attempt_login).grid(
            row=4, column=0, padx=30, pady=(5, 30)
        )
        # Bind before the first login attempt, not inside the callback.
        self.username_entry.bind("<Return>", self.attempt_login)
        self.password_entry.bind("<Return>", self.attempt_login)
        return page

    def attempt_login(self, event=None):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        # Demo credentials retained from the original login. Not production authentication.
        if username == "admin" and password == "admin":
            self.login_error.configure(text="")
            self.password_entry.delete(0, "end")
            self.current_user = username
            self.show_page("home")
        else:
            self.login_error.configure(text="Invalid username or password")
            self.password_entry.delete(0, "end")
            self.password_entry.focus_set()

    def sign_out(self):
        self.current_user = None
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.login_error.configure(text="")
        self.show_page("login")

    def project_page(self, master):
        page = ctk.CTkFrame(master, corner_radius=0)
        page.grid_rowconfigure(0, weight=1)
        page.grid_columnconfigure(0, weight=1)
        self.current_projects_frame = ctk.CTkScrollableFrame(
            page, fg_color="transparent", label_text="Current Projects"
        )
        self.current_projects_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.current_projects_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self.current_projects_frame,
            text="Project browsing is coming soon. Use Admin > Projects to manage records."
        ).grid(row=0, column=0, padx=10, pady=20)
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
        if target_page not in self.pages:
            raise ValueError(f"Unknown page: {target_page}")

        # Do not allow navigation to application pages until signed in.
        if target_page != "login" and self.current_user is None:
            target_page = "login"

        if target_page == "login":
            self.current_user = None
            self.nav_bar.grid_remove()
        else:
            self.nav_bar.grid(row=0, column=0, sticky="ew")

        for name, page in self.pages.items():
            if name == target_page:
                page.grid(row=0, column=0, sticky="nsew")
            else:
                page.grid_remove()
            if name in self.nav_buttons:
                self.nav_buttons[name].configure(
                    fg_color=("gray75", "gray25") if name == target_page else "transparent"
                )

        if target_page == "login":
            self.after_idle(self.username_entry.focus_set)
        elif target_page in ("home", "listings", "admin"):
            self.pages[target_page].on_show()

    def book_listing(self, listing):
        messagebox.showinfo(
            "Booking",
            f"Booking for {listing['JobTitle']} (listing #{listing['ListingID']}) is coming soon.",
            parent=self,
        )


if __name__ == "__main__":
    app = App()
    app.mainloop()
