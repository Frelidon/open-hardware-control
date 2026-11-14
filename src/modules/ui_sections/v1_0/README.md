# Shared UI sections 1.0

`cards.py` owns palette-aware surfaces and keyboard-accessible full-width section
headers. `reveal.py` moves only the nearest existing page scrollbar using a bounded
420 ms animation. Closing returns to the previous position only while that section
owns the automatic movement. Wheel, touch, keyboard, scrollbar interaction or page
hide cancels it. A close holds its body until the return completes to avoid a
scrollbar-range jump. Disabled page animations bypass automatic motion.

No pixels are captured, no graphics-effect buffers are allocated and no settings,
drafts or hardware values change. Profiles and the case workspace share these
surfaces; the legacy Disclosure entry delegates without changing call sites.
