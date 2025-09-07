from pydantic import BaseModel, ConfigDict


class AuthorBase(BaseModel):
    name: str


class AuthorCreate(AuthorBase):
    pass


class AuthorOut(AuthorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
