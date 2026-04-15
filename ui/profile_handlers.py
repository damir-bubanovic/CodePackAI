import tkinter as tk
from tkinter import ttk, messagebox

from services.profile_service import (
    get_profile_by_id,
    create_profile,
    update_profile,
    delete_profile,
)


class ProfileHandlers:
    def __init__(self, window):
        self.window = window

    def create_profile(self):
        dialog = tk.Toplevel(self.window.window)
        dialog.title("Create Profile")
        dialog.geometry("400x220")
        dialog.transient(self.window.window)
        dialog.grab_set()

        name_var = tk.StringVar()
        description_var = tk.StringVar()

        ttk.Label(dialog, text="Profile name:").pack(anchor="w", padx=12, pady=(12, 4))
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=40)
        name_entry.pack(fill="x", padx=12)

        ttk.Label(dialog, text="Description:").pack(anchor="w", padx=12, pady=(12, 4))
        description_entry = ttk.Entry(dialog, textvariable=description_var, width=40)
        description_entry.pack(fill="x", padx=12)

        def save_profile():
            name = name_var.get().strip()
            description = description_var.get().strip()

            if not name:
                messagebox.showerror("Error", "Profile name is required.", parent=dialog)
                return

            try:
                create_profile(name=name, description=description, is_builtin=0)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create profile:\n{e}", parent=dialog)
                return

            dialog.destroy()
            self.window.refresh_profiles()

        ttk.Button(dialog, text="Save", command=save_profile).pack(pady=16)
        name_entry.focus_set()

    def edit_profile(self):
        if self.window.selected_profile_id is None:
            messagebox.showerror("Error", "Select a profile first.", parent=self.window.window)
            return

        profile = get_profile_by_id(self.window.selected_profile_id)
        if not profile:
            messagebox.showerror("Error", "Selected profile was not found.", parent=self.window.window)
            return

        profile_id, current_name, current_description, is_builtin, _, _ = profile

        if is_builtin:
            messagebox.showerror("Error", "Built-in profiles cannot be edited.", parent=self.window.window)
            return

        dialog = tk.Toplevel(self.window.window)
        dialog.title("Edit Profile")
        dialog.geometry("400x220")
        dialog.transient(self.window.window)
        dialog.grab_set()

        name_var = tk.StringVar(value=current_name)
        description_var = tk.StringVar(value=current_description or "")

        ttk.Label(dialog, text="Profile name:").pack(anchor="w", padx=12, pady=(12, 4))
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=40)
        name_entry.pack(fill="x", padx=12)

        ttk.Label(dialog, text="Description:").pack(anchor="w", padx=12, pady=(12, 4))
        description_entry = ttk.Entry(dialog, textvariable=description_var, width=40)
        description_entry.pack(fill="x", padx=12)

        def save_profile_changes():
            new_name = name_var.get().strip()
            new_description = description_var.get().strip()

            if not new_name:
                messagebox.showerror("Error", "Profile name is required.", parent=dialog)
                return

            try:
                update_profile(profile_id=profile_id, name=new_name, description=new_description)
            except Exception as e:
                messagebox.showerror("Error", f"Could not update profile:\n{e}", parent=dialog)
                return

            dialog.destroy()
            self.window.refresh_profiles()
            self.reselect_profile(profile_id)

        ttk.Button(dialog, text="Save Changes", command=save_profile_changes).pack(pady=16)
        name_entry.focus_set()

    def delete_profile(self):
        if self.window.selected_profile_id is None:
            messagebox.showerror("Error", "Select a profile first.", parent=self.window.window)
            return

        profile = get_profile_by_id(self.window.selected_profile_id)
        if not profile:
            messagebox.showerror("Error", "Selected profile was not found.", parent=self.window.window)
            return

        _, name, _, is_builtin, _, _ = profile

        if is_builtin:
            messagebox.showerror("Error", "Built-in profiles cannot be deleted.", parent=self.window.window)
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete profile '{name}'?",
            parent=self.window.window
        )
        if not confirm:
            return

        deleted = delete_profile(self.window.selected_profile_id)
        if not deleted:
            messagebox.showerror("Error", "Could not delete profile.", parent=self.window.window)
            return

        self.window.selected_profile_id = None
        self.window.selected_rule_id = None
        self.window.details_text.delete("1.0", tk.END)
        self.window.clear_rules_table()
        self.window.refresh_profiles()

    def reselect_profile(self, profile_id: int):
        for index, profile in enumerate(self.window.profiles):
            if profile[0] == profile_id:
                self.window.profile_listbox.selection_clear(0, tk.END)
                self.window.profile_listbox.selection_set(index)
                self.window.profile_listbox.activate(index)
                self.window.selected_profile_id = profile_id
                self.window.refresh_selected_profile_details()
                break