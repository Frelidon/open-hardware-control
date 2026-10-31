# Open Hardware Control 3.4.29.61 INTERN

The application appearance is now a versioned UI Themes 1.0 module. Light and
dark definitions own independent palettes and semantic widget tokens, while a
small allowlisted registry is the only extension point required for a future
theme. Light mode replaces remaining dark-only cards, editor overlays,
navigation and status fragments with bright, higher-contrast surfaces.

Display Effects 1.5 plays every selected bundled effect MP4 in the existing
large Levita composition preview. Dark Smoke begins at its first useful motion
phase instead of presenting several black seconds. Decoding is limited to the
currently selected local catalog asset, rendered at a maximum of ten UI updates
per second, and pauses when the page is left, the window is hidden/minimized or
the user presses Pause. Controlled shutdown stops and clears the player. The
existing validated media roots, Layer 2 and sole TRCC hardware writer are
unchanged.

Selecting a library display effect now stages the validated medium and current
Layer 2 for the next LCD/full profile update; generated effects are staged once
their video exists. Display Effects includes an explicit startup-design button
and a translated reminder to update the selected profile. At the next
application start that profile restores the Levita choice before the established
delayed hand-off; browsing or staging alone performs no hardware write.

The supplied log contains successful RGB requests and a bounded visible window
restore; it shows no new RGB, LCD or process failure. No GitHub push, tag or
public release was created.
