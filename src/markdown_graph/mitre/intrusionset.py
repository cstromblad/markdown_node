from pydantic import BaseModel, Field


class Meta(BaseModel):
    external_id: str
    refs: list[str]
    synonyms: list[str]


class Technique(BaseModel):
    dest_uuid: str = Field(..., alias="dest-uuid")
    type: str


class IntrusionSet(BaseModel):
    description: str
    meta: Meta
    techniques: list[Technique] | None = Field(alias="related")
    uuid: str
    name: str = Field(alias="value")

    class Config:
        populate_by_name: bool = True
