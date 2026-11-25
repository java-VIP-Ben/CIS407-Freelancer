"""CustomTkinter Home and Listings management pages."""
import sqlite3
from tkinter import StringVar, messagebox, ttk

import customtkinter as ctk

from backend.listings_database import (
    SEARCH_FIELDS, initialize_listings, get_freelancer_options, get_listings,
    get_listings_for_freelancer, filter_listings, create_listing, update_listing,
    update_listing_for_freelancer, delete_listing, delete_listing_for_freelancer,
    parse_price, format_price,
)


class ListingsHome(ctk.CTkFrame):
    def __init__(self, master, on_book):
        super().__init__(master, corner_radius=0)
        self.on_book = on_book
        self.rows = []
        self.ready = False
        self.pending = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(self, text="Find Your Freelancer", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        bar = ctk.CTkFrame(self, corner_radius=8)
        bar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 8))
        bar.grid_columnconfigure(0, weight=1)
        self.query = StringVar(master=self)
        self.field = StringVar(master=self, value="All fields")
        ctk.CTkEntry(bar, textvariable=self.query, placeholder_text="Search listings...", height=36).grid(
            row=0, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkOptionMenu(bar, values=list(SEARCH_FIELDS), variable=self.field,
                          width=150).grid(row=0, column=1, padx=(0, 8), pady=10)
        ctk.CTkButton(bar, text="Clear", width=65, command=self.clear_search).grid(
            row=0, column=2, padx=(0, 8), pady=10)
        ctk.CTkButton(bar, text="Refresh", width=75, command=self.on_show).grid(
            row=0, column=3, padx=(0, 10), pady=10)
        self.status = ctk.CTkLabel(self, text="", anchor="w")
        self.status.grid(row=2, column=0, sticky="ew", padx=20)
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        self.query.trace_add("write", self.schedule_search)
        self.field.trace_add("write", self.schedule_search)

    def clear_search(self):
        self.query.set("")
        self.field.set("All fields")

    def schedule_search(self, *_):
        if self.pending is not None:
            self.after_cancel(self.pending)
        self.pending = self.after(150, self.run_search)

    def run_search(self):
        self.pending = None
        self.render()

    def on_show(self):
        try:
            initialize_listings()
            self.rows = get_listings()
        except (sqlite3.Error, ValueError) as exc:
            self.ready = False
            self.rows = []
            self.clear_cards()
            self.status.configure(text=f"Unable to load listings: {exc}")
            return
        self.ready = True
        self.render()

    def clear_cards(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

    def render(self):
        if self.pending is not None:
            self.after_cancel(self.pending)
            self.pending = None
        if not self.ready:
            return
        rows = filter_listings(self.rows, self.query.get(), self.field.get())
        self.clear_cards()
        self.status.configure(text=f"{len(rows)} of {len(self.rows)} listings")
        if not rows:
            text = ("No listings match your search." if self.rows else
                    "No listings yet. Open Listings to create the first one.")
            ctk.CTkLabel(self.scroll_frame, text=text).grid(row=0, column=0, pady=25)
            return
        for index, row in enumerate(rows):
            self.create_card(index, row)

    def create_card(self, index, row):
        card = ctk.CTkFrame(self.scroll_frame, corner_radius=8)
        card.grid(row=index, column=0, sticky="ew", padx=10, pady=6)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=row["JobTitle"], anchor="w", justify="left",
                     wraplength=490, font=ctk.CTkFont(size=17, weight="bold")).grid(
            row=0, column=0, sticky="ew", padx=15, pady=(12, 2))
        ctk.CTkLabel(card, text=f"By {row['Name'] or 'Unnamed freelancer'}", anchor="w",
                     text_color=("gray35", "gray70")).grid(row=1, column=0, sticky="ew", padx=15)
        review_count = row["ReviewCount"]
        rating_text = (
            f"Average rating: {row['AverageRating']:.1f}/5 ({review_count} "
            f"review{'s' if review_count != 1 else ''})"
            if review_count else "No reviews yet"
        )
        ctk.CTkLabel(
            card, text=rating_text, anchor="w",
            text_color=("#A06A00", "#F2C14E"),
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=2, column=0, sticky="ew", padx=15, pady=(2, 0))
        ctk.CTkLabel(card, text=row["Description"], anchor="w", justify="left", wraplength=490).grid(
            row=3, column=0, sticky="ew", padx=15, pady=(7, 3))
        details = f"Skills: {row['Skills']}"
        if row["Category"]:
            details += f"  |  Category: {row['Category']}"
        ctk.CTkLabel(card, text=details, anchor="w", justify="left", wraplength=490,
                     text_color=("#245B93", "#8DBFF5")).grid(
            row=4, column=0, sticky="ew", padx=15, pady=(2, 12))
        ctk.CTkLabel(card, text=format_price(row["PriceCents"]),
                     font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=1, rowspan=2, padx=15, pady=(12, 2))
        ctk.CTkButton(card, text="Book", width=90,
                      state="normal" if row["PriceCents"] is not None else "disabled",
                      command=lambda r=row: self.on_book(r)).grid(
            row=3, column=1, rowspan=2, padx=15, pady=(2, 12))


class ListingsPage(ctk.CTkFrame):
    """Create, select, update and delete service listings."""
    def __init__(self, master, freelancer_id_getter=None):
        super().__init__(master, corner_radius=0)
        self.freelancer_id_getter = freelancer_id_getter
        self.is_freelancer_mode = freelancer_id_getter is not None
        self.selected_id = None
        self.options = {}
        self.records = {}
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        ctk.CTkLabel(self, text="My Listings" if self.is_freelancer_mode else "Manage Listings",
                     font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=20, pady=(18, 4))
        ctk.CTkLabel(self, text="Create a service listing or select one of your listings to edit.",
                     anchor="w").grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 8))
        form = ctk.CTkFrame(self, corner_radius=8)
        form.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 8))
        form.grid_columnconfigure(0, weight=1, uniform="fields")
        form.grid_columnconfigure(1, weight=1, uniform="fields")
        self.freelancer = StringVar(master=self, value="Select a freelancer")
        self.freelancer_label = ctk.CTkLabel(form, text="Freelancer *", anchor="w")
        self.freelancer_label.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 0))
        self.freelancer_menu = ctk.CTkOptionMenu(form, values=["Select a freelancer"], variable=self.freelancer)
        self.freelancer_menu.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 4))
        if self.is_freelancer_mode:
            self.freelancer_label.grid_remove()
            self.freelancer_menu.grid_remove()
        self.title_entry = self.entry(form, "Job / title *", 0, 1)
        self.skills_entry = self.entry(form, "Skills * (comma separated)", 2, 0)
        self.category_entry = self.entry(form, "Category (optional)", 2, 1)
        ctk.CTkLabel(form, text="Description *", anchor="w").grid(row=4, column=0, sticky="ew", padx=12)
        self.price_entry = self.entry(form, "Fixed price (USD) *", 4, 1)
        self.description = ctk.CTkTextbox(form, height=76, wrap="word")
        self.description.grid(row=5, column=0, sticky="ew", padx=12, pady=(0, 10))
        self.price_entry.grid_configure(sticky="new")
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 8))
        self.create_button = ctk.CTkButton(actions, text="Create Listing", width=115, command=self.create_action)
        self.create_button.pack(side="left", padx=(0, 5))
        self.update_button = ctk.CTkButton(actions, text="Update", width=75, command=self.update_action)
        self.update_button.pack(side="left", padx=(0, 5))
        self.delete_button = ctk.CTkButton(actions, text="Delete", width=75, command=self.delete_action,
                                           fg_color="#B23B3B", hover_color="#8F2D2D")
        self.delete_button.pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions, text="Clear", width=65, command=self.clear).pack(side="left", padx=(0, 5))
        ctk.CTkButton(actions, text="Refresh", width=75, command=self.on_show).pack(side="left")
        table = ctk.CTkFrame(self)
        table.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 6))
        table.grid_rowconfigure(0, weight=1)
        table.grid_columnconfigure(0, weight=1)
        columns = ("ListingID", "Name", "JobTitle", "Skills", "Category", "Price")
        self.tree = ttk.Treeview(table, columns=columns, show="headings", selectmode="browse", height=4)
        self.tree.grid(row=0, column=0, sticky="nsew")
        for col, label, width in zip(columns, ("ID", "Freelancer", "Job / title", "Skills", "Category", "Price (USD)"), (55, 145, 190, 160, 120, 110)):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, minwidth=45, stretch=True)
        y = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        x = ttk.Scrollbar(table, orient="horizontal", command=self.tree.xview)
        y.grid(row=0, column=1, sticky="ns")
        x.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=y.set, xscrollcommand=x.set)
        self.tree.bind("<<TreeviewSelect>>", self.select)
        self.status = ctk.CTkLabel(self, text="", anchor="w", justify="left", wraplength=670)
        self.status.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 8))
        self.set_actions(False)

    @staticmethod
    def entry(form, label, row, col):
        ctk.CTkLabel(form, text=label, anchor="w").grid(row=row, column=col, sticky="ew", padx=12, pady=(6, 0))
        entry = ctk.CTkEntry(form, height=30)
        entry.grid(row=row+1, column=col, sticky="ew", padx=12, pady=(0, 4))
        return entry

    def set_actions(self, ready=True):
        self.create_button.configure(state="normal" if ready and self.options else "disabled")
        state = "normal" if ready and self.selected_id is not None else "disabled"
        self.update_button.configure(state=state)
        self.delete_button.configure(state=state)

    def show_status(self, text, error=False):
        self.status.configure(text=text, text_color=("#B23B3B", "#FF8888") if error else ("gray30", "gray75"))

    def on_show(self):
        return self.refresh()

    def refresh(self):
        try:
            initialize_listings()
            if self.is_freelancer_mode:
                freelancer_id = self.freelancer_id_getter()
                if freelancer_id is None:
                    raise ValueError("Sign in again to manage listings.")
                options = get_freelancer_options()
                rows = get_listings_for_freelancer(freelancer_id)
                names = {row["FreelancerID"]: row["Name"] for row in options}
                name = names.get(freelancer_id)
                self.options = {f"#{freelancer_id} — {name or 'Your listing'}": freelancer_id}
                self.freelancer.set(next(iter(self.options)))
            else:
                options = get_freelancer_options()
                rows = get_listings()
                self.options = {f"#{row['FreelancerID']} — {row['Name'] or 'Unnamed freelancer'}": row['FreelancerID'] for row in options}
                self.freelancer_menu.configure(values=list(self.options) or ["No freelancers available"])
        except (sqlite3.Error, ValueError) as exc:
            self.options = {}
            self.records = {}
            self.tree.delete(*self.tree.get_children())
            if not self.is_freelancer_mode:
                self.freelancer_menu.configure(values=["No freelancers available"])
            self.clear()
            self.set_actions(False)
            self.show_status(f"Unable to load listings: {exc}", True)
            return False
        self.clear()
        self.tree.delete(*self.tree.get_children())
        self.records = {str(row["ListingID"]): row for row in rows}
        for iid, row in self.records.items():
            self.tree.insert("", "end", iid=iid, values=[row[key] or "" for key in ("ListingID", "Name", "JobTitle", "Skills", "Category")] + [format_price(row["PriceCents"])])
        self.show_status(f"{len(rows)} listing(s)." if self.options else "Add a freelancer in Admin before creating a listing.")
        return True

    def clear(self):
        self.selected_id = None
        selection = self.tree.selection()
        if selection:
            self.tree.selection_remove(*selection)
        self.freelancer.set("Select a freelancer" if self.options else "No freelancers available")
        for entry in (self.title_entry, self.skills_entry, self.category_entry, self.price_entry):
            entry.delete(0, "end")
        self.description.delete("1.0", "end")
        self.set_actions()

    def select(self, event=None):
        selection = self.tree.selection()
        if not selection or selection[0] not in self.records:
            return
        row = self.records[selection[0]]
        self.selected_id = row["ListingID"]
        self.freelancer.set(next((label for label, fid in self.options.items()
                                  if fid == row["FreelancerID"]), "Select a freelancer"))
        for entry, key in ((self.title_entry, "JobTitle"), (self.skills_entry, "Skills"), (self.category_entry, "Category")):
            entry.delete(0, "end")
            entry.insert(0, row[key] or "")
        self.description.delete("1.0", "end")
        self.description.insert("1.0", row["Description"] or "")
        self.price_entry.delete(0, "end")
        if row["PriceCents"] is not None:
            self.price_entry.insert(0, format_price(row["PriceCents"]).replace("$", "").replace(",", ""))
        self.set_actions()
        self.show_status(f"Editing listing #{self.selected_id}.")

    def values(self):
        freelancer_id = (self.freelancer_id_getter() if self.is_freelancer_mode
                         else self.options.get(self.freelancer.get()))
        return (freelancer_id, self.title_entry.get(),
                self.description.get("1.0", "end-1c"), self.skills_entry.get(), self.category_entry.get(),
                parse_price(self.price_entry.get()))

    def report_error(self, exc):
        if isinstance(exc, sqlite3.IntegrityError):
            self.show_status(f"Unable to save: database constraint failed. {exc}", True)
        else:
            self.show_status(str(exc), True)

    def create_action(self):
        try:
            new_id = create_listing(*self.values())
        except (sqlite3.Error, ValueError) as exc:
            self.report_error(exc)
            return
        if self.refresh():
            self.show_status(f"Listing #{new_id} created. It is now visible on Home.")
        else:
            self.show_status(f"Listing #{new_id} saved, but refreshing failed. Press Refresh.", True)

    def update_action(self):
        if self.selected_id is None:
            return
        try:
            if self.is_freelancer_mode:
                count = update_listing_for_freelancer(
                    self.selected_id, *self.values()
                )
            else:
                count = update_listing(self.selected_id, *self.values())
        except (sqlite3.Error, ValueError) as exc:
            self.report_error(exc)
            return
        if self.refresh():
            self.show_status("Listing updated." if count else "Listing no longer exists.")
        else:
            self.show_status("Update completed, but refreshing failed. Press Refresh.", True)

    def delete_action(self):
        if self.selected_id is None:
            return
        if not messagebox.askyesno("Confirm Delete", "Delete this listing? The freelancer profile will be kept.", parent=self.winfo_toplevel()):
            return
        try:
            if self.is_freelancer_mode:
                count = delete_listing_for_freelancer(
                    self.selected_id, self.freelancer_id_getter()
                )
            else:
                count = delete_listing(self.selected_id)
        except (sqlite3.Error, ValueError) as exc:
            self.report_error(exc)
            return
        if self.refresh():
            self.show_status("Listing deleted." if count else "Listing no longer exists.")
        else:
            self.show_status("Delete completed, but refreshing failed. Press Refresh.", True)
