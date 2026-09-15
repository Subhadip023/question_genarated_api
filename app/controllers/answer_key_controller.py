import os
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.answer_key import AnswerKey
from app.models.test_series import TestSeries


class AnswerKeyController:

    @staticmethod
    def get(
        series_id: int,
        db: Session
    ):
        # Make sure test series exists
        series = (
            db.query(TestSeries)
            .filter(TestSeries.id == series_id)
            .first()
        )

        if not series:
            return None

        return (
            db.query(AnswerKey)
            .filter(AnswerKey.test_series_id == series_id)
            .first()
        )

    @staticmethod
    def create(
        series_id: int,
        file: UploadFile,
        db: Session
    ):
        series = (
            db.query(TestSeries)
            .filter(TestSeries.id == series_id)
            .first()
        )

        if not series:
            return None

        # Only PDF allowed
        if file.content_type != "application/pdf":
            raise ValueError("Only PDF files are allowed")

        # Check existing answer key
        existing = (
            db.query(AnswerKey)
            .filter(
                AnswerKey.test_series_id == series_id
            )
            .first()
        )

        # Directory:
        # uploads/results/{series_id}
        upload_dir = Path(
            "uploads"
        ) / "results" / str(series_id)

        upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path = upload_dir / "answer_key.pdf"

        # If replacing existing file
        if existing:
            old_file = Path(existing.path)

            if old_file.exists():
                old_file.unlink()

            with open(file_path, "wb") as buffer:
                buffer.write(file.file.read())

            existing.path = str(file_path)

            db.commit()
            db.refresh(existing)

            return existing

        # New answer key
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        answer_key = AnswerKey(
            test_series_id=series_id,
            path=str(file_path)
        )

        db.add(answer_key)
        db.commit()
        db.refresh(answer_key)

        return answer_key

    @staticmethod
    def delete(
        series_id: int,
        db: Session
    ):
        answer_key = (
            db.query(AnswerKey)
            .filter(
                AnswerKey.test_series_id == series_id
            )
            .first()
        )

        if not answer_key:
            return False

        file_path = Path(answer_key.path)

        if file_path.exists():
            file_path.unlink()

        db.delete(answer_key)
        db.commit()

        return True