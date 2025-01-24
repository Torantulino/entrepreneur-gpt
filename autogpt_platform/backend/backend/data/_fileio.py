from enum import Enum
from typing import TYPE_CHECKING, Generic, TypeVar, get_args

from pydantic import BaseModel
from pydantic.config import ConfigDict, JsonDict
from pydantic_core import ValidationError

if TYPE_CHECKING:
    from backend.data.block import BlockSchema


class MIMEType(Enum):
    # Feel free to add missing MIME types as needed.
    # Just make sure not to make duplicates, and stick to the existing naming pattern.
    TEXT = "text/plain"


MT = TypeVar("MT", bound=MIMEType)


class FileMetaIO(BaseModel, Generic[MT]):
    id: str
    name: str = ""
    content_type: MT

    @classmethod
    def allowed_content_types(cls) -> tuple[MIMEType, ...]:
        return get_args(cls.model_fields["content_type"].annotation)

    @classmethod
    def validate_file_field_schema(cls, model: type["BlockSchema"]):
        """Validates the schema of a file I/O field"""
        field_name = next(
            name for name, type in model.get_credentials_fields().items() if type is cls
        )
        field_schema = model.jsonschema()["properties"][field_name]
        try:
            _FileIOFieldSchemaExtra[MT].model_validate(field_schema)
        except ValidationError as e:
            if "Field required [type=missing" not in str(e):
                raise

            raise TypeError(
                "Field 'credentials' JSON schema lacks required extra items: "
                f"{field_schema}"
            ) from e

    @staticmethod
    def _add_json_schema_extra(schema: JsonDict, cls: "FileMetaIO"):
        schema["content_types"] = [ct.value for ct in cls.allowed_content_types()]
        # TODO: add file extensions?

    model_config = ConfigDict(
        json_schema_extra=_add_json_schema_extra,  # type: ignore
    )


class _FileIOFieldSchemaExtra(BaseModel, Generic[MT]):
    content_types: list[MT]
