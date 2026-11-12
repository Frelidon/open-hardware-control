# Help Center 1.0

`page.py` composes a top-aligned topic library and readable article surface.
`topics.py` draws original palette-aware topic cards; it performs no I/O.
`controller.py` preserves existing four-language help content, topic IDs,
search and explicit `ohc://page/` navigation. Selecting help never starts a
hardware action or changes settings. The topic tree opts out of generic
content-height fitting so it cannot be vertically centered as a short list.
