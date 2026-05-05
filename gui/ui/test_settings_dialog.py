from __future__ import annotations

from collections import defaultdict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import CheckBox as FluentCheckBox
from qfluentwidgets import MessageBox

from zapret_core.targets import Target
from ui.fluent_widgets import BodyLabel, PrimaryButton, PushButton, panel_card


RU_TEXT = {
    "Test Settings": "Настройки теста",
    "Choose targets for preset tests": "Выберите цели для проверки пресетов",
    "All": "Все",
    "None": "Ничего",
    "Select group": "Выбрать группу",
    "Save": "Сохранить",
    "Cancel": "Отмена",
    "Select at least one target.": "Выберите хотя бы одну цель.",
}


class TestSettingsDialog(QDialog):
    def __init__(
        self,
        targets: list[Target],
        selected_names: set[str],
        parent=None,
        language: str = "en",
    ) -> None:
        super().__init__(parent)
        self.language = language
        self.setWindowTitle(self.tr_text("Test Settings"))
        self.resize(520, 620)
        self.targets = targets
        self.checkboxes: dict[str, FluentCheckBox] = {}

        active_names = selected_names or {target.name for target in targets}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        title = BodyLabel(self.tr_text("Choose targets for preset tests"))
        title.setStyleSheet("font-size: 14pt; font-weight: 650;")
        layout.addWidget(title)

        quick_row = QHBoxLayout()
        self.all_btn = PushButton(self.tr_text("All"))
        self.discord_btn = PushButton("Discord")
        self.youtube_btn = PushButton("YouTube")
        self.none_btn = PushButton(self.tr_text("None"))
        quick_row.addWidget(self.all_btn)
        quick_row.addWidget(self.discord_btn)
        quick_row.addWidget(self.youtube_btn)
        quick_row.addWidget(self.none_btn)
        quick_row.addStretch(1)
        layout.addLayout(quick_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)

        grouped: dict[str, list[Target]] = defaultdict(list)
        for target in targets:
            grouped[target.category].append(target)

        for category in sorted(grouped, key=str.casefold):
            group = panel_card(category)
            group_layout = group.layout()
            group_check = FluentCheckBox(self.tr_text("Select group"))
            group_check.setTristate(False)
            group_layout.addWidget(group_check)

            child_boxes: list[FluentCheckBox] = []
            for target in grouped[category]:
                label = target.name
                if target.url:
                    label += f"  ({target.url})"
                elif target.ping_target:
                    label += f"  (PING {target.ping_target})"
                checkbox = FluentCheckBox(label)
                checkbox.setChecked(target.name in active_names)
                checkbox.setProperty("target_name", target.name)
                group_layout.addWidget(checkbox)
                self.checkboxes[target.name] = checkbox
                child_boxes.append(checkbox)

            def update_group_state(boxes=child_boxes, group_box=group_check):
                checked_count = sum(1 for box in boxes if box.isChecked())
                group_box.blockSignals(True)
                group_box.setCheckState(
                    Qt.Checked
                    if checked_count == len(boxes)
                    else Qt.Unchecked
                )
                group_box.blockSignals(False)

            def set_group_state(state, boxes=child_boxes):
                checked = state == Qt.Checked.value
                for box in boxes:
                    box.setChecked(checked)

            group_check.stateChanged.connect(set_group_state)
            for checkbox in child_boxes:
                checkbox.stateChanged.connect(update_group_state)
            update_group_state()

            content_layout.addWidget(group)

        content_layout.addStretch(1)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        ok_btn = PrimaryButton(self.tr_text("Save"))
        cancel_btn = PushButton(self.tr_text("Cancel"))
        ok_btn.setMinimumWidth(120)
        cancel_btn.setMinimumWidth(120)
        buttons.addWidget(ok_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        self.all_btn.clicked.connect(lambda: self.set_checked_by_category(None, True))
        self.none_btn.clicked.connect(lambda: self.set_checked_by_category(None, False))
        self.discord_btn.clicked.connect(lambda: self.only_category("Discord"))
        self.youtube_btn.clicked.connect(lambda: self.only_category("YouTube"))

    def selected_target_names(self) -> set[str]:
        return {name for name, checkbox in self.checkboxes.items() if checkbox.isChecked()}

    def tr_text(self, text: str) -> str:
        if self.language == "ru":
            return RU_TEXT.get(text, text)
        return text

    def accept(self) -> None:
        if not self.selected_target_names():
            MessageBox(self.tr_text("Test Settings"), self.tr_text("Select at least one target."), self).exec()
            return
        super().accept()

    def set_checked_by_category(self, category: str | None, checked: bool) -> None:
        for target in self.targets:
            if category is None or target.category.casefold() == category.casefold():
                self.checkboxes[target.name].setChecked(checked)

    def only_category(self, category: str) -> None:
        for target in self.targets:
            self.checkboxes[target.name].setChecked(target.category.casefold() == category.casefold())
