import tkinter as tk
from tkinter import ttk, messagebox

from profile_service import (
    get_all_profiles,
    get_profile_by_id,
    get_rules_for_profile_id,
    create_profile,
    delete_profile,
)


class ProfileManagerWindow:
    def __init__(self, parent: tk.Tk) -> None:
        self.window = tk.Toplevel(parent)
        self.window.title("Manage Profiles")
        self.window.geometry("900x500")

        self.selected_profile_id = None
        self.profiles = []

        self._build_ui()
        self._load_profiles()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.window, padding=12)
        main_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 12))

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew")

        ttk.Label(left_frame, text="Profiles").pack(anchor="w")

        self.profile_listbox = tk.Listbox(left_frame, height=20, width=35)
        self.profile_listbox.pack(fill="y", expand=False, pady=(6, 10))
        self.profile_listbox.bind("<<ListboxSelect>>", self._on_profile_selected)

        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill="x")

        self.create_button = ttk.Button(
            button_frame,
            text="Create Profile",
            command=self._create_profile
        )
        self.create_button.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.refresh_button = ttk.Button(
            button_frame,
            text="Refresh",
            command=self._load_profiles
        )
        self.refresh_button.grid(row=0, column=1, sticky="ew", padx=(0, 6))

        self.delete_button = ttk.Button(
            button_frame,
            text="Delete Profile",
            command=self._delete_profile
        )
        self.delete_button.grid(row=0, column=2, sticky="ew")

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Label(right_frame, text="Profile Details").grid(row=0, column=0, sticky="w")

        self.details_text = tk.Text(right_frame, wrap="word", height=25)
        self.details_text.grid(row=1, column=0, sticky="nsew", pady=(6, 0))

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.details_text.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.details_text.configure(yscrollcommand=scrollbar.set)

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

    def _load_profiles(self) -> None:
        self.profiles = get_all_profiles()
        self.profile_listbox.delete(0, tk.END)

        for profile in self.profiles:
            profile_id, name, description, is_builtin = profile
            label = f"{name} {'[built-in]' if is_builtin else '[custom]'}"
            self.profile_listbox.insert(tk.END, label)

        self.details_text.delete("1.0", tk.END)
        self.selected_profile_id = None

    def _on_profile_selected(self, _event=None) -> None:
        selection = self.profile_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        profile = self.profiles[index]
        profile_id = profile[0]
        self.selected_profile_id = profile_id

        self._show_profile_details(profile_id)

    def _show_profile_details(self, profile_id: int) -> None:
        profile = get_profile_by_id(profile_id)
        rules = get_rules_for_profile_id(profile_id)

        if not profile:
            return

        profile_id, name, description, is_builtin, created_at, updated_at = profile

        lines = [
            f"ID: {profile_id}",
            f"Name: {name}",
            f"Description: {description}",
            f"Type: {'Built-in' if is_builtin else 'Custom'}",
            f"Created: {created_at}",
            f"Updated: {updated_at}",
            "",
            "Rules:",
        ]

        if not rules:
            lines.append("  No rules found.")
        else:
            for rule in rules:
                rule_id, rule_type, target_type, pattern, enabled, priority, notes = rule
                lines.append(
                    f"  - [{rule_id}] {rule_type} | {target_type} | {pattern} | "
                    f"enabled={enabled} | priority={priority} | notes={notes or ''}"
                )

        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, "\n".join(lines))

    def _create_profile(self) -> None:
        dialog = tk.Toplevel(self.window)
        dialog.title("Create Profile")
        dialog.geometry("400x220")
        dialog.transient(self.window)
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
            self._load_profiles()

        ttk.Button(dialog, text="Save", command=save_profile).pack(pady=16)
        name_entry.focus_set()

    def _delete_profile(self) -> None:
        if self.selected_profile_id is None:
            messagebox.showerror("Error", "Select a profile first.", parent=self.window)
            return

        profile = get_profile_by_id(self.selected_profile_id)
        if not profile:
            messagebox.showerror("Error", "Selected profile was not found.", parent=self.window)
            return

        _, name, _, is_builtin, _, _ = profile

        if is_builtin:
            messagebox.showerror("Error", "Built-in profiles cannot be deleted.", parent=self.window)
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete profile '{name}'?",
            parent=self.window
        )
        if not confirm:
            return

        deleted = delete_profile(self.selected_profile_id)
        if not deleted:
            messagebox.showerror("Error", "Could not delete profile.", parent=self.window)
            return

        self.selected_profile_id = None
        self.details_text.delete("1.0", tk.END)
        self._load_profiles()