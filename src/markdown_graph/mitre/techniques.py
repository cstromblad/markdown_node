from pydantic import BaseModel, Field


class TechniqueMeta(BaseModel):
    external_id: str
    kill_chain: list[str] = Field(default=[])
    refs: list[str]


class AttackTechnique(BaseModel):
    description: str
    meta: TechniqueMeta
    uuid: str
    name: str = Field(alias="value")

    class Config:
        populate_by_name: bool = True
