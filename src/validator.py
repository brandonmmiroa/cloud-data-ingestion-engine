from typing import Optional
from pydantic import BaseModel, Field, field_validator, ValidationError

class PostModel(BaseModel):
    post_id: int = Field(..., alias="id")
    user_id: int = Field(..., alias="userId")
    title: str = Field(...)
    body: str = Field(...)

    class Config:
        extra = "forbid"

    @field_validator("title", "body")
    def sanitize_and_check_non_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or blank whitespace.")
        return cleaned


class DataValidator:
    @staticmethod
    def validate_batch(raw_records: list[dict]) -> tuple[list[dict], list[dict]]:
        valid_records = []
        failed_records = []

        for record in raw_records:
            try:
                validated = PostModel(**record)
                # Export using field names matching database columns
                valid_records.append({
                    "post_id": validated.post_id,
                    "user_id": validated.user_id,
                    "title": validated.title,
                    "body": validated.body
                })
            except ValidationError as ve:
                failed_records.append({
                    "raw_payload": record,
                    "error_type": "PydanticValidationError",
                    "error_details": ve.errors()
                })

        return valid_records, failed_records
