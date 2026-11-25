"""Proposal inbox for signed-in freelancers."""
import sqlite3
from tkinter import messagebox

import customtkinter as ctk

from backend.database import get_freelancer_proposals, respond_to_project_proposal
from backend.listings_database import format_price


class FreelancerProposalsPage(ctk.CTkFrame):
    """Show project invitations and let the recipient accept or decline."""

    def __init__(self, master, get_freelancer_id):
        super().__init__(master, corner_radius=0)
        self.get_freelancer_id = get_freelancer_id
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self, text="Project Proposals",
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
            self.status.configure(text="Sign in as a freelancer to view proposals.")
            return False
        try:
            proposals = get_freelancer_proposals(freelancer_id, include_price=True)
        except (sqlite3.Error, ValueError) as exc:
            self.status.configure(text=f"Unable to load proposals: {exc}")
            return False

        pending_count = sum(row[6] == "pending" for row in proposals)
        self.status.configure(
            text=f"{len(proposals)} proposal(s), {pending_count} awaiting your response."
        )
        if not proposals:
            ctk.CTkLabel(
                self.scroll_frame, text="You have no project proposals."
            ).grid(row=0, column=0, pady=25)
            return True

        for index, proposal in enumerate(proposals):
            self.create_card(index, proposal)
        return True

    def clear_cards(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

    def create_card(self, index, proposal):
        proposal_id, proposal_name, project_id, project_name, client_id, client_name, status, price_cents = proposal
        card = ctk.CTkFrame(
            self.scroll_frame, corner_radius=12, border_width=1,
            border_color=("gray82", "gray28"),
        )
        card.grid(row=index, column=0, sticky="ew", padx=10, pady=6)
        card.grid_columnconfigure(0, weight=1)

        title = project_name or proposal_name or f"Project #{project_id}"
        client = client_name or f"Client #{client_id}"
        ctk.CTkLabel(
            card, text=title, anchor="w", justify="left", wraplength=650,
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(13, 3))
        ctk.CTkLabel(
            card, text=f"PROJECT #{project_id}  |  PROPOSAL #{proposal_id}",
            anchor="w", text_color=("gray45", "gray65"),
            font=ctk.CTkFont(size=11, weight="bold"),
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))
        ctk.CTkLabel(
            card, text=f"{client} invited you to join this project.\nOffered price: {format_price(price_cents)}",
            anchor="w", justify="left", wraplength=650,
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))

        if status == "pending":
            ctk.CTkLabel(
                card,
                text="Accepting assigns you to this project, replacing its current freelancer if any.",
                anchor="w", justify="left", wraplength=650,
                text_color=("gray45", "gray65"),
            ).grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 10))
            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.grid(row=4, column=0, sticky="e", padx=16, pady=(0, 13))
            ctk.CTkButton(
                actions, text="Decline", width=90,
                fg_color="transparent", border_width=1,
                command=lambda pid=proposal_id: self.respond(pid, False),
            ).pack(side="right", padx=(8, 0))
            ctk.CTkButton(
                actions, text="Accept", width=90,
                command=lambda pid=proposal_id: self.respond(pid, True),
            ).pack(side="right")
        else:
            ctk.CTkLabel(
                card, text=f"Status: {status.title()}", anchor="w",
                text_color=("gray45", "gray65"),
            ).grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 13))

    def respond(self, proposal_id, accept):
        freelancer_id = self.get_freelancer_id()
        if freelancer_id is None:
            self.status.configure(text="Your freelancer session is no longer active.")
            return
        try:
            updated = respond_to_project_proposal(
                proposal_id, freelancer_id, accept
            )
        except (sqlite3.Error, ValueError) as exc:
            messagebox.showerror("Unable to Respond", str(exc), parent=self.winfo_toplevel())
            return

        if not updated:
            self.status.configure(text="This proposal is no longer pending.")
            self.on_show()
            return
        self.on_show()
