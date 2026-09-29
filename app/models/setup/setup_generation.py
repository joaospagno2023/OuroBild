from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class SetupGeneration:
    generation_id: str
    version: str | None
    revision: int | None
    environment_id: str
    status: str
    started_at: datetime
    finished_at: datetime | None
    last_file_path: str | None
    last_file_generated_at: datetime | None
    validity_minutes: int
    created_by: str | None
    execution_id: str | None


@dataclass(slots=True)
class SetupGenerationFile:
    id: int | None
    generation_id: str
    project_id: str
    file_path: str
    generated_at: datetime
    success: bool
