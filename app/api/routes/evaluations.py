"""Evaluation report routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.evaluation.runner import EvaluationRunner
from app.schemas.evaluation import EvaluationReport

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("", response_model=EvaluationReport)
def get_evaluations(session: Annotated[Session, Depends(get_db)]) -> EvaluationReport:
    return EvaluationRunner(session).report()


@router.post("/run", response_model=EvaluationReport)
def run_evaluations(session: Annotated[Session, Depends(get_db)]) -> EvaluationReport:
    return EvaluationRunner(session).run_all()
