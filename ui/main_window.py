import tkinter as tk
from tkinter import ttk
from pathlib import Path

from ui.main_window_handlers import MainWindowHandlers


class CodePackAIWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("CodePackAI")
        self.root.geometry("820x620")

        icon_path = Path("images/logo.png")
        if icon_path.exists():
            self.app_icon = tk.PhotoImage(file=str(icon_path))
            self.root.iconphoto(True, self.app_icon)

        self.project_folder_var = tk.StringVar()
        self.output_folder_var = tk.StringVar()
        self.profile_var = tk.StringVar()
        self.include_review_var = tk.BooleanVar(value=False)
        self.max_size_var = tk.StringVar()
        self.size_review_only_var = tk.BooleanVar(value=True)

        self.profiles = []
        self.last_results = None
        self.last_project_folder = None
        self.last_profile = None

        self.handlers = MainWindowHandlers(self)

        self._build_ui()
        self.handlers.refresh_profiles()

    def _build_ui(self) -> None:
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill="both", expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        logo_path = Path("images/logo.png")
        if logo_path.exists():
            self.logo_img = tk.PhotoImage(file=str(logo_path))
            logo_label = ttk.Label(header_frame, image=self.logo_img)
            logo_label.pack(side="left", padx=(0, 10))

        title_label = ttk.Label(
            header_frame,
            text="CodePackAI",
            font=("Segoe UI", 14, "bold")
        )
        title_label.pack(side="left")

        author_label = ttk.Label(
            header_frame,
            text="  by Damir Bubanović",
            font=("Segoe UI", 10)
        )
        author_label.pack(side="left")

        folder_label = ttk.Label(main_frame, text="Project folder:")
        folder_label.grid(row=1, column=0, sticky="w", pady=(0, 6))

        folder_entry = ttk.Entry(main_frame, textvariable=self.project_folder_var, width=80)
        folder_entry.grid(row=2, column=0, sticky="ew", padx=(0, 8))

        browse_project_button = ttk.Button(
            main_frame,
            text="Browse...",
            command=self.handlers.browse_project_folder
        )
        browse_project_button.grid(row=2, column=1, sticky="ew")

        output_label = ttk.Label(main_frame, text="Output folder:")
        output_label.grid(row=3, column=0, sticky="w", pady=(14, 6))

        output_entry = ttk.Entry(main_frame, textvariable=self.output_folder_var, width=80)
        output_entry.grid(row=4, column=0, sticky="ew", padx=(0, 8))

        browse_output_button = ttk.Button(
            main_frame,
            text="Browse...",
            command=self.handlers.browse_output_folder
        )
        browse_output_button.grid(row=4, column=1, sticky="ew")

        profile_label = ttk.Label(main_frame, text="Profile:")
        profile_label.grid(row=5, column=0, sticky="w", pady=(14, 6))

        self.profile_combo = ttk.Combobox(main_frame, textvariable=self.profile_var, state="readonly")
        self.profile_combo.grid(row=6, column=0, sticky="ew", padx=(0, 8))

        manage_profiles_button = ttk.Button(
            main_frame,
            text="Manage Profiles",
            command=self.handlers.open_profile_manager
        )
        manage_profiles_button.grid(row=6, column=1, sticky="ew", pady=(0, 6))

        include_review_check = ttk.Checkbutton(
            main_frame,
            text="Include review files (images/assets)",
            variable=self.include_review_var
        )
        include_review_check.grid(row=7, column=0, sticky="w", pady=(14, 6))

        size_label = ttk.Label(main_frame, text="Max file size (KB, optional):")
        size_label.grid(row=8, column=0, sticky="w", pady=(6, 2))

        size_entry = ttk.Entry(main_frame, textvariable=self.max_size_var, width=20)
        size_entry.grid(row=9, column=0, sticky="w", pady=(0, 6))

        size_mode_check = ttk.Checkbutton(
            main_frame,
            text="Apply size limit only to review files",
            variable=self.size_review_only_var
        )
        size_mode_check.grid(row=10, column=0, sticky="w", pady=(0, 10))

        scan_button = ttk.Button(main_frame, text="Scan", command=self.handlers.run_scan)
        scan_button.grid(row=11, column=0, sticky="w", pady=(0, 6))

        pack_button = ttk.Button(main_frame, text="Pack", command=self.handlers.pack)
        pack_button.grid(row=11, column=1, sticky="w", pady=(0, 6))

        result_label = ttk.Label(main_frame, text="Results:")
        result_label.grid(row=12, column=0, sticky="w", pady=(8, 6))

        self.results_text = tk.Text(main_frame, height=20, wrap="word")
        self.results_text.grid(row=13, column=0, columnspan=2, sticky="nsew")

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.grid(row=13, column=2, sticky="ns")
        self.results_text.configure(yscrollcommand=scrollbar.set)

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(13, weight=1)

    def write_result(self, text: str) -> None:
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, text)


def launch_app() -> None:
    root = tk.Tk()
    CodePackAIWindow(root)
    root.mainloop()