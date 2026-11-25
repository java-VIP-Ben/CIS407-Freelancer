"""CustomTkinter project management page."""
import sqlite3
from tkinter import messagebox, ttk

import customtkinter as ctk

from backend.database import (
    create_client_project, create_projects, delete_projects, get_projects,
    get_projects_for_client, get_projects_for_freelancer, update_projects,
)


from backend.listings_database import format_price


PROJECT_FIELDS = (
    ("FreelancerID", "Freelancer ID"),
    ("ClientID", "Client ID"),
    ("PaymentID", "Payment ID"),
    ("SkillsID", "Skills ID"),
    ("MilestonesID", "Milestones ID"),
    ("ProposalID", "Proposal ID"),
)


class ProjectsHome(ctk.CTkFrame):
    """Create, select, update and delete project records."""

    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.selected_id = None
        self.records = {}
        self.entries = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            self, text="Manage Projects",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 4))
        ctk.CTkLabel(
            self,
            text="Create a project or select an existing project to edit. "
                 "Leave optional relationship IDs blank when they do not apply.",
            anchor="w", justify="left", wraplength=800,
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 8))

        form = ctk.CTkFrame(self, corner_radius=8)
        form.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 8))
        for column in (0, 1, 2):
            form.grid_columnconfigure(column, weight=1, uniform="fields")
        for index, (field, label) in enumerate(PROJECT_FIELDS):
            row, column = divmod(index, 3)
            ctk.CTkLabel(form, text=label, anchor="w").grid(
                row=row * 2, column=column, sticky="ew", padx=12, pady=(8, 0)
            )
            entry = ctk.CTkEntry(form, height=30, placeholder_text="Optional ID")
            entry.grid(
                row=row * 2 + 1, column=column, sticky="ew",
                padx=12, pady=(0, 8),
            )
            self.entries[field] = entry

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 8))
        self.create_button = ctk.CTkButton(
            actions, text="Create Project", width=120, command=self.create_action
        )
        self.create_button.pack(side="left", padx=(0, 5))
        self.update_button = ctk.CTkButton(
            actions, text="Update", width=75, command=self.update_action
        )
        self.update_button.pack(side="left", padx=(0, 5))
        self.delete_button = ctk.CTkButton(
            actions, text="Delete", width=75, command=self.delete_action,
            fg_color="#B23B3B", hover_color="#8F2D2D",
        )
        self.delete_button.pack(side="left", padx=(0, 5))
        ctk.CTkButton(
            actions, text="Clear", width=65, command=self.clear
        ).pack(side="left", padx=(0, 5))
        ctk.CTkButton(
            actions, text="Refresh", width=75, command=self.on_show
        ).pack(side="left")

        table = ctk.CTkFrame(self)
        table.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 6))
        table.grid_rowconfigure(0, weight=1)
        table.grid_columnconfigure(0, weight=1)
        columns = ("ProjectID",) + tuple(field for field, _ in PROJECT_FIELDS)
        self.tree = ttk.Treeview(
            table, columns=columns, show="headings", selectmode="browse", height=4
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        labels = ("ID",) + tuple(label for _, label in PROJECT_FIELDS)
        for column, label in zip(columns, labels):
            self.tree.heading(column, text=label)
            self.tree.column(column, width=115, minwidth=75, stretch=True)
        vertical = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        horizontal = ttk.Scrollbar(table, orient="horizontal", command=self.tree.xview)
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.tree.bind("<<TreeviewSelect>>", self.select)

        self.status = ctk.CTkLabel(self, text="", anchor="w", justify="left")
        self.status.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 8))
        self.set_actions()

    def on_show(self):
        return self.refresh()

    def set_actions(self):
        state = "normal" if self.selected_id is not None else "disabled"
        self.update_button.configure(state=state)
        self.delete_button.configure(state=state)

    def show_status(self, text, error=False):
        color = ("#B23B3B", "#FF8888") if error else ("gray30", "gray75")
        self.status.configure(text=text, text_color=color)

    def clear(self):
        self.selected_id = None
        selection = self.tree.selection()
        if selection:
            self.tree.selection_remove(*selection)
        for entry in self.entries.values():
            entry.delete(0, "end")
        self.set_actions()

    def select(self, _event=None):
        selection = self.tree.selection()
        if not selection or selection[0] not in self.records:
            return
        row = self.records[selection[0]]
        self.selected_id = row[0]
        for (field, _), value in zip(PROJECT_FIELDS, row[1:]):
            entry = self.entries[field]
            entry.delete(0, "end")
            if value is not None:
                entry.insert(0, str(value))
        self.set_actions()
        self.show_status(f"Editing project #{self.selected_id}.")

    def values(self):
        values = []
        for field, _ in PROJECT_FIELDS:
            raw = self.entries[field].get().strip()
            if not raw:
                values.append(None)
                continue
            try:
                values.append(int(raw))
            except ValueError:
                raise ValueError(f"{field} must be a whole number or blank.") from None
        return values

    def refresh(self):
        try:
            rows = get_projects()
        except sqlite3.Error as exc:
            self.tree.delete(*self.tree.get_children())
            self.records = {}
            self.clear()
            self.show_status(f"Unable to load projects: {exc}", True)
            return False

        self.clear()
        self.tree.delete(*self.tree.get_children())
        self.records = {str(row[0]): row for row in rows}
        for iid, row in self.records.items():
            self.tree.insert(
                "", "end", iid=iid,
                values=["" if value is None else value for value in row],
            )
        self.show_status(f"{len(rows)} project(s).")
        return True

    def report_error(self, exc, action="save"):
        if isinstance(exc, sqlite3.IntegrityError):
            self.show_status(
                f"Unable to {action}: database constraint failed. {exc}", True
            )
        else:
            self.show_status(f"Unable to {action}: {exc}", True)

    def create_action(self):
        try:
            project_id = create_projects(*self.values())
        except (sqlite3.Error, ValueError) as exc:
            self.report_error(exc)
            return
        if self.refresh():
            self.show_status(f"Project #{project_id} created.")
        else:
            self.show_status(
                f"Project #{project_id} saved, but refreshing failed. Press Refresh.",
                True,
            )

    def update_action(self):
        if self.selected_id is None:
            return
        try:
            count = update_projects(self.selected_id, *self.values())
        except (sqlite3.Error, ValueError) as exc:
            self.report_error(exc)
            return
        if self.refresh():
            self.show_status("Project updated." if count else "Project no longer exists.")
        else:
            self.show_status("Update completed, but refreshing failed. Press Refresh.", True)

    def delete_action(self):
        if self.selected_id is None:
            return
        if not messagebox.askyesno(
            "Confirm Delete", "Delete this project?", parent=self.winfo_toplevel()
        ):
            return
        try:
            count = delete_projects(self.selected_id)
        except sqlite3.Error as exc:
            self.report_error(exc, "delete")
            return
        if self.refresh():
            self.show_status("Project deleted." if count else "Project no longer exists.")
        else:
            self.show_status("Delete completed, but refreshing failed. Press Refresh.", True)


