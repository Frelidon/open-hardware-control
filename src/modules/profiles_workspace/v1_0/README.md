# Profiles workspace 1.0

`page.py` composes a searchable card library, saved-section summaries and collapsed
editor/details/transfer panels. `model.py` is pure and defensive. `cards.py` owns
palette-aware pointer/keyboard selection. Existing parent-owned hidden table keeps
legacy ID-based CRUD, bundle import and startup contracts; selection never applies.
No persistence schema, hardware writer or profile ID changes. Dynamic language
refresh retains unsaved fields, search, filter and selected ID.
