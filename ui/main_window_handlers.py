from tkinter import filedialog, messagebox
from pathlib import Path

from services.profile_service import get_all_profiles, get_rules_for_profile
from core.scanner import scan_project, summarize_results
from core.packer import create_zip_from_results
from ui.profile_manager_window import ProfileManagerWindow


class MainWindowHandlers:
    def __init__(self, window) -> None:
        self.window = window

    def browse_project_folder(self) -> None:
        initial_dir = self.window.project_folder_var.get().strip() or str(Path.home())
        folder = filedialog.askdirectory(
            parent=self.window.root,
            title="Select Project Folder",
            initialdir=initial_dir,
        )
        if folder:
            self.window.project_folder_var.set(folder)

    def browse_output_folder(self) -> None:
        initial_dir = self.window.output_folder_var.get().strip() or str(Path.home())
        folder = filedialog.askdirectory(
            parent=self.window.root,
            title="Select Output Folder",
            initialdir=initial_dir,
        )
        if folder:
            self.window.output_folder_var.set(folder)

    def refresh_profiles(self) -> None:
        profiles = get_all_profiles()
        self.window.profiles = profiles

        profile_names = [profile[1] for profile in profiles]
        self.window.profile_combo["values"] = profile_names

        if profile_names:
            current_value = self.window.profile_var.get().strip()
            if current_value in profile_names:
                self.window.profile_var.set(current_value)
            else:
                self.window.profile_var.set("Python" if "Python" in profile_names else profile_names[0])

    def open_profile_manager(self) -> None:
        manager = ProfileManagerWindow(self.window.root)
        manager.window.wait_window()
        self.refresh_profiles()

    def run_scan(self) -> None:
        project_folder = self.window.project_folder_var.get().strip()
        profile_name = self.window.profile_var.get().strip()

        if not project_folder:
            messagebox.showerror("Error", "Please select a project folder.", parent=self.window.root)
            return

        if not Path(project_folder).exists():
            messagebox.showerror("Error", "Selected project folder does not exist.", parent=self.window.root)
            return

        rules = get_rules_for_profile(profile_name)
        if not rules:
            messagebox.showerror("Error", f"No rules found for profile: {profile_name}", parent=self.window.root)
            return

        results = scan_project(project_folder, rules)
        summary = summarize_results(results)

        self.window.last_results = results
        self.window.last_project_folder = project_folder
        self.window.last_profile = profile_name

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

        self.window.write_result("\n".join(result_lines))

    def pack(self) -> None:
        if not self.window.last_results:
            messagebox.showerror("Error", "Run scan first.", parent=self.window.root)
            return

        include_review = self.window.include_review_var.get()
        size_review_only = self.window.size_review_only_var.get()

        max_size_kb = self.window.max_size_var.get().strip()
        max_size_bytes = None

        if max_size_kb:
            try:
                max_size_bytes = int(max_size_kb) * 1024
            except ValueError:
                messagebox.showerror("Error", "Max file size must be a number.", parent=self.window.root)
                return

        allowed = {"include"}
        if include_review:
            allowed.add("review")

        output_folder = self.window.output_folder_var.get().strip()
        if not output_folder:
            output_folder = str(Path(self.window.last_project_folder).resolve().parent)

        output_folder_path = Path(output_folder).resolve()
        if not output_folder_path.exists():
            messagebox.showerror("Error", "Selected output folder does not exist.", parent=self.window.root)
            return

        project_path = Path(self.window.last_project_folder).resolve()
        zip_name = f"{project_path.name}_{self.window.last_profile}.zip"
        output_zip_path = str(output_folder_path / zip_name)

        filtered_results = []
        skipped_large_files = []

        for result in self.window.last_results:
            classification = result["classification"]

            if classification not in allowed:
                continue

            if max_size_bytes is None:
                filtered_results.append(result)
                continue

            if size_review_only:
                if classification == "include":
                    filtered_results.append(result)
                elif classification == "review":
                    if result["size_bytes"] <= max_size_bytes:
                        filtered_results.append(result)
                    else:
                        skipped_large_files.append(result)
            else:
                if result["size_bytes"] <= max_size_bytes:
                    filtered_results.append(result)
                else:
                    skipped_large_files.append(result)

        skipped_large_files = sorted(
            skipped_large_files,
            key=lambda x: x["size_bytes"],
            reverse=True
        )

        files_added, total_bytes = create_zip_from_results(
            project_folder=self.window.last_project_folder,
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

        self.window.write_result("\n".join(result_lines))