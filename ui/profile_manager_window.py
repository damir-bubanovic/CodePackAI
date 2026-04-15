import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from services.profile_service import (
    get_all_profiles,
    get_profile_by_id,
    get_rules_for_profile_id,
    create_profile,
    update_profile,
    delete_profile,
    create_rule,
    import_rules_to_profile,
    update_rule,
    delete_rule,
)


class ProfileManagerWindow:
    def __init__(self, parent: tk.Tk) -> None:
        self.window = tk.Toplevel(parent)
        self.window.title("Manage Profiles")
        self.window.geometry("1100x620")

        self.selected_profile_id = None
        self.selected_rule_id = None
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

        self.profile_listbox = tk.Listbox(left_frame, height=24, width=35)
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

        self.edit_button = ttk.Button(
            button_frame,
            text="Edit Profile",
            command=self._edit_profile
        )
        self.edit_button.grid(row=0, column=1, sticky="ew", padx=(0, 6))

        self.refresh_button = ttk.Button(
            button_frame,
            text="Refresh",
            command=self._load_profiles
        )
        self.refresh_button.grid(row=0, column=2, sticky="ew", padx=(0, 6))

        self.delete_button = ttk.Button(
            button_frame,
            text="Delete Profile",
            command=self._delete_profile
        )
        self.delete_button.grid(row=0, column=3, sticky="ew")

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.columnconfigure(3, weight=1)

        ttk.Label(right_frame, text="Profile Details").grid(row=0, column=0, sticky="w")

        self.details_text = tk.Text(right_frame, wrap="word", height=8)
        self.details_text.grid(row=1, column=0, sticky="nsew", pady=(6, 10))

        details_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.details_text.yview)
        details_scrollbar.grid(row=1, column=1, sticky="ns", pady=(6, 10))
        self.details_text.configure(yscrollcommand=details_scrollbar.set)

        ttk.Label(right_frame, text="Rules").grid(row=2, column=0, sticky="w", pady=(4, 4))

        self.rules_tree = ttk.Treeview(
            right_frame,
            columns=("id", "rule_type", "target_type", "pattern", "enabled", "priority", "notes"),
            show="headings",
            height=12
        )
        self.rules_tree.grid(row=3, column=0, sticky="nsew")

        self.rules_tree.heading("id", text="ID")
        self.rules_tree.heading("rule_type", text="Rule Type")
        self.rules_tree.heading("target_type", text="Target Type")
        self.rules_tree.heading("pattern", text="Pattern")
        self.rules_tree.heading("enabled", text="Enabled")
        self.rules_tree.heading("priority", text="Priority")
        self.rules_tree.heading("notes", text="Notes")

        self.rules_tree.column("id", width=70, minwidth=60, anchor="center", stretch=False)
        self.rules_tree.column("rule_type", width=120, minwidth=100, anchor="w", stretch=False)
        self.rules_tree.column("target_type", width=130, minwidth=110, anchor="w", stretch=False)
        self.rules_tree.column("pattern", width=260, minwidth=180, anchor="w", stretch=True)
        self.rules_tree.column("enabled", width=80, minwidth=70, anchor="center", stretch=False)
        self.rules_tree.column("priority", width=80, minwidth=70, anchor="center", stretch=False)
        self.rules_tree.column("notes", width=320, minwidth=180, anchor="w", stretch=True)

        self.rules_tree.bind("<<TreeviewSelect>>", self._on_rule_selected)

        rules_scrollbar_y = ttk.Scrollbar(right_frame, orient="vertical", command=self.rules_tree.yview)
        rules_scrollbar_y.grid(row=3, column=1, sticky="ns")

        rules_scrollbar_x = ttk.Scrollbar(right_frame, orient="horizontal", command=self.rules_tree.xview)
        rules_scrollbar_x.grid(row=4, column=0, sticky="ew", pady=(2, 0))

        self.rules_tree.configure(
            yscrollcommand=rules_scrollbar_y.set,
            xscrollcommand=rules_scrollbar_x.set
        )

        rule_action_frame = ttk.Frame(right_frame)
        rule_action_frame.grid(row=5, column=0, sticky="w", pady=(10, 0))

        self.add_rule_button = ttk.Button(
            rule_action_frame,
            text="Add Rule",
            command=self._add_rule
        )
        self.add_rule_button.grid(row=0, column=0, padx=(0, 8))

        self.import_rules_button = ttk.Button(
            rule_action_frame,
            text="Import Rules",
            command=self._import_rules
        )
        self.import_rules_button.grid(row=0, column=1, padx=(0, 8))

        self.edit_rule_button = ttk.Button(
            rule_action_frame,
            text="Edit Selected Rule",
            command=self._edit_rule
        )
        self.edit_rule_button.grid(row=0, column=2, padx=(0, 8))

        self.delete_rule_button = ttk.Button(
            rule_action_frame,
            text="Delete Selected Rule",
            command=self._delete_rule
        )
        self.delete_rule_button.grid(row=0, column=3)

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=0)
        right_frame.rowconfigure(3, weight=1)
        right_frame.rowconfigure(4, weight=0)
        right_frame.rowconfigure(5, weight=0)

    def _load_profiles(self) -> None:
        self.profiles = get_all_profiles()
        self.profile_listbox.delete(0, tk.END)

        for profile in self.profiles:
            profile_id, name, description, is_builtin = profile
            label = f"{name} {'[built-in]' if is_builtin else '[custom]'}"
            self.profile_listbox.insert(tk.END, label)

        self.details_text.delete("1.0", tk.END)
        self._clear_rules_table()
        self.selected_profile_id = None
        self.selected_rule_id = None

    def _clear_rules_table(self) -> None:
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)

    def _on_profile_selected(self, _event=None) -> None:
        selection = self.profile_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        profile = self.profiles[index]
        profile_id = profile[0]
        self.selected_profile_id = profile_id
        self.selected_rule_id = None

        self._show_profile_details(profile_id)

    def _on_rule_selected(self, _event=None) -> None:
        selection = self.rules_tree.selection()
        if not selection:
            self.selected_rule_id = None
            return

        item_id = selection[0]
        values = self.rules_tree.item(item_id, "values")
        if values:
            self.selected_rule_id = int(values[0])

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
        ]

        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, "\n".join(lines))

        self._clear_rules_table()
        self.selected_rule_id = None

        for rule in rules:
            rule_id, rule_type, target_type, pattern, enabled, priority, notes = rule
            self.rules_tree.insert(
                "",
                tk.END,
                values=(
                    rule_id,
                    rule_type,
                    target_type,
                    pattern,
                    enabled,
                    priority,
                    notes or "",
                )
            )

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

    def _edit_profile(self) -> None:
        if self.selected_profile_id is None:
            messagebox.showerror("Error", "Select a profile first.", parent=self.window)
            return

        profile = get_profile_by_id(self.selected_profile_id)
        if not profile:
            messagebox.showerror("Error", "Selected profile was not found.", parent=self.window)
            return

        profile_id, current_name, current_description, is_builtin, _, _ = profile

        if is_builtin:
            messagebox.showerror("Error", "Built-in profiles cannot be edited.", parent=self.window)
            return

        dialog = tk.Toplevel(self.window)
        dialog.title("Edit Profile")
        dialog.geometry("400x220")
        dialog.transient(self.window)
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
            self._load_profiles()
            self._reselect_profile(profile_id)

        ttk.Button(dialog, text="Save Changes", command=save_profile_changes).pack(pady=16)
        name_entry.focus_set()

    def _reselect_profile(self, profile_id: int) -> None:
        for index, profile in enumerate(self.profiles):
            if profile[0] == profile_id:
                self.profile_listbox.selection_clear(0, tk.END)
                self.profile_listbox.selection_set(index)
                self.profile_listbox.activate(index)
                self.selected_profile_id = profile_id
                self._show_profile_details(profile_id)
                break

    def _add_rule(self) -> None:
        if self.selected_profile_id is None:
            messagebox.showerror("Error", "Select a profile first.", parent=self.window)
            return

        dialog = tk.Toplevel(self.window)
        dialog.title("Add Rule")
        dialog.geometry("430x420")
        dialog.transient(self.window)
        dialog.grab_set()

        rule_type_var = tk.StringVar(value="include")
        target_type_var = tk.StringVar(value="extension")
        pattern_var = tk.StringVar()
        enabled_var = tk.BooleanVar(value=True)
        priority_var = tk.StringVar(value="100")
        notes_var = tk.StringVar()

        content = ttk.Frame(dialog, padding=12)
        content.pack(fill="both", expand=True)

        ttk.Label(content, text="Rule type:").grid(row=0, column=0, sticky="w", pady=(0, 4))
        rule_type_combo = ttk.Combobox(
            content,
            textvariable=rule_type_var,
            state="readonly",
            values=["include", "exclude", "review", "detect", "always_keep"]
        )
        rule_type_combo.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(content, text="Target type:").grid(row=2, column=0, sticky="w", pady=(0, 4))
        target_type_combo = ttk.Combobox(
            content,
            textvariable=target_type_var,
            state="readonly",
            values=["extension", "filename", "folder_name", "path_contains"]
        )
        target_type_combo.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(content, text="Pattern:").grid(row=4, column=0, sticky="w", pady=(0, 4))
        pattern_entry = ttk.Entry(content, textvariable=pattern_var)
        pattern_entry.grid(row=5, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(content, text="Priority:").grid(row=6, column=0, sticky="w", pady=(0, 4))
        priority_entry = ttk.Entry(content, textvariable=priority_var)
        priority_entry.grid(row=7, column=0, sticky="ew", pady=(0, 10))

        enabled_check = ttk.Checkbutton(
            content,
            text="Enabled",
            variable=enabled_var
        )
        enabled_check.grid(row=8, column=0, sticky="w", pady=(0, 10))

        ttk.Label(content, text="Notes (optional):").grid(row=9, column=0, sticky="w", pady=(0, 4))
        notes_entry = ttk.Entry(content, textvariable=notes_var)
        notes_entry.grid(row=10, column=0, sticky="ew", pady=(0, 14))

        def save_rule():
            rule_type = rule_type_var.get().strip()
            target_type = target_type_var.get().strip()
            pattern = pattern_var.get().strip()
            notes = notes_var.get().strip() or None

            if not pattern:
                messagebox.showerror("Error", "Pattern is required.", parent=dialog)
                return

            try:
                priority = int(priority_var.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Priority must be a number.", parent=dialog)
                return

            try:
                create_rule(
                    profile_id=self.selected_profile_id,
                    rule_type=rule_type,
                    target_type=target_type,
                    pattern=pattern,
                    enabled=1 if enabled_var.get() else 0,
                    priority=priority,
                    notes=notes,
                )
            except Exception as e:
                messagebox.showerror("Error", f"Could not create rule:\n{e}", parent=dialog)
                return

            dialog.destroy()
            if self.selected_profile_id is not None:
                self._show_profile_details(self.selected_profile_id)

        save_button = ttk.Button(content, text="Save Rule", command=save_rule)
        save_button.grid(row=11, column=0, sticky="w")

        content.columnconfigure(0, weight=1)
        pattern_entry.focus_set()

    def _import_rules(self) -> None:
        if self.selected_profile_id is None:
            messagebox.showerror("Error", "Select a profile first.", parent=self.window)
            return

        file_path = filedialog.askopenfilename(
            parent=self.window,
            title="Import Rules JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("JSON root must be an object.")

            rules = data.get("rules")
            if not isinstance(rules, list):
                raise ValueError("JSON must contain a 'rules' list.")

            allowed_rule_types = {"include", "exclude", "review", "detect", "always_keep"}
            allowed_target_types = {"extension", "filename", "folder_name", "path_contains"}

            normalized_rules = []
            for i, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    raise ValueError(f"Rule at index {i} must be an object.")

                rule_type = str(rule.get("rule_type", "")).strip()
                target_type = str(rule.get("target_type", "")).strip()
                pattern = str(rule.get("pattern", "")).strip()

                if rule_type not in allowed_rule_types:
                    raise ValueError(f"Invalid rule_type at index {i}: {rule_type}")

                if target_type not in allowed_target_types:
                    raise ValueError(f"Invalid target_type at index {i}: {target_type}")

                if not pattern:
                    raise ValueError(f"Missing pattern at index {i}")

                enabled = rule.get("enabled", 1)
                priority = rule.get("priority", 100)
                notes = rule.get("notes")

                normalized_rules.append({
                    "rule_type": rule_type,
                    "target_type": target_type,
                    "pattern": pattern,
                    "enabled": 1 if int(enabled) else 0,
                    "priority": int(priority),
                    "notes": notes,
                })

            replace_existing = messagebox.askyesno(
                "Import Rules",
                "Replace existing rules for this profile?\n\nYes = replace all existing rules\nNo = append imported rules",
                parent=self.window
            )

            imported_count = import_rules_to_profile(
                profile_id=self.selected_profile_id,
                rules=normalized_rules,
                replace_existing=replace_existing,
            )

            messagebox.showinfo(
                "Import Complete",
                f"Imported {imported_count} rules successfully.",
                parent=self.window
            )

            self._show_profile_details(self.selected_profile_id)

        except Exception as e:
            messagebox.showerror("Import Error", str(e), parent=self.window)

    def _edit_rule(self) -> None:
        if self.selected_rule_id is None:
            messagebox.showerror("Error", "Select a rule first.", parent=self.window)
            return

        selected_item = self.rules_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a rule first.", parent=self.window)
            return

        values = self.rules_tree.item(selected_item[0], "values")

        rule_id = int(values[0])
        rule_type_val = values[1]
        target_type_val = values[2]
        pattern_val = values[3]
        enabled_val = bool(int(values[4]))
        priority_val = str(values[5])
        notes_val = values[6]

        dialog = tk.Toplevel(self.window)
        dialog.title("Edit Rule")
        dialog.geometry("430x420")
        dialog.transient(self.window)
        dialog.grab_set()

        rule_type_var = tk.StringVar(value=rule_type_val)
        target_type_var = tk.StringVar(value=target_type_val)
        pattern_var = tk.StringVar(value=pattern_val)
        enabled_var = tk.BooleanVar(value=enabled_val)
        priority_var = tk.StringVar(value=priority_val)
        notes_var = tk.StringVar(value=notes_val)

        content = ttk.Frame(dialog, padding=12)
        content.pack(fill="both", expand=True)

        ttk.Label(content, text="Rule type:").grid(row=0, column=0, sticky="w", pady=(0, 4))
        ttk.Combobox(
            content,
            textvariable=rule_type_var,
            state="readonly",
            values=["include", "exclude", "review", "detect", "always_keep"]
        ).grid(row=1, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(content, text="Target type:").grid(row=2, column=0, sticky="w", pady=(0, 4))
        ttk.Combobox(
            content,
            textvariable=target_type_var,
            state="readonly",
            values=["extension", "filename", "folder_name", "path_contains"]
        ).grid(row=3, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(content, text="Pattern:").grid(row=4, column=0, sticky="w", pady=(0, 4))
        ttk.Entry(content, textvariable=pattern_var).grid(row=5, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(content, text="Priority:").grid(row=6, column=0, sticky="w", pady=(0, 4))
        ttk.Entry(content, textvariable=priority_var).grid(row=7, column=0, sticky="ew", pady=(0, 10))

        ttk.Checkbutton(content, text="Enabled", variable=enabled_var).grid(row=8, column=0, sticky="w", pady=(0, 10))

        ttk.Label(content, text="Notes (optional):").grid(row=9, column=0, sticky="w", pady=(0, 4))
        ttk.Entry(content, textvariable=notes_var).grid(row=10, column=0, sticky="ew", pady=(0, 14))

        def save_changes():
            pattern = pattern_var.get().strip()
            if not pattern:
                messagebox.showerror("Error", "Pattern is required.", parent=dialog)
                return

            try:
                priority = int(priority_var.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Priority must be a number.", parent=dialog)
                return

            try:
                update_rule(
                    rule_id=rule_id,
                    rule_type=rule_type_var.get().strip(),
                    target_type=target_type_var.get().strip(),
                    pattern=pattern,
                    enabled=1 if enabled_var.get() else 0,
                    priority=priority,
                    notes=notes_var.get().strip() or None,
                )
            except Exception as e:
                messagebox.showerror("Error", f"Could not update rule:\n{e}", parent=dialog)
                return

            dialog.destroy()
            if self.selected_profile_id is not None:
                self._show_profile_details(self.selected_profile_id)

        ttk.Button(content, text="Save Changes", command=save_changes).grid(row=11, column=0, sticky="w")

        content.columnconfigure(0, weight=1)

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
        self.selected_rule_id = None
        self.details_text.delete("1.0", tk.END)
        self._clear_rules_table()
        self._load_profiles()

    def _delete_rule(self) -> None:
        if self.selected_profile_id is None:
            messagebox.showerror("Error", "Select a profile first.", parent=self.window)
            return

        if self.selected_rule_id is None:
            messagebox.showerror("Error", "Select a rule from the table first.", parent=self.window)
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Delete selected rule?",
            parent=self.window
        )
        if not confirm:
            return

        try:
            delete_rule(self.selected_rule_id)
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete rule:\n{e}", parent=self.window)
            return

        self.selected_rule_id = None

        if self.selected_profile_id is not None:
            self._show_profile_details(self.selected_profile_id)