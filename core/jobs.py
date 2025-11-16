from __future__ import annotations

import os
from typing import Any, Dict, List
from rq import Queue
from redis import Redis
from rq.job import Job


def get_connection() -> Redis:
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return Redis.from_url(url)


def get_queue(name: str = "default") -> Queue:
    return Queue(name, connection=get_connection())


def enqueue(func_path: str, *args, **kwargs) -> str:
    q = get_queue()
    job: Job = q.enqueue(func_path, *args, **kwargs)
    return job.get_id()


def get_job(job_id: str) -> Dict[str, Any]:
    try:
        job = Job.fetch(job_id, connection=get_connection())
        return {
            "id": job.get_id(),
            "status": job.get_status(),
            "result": job.result if job.is_finished else None,
            "meta": job.meta,
            "enqueued_at": str(job.enqueued_at) if job.enqueued_at else None,
            "ended_at": str(job.ended_at) if job.ended_at else None,
        }
    except Exception as ex:
        return {"id": job_id, "status": "unknown", "error": str(ex)}


