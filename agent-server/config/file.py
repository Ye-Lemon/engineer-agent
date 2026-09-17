from pathlib import Path


# 后端项目根路径
BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 100 * 1024 * 1024

ALLOWED_EXTENSIONS = {"docx", "doc", "pdf", "xls", "xlsx", "ppt", "pptx", "txt", "md", "markdown", "csv", "tsv", "json", "html", "htm", "xhtml"}
