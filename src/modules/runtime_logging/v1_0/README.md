# Runtime logging module 1.0

Pure one-hour rolling buffers for the visible general and hardware logs plus
classification of high-signal failures for the persistent privacy-filtered
`errors.log`. The Qt adapter remains in `src/log_view_support.py`.

The time window is the primary retention rule. Generous entry and character
ceilings are independent emergency bounds against pathological log floods.

`error_capture.py` preserves existing Python/thread/unraisable hooks, records Qt
warnings/critical failures, deduplicates repeats and bounds a thread-safe queue.
`error_bridge.py` drains it only on the GUI thread. Existing durable module events
notify the same capture; GUI writes suppress that notification and bridge writes
suppress durable persistence, avoiding loops/duplicate error records. Nothing is
uploaded. Existing crash/native-fault logging remains installed underneath.
