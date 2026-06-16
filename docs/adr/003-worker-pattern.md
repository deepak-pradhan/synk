# ADR-003: QRunnable + QThreadPool Worker Pattern

**Status:** Accepted  
**Date:** 2026-06-16  
**Authors:** dp

## Context

Directory comparison involves recursive filesystem traversal + content hashing for every file. On a directory with 100k+ files, this blocks the UI thread for seconds to minutes. Qt widgets must not be touched from non-main threads.

## Decision

Use **`QRunnable` + `QThreadPool`** for background comparison work, with **`WorkerSignals`** (a `QObject` with `Signal` instances) to communicate results back to the UI thread.

## Rationale

- `QRunnable` is lighter than `QThread` — no event loop overhead, just a `run()` method. Ideal for one-shot comparison jobs.
- `QThreadPool` manages thread lifecycle and caps concurrency (default: CPU core count). Multiple comparisons can run in parallel without unbounded thread creation.
- Signals are queued (auto-connection) — the emitting thread posts the signal, and the receiving slot executes on the main thread's event loop. This guarantees thread-safe UI updates without explicit locks.
- `setAutoDelete(True)` means the runnable is garbage-collected after `run()` completes — no manual cleanup.

## Consequences

**Positive:**
- UI remains responsive during multi-minute comparisons — user can cancel, change settings, or start a new comparison
- Progress reporting via `progress(int, int)` signal
- Clean separation: worker logic is fully unit-testable without Qt (the `run()` method is plain Python)

**Negative:**
- Signals carry copies of data — for very large file lists, the inter-thread marshalling adds latency
- Cancellation requires a flag check in the worker loop (no forced thread termination)
- Debugging thread-related issues (race conditions, signal ordering) is harder than synchronous code

## Implementation

`src/core/worker.py:9` — `WorkerSignals`:

```python
class WorkerSignals(QObject):
    update_item = Signal(str, str, str, str, object)  # pane_id, name, status, color, is_dir
    finished = Signal()
    progress = Signal(int, int)  # current, total
```

`CompareWorker` subclasses `QRunnable`, receives `Hasher` + paths, emits signals per file.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| `QThread` with event loop | Heavier than QRunnable for one-shot jobs; requires manual thread management |
| `asyncio` + `aiofiles` | No Qt event-loop integration without `qasync`; adds dependency |
| `concurrent.futures.ThreadPoolExecutor` | Results must be polled or use callbacks that need `QMetaObject.invokeMethod` to cross thread boundary — more boilerplate |
| Synchronous (block main thread) | Unacceptable UX — freezes window, no progress indicator |
