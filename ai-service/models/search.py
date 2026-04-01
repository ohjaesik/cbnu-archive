from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class RankedProject:
    rank: int
    project_id: int
    title: str
    topic: Optional[str]
    tech_stack: List[str]
    difficulty: Optional[str]
    project_type: Optional[str]
    semantic_score: float
    metadata_score: float
    final_score: float
    reasons: List[str]