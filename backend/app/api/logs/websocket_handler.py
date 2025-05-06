import logging
import queue

from .schema import LogEntry


class NonBlockingQueue(logging.Handler):
    def __init__(self, q: queue.Queue) -> None:
        super().__init__()
        self.queue: queue.Queue = q

    def emit(self, record: logging.LogRecord) -> None:
        try:
            log_entry = LogEntry.create(record)
        except Exception:
            return
        try:
            self.queue.put_nowait(log_entry)
        except queue.Full:
            self._try_enqueue(log_entry)

    def _try_enqueue(self, log_entry: LogEntry) -> None:
        try:
            self.queue.get_nowait()
            self.queue.put_nowait(log_entry)
        except queue.Full:
            pass
