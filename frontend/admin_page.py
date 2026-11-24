"""A self-contained management page for the marketplace."""
import sqlite3
from tkinter import ttk, END
import customtkinter as ctk
from backend.admin_database import (
    TABLES, get_schema, get_records, create_record, update_record, delete_record,
)

LABELS = {
    'freelancers': 'Freelancers', 'clients': 'Clients', 'projects': 'Projects',
    'payments': 'Payments', 'proposals': 'Proposals', 'reviews': 'Reviews',
    'skillsList': 'Skills List', 'milestones': 'Milestones',
}


class AdminPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.table = None
        self.schema = None
        self.selected_id = None
        self.entries = {}
        self.records = {}
        self.buttons = {}
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=155, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky='ns')
        ctk.CTkLabel(sidebar, text='Admin Panel', font=ctk.CTkFont(size=20, weight='bold')).pack(padx=12, pady=(18, 14))
        for table in TABLES:
            button = ctk.CTkButton(sidebar, text=LABELS[table], width=138,
                                   command=lambda t=table: self.open_table(t))
            button.pack(fill='x', padx=8, pady=4)
            self.buttons[table] = button

        self.content = ctk.CTkFrame(self, fg_color='transparent')
        self.content.grid(row=0, column=1, sticky='nsew', padx=14, pady=12)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(4, weight=1)
        self.heading = ctk.CTkLabel(self.content, text='Admin Panel', font=ctk.CTkFont(size=24, weight='bold'))
        self.heading.grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.hint = ctk.CTkLabel(self.content, text='Select a table to begin.', anchor='w', justify='left', wraplength=560)
        self.hint.grid(row=1, column=0, sticky='ew', pady=(0, 5))
        self.form = ctk.CTkFrame(self.content)
        self.form.grid(row=2, column=0, sticky='ew')
        for col in (0, 1):
            self.form.grid_columnconfigure(col, weight=1, uniform='fields')

        actions = ctk.CTkFrame(self.content, fg_color='transparent')
        actions.grid(row=3, column=0, sticky='ew', pady=8)
        self.action_buttons = []
        for label, callback in [('Create', self.create), ('Update', self.update),
                                ('Delete', self.delete), ('Clear', self.clear),
                                ('Refresh', self.refresh)]:
            kwargs = {'fg_color': '#B23B3B', 'hover_color': '#8F2D2D'} if label == 'Delete' else {}
            button = ctk.CTkButton(actions, text=label, width=76, command=callback, **kwargs)
            button.pack(side='left', padx=(0, 5))
            self.action_buttons.append(button)

        # Use a native Treeview rather than nested CTkScrollableFrames.
        # Both scrollbars are provided for tables with many fields/records.
        table_box = ctk.CTkFrame(self.content)
        table_box.grid(row=4, column=0, sticky='nsew')
        table_box.grid_rowconfigure(0, weight=1)
        table_box.grid_columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(table_box, show='headings', selectmode='browse')
        self.tree.grid(row=0, column=0, sticky='nsew')
        vertical = ttk.Scrollbar(table_box, orient='vertical', command=self.tree.yview)
        horizontal = ttk.Scrollbar(table_box, orient='horizontal', command=self.tree.xview)
        vertical.grid(row=0, column=1, sticky='ns')
        horizontal.grid(row=1, column=0, sticky='ew')
        self.tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        self.tree.bind('<<TreeviewSelect>>', self.select_record)
        self.status = ctk.CTkLabel(self.content, text='', anchor='w')
        self.status.grid(row=5, column=0, sticky='ew', pady=(5, 0))
        self.set_actions(False)

    def set_actions(self, enabled):
        for button in self.action_buttons:
            button.configure(state='normal' if enabled else 'disabled')

    def on_show(self):
        """Called when the main app navigates to Admin."""
        self.open_table(self.table or 'freelancers')

    def open_table(self, table):
        try:
            schema = get_schema(table)
            rows = get_records(table)
        except (sqlite3.Error, ValueError) as exc:
            self.show_error(exc)
            return
        self.table, self.schema = table, schema
        self.heading.configure(text=f'{LABELS[table]} Management')
        self.hint.configure(text='Select a row to edit. Blank optional fields become NULL; on Create, blank fields with defaults use those defaults. Foreign key fields accept existing IDs.')
        for key, button in self.buttons.items():
            button.configure(fg_color=('gray65', 'gray30') if key == table else ('#3B8ED0', '#1F6AA5'))
        for widget in self.form.winfo_children():
            widget.destroy()
        self.entries = {}
        foreign = {fk['from']: fk for fk in schema['foreign_keys']}
        editable = [col for col in schema['columns'] if not col['pk']]
        for index, col in enumerate(editable):
            name = col['name']
            label = name + (' *' if col['notnull'] and col['dflt_value'] is None else '')
            if name in foreign:
                fk = foreign[name]
                label += f' → {fk["table"]}'
            field = ctk.CTkFrame(self.form, fg_color='transparent')
            field.grid(row=index // 2, column=index % 2, sticky='ew', padx=8, pady=3)
            ctk.CTkLabel(field, text=label, anchor='w').pack(fill='x')
            entry = ctk.CTkEntry(field, height=30)
            entry.pack(fill='x')
            self.entries[name] = entry
        columns = [col['name'] for col in schema['columns']]
        self.tree.configure(columns=columns)
        for name in columns:
            self.tree.heading(name, text=name)
            self.tree.column(name, width=120, minwidth=75, stretch=True)
        self.set_actions(True)
        self.render(rows)

    def render(self, rows):
        self.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.records = {}
        pk = self.schema['primary_key']
        columns = [col['name'] for col in self.schema['columns']]
        for row in rows:
            iid = str(row[pk])
            self.records[iid] = row
            self.tree.insert('', END, iid=iid, values=[
                '' if row[col] is None else str(row[col]) for col in columns])
        self.status.configure(text=f'{len(rows)} record(s) • Select a row to edit or delete.')

    def refresh(self):
        if self.table is None:
            return
        try:
            rows = get_records(self.table)
        except (sqlite3.Error, ValueError) as exc:
            self.show_error(exc)
            return
        self.render(rows)

    def clear(self):
        self.selected_id = None
        selection = self.tree.selection()
        if selection:
            self.tree.selection_remove(*selection)
        for entry in self.entries.values():
            entry.delete(0, END)

    def select_record(self, _event=None):
        selection = self.tree.selection()
        if not selection or selection[0] not in self.records:
            return
        row = self.records[selection[0]]
        self.selected_id = row[self.schema['primary_key']]
        for name, entry in self.entries.items():
            entry.delete(0, END)
            if row[name] is not None:
                entry.insert(0, str(row[name]))
        self.status.configure(text=f'Selected {self.schema["primary_key"]}: {self.selected_id}')

    def form_values(self, creating=False):
        values = {}
        for col in self.schema['columns']:
            name = col['name']
            if name not in self.entries:
                continue
            raw = self.entries[name].get()
            if not raw.strip():
                if creating and col['dflt_value'] is not None:
                    continue
                if col['notnull']:
                    raise ValueError(f'{name} is required.')
                values[name] = None
                continue
            declared = col['type'].upper()
            try:
                if 'INT' in declared:
                    values[name] = int(raw)
                elif any(t in declared for t in ('REAL', 'FLOA', 'DOUB')):
                    values[name] = float(raw)
                else:
                    values[name] = raw
            except ValueError:
                raise ValueError(f'{name} must contain a valid number.') from None
        return values

    def show_error(self, exc):
        if isinstance(exc, sqlite3.IntegrityError) and 'foreign key' in str(exc).lower():
            message = ('A referenced ID does not exist, or another record still references '
                       'this record. Check related tables before saving or deleting.')
        elif isinstance(exc, sqlite3.OperationalError) and 'locked' in str(exc).lower():
            message = 'The database is busy. Close other database editors or finish their transactions, then retry.'
        else:
            message = str(exc)
        # Error text is shown inline, avoiding the modal mouse-wheel issue
        # previously seen with CTkScrollableFrame and message dialogs.
        self.status.configure(text='Error: ' + message, wraplength=600)

    def create(self):
        try:
            record_id = create_record(self.table, self.form_values(creating=True))
        except (sqlite3.Error, ValueError) as exc:
            self.show_error(exc)
            return
        self.after_write(f'Created record #{record_id}.')

    def update(self):
        if self.selected_id is None:
            self.status.configure(text='Select a record before updating.')
            return
        try:
            count = update_record(self.table, self.selected_id, self.form_values())
        except (sqlite3.Error, ValueError) as exc:
            self.show_error(exc)
            return
        self.after_write('Record updated.' if count else 'Record no longer exists.')

    def delete(self):
        if self.selected_id is None:
            self.status.configure(text='Select a record before deleting.')
            return
        # Use a CTk confirmation window instead of a native messagebox.
        table, record_id = self.table, self.selected_id
        dialog = ctk.CTkToplevel(self)
        dialog.title('Confirm Delete')
        dialog.transient(self.winfo_toplevel())
        dialog.resizable(False, False)
        ctk.CTkLabel(dialog, text=f'Delete {LABELS[table]} record #{record_id}?', padx=20, pady=16).pack()
        actions = ctk.CTkFrame(dialog, fg_color='transparent')
        actions.pack(padx=10, pady=(0, 12))

        def confirm():
            dialog.destroy()
            try:
                count = delete_record(table, record_id)
            except (sqlite3.Error, ValueError) as exc:
                self.show_error(exc)
                return
            self.after_write('Record deleted.' if count else 'Record no longer exists.')

        ctk.CTkButton(actions, text='Cancel', command=dialog.destroy).pack(side='left', padx=5)
        ctk.CTkButton(actions, text='Delete', fg_color='#B23B3B', command=confirm).pack(side='left', padx=5)
        dialog.wait_visibility()
        dialog.grab_set()

    def after_write(self, message):
        try:
            rows = get_records(self.table)
        except (sqlite3.Error, ValueError) as exc:
            self.status.configure(text=f'{message} Refresh failed: {exc}')
            return
        self.render(rows)
        self.status.configure(text=message)
