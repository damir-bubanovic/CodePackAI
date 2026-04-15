import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pathlib import Path

from services.profile_service import get_all_profiles, get_rules_for_profile
from core.scanner import scan_project, summarize_results
from core.packer import create_zip_from_results
from ui.profile_manager_window import ProfileManagerWindow


class CodePackAIWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("CodePackAI")
        self.root.geometry("820x620")

        self.project_folder_var = tk.StringVar()
        self.output_folder_var = tk.StringVar()
        self.profile_var = tk.StringVar()
        self.include_review_var = tk.BooleanVar(value=False)
        self.max_size_var = tk.StringVar()
        self.size_review_only_var = tk.BooleanVar(value=True)

        self.last_results = None
        self.last_project_folder = None
        self.last_profile = None

        self._build_ui()
        self._load_profiles()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill="both", expand=True)

        folder_label = ttk.Label(main_frame, text="Project folder:")
        folder_label.grid(row=0, column=0, sticky="w", pady=(0, 6))

        folder_entry = ttk.Entry(main_frame, textvariable=self.project_folder_var, width=80)
        folder_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        browse_project_button = ttk.Button(main_frame, text="Browse...", command=self._browse_project_folder)
        browse_project_button.grid(row=1, column=1, sticky="ew")

        output_label = ttk.Label(main_frame, text="Output folder:")
        output_label.grid(row=2, column=0, sticky="w", pady=(14, 6))

        output_entry = ttk.Entry(main_frame, textvariable=self.output_folder_var, width=80)
        output_entry.grid(row=3, column=0, sticky="ew", padx=(0, 8))

        browse_output_button = ttk.Button(main_frame, text="Browse...", command=self._browse_output_folder)
        browse_output_button.grid(row=3, column=1, sticky="ew")

        profile_label = ttk.Label(main_frame, text="Profile:")
        profile_label.grid(row=4, column=0, sticky="w", pady=(14, 6))

        self.profile_combo = ttk.Combobox(main_frame, textvariable=self.profile_var, state="readonly")
        self.profile_combo.grid(row=5, column=0, sticky="ew", padx=(0, 8))

        manage_profiles_button = ttk.Button(
            main_frame,
            text="Manage Profiles",
            command=self._open_profile_manager
        )
        manage_profiles_button.grid(row=5, column=1, sticky="ew", pady=(0, 6))

        include_review_check = ttk.Checkbutton(
            main_frame,
            text="Include review files (images/assets)",
            variable=self.include_review_var
        )
        include_review_check.grid(row=6, column=0, sticky="w", pady=(14, 6))

        size_label = ttk.Label(main_frame, text="Max file size (KB, optional):")
        size_label.grid(row=7, column=0, sticky="w", pady=(6, 2))

        size_entry = ttk.Entry(main_frame, textvariable=self.max_size_var, width=20)
        size_entry.grid(row=8, column=0, sticky="w", pady=(0, 6))

        size_mode_check = ttk.Checkbutton(
            main_frame,
            text="Apply size limit only to review files",
            variable=self.size_review_only_var
        )
        size_mode_check.grid(row=9, column=0, sticky="w", pady=(0, 10))

        scan_button = ttk.Button(main_frame, text="Scan", command=self._scan)
        scan_button.grid(row=10, column=0, sticky="w", pady=(0, 6))

        pack_button = ttk.Button(main_frame, text="Pack", command=self._pack)
        pack_button.grid(row=10, column=1, sticky="w", pady=(0, 6))

        result_label = ttk.Label(main_frame, text="Results:")
        result_label.grid(row=11, column=0, sticky="w", pady=(8, 6))

        self.result_text = tk.Text(main_frame, height=20, wrap="word")
        self.result_text.grid(row=12, column=0, columnspan=2, sticky="nsew")

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.grid(row=12, column=2, sticky="ns")
        self.result_text.configure(yscrollcommand=scrollbar.set)

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(12, weight=1)

    def _load_profiles(self) -> None:
        profiles = get_all_profiles()
        profile_names = [profile[1] for profile in profiles]
        self.profile_combo["values"] = profile_names

        if profile_names:
            current_value = self.profile_var.get().strip()
            if current_value in profile_names:
                self.profile_var.set(current_value)
            else:
                self.profile_var.set("Python" if "Python" in profile_names else profile_names[0])

    def _open_profile_manager(self) -> None:
        manager = ProfileManagerWindow(self.root)
        self.root.wait_window(manager.window)
        self._load_profiles()

    def _browse_project_folder(self) -> None:
        initial_dir = self.project_folder_var.get().strip() or str(Path.home())
        selected_folder = filedialog.askdirectory(initialdir=initial_dir)
        if selected_folder:
            self.project_folder_var.set(selected_folder)

    def _browse_output_folder(self) -> None:
        initial_dir = self.output_folder_var.get().strip() or str(Path.home())
        selected_folder = filedialog.askdirectory(initialdir=initial_dir)
        if selected_folder:
            self.output_folder_var.set(selected_folder)

    def _write_result(self, text: str) -> None:
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)

    def _scan(self) -> None:
        project_folder = self.project_folder_var.get().strip()
        profile_name = self.profile_var.get().strip()

        if not project_folder:
            messagebox.showerror("Error", "Please select a project folder.")
            return

        if not Path(project_folder).exists():
            messagebox.showerror("Error", "Selected project folder does not exist.")
            return

        rules = get_rules_for_profile(profile_name)
        if not rules:
            messagebox.showerror("Error", f"No rules found for profile: {profile_name}")
            return

        results = scan_project(project_folder, rules)
        summary = summarize_results(results)

        self.last_results = results
        self.last_project_folder = project_folder
        self.last_profile = profile_name

        included_files = sorted(
            [r for r in results if r["classification"] == "include"],
            key=lambda x: x["size_bytes"],
            reverse=True
        )

        review_files = sorted(
            [r for r in results if r["classification"] == "review"],
            key=lambda x: x["size_bytes"],
            reverse=True
        )

        result_lines = [
            "Scan Results",
            "",
            f"Project folder: {project_folder}",
            f"Profile: {profile_name}",
            "",
            "Summary:",
        ]

        for classification, data in summary.items():
            result_lines.append(
                f"  {classification}: files={data['count']}, size={data['size_bytes']} bytes"
            )

        result_lines.append("")
        result_lines.append("Top Included Files:")

        for item in included_files[:20]:
            result_lines.append(f"  {item['relative_path']} ({item['size_bytes'] / 1024:.1f} KB)")

        result_lines.append("")
        result_lines.append("Top Review Files:")

        for item in review_files[:20]:
            result_lines.append(f"  {item['relative_path']} ({item['size_bytes'] / 1024:.1f} KB)")

        self._write_result("\n".join(result_lines))

    def _pack(self) -> None:
        if not self.last_results:
            messagebox.showerror("Error", "Run scan first.")
            return

        include_review = self.include_review_var.get()
        size_review_only = self.size_review_only_var.get()

        max_size_kb = self.max_size_var.get().strip()
        max_size_bytes = None

        if max_size_kb:
            try:
                max_size_bytes = int(max_size_kb) * 1024
            except ValueError:
                messagebox.showerror("Error", "Max file size must be a number.")
                return

        allowed = {"include"}
        if include_review:
            allowed.add("review")

        output_folder = self.output_folder_var.get().strip()
        if not output_folder:
            output_folder = str(Path(self.last_project_folder).resolve().parent)

        output_folder_path = Path(output_folder).resolve()
        if not output_folder_path.exists():
            messagebox.showerror("Error", "Selected output folder does not exist.")
            return

        project_path = Path(self.last_project_folder).resolve()
        zip_name = f"{project_path.name}_{self.last_profile}.zip"
        output_zip_path = str(output_folder_path / zip_name)

        filtered_results = []
        skipped_large_files = []

        for r in self.last_results:
            classification = r["classification"]

            if classification not in allowed:
                filtered_results.append(r)
                continue

            if max_size_bytes is None:
                filtered_results.append(r)
                continue

            if size_review_only:
                if classification == "include":
                    filtered_results.append(r)
                elif classification == "review":
                    if r["size_bytes"] <= max_size_bytes:
                        filtered_results.append(r)
                    else:
                        skipped_large_files.append(r)
            else:
                if r["size_bytes"] <= max_size_bytes:
                    filtered_results.append(r)
                else:
                    skipped_large_files.append(r)

        skipped_large_files = sorted(
            skipped_large_files,
            key=lambda x: x["size_bytes"],
            reverse=True
        )

        files_added, total_bytes = create_zip_from_results(
            project_folder=self.last_project_folder,
            results=filtered_results,
            output_zip_path=output_zip_path,
            allowed_classifications=allowed,
        )

        zip_size_bytes = 0
        if Path(output_zip_path).exists():
            zip_size_bytes = Path(output_zip_path).stat().st_size

        result_lines = [
            "Pack Results",
            "",
            f"Include review files: {'Yes' if include_review else 'No'}",
            f"Max file size filter: {max_size_kb + ' KB' if max_size_kb else 'None'}",
            f"Apply size limit only to review files: {'Yes' if size_review_only else 'No'}",
            "",
            f"Output folder: {output_folder_path}",
            f"Zip path: {output_zip_path}",
            f"Files added: {files_added}",
            f"Total uncompressed bytes: {total_bytes}",
            f"Zip file size: {zip_size_bytes} bytes",
        ]

        if skipped_large_files:
            result_lines.append("")
            result_lines.append("Skipped (too large files):")

            for item in skipped_large_files[:20]:
                result_lines.append(
                    f"  {item['relative_path']} ({item['size_bytes'] / 1024:.1f} KB)"
                )

        self._write_result("\n".join(result_lines))


def launch_app() -> None:
    root = tk.Tk()
    CodePackAIWindow(root)
    root.mainloop()