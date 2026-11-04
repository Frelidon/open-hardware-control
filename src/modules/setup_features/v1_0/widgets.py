# SPDX-License-Identifier: GPL-3.0-or-later
"""Small animated, hardware-inert feature cards for the setup wizard."""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtWidgets import QCheckBox, QFrame, QGraphicsOpacityEffect, QHBoxLayout, QLabel, QVBoxLayout

from modules.feature_lifecycle.v1_0 import feature_lifecycle

from .model import FeatureChoice


class FeatureCard(QFrame):
    def __init__(self, feature: FeatureChoice, translate, parent=None) -> None:
        super().__init__(parent)
        self.feature = feature
        self.setObjectName("setupFeatureCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setToolTip(translate(feature.description))
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(6)
        row = QHBoxLayout()
        icon = QLabel(feature.icon)
        icon.setObjectName("moduleHeroIcon")
        icon.setFixedSize(38, 38)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copy = QVBoxLayout()
        self.title_label = QLabel(translate(feature.title))
        self.title_label.setObjectName("cardTitle")
        self.status_label = QLabel(translate(feature.availability))
        self.status_label.setObjectName("muted" if feature.available else "warningText")
        copy.addWidget(self.title_label)
        copy.addWidget(self.status_label)
        lifecycle = feature_lifecycle(feature.key)
        self.lifecycle_label = QLabel(
            f"{translate(lifecycle.stage)} · v{lifecycle.version}" if lifecycle else ""
        )
        self.lifecycle_label.setObjectName("featureLifecycleBadge")
        self.lifecycle_label.setVisible(lifecycle is not None)
        copy.addWidget(self.lifecycle_label)
        self.toggle = QCheckBox(translate("Feature verwenden"))
        self.toggle.setChecked(feature.default_enabled)
        self.toggle.setEnabled(feature.available)
        row.addWidget(icon)
        row.addLayout(copy, 1)
        row.addWidget(self.toggle)
        outer.addLayout(row)
        self.details = QLabel(translate(feature.description))
        self.details.setWordWrap(True)
        self.details.setObjectName("infoText")
        # Reserve the description area permanently.  Hovering may change its
        # opacity, but must never reflow the authority section below it.
        self.details.setFixedHeight(58)
        outer.addWidget(self.details)
        self.details_opacity = QGraphicsOpacityEffect(self.details)
        self.details_opacity.setOpacity(0.0)
        self.details.setGraphicsEffect(self.details_opacity)
        self.animation = QPropertyAnimation(self.details_opacity, b"opacity", self)
        self.animation.setDuration(170)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def refresh_language(self, translate) -> None:
        self.setToolTip(translate(self.feature.description))
        self.title_label.setText(translate(self.feature.title))
        self.status_label.setText(translate(self.feature.availability))
        lifecycle = feature_lifecycle(self.feature.key)
        if lifecycle is not None:
            self.lifecycle_label.setText(f"{translate(lifecycle.stage)} · v{lifecycle.version}")
        self.toggle.setText(translate("Feature verwenden"))
        self.details.setText(translate(self.feature.description))

    def enterEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self.animation.stop()
        self.animation.setStartValue(self.details_opacity.opacity())
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        self.animation.stop()
        self.animation.setStartValue(self.details_opacity.opacity())
        self.animation.setEndValue(0.0)
        self.animation.start()
        super().leaveEvent(event)
