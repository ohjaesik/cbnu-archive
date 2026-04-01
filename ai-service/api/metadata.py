from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter

from models.project import ProjectInput
from services.metadata_analyzer import MetadataAnalyzer

router = APIRouter(prefix="/metadata", tags=["metadata"])

analyzer = MetadataAnalyzer()


@router.post("/analyze")
def analyze_metadata(project: ProjectInput):
    result = analyzer.analyze(project)
    return asdict(result)