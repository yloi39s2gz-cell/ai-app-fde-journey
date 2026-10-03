from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class Resume(BaseModel):
    name: str = Field(description="候选人姓名")
    years_experience: float | None = Field(
        default=None, description="工作年限，年。没有就 null，不要编"
    )
    skills: list[str] = Field(default_factory=list, description="技能列表，短词")
    latest_title: str | None = Field(default=None, description="最近一份职位")
    latest_company: str | None = Field(default=None, description="最近一份公司")
    education: str | None = Field(default=None, description="最高学历，如本科/硕士")
    email: str | None = Field(default=None, description="邮箱，没有就 null")
    phone: str | None = Field(default=None, description="电话，没有就 null")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v or v in {"未知", "无", "N/A", "null"}:
            raise ValueError("name 不能为空或占位符")
        return v

    @field_validator("skills")
    @classmethod
    def skills_clean(cls, v: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in v:
            s = item.strip()
            if not s:
                continue
            key = s.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(s)
        return out
