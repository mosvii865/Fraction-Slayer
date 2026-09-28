from dataclasses import dataclass, field


@dataclass
class InternshipReport:
    practitioner: str
    company: str = "DDI"
    area: str = "Quality Control"
    observations: list[str] = field(default_factory=list)
    measurements: list[dict] = field(default_factory=list)
    incidents: list[dict] = field(default_factory=list)
    project_utcj: list[str] = field(default_factory=list)
