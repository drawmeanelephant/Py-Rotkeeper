from __future__ import annotations
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Optional


@dataclass
class Page:
    title: str
    path: str          # output-relative .html path
    source: str        # content-relative .md path
    author: str = "Misc"
    date: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    rotkeeper_nav: list[str] = field(default_factory=list)
    show_in_nav: bool = True
    description: str = ""

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, data: dict) -> "Page":
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})
