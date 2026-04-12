from datetime import datetime, UTC
from database import get_connection


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def seed_profiles() -> None:
    profiles = [
        ("General", "Generic mixed-language project", 1),
        ("Python", "Python application or script project", 1),
        ("Java", "Java project", 1),
        ("PHP", "Generic PHP project", 1),
        ("Laravel", "Laravel PHP project", 1),
        ("JavaScript_Web", "JavaScript or website project", 1),
        ("CSharp_DotNet", "C# / .NET / Visual Studio project", 1),
        ("Android", "Android application project", 1),
        ("Unity", "Unity game project", 1),
    ]

    now = _now_iso()

    with get_connection() as conn:
        cursor = conn.cursor()

        for name, description, is_builtin in profiles:
            cursor.execute("""
                INSERT OR IGNORE INTO profiles (name, description, is_builtin, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (name, description, is_builtin, now, now))

        conn.commit()


def _get_profile_id(cursor, profile_name: str) -> int | None:
    cursor.execute("SELECT id FROM profiles WHERE name = ?", (profile_name,))
    row = cursor.fetchone()
    return row[0] if row else None


def _insert_rule(
    cursor,
    profile_id: int,
    rule_type: str,
    target_type: str,
    pattern: str,
    enabled: int = 1,
    priority: int = 100,
    notes: str | None = None,
) -> None:
    cursor.execute("""
        INSERT OR IGNORE INTO rules (
            profile_id, rule_type, target_type, pattern, enabled, priority, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (profile_id, rule_type, target_type, pattern, enabled, priority, notes))


def seed_rules() -> None:
    rules_by_profile = {
        "General": [
            ("include", "extension", ".py", 1, 100, "Python source"),
            ("include", "extension", ".java", 1, 100, "Java source"),
            ("include", "extension", ".php", 1, 100, "PHP source"),
            ("include", "extension", ".js", 1, 100, "JavaScript source"),
            ("include", "extension", ".ts", 1, 100, "TypeScript source"),
            ("include", "extension", ".html", 1, 100, "HTML file"),
            ("include", "extension", ".css", 1, 100, "CSS file"),
            ("include", "extension", ".cs", 1, 100, "C# source"),
            ("include", "extension", ".json", 1, 100, "JSON config"),
            ("include", "extension", ".md", 1, 100, "Markdown docs"),
            ("include", "extension", ".txt", 1, 100, "Text docs"),
            ("exclude", "folder_name", ".git", 1, 100, "Git metadata"),
            ("exclude", "folder_name", "__pycache__", 1, 100, "Python cache"),
            ("exclude", "folder_name", "node_modules", 1, 100, "Node dependencies"),
            ("exclude", "folder_name", "venv", 1, 100, "Virtual environment"),
            ("exclude", "folder_name", ".venv", 1, 100, "Virtual environment"),
            ("exclude", "folder_name", "dist", 1, 100, "Build output"),
            ("exclude", "folder_name", "build", 1, 100, "Build output"),
            ("review", "extension", ".png", 1, 100, "Image asset"),
            ("review", "extension", ".jpg", 1, 100, "Image asset"),
            ("review", "extension", ".jpeg", 1, 100, "Image asset"),
            ("review", "extension", ".csv", 1, 100, "CSV data"),
            ("review", "extension", ".sql", 1, 100, "SQL data"),
            ("review", "extension", ".db", 1, 100, "Database file"),
            ("review", "extension", ".sqlite", 1, 100, "SQLite database"),
        ],
        "Python": [
            ("detect", "filename", "requirements.txt", 1, 100, "Python dependency file"),
            ("detect", "filename", "pyproject.toml", 1, 100, "Python project file"),
            ("detect", "filename", "setup.py", 1, 100, "Python setup script"),
            ("include", "extension", ".py", 1, 100, "Python source"),
            ("include", "extension", ".pyi", 1, 100, "Python typing stub"),
            ("include", "filename", "requirements.txt", 1, 100, "Dependencies"),
            ("include", "filename", "pyproject.toml", 1, 100, "Project config"),
            ("include", "filename", "setup.py", 1, 100, "Setup script"),
            ("include", "filename", ".env.example", 1, 100, "Environment example"),
            ("exclude", "folder_name", "__pycache__", 1, 100, "Python cache"),
            ("exclude", "folder_name", ".pytest_cache", 1, 100, "Pytest cache"),
            ("exclude", "folder_name", "venv", 1, 100, "Virtual environment"),
            ("exclude", "folder_name", ".venv", 1, 100, "Virtual environment"),
            ("exclude", "folder_name", "dist", 1, 100, "Distribution output"),
            ("exclude", "folder_name", "build", 1, 100, "Build output"),
            ("review", "filename", ".env", 1, 100, "Sensitive environment file"),
            ("review", "extension", ".db", 1, 100, "Database file"),
            ("review", "extension", ".sqlite", 1, 100, "SQLite database"),
            ("review", "extension", ".csv", 1, 100, "CSV data"),
        ],
        "Java": [
            ("detect", "filename", "pom.xml", 1, 100, "Maven project"),
            ("detect", "filename", "build.gradle", 1, 100, "Gradle build file"),
            ("detect", "filename", "settings.gradle", 1, 100, "Gradle settings"),
            ("include", "extension", ".java", 1, 100, "Java source"),
            ("include", "extension", ".kt", 1, 100, "Kotlin source"),
            ("include", "filename", "pom.xml", 1, 100, "Maven config"),
            ("include", "filename", "build.gradle", 1, 100, "Gradle build"),
            ("include", "filename", "settings.gradle", 1, 100, "Gradle settings"),
            ("exclude", "folder_name", "target", 1, 100, "Maven output"),
            ("exclude", "folder_name", "build", 1, 100, "Gradle output"),
            ("exclude", "extension", ".class", 1, 100, "Compiled Java bytecode"),
            ("review", "extension", ".jar", 1, 100, "Packaged Java archive"),
            ("review", "extension", ".sql", 1, 100, "SQL data"),
        ],
        "PHP": [
            ("detect", "filename", "composer.json", 1, 100, "Composer project"),
            ("include", "extension", ".php", 1, 100, "PHP source"),
            ("include", "filename", "composer.json", 1, 100, "Composer config"),
            ("include", "filename", "composer.lock", 1, 100, "Composer lock"),
            ("exclude", "folder_name", "vendor", 1, 100, "Vendor dependencies"),
            ("review", "filename", ".env", 1, 100, "Sensitive environment file"),
            ("review", "extension", ".sql", 1, 100, "SQL data"),
            ("review", "extension", ".csv", 1, 100, "CSV data"),
        ],
        "Laravel": [
            ("detect", "filename", "artisan", 1, 100, "Laravel marker"),
            ("detect", "filename", "composer.json", 1, 100, "Composer project"),
            ("detect", "folder_name", "routes", 1, 100, "Laravel routes folder"),
            ("include", "extension", ".php", 1, 100, "PHP source"),
            ("include", "filename", "artisan", 1, 100, "Laravel CLI"),
            ("include", "filename", "composer.json", 1, 100, "Composer config"),
            ("include", "filename", "composer.lock", 1, 100, "Composer lock"),
            ("include", "path_contains", "routes/", 1, 100, "Laravel routes"),
            ("include", "path_contains", "resources/views/", 1, 100, "Blade views"),
            ("exclude", "folder_name", "vendor", 1, 100, "Vendor dependencies"),
            ("exclude", "folder_name", "node_modules", 1, 100, "Node dependencies"),
            ("exclude", "folder_name", "bootstrap/cache", 1, 100, "Laravel cache"),
            ("review", "filename", ".env", 1, 100, "Sensitive environment file"),
            ("review", "folder_name", "storage", 1, 100, "May contain useful or generated data"),
            ("review", "folder_name", "public", 1, 100, "May contain useful assets"),
            ("review", "extension", ".sql", 1, 100, "SQL data"),
        ],
        "JavaScript_Web": [
            ("detect", "filename", "package.json", 1, 100, "Node package file"),
            ("detect", "filename", "package-lock.json", 1, 100, "NPM lock file"),
            ("detect", "filename", "vite.config.js", 1, 100, "Vite config"),
            ("detect", "filename", "webpack.config.js", 1, 100, "Webpack config"),
            ("include", "extension", ".js", 1, 100, "JavaScript source"),
            ("include", "extension", ".ts", 1, 100, "TypeScript source"),
            ("include", "extension", ".jsx", 1, 100, "React JSX"),
            ("include", "extension", ".tsx", 1, 100, "React TSX"),
            ("include", "extension", ".html", 1, 100, "HTML file"),
            ("include", "extension", ".css", 1, 100, "CSS file"),
            ("include", "filename", "package.json", 1, 100, "Package config"),
            ("include", "filename", "package-lock.json", 1, 100, "Package lock"),
            ("exclude", "folder_name", "node_modules", 1, 100, "Node dependencies"),
            ("exclude", "folder_name", "dist", 1, 100, "Build output"),
            ("exclude", "folder_name", "build", 1, 100, "Build output"),
            ("exclude", "folder_name", "coverage", 1, 100, "Coverage output"),
            ("review", "filename", ".env", 1, 100, "Sensitive environment file"),
            ("review", "extension", ".png", 1, 100, "Image asset"),
            ("review", "extension", ".jpg", 1, 100, "Image asset"),
            ("review", "extension", ".svg", 1, 100, "Image asset"),
        ],
        "CSharp_DotNet": [
            ("detect", "extension", ".sln", 1, 100, "Solution file"),
            ("detect", "extension", ".csproj", 1, 100, "Project file"),
            ("include", "extension", ".cs", 1, 100, "C# source"),
            ("include", "extension", ".csproj", 1, 100, "Project file"),
            ("include", "extension", ".sln", 1, 100, "Solution file"),
            ("include", "extension", ".xaml", 1, 100, "XAML UI file"),
            ("include", "extension", ".razor", 1, 100, "Blazor Razor file"),
            ("include", "extension", ".cshtml", 1, 100, "ASP.NET Razor view"),
            ("include", "filename", "appsettings.json", 1, 100, "Application config"),
            ("exclude", "folder_name", "bin", 1, 100, "Compiled output"),
            ("exclude", "folder_name", "obj", 1, 100, "Build intermediates"),
            ("exclude", "folder_name", ".vs", 1, 100, "Visual Studio metadata"),
            ("exclude", "folder_name", "TestResults", 1, 100, "Test output"),
            ("review", "filename", ".env", 1, 100, "Sensitive environment file"),
            ("review", "extension", ".db", 1, 100, "Database file"),
            ("review", "extension", ".sqlite", 1, 100, "SQLite database"),
        ],
        "Android": [
            ("detect", "filename", "AndroidManifest.xml", 1, 100, "Android manifest"),
            ("detect", "filename", "build.gradle", 1, 100, "Gradle build file"),
            ("detect", "filename", "settings.gradle", 1, 100, "Gradle settings"),
            ("include", "filename", "AndroidManifest.xml", 1, 100, "Android manifest"),
            ("include", "extension", ".kt", 1, 100, "Kotlin source"),
            ("include", "extension", ".java", 1, 100, "Java source"),
            ("include", "extension", ".xml", 1, 100, "Android XML"),
            ("include", "filename", "build.gradle", 1, 100, "Gradle build"),
            ("include", "filename", "settings.gradle", 1, 100, "Gradle settings"),
            ("include", "filename", "gradle.properties", 1, 100, "Gradle properties"),
            ("exclude", "folder_name", "build", 1, 100, "Build output"),
            ("exclude", "folder_name", ".gradle", 1, 100, "Gradle cache"),
            ("review", "folder_name", "res/drawable", 1, 100, "Image resources"),
            ("review", "folder_name", "assets", 1, 100, "App assets"),
            ("review", "extension", ".png", 1, 100, "Image asset"),
            ("review", "extension", ".jpg", 1, 100, "Image asset"),
        ],
        "Unity": [
            ("detect", "folder_name", "Assets", 1, 100, "Unity assets folder"),
            ("detect", "folder_name", "Packages", 1, 100, "Unity packages folder"),
            ("detect", "folder_name", "ProjectSettings", 1, 100, "Unity project settings"),
            ("include", "path_contains", "Assets/", 1, 100, "Unity assets"),
            ("include", "path_contains", "Packages/", 1, 100, "Unity packages"),
            ("include", "path_contains", "ProjectSettings/", 1, 100, "Unity project settings"),
            ("exclude", "folder_name", "Library", 1, 100, "Unity cache"),
            ("exclude", "folder_name", "Temp", 1, 100, "Temporary files"),
            ("exclude", "folder_name", "Logs", 1, 100, "Log files"),
            ("exclude", "folder_name", "Obj", 1, 100, "Intermediate objects"),
            ("exclude", "folder_name", "Build", 1, 100, "Build output"),
            ("exclude", "folder_name", "Builds", 1, 100, "Build output"),
            ("exclude", "folder_name", "UserSettings", 1, 100, "User settings"),
            ("review", "extension", ".png", 1, 100, "Texture asset"),
            ("review", "extension", ".jpg", 1, 100, "Texture asset"),
            ("review", "extension", ".wav", 1, 100, "Audio asset"),
            ("review", "extension", ".mp3", 1, 100, "Audio asset"),
            ("review", "extension", ".mp4", 1, 100, "Video asset"),
        ],
    }

    with get_connection() as conn:
        cursor = conn.cursor()

        for profile_name, rules in rules_by_profile.items():
            profile_id = _get_profile_id(cursor, profile_name)
            if profile_id is None:
                continue

            for rule in rules:
                rule_type, target_type, pattern, enabled, priority, notes = rule
                _insert_rule(
                    cursor=cursor,
                    profile_id=profile_id,
                    rule_type=rule_type,
                    target_type=target_type,
                    pattern=pattern,
                    enabled=enabled,
                    priority=priority,
                    notes=notes,
                )

        conn.commit()