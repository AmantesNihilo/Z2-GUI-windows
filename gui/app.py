from __future__ import annotations

import sys
from pathlib import Path

from zapret_core.paths import AppPaths


def add_tg_ws_vendor_path(paths: AppPaths) -> None:
    vendor_path = paths.root / "vendor" / "tg-ws-proxy-src"
    if vendor_path.exists() and str(vendor_path) not in sys.path:
        sys.path.insert(0, str(vendor_path))


def run_tg_ws_proxy_helper(paths: AppPaths) -> int:
    add_tg_ws_vendor_path(paths)
    from proxy.tg_ws_proxy import main as tg_ws_main

    tg_ws_main()
    return 0


def main() -> int:
    paths = AppPaths.from_app_file(Path(__file__))
    if "--z2-tg-ws-proxy" in sys.argv:
        sys.argv.remove("--z2-tg-ws-proxy")
        return run_tg_ws_proxy_helper(paths)

    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("Z2 GUI")
    app.setOrganizationName("Zapret2")

    icon_path = paths.root / "gui" / "ui" / "assets" / "Z2.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow(paths)
    window.resize(1180, 660)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
