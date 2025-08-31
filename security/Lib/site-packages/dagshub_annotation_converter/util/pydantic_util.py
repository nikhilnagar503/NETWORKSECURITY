from pydantic import BaseModel


# Make all models be built only on creation/validation, since this is a library
class ParentModel(BaseModel, defer_build=True, extra="allow"): ...
