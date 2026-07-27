import os
import time
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile, status

from app.config import settings

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


class FileService:
    """Service to handle storing and deleting files locally in the application."""

    @staticmethod
    def validate_file_extension(filename: str) -> str:
        """Ensure file extension is allowed and return lowercase extension."""
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            allowed_str = ", ".join(ALLOWED_EXTENSIONS)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension '{ext}'. Allowed extensions: {allowed_str}",
            )
        return ext

    @staticmethod
    def save_diagram_file(
        file: UploadFile,
        diagram_type: int | str = 0,
    ) -> str:
        """
        Saves an uploaded diagram file locally under uploads/diagrams/{category}/.
        
        Args:
            file: The FastAPI UploadFile object.
            diagram_type: 0 or "question" for question diagrams, 1 or "option" for option diagrams.

        Returns:
            Relative path string formatted with forward slashes (e.g., 'uploads/diagrams/question/uuid_timestamp.png')
        """
        # Normalize target category folder ('question' or 'option')
        if diagram_type in (0, "0", "question"):
            category = "question"
        elif diagram_type in (1, "1", "option"):
            category = "option"
        else:
            category = "question"

        subfolder = f"diagrams/{category}"
        return FileService.upload_image(source=file, subfolder=subfolder)

    @staticmethod
    def store_image(
        source: UploadFile | str | Path,
        subfolder: str = "images",
    ) -> str:
        """
        Helper function to store any image file locally.
        
        Args:
            source: An UploadFile object OR a local file path string / Path.
            subfolder: Subdirectory inside uploads/ (e.g. 'images', 'general', 'avatars').

        Returns:
            Relative path string formatted with forward slashes (e.g., 'uploads/images/uuid_timestamp.png').
        """
        return FileService.upload_image(source=source, subfolder=subfolder)

    @staticmethod
    def upload_image(
        source: UploadFile | str | Path,
        subfolder: str = "images",
    ) -> str:
        """
        Uploads/saves an image file locally under uploads/{subfolder}/.

        Args:
            source: An UploadFile object OR a local file path (str/Path).
            subfolder: Subdirectory inside uploads/ (e.g., 'images', 'diagrams', 'general').

        Returns:
            Relative path string formatted with forward slashes (e.g., 'uploads/images/uuid_timestamp.png').
        """
        if isinstance(source, UploadFile):
            filename = source.filename
            if not filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Uploaded file must have a filename",
                )
            ext = FileService.validate_file_extension(filename)
            source.file.seek(0)
            content = source.file.read()
        else:
            path_obj = Path(source)
            if not path_obj.exists() or not path_obj.is_file():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Source file not found at path '{source}'",
                )
            ext = FileService.validate_file_extension(path_obj.name)
            with open(path_obj, "rb") as f:
                content = f.read()

        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB",
            )

        # Construct target directory: uploads/<subfolder>/
        base_upload_dir = Path(settings.upload_dir)
        target_dir = base_upload_dir / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename: uuid_timestamp.ext
        unique_id = uuid.uuid4().hex
        timestamp = int(time.time())
        new_filename = f"{unique_id}_{timestamp}{ext}"

        file_path = target_dir / new_filename

        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save image file: {str(exc)}",
            ) from exc

        return file_path.as_posix()

    @staticmethod
    def delete_file(relative_path: str) -> bool:
        """Delete a local file if it exists."""
        try:
            path = Path(relative_path)
            if path.exists() and path.is_file():
                path.unlink()
                return True
        except Exception:
            pass
        return False


# ─── Module-Level Standalone Helper Functions ─────────────────────────────────

store_image = FileService.store_image
upload_image = FileService.upload_image
save_diagram_file = FileService.save_diagram_file
delete_file = FileService.delete_file
