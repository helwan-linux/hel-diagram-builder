import sys
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QAction, QFileDialog,
    QLabel, QVBoxLayout, QWidget, QMessageBox, QMenu, QComboBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from core.tree_generator import generate_tree_diagram
from core.tree_builder import build_tree_from_file

# Optional: watchdog for live preview
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class FolderWatcher(FileSystemEventHandler):
    def __init__(self, update_callback):
        self.update_callback = update_callback

    def on_any_event(self, event):
        self.update_callback()


class HelDiagramApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("hel-diagram")
        self.setWindowIcon(QIcon("gui/icon.png"))
        self.setGeometry(100, 100, 800, 600)

        self.text_area = QTextEdit()
        self.label = QLabel("Ready.")
        self.current_folder = None
        self.filter_mode = "all"
        self.observer = None

        self.filter_box = QComboBox()
        self.filter_box.addItems(["All", "Folders Only", "Files Only"])
        self.filter_box.currentIndexChanged.connect(self.refresh_folder_view)

        self._setup_menus()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.filter_box)
        layout.addWidget(self.text_area)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _setup_menus(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        open_folder = QAction("Open Folder", self)
        open_folder.triggered.connect(self.select_folder)
        file_menu.addAction(open_folder)

        open_diagram = QAction("Open Diagram File", self)
        open_diagram.triggered.connect(self.open_diagram_file)
        file_menu.addAction(open_diagram)

        save_diagram = QAction("Save Diagram", self)
        save_diagram.triggered.connect(self.save_diagram)
        file_menu.addAction(save_diagram)

        tpl_menu = QMenu("New Project from Template", self)
        file_menu.addMenu(tpl_menu)
        tpl_menu.addAction("Python App", lambda: self.load_template("python"))
        tpl_menu.addAction("Web Project", lambda: self.load_template("web"))
        tpl_menu.addAction("Node.js Starter", lambda: self.load_template("node"))

        build_menu = menu_bar.addMenu("Build")
        build_action = QAction("Build from Diagram...", self)
        build_action.triggered.connect(self.build_from_diagram_file)
        build_menu.addAction(build_action)

        export_menu = menu_bar.addMenu("Export")
        export_html = QAction("Export as HTML", self)
        export_html.triggered.connect(self.export_as_html)
        export_menu.addAction(export_html)

        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("Help", self.show_help)
        help_menu.addAction("About", self.show_about)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.current_folder = folder
            self.refresh_folder_view()
            self.watch_folder(folder)

    def refresh_folder_view(self):
        if not self.current_folder:
            return
        folder_name = os.path.basename(self.current_folder.rstrip("/\\"))
        raw_tree = generate_tree_diagram(self.current_folder)
        lines = raw_tree.splitlines()
        filtered = []

        self.filter_mode = self.filter_box.currentText().lower()

        for line in lines:
            if self.filter_mode == "folders only" and "📄" in line:
                continue
            elif self.filter_mode == "files only" and "📁" in line:
                continue
            filtered.append(line)

        final_tree = f"{folder_name}/\n" + "\n".join(filtered)
        self.text_area.setPlainText(final_tree)
        self.label.setText(f"Tree loaded from: {self.current_folder}")

    def open_diagram_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Diagram File", "", "Text Files (*.txt *.md)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.text_area.setPlainText(f.read())
            self.label.setText(f"Diagram loaded from: {path}")

    def save_diagram(self):
        text = self.text_area.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Warning", "No diagram to save.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Diagram", "diagram.txt", "Text Files (*.txt *.md)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            self.label.setText(f"Diagram saved to: {path}")
            QMessageBox.information(self, "Saved", f"Diagram saved to: {path}")

    def build_from_diagram_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Diagram File", "", "Text Files (*.txt *.md)")
        if not path:
            return
        out_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if out_dir:
            build_tree_from_file(path, out_dir)
            QMessageBox.information(self, "Success", "Structure built successfully!")
            self.label.setText("Structure created from diagram file.")

    def export_as_html(self):
        text = self.text_area.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Warning", "No diagram to export.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export as HTML", "diagram.html", "HTML Files (*.html)")
        if path:
            html = "<html><body><pre style='font-family:monospace;'>\n"
            html += text + "\n</pre></body></html>"
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            self.label.setText(f"Exported HTML: {path}")

    def load_template(self, name):
        templates = {
            "python": "ProjectName/\n├── main.py\n└── requirements.txt",
            "web": "WebApp/\n├── index.html\n├── css/\n│   └── style.css\n└── js/\n    └── app.js",
            "node": "NodeStarter/\n├── app.js\n├── package.json\n└── routes/\n    └── index.js"
        }
        self.text_area.setPlainText(templates.get(name, ""))
        self.label.setText(f"Template loaded: {name}")

    def watch_folder(self, path):
        if not WATCHDOG_AVAILABLE:
            return
        if self.observer:
            self.observer.stop()
        event_handler = FolderWatcher(self.delayed_refresh)
        self.observer = Observer()
        self.observer.schedule(event_handler, path, recursive=True)
        self.observer.start()

    def delayed_refresh(self):
        QTimer.singleShot(500, self.refresh_folder_view)

    def show_help(self):
        QMessageBox.information(self, "Help",
            "• File > Open Folder: generate diagram\n"
            "• Filter options: show folders/files/all\n"
            "• Build > Build from Diagram: create structure\n"
            "• Live Preview active while folder open")

    def show_about(self):
        QMessageBox.information(self, "About",
            "hel-diagram v1.0\n"
            "Helwan Linux Project\n"
            "Live preview · Filters · Templates · Build with contents")

def run_app():
    app = QApplication(sys.argv)

    # Load Helwan Style (QSS)
    style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "helwan_style.qss")
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = HelDiagramApp()
    window.show()
    sys.exit(app.exec_())

