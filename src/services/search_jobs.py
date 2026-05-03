from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from src.api.schemas.search import (
    SearchExecuteRequest,
    SearchExecuteResponse,
    SearchJobCreateRequest,
    SearchJobCreateResponse,
    SearchJobProgress,
    SearchJobStatus,
    SearchJobStatusResponse,
)
from src.config import Settings
from src.services.search_service import build_search_execute_response

POLL_AFTER_SECONDS = 3
QUEUED_POLLS_BEFORE_RUNNING = 2
RUNNING_POLLS_BEFORE_SUCCEEDED = 4
ACTIVE_JOB_STATUSES: set[SearchJobStatus] = {"queued", "running"}
TERMINAL_JOB_STATUSES: set[SearchJobStatus] = {"succeeded", "failed", "canceled"}


@dataclass
class _SearchJobRecord:
    job_id: str
    idempotency_key: str
    status: SearchJobStatus
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    status_checks: int
    result: SearchExecuteResponse


@dataclass(frozen=True)
class SearchJobResultLookup:
    status: SearchJobStatusResponse | None
    result: SearchExecuteResponse | None


_jobs_by_id: dict[str, _SearchJobRecord] = {}
_job_id_by_idempotency_key: dict[str, str] = {}
_jobs_lock = Lock()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _build_job_progress(status: SearchJobStatus) -> SearchJobProgress:
    if status == "queued":
        return SearchJobProgress(stage="queued", percent=0)
    if status == "running":
        return SearchJobProgress(stage="mock_search", percent=50)
    if status == "succeeded":
        return SearchJobProgress(stage="completed", percent=100)
    if status == "failed":
        return SearchJobProgress(stage="failed", percent=100)
    return SearchJobProgress(stage="canceled", percent=100)


def _to_job_create_response(job: _SearchJobRecord) -> SearchJobCreateResponse:
    return SearchJobCreateResponse(
        job_id=job.job_id,
        status=job.status,
        created_at=job.created_at,
        poll_after_seconds=0 if job.status in TERMINAL_JOB_STATUSES else POLL_AFTER_SECONDS,
    )


def _to_job_status_response(job: _SearchJobRecord) -> SearchJobStatusResponse:
    return SearchJobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        poll_after_seconds=0 if job.status in TERMINAL_JOB_STATUSES else POLL_AFTER_SECONDS,
        result_available=job.status == "succeeded",
        error=None,
        progress=_build_job_progress(job.status),
    )


def _advance_job_state(job: _SearchJobRecord) -> None:
    if job.status in TERMINAL_JOB_STATUSES:
        return

    job.status_checks += 1
    now = _utcnow()

    if job.status == "queued" and job.status_checks >= QUEUED_POLLS_BEFORE_RUNNING:
        job.status = "running"
        if job.started_at is None:
            job.started_at = now

    if job.status == "running" and job.status_checks >= RUNNING_POLLS_BEFORE_SUCCEEDED:
        job.status = "succeeded"
        if job.started_at is None:
            job.started_at = now
        if job.completed_at is None:
            job.completed_at = now


def create_search_job(
    payload: SearchJobCreateRequest,
    settings: Settings | None = None,
) -> SearchJobCreateResponse:
    with _jobs_lock:
        existing_job_id = _job_id_by_idempotency_key.get(payload.idempotency_key)
        if existing_job_id is not None:
            existing_job = _jobs_by_id.get(existing_job_id)
            if existing_job is not None and existing_job.status in ACTIVE_JOB_STATUSES:
                return _to_job_create_response(existing_job)

        job_id = f"job_{uuid4().hex[:24]}"
        created_at = _utcnow()
        execute_request = SearchExecuteRequest(
            query=payload.query,
            filters=payload.filters,
            output_preferences=payload.output_preferences,
            context=payload.context,
        )
        result = build_search_execute_response(execute_request, settings=settings)

        job = _SearchJobRecord(
            job_id=job_id,
            idempotency_key=payload.idempotency_key,
            status="queued",
            created_at=created_at,
            started_at=None,
            completed_at=None,
            status_checks=0,
            result=result,
        )
        _jobs_by_id[job_id] = job
        _job_id_by_idempotency_key[payload.idempotency_key] = job_id
        return _to_job_create_response(job)


def get_search_job_status(job_id: str) -> SearchJobStatusResponse | None:
    with _jobs_lock:
        job = _jobs_by_id.get(job_id)
        if job is None:
            return None
        _advance_job_state(job)
        return _to_job_status_response(job)


def get_search_job_result(job_id: str) -> SearchJobResultLookup:
    with _jobs_lock:
        job = _jobs_by_id.get(job_id)
        if job is None:
            return SearchJobResultLookup(status=None, result=None)

        _advance_job_state(job)
        status = _to_job_status_response(job)
        if job.status != "succeeded":
            return SearchJobResultLookup(status=status, result=None)

        return SearchJobResultLookup(status=status, result=job.result)
