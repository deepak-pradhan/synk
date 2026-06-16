---
thing_id:        "synk-adr-0003"
thing_type:      "adr"
adr_id:          "0003"
domain:          "synk"
phase:           "p0-foundations"
version:         "1.0"
lifecycle_state: "approved"
deciders:        "Deepak"
reversibility:   "high"
decision_date:   "2026-06-14"
last_updated:    "2026-06-16"
next_review_date: "2026-09-16"
priority:        "high"
confidentiality: "internal"
tags:            [concurrency, threading, qrunnable, worker, ui-responsiveness]
relations:
  depends_on:    ["synk-adr-0001"]
  related_to:    []
  enables:       []
---

# ADR-0003: QRunnable + QThreadPool Worker Pattern

## Status

**Accepted** (2026-06-14). Implementation verified in v0.1 M2.

## Context

Directory comparison involves recursive filesystem traversal + content hashing for every file. On
a directory with 100k+ files, this blocks the UI thread for seconds to minutes. Qt widgets must
not be touched from non-main threads.

## Decision

Use **`QRunnable` + `QThreadPool`** for background comparison work, with **`WorkerSignals`** (a
`QObject` with `Signal` instances) to communicate results back to the UI thread.

## Rationale

- `QRunnable` is lighter than `QThread` — no event loop overhead, just a `run()` method.
- `QThreadPool` manages thread lifecycle and caps concurrency (default: CPU core count).
- Signals are queued (auto-connection) — the emitting thread posts the signal, the receiving slot
  executes on the main thread's event loop. Thread-safe UI updates without explicit locks.
- `setAutoDelete(True)` means the runnable is GC'd after `run()` completes.

## Consequences

**Positive:**
- UI remains responsive during multi-minute comparisons.
- Progress reporting via `progress(int, int)` signal.
- Worker logic is fully unit-testable without Qt (the `run()` method is pure Python).

**Negative:**
- Signals carry copies of data — for very large file lists, inter-thread marshalling adds latency.
- Cancellation requires a flag check in the worker loop (no forced thread termination).
- Debugging thread-related issues is harder than synchronous code.

## Implementation

`src/core/worker.py:9` — `WorkerSignals` with `update_item`, `finished`, `progress` signals.
`CompareWorker` subclasses `QRunnable`, receives `Hasher` + paths.

## Alternatives Not Selected

| Alternative | Why Rejected |
|-------------|-------------|
| `QThread` with event loop | Heavier than QRunnable for one-shot jobs |
| `asyncio` + `aiofiles` | No Qt event-loop integration without `qasync` |
| `concurrent.futures` | Must use `QMetaObject.invokeMethod` to cross thread boundary |
| Synchronous (block main thread) | Unacceptable UX — freezes window |
