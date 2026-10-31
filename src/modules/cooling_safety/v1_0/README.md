# Cooling safety 1.0

This fail-closed policy centralizes model-specific software PWM floors. For the
Thermalright Levita Vision 360 ARGB Black, Thermalright publishes rated maximum
speeds but no minimum PWM duty. OHC therefore labels and enforces its own
conservative floor (pump 50%, radiator 25%) instead of presenting an invented
manufacturer minimum. Every manual value, quick profile and software curve is
clamped again immediately before a supported hardware write.
