from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InjectionContext:
    level: str
    mode: str
    get: dict[str, str] = field(default_factory=dict)
    post: dict[str, str] = field(default_factory=dict)
    cookie: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, data: dict[str, Any]) -> InjectionContext:
        def norm_map(x: Any) -> dict[str, str]:
            if not isinstance(x, dict):
                return {}
            return {str(k): "" if v is None else str(v) for k, v in x.items()}

        return cls(
            level=str(data.get("level", "0")),
            mode=str(data.get("mode", "practice")),
            get=norm_map(data.get("get")),
            post=norm_map(data.get("post")),
            cookie=norm_map(data.get("cookie")),
            headers={k.lower(): v for k, v in norm_map(data.get("headers")).items()},
        )

    def get_param(self, name: str, default: str = "") -> str:
        return self.get.get(name, default)

    def post_param(self, name: str, default: str = "") -> str:
        return self.post.get(name, default)

    def cookie_param(self, name: str, default: str = "") -> str:
        return self.cookie.get(name, default)

    def header(self, name: str, default: str = "") -> str:
        return self.headers.get(name.lower(), default)