class ClientProjectsPage(ctk.CTkFrame):
    """Display project cards belonging to the currently signed-in client."""

    def __init__(self, master, get_client_id):
        super().__init__(master, corner_radius=0)
        self.get_client_id = get_client_id
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self, text="My Projects",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 8))
        ctk.CTkButton(
            self, text="New Project", width=105, command=self.create_project_dialog,
        ).grid(row=0, column=1, padx=(0, 8), pady=(18, 8))
        ctk.CTkButton(
            self, text="Refresh", width=85, command=self.on_show,
        ).grid(row=0, column=2, sticky="e", padx=20, pady=(18, 8))
        self.status = ctk.CTkLabel(self, text="", anchor="w")
        self.status.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 8))
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def on_show(self):
        return self.refresh()

    def create_project_dialog(self):
        client_id = self.get_client_id()
        if client_id is None:
            self.status.configure(text="Sign in with a client email to create a project.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Create Project")
        dialog.geometry("440x205")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            dialog, text="Create a new project",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=22, pady=(20, 8))
        name_entry = ctk.CTkEntry(
            dialog, placeholder_text="Project name", height=36,
        )
        name_entry.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 8))
        error = ctk.CTkLabel(
            dialog, text="", anchor="w", text_color=("#B23B3B", "#FF8888"),
        )
        error.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 4))

        def save():
            project_name = name_entry.get().strip()
            try:
                project_id = create_client_project(client_id, project_name)
            except (sqlite3.Error, ValueError) as exc:
                error.configure(text=str(exc))
                return

            dialog.destroy()
            if self.refresh():
                self.status.configure(text=f"Project '{project_name}' created.")
            else:
                self.status.configure(
                    text=f"Project #{project_id} was created, but the list could not refresh."
                )

        actions = ctk.CTkFrame(dialog, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="e", padx=22, pady=(4, 16))
        ctk.CTkButton(
            actions, text="Cancel", width=85, fg_color="transparent",
            border_width=1, command=dialog.destroy,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            actions, text="Create", width=85, command=save,
        ).pack(side="right")

    def clear_cards(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

    def refresh(self):
        self.clear_cards()
        client_id = self.get_client_id()
        if client_id is None:
            self.status.configure(text="Sign in with a client email to view projects.")
            return False

        try:
            rows = get_projects_for_client(client_id, include_price=True)
        except sqlite3.Error as exc:
            self.status.configure(text=f"Unable to load your projects: {exc}")
            return False

        self.status.configure(text=f"{len(rows)} project(s) for Client #{client_id}.")
        if not rows:
            ctk.CTkLabel(
                self.scroll_frame, text="No projects are currently assigned to your client."
            ).grid(row=0, column=0, pady=25)
            return True

        for index, row in enumerate(rows):
            self.create_card(index, row)
        return True

    def create_card(self, index, row):
        card = ctk.CTkFrame(
            self.scroll_frame, corner_radius=12, border_width=1,
            border_color=("gray82", "gray28"),
        )
        card.grid(row=index, column=0, sticky="ew", padx=10, pady=6)
        card.grid_columnconfigure(0, weight=1)
        project_name = str(row[1]).strip() if row[1] is not None else ""
        project_name = project_name or f"Untitled project #{row[0]}"
        freelancer_name = str(row[2]).strip() if row[2] is not None else ""
        if freelancer_name and row[3] is not None:
            freelancer_name = f"{freelancer_name} (ID #{row[3]})"
        elif row[3] is not None:
            freelancer_name = f"Freelancer #{row[3]}"
        else:
            freelancer_name = "No freelancer assigned"

        ctk.CTkLabel(
            card, text=project_name, anchor="w", justify="left", wraplength=620,
            font=ctk.CTkFont(size=19, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 2))
        ctk.CTkLabel(
            card, text=f"PROJECT #{row[0]}", anchor="w",
            text_color=("gray45", "gray65"),
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        ctk.CTkFrame(
            card, height=1, fg_color=("gray82", "gray28"),
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
        ctk.CTkLabel(
            card, text="FREELANCER", anchor="w",
            text_color=("gray45", "gray65"),
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=3, column=0, sticky="ew", padx=16)
        ctk.CTkLabel(
            card, text=freelancer_name, anchor="w",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=4, column=0, sticky="ew", padx=16, pady=(2, 8))
        ctk.CTkLabel(card, text=f"Agreed price: {format_price(row[4])}", anchor="w").grid(
            row=5, column=0, sticky="ew", padx=16, pady=(0, 14))


class FreelancerProjectsPage(ctk.CTkFrame):
    """Display projects assigned to the currently signed-in freelancer."""

    def __init__(self, master, get_freelancer_id):
        super().__init__(master, corner_radius=0)
        self.get_freelancer_id = get_freelancer_id
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self, text="My Projects",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(18, 8))
        ctk.CTkButton(
            self, text="Refresh", width=85, command=self.on_show,
        ).grid(row=0, column=1, sticky="e", padx=20, pady=(18, 8))
        self.status = ctk.CTkLabel(self, text="", anchor="w")
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 8))
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(
            row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10)
        )
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def on_show(self):
        self.clear_cards()
        freelancer_id = self.get_freelancer_id()
        if freelancer_id is None:
            self.status.configure(text="Sign in as a freelancer to view projects.")
            return False
        try:
            rows = get_projects_for_freelancer(freelancer_id, include_price=True)
        except sqlite3.Error as exc:
            self.status.configure(text=f"Unable to load your projects: {exc}")
            return False

        self.status.configure(text=f"{len(rows)} project(s) assigned to you.")
        if not rows:
            ctk.CTkLabel(
                self.scroll_frame, text="You are not currently assigned to any projects."
            ).grid(row=0, column=0, pady=25)
            return True

        for index, row in enumerate(rows):
            self.create_card(index, row)
        return True

    def clear_cards(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

    def create_card(self, index, row):
        project_id, project_name, client_id, client_name, price_cents = row
        title = project_name.strip() if project_name else f"Untitled project #{project_id}"
        client = client_name.strip() if client_name else f"Client #{client_id}"
        card = ctk.CTkFrame(
            self.scroll_frame, corner_radius=12, border_width=1,
            border_color=("gray82", "gray28"),
        )
        card.grid(row=index, column=0, sticky="ew", padx=10, pady=6)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card, text=title, anchor="w", justify="left", wraplength=620,
            font=ctk.CTkFont(size=19, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 2))
        ctk.CTkLabel(
            card, text=f"PROJECT #{project_id}",
            anchor="w", text_color=("gray45", "gray65"),
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        ctk.CTkFrame(
            card, height=1, fg_color=("gray82", "gray28"),
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
        ctk.CTkLabel(
            card, text=f"CLIENT  |  {client} (ID #{client_id})",
            anchor="w", font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 8))
        ctk.CTkLabel(card, text=f"Agreed price: {format_price(price_cents)}", anchor="w").grid(
            row=4, column=0, sticky="ew", padx=16, pady=(0, 14))
