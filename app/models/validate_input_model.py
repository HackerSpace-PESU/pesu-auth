from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from app.constants import PESUAcademyConstants


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
            valid_fields = PESUAcademyConstants.DEFAULT_FIELDS
            invalid_fields = [field for field in v if field not in valid_fields]
            if invalid_fields:
                raise ValueError(
                    f"Invalid fields: {', '.join(invalid_fields)}. Valid fields are: {', '.join(valid_fields)}"
                )
        return v
