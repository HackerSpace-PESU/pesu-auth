from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional


class ValidateInputModel(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str
    password: str
    profile: bool = False
    fields: Optional[list[str]] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not v:
            raise ValueError("Password cannot be empty")
        return v

    @field_validator("fields")
    @classmethod
    def validate_fields(cls, v):
        if v is not None:
            if not isinstance(v, list) or not v:
                raise ValueError("Fields must be a non-empty list or None")

            valid_fields = [
                "name",
                "prn",
                "srn",
                "program",
                "branch_short_code",
                "branch",
                "semester",
                "section",
                "email",
                "phone",
                "campus_code",
                "campus",
            ]

            for field in v:
                if not isinstance(field, str) or field not in valid_fields:
                    raise ValueError(
                        f"Invalid field: '{field}'. Valid fields are: {valid_fields}"
                    )
        return v
