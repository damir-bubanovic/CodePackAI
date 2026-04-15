import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from services.profile_service import (
    create_rule,
    import_rules_to_profile,
    update_rule,
    delete_rule,
)


class RuleHandlers:
    def __init__(self, window) -> None:
        self.window = window

    def on_rule_selected(self, _event=None) -> None:
        selection = self.window.rules_tree.selection()
        if not selection:
            self.window.selected_rule_id = None
            return

        item_id = selection[0]
        values = self.window.rules_tree.item(item_id, "values")
        if values:
            self.window.selected_rule_id = int(values[0])

    def add_rule(self) -> None:
        if self.window.selected_profile_id is None:
            messagebox.showerror("Error", "Select a profile first.", parent=self.window.window)
            return

        dialog = tk.Toplevel(self.window.window)
        dialog.title("Add Rule")
        dialog.geometry("430x420")
        dialog.transient(self.window.window)
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
                    profile_id=self.window.selected_profile_id,
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
            self.window.refresh_selected_profile_details()

        save_button = ttk.Button(content, text="Save Rule", command=save_rule)
        save_button.grid(row=11, column=0, sticky="w")

        content.columnconfigure(0, weight=1)
        pattern_entry.focus_set()

    def import_rules(self) -> None:
        if self.window.selected_profile_id is None:
            messagebox.showerror("Error", "Select a profile first.", parent=self.window.window)
            return

        file_path = filedialog.askopenfilename(
            parent=self.window.window,
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
                parent=self.window.window
            )

            imported_count = import_rules_to_profile(
                profile_id=self.window.selected_profile_id,
                rules=normalized_rules,
                replace_existing=replace_existing,
            )

            messagebox.showinfo(
                "Import Complete",
                f"Imported {imported_count} rules successfully.",
                parent=self.window.window
            )

            self.window.refresh_selected_profile_details()

        except Exception as e:
            messagebox.showerror("Import Error", str(e), parent=self.window.window)

    def edit_rule(self) -> None:
        if self.window.selected_rule_id is None:
            messagebox.showerror("Error", "Select a rule first.", parent=self.window.window)
            return

        selected_item = self.window.rules_tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Select a rule first.", parent=self.window.window)
            return

        values = self.window.rules_tree.item(selected_item[0], "values")

        rule_id = int(values[0])
        rule_type_val = values[1]
        target_type_val = values[2]
        pattern_val = values[3]
        enabled_val = bool(int(values[4]))
        priority_val = str(values[5])
        notes_val = values[6]

        dialog = tk.Toplevel(self.window.window)
        dialog.title("Edit Rule")
        dialog.geometry("430x420")
        dialog.transient(self.window.window)
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
            self.window.refresh_selected_profile_details()

        ttk.Button(content, text="Save Changes", command=save_changes).grid(row=11, column=0, sticky="w")

        content.columnconfigure(0, weight=1)

    def delete_rule(self) -> None:
        if self.window.selected_profile_id is None:
            messagebox.showerror("Error", "Select a profile first.", parent=self.window.window)
            return

        if self.window.selected_rule_id is None:
            messagebox.showerror("Error", "Select a rule from the table first.", parent=self.window.window)
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Delete selected rule?",
            parent=self.window.window
        )
        if not confirm:
            return

        try:
            delete_rule(self.window.selected_rule_id)
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete rule:\n{e}", parent=self.window.window)
            return

        self.window.selected_rule_id = None
        self.window.refresh_selected_profile_details()