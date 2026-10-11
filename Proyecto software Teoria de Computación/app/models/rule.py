
from dataclasses import dataclass, field


@dataclass
class Rule:
    source: str

    @classmethod
    def from_dict(cls, data):
        source = data.get("source", "")

        if not isinstance(source, str):
            raise ValueError("La regla debe ser texto.")

        return cls(source=source)


@dataclass
class AnalysisResult:
    tokens: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    line_count: int = 0

    def to_dict(self):
        return {
            "tokens": self.tokens,
            "errors": self.errors,
            "token_count": len(self.tokens),
            "line_count": self.line_count,
            "error_count": len(self.errors),
            "valid": len(self.errors) == 0
        }
    