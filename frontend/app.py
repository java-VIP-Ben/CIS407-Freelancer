import sys
import sqlite3
from pathlib import Path
from tkinter import StringVar, messagebox

# Support both importing App from main.py and running this file directly.
if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from backend.database import (
    create_project_proposal, get_client_id_by_email,
    get_freelancer_id_by_email, get_projects_for_client,
)
from frontend.admin_page import AdminPage
from frontend.proposal_page import FreelancerProposalsPage

from frontend.listings_page import ListingsHome, ListingsPage

from frontend.project_page import (
    ClientProjectsPage, FreelancerProjectsPage, ProjectsHome,
)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Freelancer")
        self.geometry("1080x720")
        self.minsize(860, 600)
        self.current_user = None
        self.current_client_id = None
        self.current_freelancer_id = None
        self.current_role = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        nav_bar = self.nav_bar = ctk.CTkFrame(self, height=50, corner_radius=0)
        nav_bar.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(nav_bar, text="Freelancer", font=ctk.CTkFont(size=20, weight="bold")).pack(
            side="left", padx=20, pady=14
        )
        self.nav_buttons = {}
        page_names = (
            "home", "listings", "projects", "my_projects", "proposals",
            "admin", "settings",
        )
        for page_name in page_names:
            button = ctk.CTkButton(
                nav_bar,
                text={
                    "my_projects": "My Projects",
                    "proposals": "Proposals",
                }.get(page_name, page_name.title()),
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda name=page_name: self.show_page(name),
                width=100 if page_name == "my_projects" else 85,
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
            "projects": ProjectsHome(self.main_container),
            "client_projects": ClientProjectsPage(
                self.main_container, lambda: self.current_client_id
            ),
            "freelancer_projects": FreelancerProjectsPage(
                self.main_container, lambda: self.current_freelancer_id
            ),
            "proposals": FreelancerProposalsPage(
                self.main_container, lambda: self.current_freelancer_id
            ),
            "admin": AdminPage(self.main_container),
            "settings": self.settings_page(self.main_container),
        }
        self.update_nav_access()
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
        self.username_entry = ctk.CTkEntry(
            form, width=260, placeholder_text="Admin username or account email"
        )
        self.username_entry.grid(row=1, column=0, padx=30, pady=8)
        self.password_entry = ctk.CTkEntry(
            form, width=260, placeholder_text="Admin password", show="*"
        )
        self.password_entry.grid(row=2, column=0, padx=30, pady=8)
        self.login_error = ctk.CTkLabel(form, text="", text_color=("#B23B3B", "#ff7777"))
        self.login_error.grid(row=3, column=0, padx=30, pady=(2, 8))
        ctk.CTkButton(form, text="Login", width=260, command=self.attempt_login).grid(
            row=4, column=0, padx=30, pady=(5, 8)
        )
        ctk.CTkButton(
            form, text="Sign In with Client Email", width=260,
            command=self.client_login,
        ).grid(row=5, column=0, padx=30, pady=5)
        ctk.CTkButton(
            form, text="Sign In with Freelancer Email", width=260,
            command=self.freelancer_login,
        ).grid(row=6, column=0, padx=30, pady=5)
        ctk.CTkLabel(
            form, text="Demo client and freelancer access use email only.",
            anchor="w",
        ).grid(row=7, column=0, padx=30, pady=(2, 20))
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
            self.current_client_id = None
            self.current_freelancer_id = None
            self.current_role = "admin"
            self.update_nav_access()
            self.show_page("home")
        else:
            self.login_error.configure(text="Invalid username or password")
            self.password_entry.delete(0, "end")
            self.password_entry.focus_set()

    def client_login(self):
        email = self.username_entry.get().strip()
        try:
            client_id = get_client_id_by_email(email)
        except (sqlite3.Error, ValueError) as exc:
            self.login_error.configure(text=f"Unable to sign in: {exc}")
            return
        if client_id is None:
            self.login_error.configure(text="No client account found for that email.")
            return

        self.login_error.configure(text="")
        self.password_entry.delete(0, "end")
        self.current_user = email
        self.current_client_id = client_id
        self.current_freelancer_id = None
        self.current_role = "client"
        self.update_nav_access()
        self.show_page("client_projects")

    def freelancer_login(self):
        email = self.username_entry.get().strip()
        try:
            freelancer_id = get_freelancer_id_by_email(email)
        except (sqlite3.Error, ValueError) as exc:
            self.login_error.configure(text=f"Unable to sign in: {exc}")
            return
        if freelancer_id is None:
            self.login_error.configure(text="No freelancer account found for that email.")
            return

        self.login_error.configure(text="")
        self.password_entry.delete(0, "end")
        self.current_user = email
        self.current_client_id = None
        self.current_freelancer_id = freelancer_id
        self.current_role = "freelancer"
        self.update_nav_access()
        self.show_page("my_projects")

    def sign_out(self):
        self.current_user = None
        self.current_client_id = None
        self.current_freelancer_id = None
        self.current_role = None
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.login_error.configure(text="")
        self.update_nav_access()
        self.show_page("login")

    def update_nav_access(self):
        role = self.current_role
        for page_name, button in self.nav_buttons.items():
            if role == "client":
                restricted = page_name in (
                    "listings", "projects", "proposals", "admin",
                )
            elif role == "freelancer":
                restricted = page_name not in (
                    "my_projects", "proposals", "settings",
                )
            else:
                restricted = page_name in ("my_projects", "proposals")
            button.configure(state="disabled" if restricted else "normal")

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
        if target_page == "my_projects":
            if self.current_role == "client":
                target_page = "client_projects"
            elif self.current_role == "freelancer":
                target_page = "freelancer_projects"
            else:
                target_page = "home" if self.current_user is not None else "login"

        if target_page not in self.pages:
            raise ValueError(f"Unknown page: {target_page}")

        # Do not allow navigation to application pages until signed in.
        if target_page != "login" and self.current_user is None:
            target_page = "login"
        elif self.current_role == "client" and target_page in (
            "listings", "projects", "freelancer_projects", "proposals", "admin",
        ):
            target_page = "client_projects"
        elif self.current_role == "freelancer" and target_page not in (
            "freelancer_projects", "proposals", "settings",
        ):
            target_page = "freelancer_projects"
        elif self.current_role != "client" and target_page == "client_projects":
            target_page = "home" if self.current_user is not None else "login"
        elif self.current_role != "freelancer" and target_page == "freelancer_projects":
            target_page = "home" if self.current_user is not None else "login"
        elif self.current_role != "freelancer" and target_page == "proposals":
            target_page = "home" if self.current_user is not None else "login"

        if target_page == "login":
            self.current_user = None
            self.current_client_id = None
            self.current_freelancer_id = None
            self.current_role = None
            self.update_nav_access()
            self.nav_bar.grid_remove()
        else:
            self.nav_bar.grid(row=0, column=0, sticky="ew")

        nav_target = (
            "my_projects"
            if target_page in ("client_projects", "freelancer_projects")
            else target_page
        )
        for name, page in self.pages.items():
            if name == target_page:
                page.grid(row=0, column=0, sticky="nsew")
            else:
                page.grid_remove()
            if name in self.nav_buttons:
                self.nav_buttons[name].configure(
                    fg_color=("gray75", "gray25") if name == nav_target else "transparent"
                )

        if target_page == "login":
            self.after_idle(self.username_entry.focus_set)
        elif target_page in (
            "home", "listings", "projects", "client_projects",
            "freelancer_projects", "proposals", "admin",
        ):
            self.pages[target_page].on_show()

    def book_listing(self, listing):
        if self.current_role != "client" or self.current_client_id is None:
            messagebox.showinfo(
                "Client Sign-In Required",
                "Sign in with a client email to invite a freelancer to a project.",
                parent=self,
            )
            return

        try:
            projects = get_projects_for_client(self.current_client_id)
        except sqlite3.Error as exc:
            messagebox.showerror("Unable to Load Projects", str(exc), parent=self)
            return
        if not projects:
            messagebox.showinfo(
                "No Projects",
                "Create a project before inviting a freelancer.",
                parent=self,
            )
            return
        if listing["FreelancerID"] is None:
            messagebox.showerror(
                "Unable to Send Proposal",
                "This listing is not associated with a freelancer.",
                parent=self,
            )
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Invite Freelancer to Project")
        dialog.geometry("500x265")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            dialog,
            text=f"Invite {listing['Name'] or 'this freelancer'}",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(20, 4))
        ctk.CTkLabel(
            dialog,
            text=f"Choose which project '{listing['JobTitle']}' is for.",
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 12))

        project_options = {}
        for project in projects:
            project_id, project_name, freelancer_name, assigned_id = project
            name = project_name.strip() if project_name else f"Untitled project #{project_id}"
            option = f"#{project_id} — {name}"
            if assigned_id is not None:
                assigned = freelancer_name or f"Freelancer #{assigned_id}"
                option += f" (currently assigned: {assigned})"
            project_options[option] = project

        selected_project = StringVar(master=dialog, value=next(iter(project_options)))
        ctk.CTkOptionMenu(
            dialog, values=list(project_options), variable=selected_project,
        ).grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 10))
        ctk.CTkLabel(
            dialog,
            text="The freelancer will be assigned only if they accept. "
                 "Acceptance replaces any current assignment.",
            anchor="w", justify="left", wraplength=440,
            text_color=("gray45", "gray65"),
        ).grid(row=3, column=0, sticky="ew", padx=22, pady=(0, 12))

        def send_proposal():
            project = project_options[selected_project.get()]
            project_id, project_name, freelancer_name, assigned_id = project
            if assigned_id is not None:
                current_name = freelancer_name or f"Freelancer #{assigned_id}"
                if not messagebox.askyesno(
                    "Invite to Assigned Project?",
                    f"This project is currently assigned to {current_name}. "
                    "If the invited freelancer accepts, they will replace that assignment. Continue?",
                    parent=dialog,
                ):
                    return

            try:
                proposal_id = create_project_proposal(
                    project_id, listing["FreelancerID"], self.current_client_id
                )
            except (sqlite3.Error, ValueError) as exc:
                messagebox.showerror(
                    "Unable to Send Proposal", str(exc), parent=dialog
                )
                return

            dialog.destroy()
            messagebox.showinfo(
                "Proposal Sent",
                f"Proposal #{proposal_id} was sent to {listing['Name'] or 'the freelancer'}. "
                "The project will be assigned if they accept.",
                parent=self,
            )

        actions = ctk.CTkFrame(dialog, fg_color="transparent")
        actions.grid(row=4, column=0, sticky="e", padx=22, pady=(0, 18))
        ctk.CTkButton(
            actions, text="Cancel", width=90, fg_color="transparent",
            border_width=1, command=dialog.destroy,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            actions, text="Send Proposal", width=120, command=send_proposal,
        ).pack(side="right")


if __name__ == "__main__":
    app = App()
    app.mainloop()
