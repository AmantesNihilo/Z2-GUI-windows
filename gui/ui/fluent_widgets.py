from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import QHBoxLayout, QTableWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel as FluentBodyLabel,
    CardWidget,
    ComboBox as FluentComboBox,
    PrimaryPushButton as FluentPrimaryPushButton,
    ProgressBar as FluentProgressBar,
    PushButton as FluentPushButton,
    SearchLineEdit as FluentSearchLineEdit,
    StrongBodyLabel as FluentStrongBodyLabel,
    SubtitleLabel as FluentSubtitleLabel,
    TableWidget as FluentTableWidget,
    TextEdit as FluentTextEdit,
    TitleLabel as FluentTitleLabel,
    isDarkTheme,
)
from qfluentwidgets.components.widgets.menu import MenuAnimationType
from qfluentwidgets.components.widgets.combo_box import ComboBoxMenu


SORT_VALUE_ROLE = 0x0100 + 100


class PushButton(FluentPushButton):
    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if text:
            self.setText(text)


class PrimaryButton(FluentPrimaryPushButton):
    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if text:
            self.setText(text)


class SearchLineEdit(FluentSearchLineEdit):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)


class TextEdit(FluentTextEdit):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)


class ComboBox(FluentComboBox):
    def _createComboMenu(self) -> ComboBoxMenu:
        menu = ComboBoxMenu(self)
        menu.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        menu.view.setViewportMargins(0, 0, 0, 0)
        menu.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        menu.setStyleSheet("ComboBoxMenu, RoundMenu { background: transparent; border: none; }")
        if isDarkTheme():
            menu_bg = "#2b2b2b"
            item_hover = "#3a3a3a"
            text = "#f3f3f3"
        else:
            menu_bg = "#ffffff"
            item_hover = "#f2f2f2"
            text = "#1f1f1f"
        menu.view.setStyleSheet(
            f"""
            QListView#comboListWidget {{
                border: none;
                border-radius: 8px;
                background: {menu_bg};
                padding: 4px;
            }}
            QListView#comboListWidget::item {{
                min-height: 32px;
                padding: 0 12px;
                border-radius: 6px;
                color: {text};
                background: transparent;
            }}
            QListView#comboListWidget::item:selected,
            QListView#comboListWidget::item:hover {{
                background: {item_hover};
            }}
            """
        )
        menu.setShadowEffect(blurRadius=0, offset=(0, 0), color=QColor(0, 0, 0, 0))
        menu.view.setGraphicsEffect(None)
        menu.setWindowFlag(Qt.NoDropShadowWindowHint, True)
        return menu

    def _showComboMenu(self) -> None:
        if not self.items:
            return

        menu = self._createComboMenu()
        for item in self.items:
            action = QAction(item.icon, item.text)
            action.setEnabled(item.isEnabled)
            menu.addAction(action)

        menu.view.itemClicked.connect(lambda i: self._onItemClicked(self.findText(i.text().lstrip())))
        if menu.view.width() < self.width():
            menu.view.setMinimumWidth(self.width())
            menu.adjustSize()

        menu.setMaxVisibleItems(max(len(self.items), self.maxVisibleItems()))
        menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        menu.closedSignal.connect(self._onDropMenuClosed)
        self.dropMenu = menu

        if self.currentIndex() >= 0 and self.items:
            menu.setDefaultAction(menu.actions()[self.currentIndex()])

        x = -menu.width() // 2 + menu.layout().contentsMargins().left() + self.width() // 2
        pos = self.mapToGlobal(QPoint(x, self.height()))
        menu.view.adjustSize(pos, MenuAnimationType.NONE)
        menu.exec(pos, aniType=MenuAnimationType.NONE)


class BodyLabel(FluentBodyLabel):
    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if text:
            self.setText(text)


class StrongBodyLabel(FluentStrongBodyLabel):
    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if text:
            self.setText(text)


class SubtitleLabel(FluentSubtitleLabel):
    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if text:
            self.setText(text)


class TitleLabel(FluentTitleLabel):
    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        if text:
            self.setText(text)


class ProgressBar(FluentProgressBar):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)


class TableWidget(FluentTableWidget):
    def __init__(self, rows: int = 0, columns: int = 0, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setRowCount(rows)
        self.setColumnCount(columns)


class SortableTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other: QTableWidgetItem) -> bool:
        left = self.data(SORT_VALUE_ROLE)
        right = other.data(SORT_VALUE_ROLE)
        if left is not None and right is not None:
            return left < right
        return super().__lt__(other)


class FluentCard(CardWidget):
    def __init__(self, title: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("FluentCard")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(10)
        if title:
            title_label = StrongBodyLabel(title)
            title_label.setObjectName("CardTitle")
            self.layout.addWidget(title_label)


class FluentCommandBar(CardWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CommandBar")


def setting_row(title: str, control: QWidget) -> QWidget:
    row = QWidget()
    row.setObjectName("SettingRow")
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    label = StrongBodyLabel(title)
    label.setObjectName("SectionTitle")
    layout.addWidget(label)
    layout.addStretch(1)
    layout.addWidget(control)
    return row


def panel_card(title: str = "") -> CardWidget:
    card = CardWidget()
    card.setObjectName("Panel")
    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(10)
    if title:
        title_label = StrongBodyLabel(title)
        title_label.setObjectName("CardTitle")
        layout.addWidget(title_label)
    return card
