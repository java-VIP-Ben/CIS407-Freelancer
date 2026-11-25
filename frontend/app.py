import sys
import sqlite3
from pathlib import Path
from tkinter import StringVar, messagebox

# Support both importing App from main.py and running this file directly.
if __name__ == "__main__" and not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import customtkinter as ctk
from backend.database import (
    create_project_proposal, get_projects_for_client, initialize_project_workflow,
)
from backend.client_auth import (
    initialize_auth, authenticate_admin, authenticate_client,
    authenticate_freelancer, register_client, register_freelancer,
)
from backend.listings_database import format_price
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
            "register": self.registration_page(self.main_container),
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
        self.login_role = StringVar(master=self, value="Client")
        ctk.CTkOptionMenu(form, values=["Client", "Freelancer", "Admin"],
                          variable=self.login_role, width=260,
                          command=self.on_login_role_change).grid(row=1, column=0, padx=30, pady=8)
        self.username_entry = ctk.CTkEntry(form, width=260, placeholder_text="Email or admin username")
        self.username_entry.grid(row=2, column=0, padx=30, pady=8)
        self.password_entry = ctk.CTkEntry(form, width=260, placeholder_text="Password", show="*")
        self.password_entry.grid(row=3, column=0, padx=30, pady=8)
        self.login_error = ctk.CTkLabel(form, text="", wraplength=300,
                                       text_color=("#B23B3B", "#ff7777"))
        self.login_error.grid(row=4, column=0, padx=30, pady=(2, 8))
        ctk.CTkButton(form, text="Login", width=260, command=self.attempt_login).grid(
            row=5, column=0, padx=30, pady=(5, 8))
        self.register_button = ctk.CTkButton(
            form, text="Create Client Account", width=260,
            fg_color="transparent", border_width=1,
            command=self.open_registration,
        )
        self.register_button.grid(row=6, column=0, padx=30, pady=(5, 24))
        self.username_entry.bind("<Return>", self.attempt_login)
        self.password_entry.bind("<Return>", self.attempt_login)
        return page

    def registration_page(self, master):
        page = ctk.CTkFrame(master, corner_radius=0)
        page.grid_rowconfigure(0, weight=1)
        page.grid_columnconfigure(0, weight=1)
        form = ctk.CTkFrame(page, corner_radius=12)
        form.grid(row=0, column=0, padx=20, pady=16)
        self.register_role = "Client"
        self.register_heading = ctk.CTkLabel(
            form, text="Create Client Account",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.register_heading.grid(row=0, column=0, padx=30, pady=(20, 10))
        self.register_entries = {}
        fields = (("name", "Full name"), ("email", "Email address"),
                  ("address", "Address"), ("phone", "Phone"),
                  ("password", "Password (12+ characters)"), ("confirm", "Confirm password"))
        for row, (key, label) in enumerate(fields, 1):
            entry = ctk.CTkEntry(form, width=300, height=32, placeholder_text=label,
                                 **({"show": "*"} if key in ("password", "confirm") else {}))
            entry.grid(row=row, column=0, padx=30, pady=5)
            self.register_entries[key] = entry
        self.register_error = ctk.CTkLabel(form, text="", wraplength=300,
                                          text_color=("#B23B3B", "#ff7777"))
        self.register_error.grid(row=7, column=0, padx=20, pady=4)
        ctk.CTkButton(form, text="Register", width=300, command=self.attempt_register).grid(
            row=8, column=0, padx=30, pady=5)
        ctk.CTkButton(form, text="Back to Sign In", width=300, fg_color="transparent",
                      border_width=1, command=self.cancel_registration).grid(
            row=9, column=0, padx=30, pady=(5, 18))
        self.register_entries["confirm"].bind("<Return>", self.attempt_register)
        return page

    def update_registration_button(self):
        role = self.login_role.get()
        if role in ("Client", "Freelancer"):
            self.register_button.configure(text=f"Create {role} Account", state="normal")
            self.register_button.grid()
        else:
            self.register_button.configure(state="disabled")
            self.register_button.grid_remove()

    def open_registration(self):
        role = self.login_role.get()
        if self.current_role is not None or role not in ("Client", "Freelancer"):
            return
        self.clear_registration()
        self.clear_login_fields()
        self.login_error.configure(text="")
        self.register_role = role
        self.register_heading.configure(text=f"Create {role} Account")
        if role == "Freelancer":
            self.register_entries["address"].grid_remove()
        else:
            self.register_entries["address"].grid()
        self.show_page("register")

    def clear_registration(self):
        for entry in self.register_entries.values():
            if entry.get():
                entry.delete(0, "end")
        self.register_error.configure(text="")
        self.restore_auth_placeholders()

    def cancel_registration(self):
        self.clear_registration()
        self.show_page("login")

    def attempt_register(self, event=None):
        if self.current_role is not None:
            return
        data = {key: entry.get() for key, entry in self.register_entries.items()}
        try:
            if data["password"] != data["confirm"]:
                raise ValueError("Passwords do not match.")
            initialize_project_workflow()
            if self.register_role == "Client":
                register_client(data["name"], data["email"], data["address"],
                                data["phone"], data["password"])
            elif self.register_role == "Freelancer":
                register_freelancer(data["name"], data["email"],
                                    data["phone"], data["password"])
            else:
                raise ValueError("Invalid registration account type.")
        except (sqlite3.Error, ValueError) as exc:
            self.register_error.configure(text=str(exc))
            return
        finally:
            for key in ("password", "confirm"):
                entry = self.register_entries[key]
                if entry.get():
                    entry.delete(0, "end")
            self.restore_auth_placeholders()
        self.clear_registration()
        self.login_role.set(self.register_role)
        self.clear_login_fields()
        self.username_entry.insert(0, data["email"].strip())
        self.show_page("login")
        self.login_error.configure(text="Account created. Sign in with your password.")

    def restore_auth_placeholders(self):
        """Refresh empty auth fields once the page is mapped and focus has settled."""
        self.focus_set()
        self.after_idle(self.refresh_auth_placeholders)

    def refresh_auth_placeholders(self):
        if self.current_role is not None:
            return
        focused = self.focus_get()
        entries = [(self.username_entry, False), (self.password_entry, True)]
        entries.extend((entry, key in ("password", "confirm"))
                       for key, entry in self.register_entries.items())
        for entry, masked in entries:
            # Do not interfere if the user has already started typing or focused a field.
            if entry.get() or focused is entry or getattr(focused, "master", None) is entry:
                continue
            entry.configure(placeholder_text=entry.cget("placeholder_text"))
            if masked:
                # CTkEntry remembers the mask while its placeholder is visible.
                entry.configure(show="*")

    def clear_login_fields(self):
        for entry in (self.username_entry, self.password_entry):
            if entry.get():
                entry.delete(0, "end")
        self.restore_auth_placeholders()

    def on_login_role_change(self, _role):
        self.clear_login_fields()
        self.login_error.configure(text="")
        self.update_registration_button()
        self.restore_auth_placeholders()

    def attempt_login(self, event=None):
        if self.current_role is not None:
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        role = self.login_role.get().lower()
        try:
            if role == "admin":
                account = {"Name": "admin"} if authenticate_admin(username, password) else None
            elif role == "client":
                account = authenticate_client(username, password)
            elif role == "freelancer":
                account = authenticate_freelancer(username, password)
            else:
                account = None
            if account is None:
                self.login_error.configure(text="Invalid credentials or account not activated.")
                return
            initialize_auth()
            initialize_project_workflow()
        except (sqlite3.Error, ValueError) as exc:
            self.login_error.configure(text=f"Unable to sign in: {exc}")
            return
        finally:
            self.clear_login_fields()
        self.current_user = account["Name"] or username
        self.current_client_id = account.get("ClientID") if role == "client" else None
        self.current_freelancer_id = account.get("FreelancerID") if role == "freelancer" else None
        self.current_role = role
        self.login_error.configure(text="")
        self.update_nav_access()
        self.show_page("my_projects" if role == "freelancer" else "home")

    def sign_out(self):
        self.current_user = None
        self.current_client_id = None
        self.current_freelancer_id = None
        self.current_role = None
        self.clear_login_fields()
        self.login_error.configure(text="")
        self.login_role.set("Client")
        self.clear_registration()
        self.pages["home"].clear_search()
        self.update_nav_access()
        self.show_page("login")

    def update_nav_access(self):
        allowed = {
            "client": {"home", "my_projects", "settings"},
            "freelancer": {"my_projects", "proposals", "settings"},
            "admin": {"home", "listings", "projects", "admin", "settings"},
        }.get(self.current_role, set())
        for name, button in self.nav_buttons.items():
            button.configure(state="normal" if name in allowed else "disabled")

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
        role = self.current_role
        if target_page == "my_projects":
            target_page = {"client": "client_projects", "freelancer": "freelancer_projects"}.get(role, "home")
        if target_page not in self.pages:
            raise ValueError(f"Unknown page: {target_page}")
        allowed = {
            None: {"login", "register"},
            "client": {"home", "client_projects", "settings"},
            "freelancer": {"freelancer_projects", "proposals", "settings"},
            "admin": {"home", "listings", "projects", "admin", "settings"},
        }.get(role, {"login"})
        if target_page not in allowed:
            target_page = "login" if role is None else ("freelancer_projects" if role == "freelancer" else "home")
        if role is None:
            self.nav_bar.grid_remove()
        else:
            self.nav_bar.grid(row=0, column=0, sticky="ew")
        nav_target = "my_projects" if target_page in ("client_projects", "freelancer_projects") else target_page
        for name, page in self.pages.items():
            if name == target_page:
                page.grid(row=0, column=0, sticky="nsew")
            else:
                page.grid_remove()
        for name, button in self.nav_buttons.items():
            button.configure(fg_color=("gray75", "gray25") if name == nav_target else "transparent")
        if target_page == "login":
            self.update_registration_button()
            self.restore_auth_placeholders()
        elif target_page == "register":
            self.restore_auth_placeholders()
        elif target_page in ("home", "listings", "projects", "client_projects",
                             "freelancer_projects", "proposals", "admin"):
            self.pages[target_page].on_show()

    def book_listing(self, listing):
        if self.current_role != "client" or self.current_client_id is None:
            messagebox.showinfo(
                "Client Sign-In Required",
                "Sign in as a client to invite a freelancer to a project.",
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

        if listing.get("PriceCents") is None:
            messagebox.showerror("Price Required", "This listing does not have a price yet.", parent=self)
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Invite Freelancer to Project")
        dialog.geometry("500x310")
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
            text=f"Choose which project '{listing['JobTitle']}' is for.\nFixed price: {format_price(listing['PriceCents'])} USD",
            anchor="w", justify="left", wraplength=450,
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

        client_id = self.current_client_id

        def send_proposal():
            if self.current_role != "client" or self.current_client_id != client_id:
                dialog.destroy()
                return
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
                    project_id, listing["FreelancerID"], client_id,
                    listing_id=listing["ListingID"], expected_price_cents=listing["PriceCents"],
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
