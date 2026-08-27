from pathlib import Path


EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
}


def detect_languages(changed_files: list[str]) -> set[str]:
    """
    Detect programming languages represented in the
    files changed by a PR.
    """

    languages = set()

    for file_path in changed_files:
        extension = Path(file_path).suffix.lower()

        language = EXTENSION_TO_LANGUAGE.get(extension)

        if language:
            languages.add(language)

    return languages