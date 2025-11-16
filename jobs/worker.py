from __future__ import annotations

import os
from rq import Worker, Queue, Connection
from core.jobs import get_connection


def main() -> None:
    listen = ["default"]
    conn = get_connection()
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()


if __name__ == "__main__":
    main()


