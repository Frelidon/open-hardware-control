# Runtime logging module 1.0

Pure one-hour rolling buffers for the visible general and hardware logs plus
classification of high-signal failures for the persistent privacy-filtered
`errors.log`. The Qt adapter remains in `src/log_view_support.py`.

The time window is the primary retention rule. Generous entry and character
ceilings are independent emergency bounds against pathological log floods.
