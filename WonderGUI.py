import pyautogui
import os
import sys
import json
import pygetwindow as gw
import pyperclip
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QListWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class DirectoryWatcher(QThread):
    directory_changed = pyqtSignal()

    def __init__(self, directory):
        super().__init__()
        self.directory = directory
        self.observer = Observer()

    def run(self):
        event_handler = FileSystemEventHandler()
        event_handler.on_modified = self.on_change
        event_handler.on_created = self.on_change
        event_handler.on_deleted = self.on_change

        self.observer.schedule(event_handler, self.directory, recursive=False)
        self.observer.start()
        self.exec_()  # Maintient le thread actif

    def on_change(self, event):
        self.directory_changed.emit()

    def stop(self):
        self.observer.stop()
        self.observer.join()


class CustomWindow(QMainWindow):
    SETTINGS_FILE = "settings.json"

    def __init__(self):
        super().__init__()

        self.load_settings()

        self.setWindowTitle("Wonder - TAS GUI")
        self.setWindowOpacity(1)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setGeometry(30, 580, 400, 300)
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgba(18, 18, 18, 200);
                border-radius: 8px;
                box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.5);
            }
            QLabel {
                color: #E5E5E5;
                font-size: 13px;
                font-family: 'Helvetica Neue', sans-serif;
                padding: 5px;
            }
            QPushButton {
                background-color: #333333;
                color: #E5E5E5;
                font-size: 13px;
                font-weight: normal;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 6px 12px;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QListWidget {
                background-color: #222222;
                color: #E5E5E5;
                border: 1px solid #444444;
                border-radius: 10px;
                padding: 8px;
                font-size: 13px;
                transition: all 0.3s ease;
            }
            QListWidget::item {
                padding: 2px;
                margin-bottom: 10px;
                border-radius: 8px;
                background-color: #333333;
                transition: background-color 0.2s;
            }
            QListWidget::item:hover {
                background-color: #444444;
            }
            QListWidget::item:selected {
                background-color: #555555;
            }
        """)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        self.add_header(main_layout)
        self.add_buttons(main_layout)
        self.add_scripts_list(main_layout)

        self.current_frame_output = QLabel("No Previous Line found")
        self.current_frame_output.setStyleSheet("""
        background-color: #333333;
        padding: 5px;
        border-radius: 8px;
        color: #E5E5E5;
        border: 1px solid #444444;
        """)
        main_layout.addWidget(self.current_frame_output)

        # Début de l'observation
        self.directory_to_watch = os.path.dirname(os.path.realpath(__file__))
        self.directory_watcher = DirectoryWatcher(self.directory_to_watch)
        self.directory_watcher.directory_changed.connect(self.refresh_scripts_list)
        self.directory_watcher.start()

    def add_header(self, layout):
        header_container = QWidget()
        header_layout = QHBoxLayout()
        header_container.setLayout(header_layout)

        title_label = QLabel("")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #E5E5E5;
            padding: 2px;
            text-align: center;
            margin-top: 20px;
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()
        layout.addWidget(header_container)

    def add_buttons(self, layout):
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_container.setLayout(buttons_layout)

        run_button = QPushButton("Run")
        run_button.setStyleSheet(self.button_style())
        run_button.clicked.connect(self.run_script)
        buttons_layout.addWidget(run_button)

        stop_button = QPushButton("Stop")
        stop_button.setStyleSheet(self.button_style("#FF6B6B"))
        stop_button.clicked.connect(self.stop_script)
        buttons_layout.addWidget(stop_button)

        pause_button = QPushButton("Pause")
        pause_button.setStyleSheet(self.button_style("#666666"))
        pause_button.clicked.connect(self.pause_game)
        buttons_layout.addWidget(pause_button)

        frames_buttons_row = QWidget()
        frames_buttons_layout = QHBoxLayout()
        frames_buttons_row.setLayout(frames_buttons_layout)
        frames_buttons_layout.setSpacing(15)

        plus_15_button = QPushButton("+15 Frames")
        plus_15_button.setStyleSheet(self.button_style("#FF6600"))
        plus_15_button.clicked.connect(self.plus_fifteen_frames)
        frames_buttons_layout.addWidget(plus_15_button)

        plus_1_button = QPushButton("+1 Frame")
        plus_1_button.setStyleSheet(self.button_style("#FF6600"))
        plus_1_button.clicked.connect(self.plus_one_frame)
        frames_buttons_layout.addWidget(plus_1_button)

        current_frame_button = QPushButton("Current Frame")
        current_frame_button.setStyleSheet(self.button_style("#FF6600"))
        current_frame_button.clicked.connect(self.show_previous_lines)
        frames_buttons_layout.addWidget(current_frame_button)

        buttons_layout.addWidget(frames_buttons_row)

        layout.addWidget(buttons_container)

    def add_scripts_list(self, layout):
        scripts_section = QWidget()
        scripts_layout = QVBoxLayout()
        scripts_section.setLayout(scripts_layout)

        self.scripts_list = QListWidget()
        self.scripts_list.itemClicked.connect(self.display_selected_file)
        scripts_layout.addWidget(self.scripts_list)

        self.load_scripts()

        self.selected_file_label = QLabel("No file selected")
        self.selected_file_label.setStyleSheet("""
            background-color: #333333;
            padding: 5px;
            border-radius: 8px;
            color: #E5E5E5;
        """)
        scripts_layout.addWidget(self.selected_file_label)

        layout.addWidget(scripts_section)

    def button_style(self, color="#333333"):
        return f"""
            QPushButton {{
            background-color: {color};
            color: #E5E5E5;
            font-size: 14px;
            font-weight: normal;
            border: 1px solid #444444;
            border-radius: 5px;
            padding: 8px 16px;
        }}
        QPushButton:hover {{
            background-color: #444444;
        }}
        QPushButton:pressed {{
            background-color: #555555;
        }}
    """

    def load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            with open(self.SETTINGS_FILE, "r") as f:
                self.settings = json.load(f)
        else:
            self.settings = {}

    def save_settings(self):
        with open(self.SETTINGS_FILE, "w") as f:
            json.dump(self.settings, f, indent=4)

    def load_scripts(self):
        self.scripts_list.clear()
        scripts_folder = os.path.dirname(os.path.realpath(__file__))
        for file_name in os.listdir(scripts_folder):
            if file_name.endswith(".stas"):
                self.scripts_list.addItem(file_name)

    def refresh_scripts_list(self):
        self.load_scripts()

    def display_selected_file(self, item):
        self.selected_file_label.setText(f"Selected file: {item.text()}")

    def run_script(self):
        selected_item = self.scripts_list.currentItem()
        if selected_item:
            file_name = selected_item.text()
            command = f"start {file_name}"
            self.execute_cmd_command(command)

    def stop_script(self):
        self.execute_cmd_command("stop")

    def pause_game(self):
        self.execute_cmd_command("t")

    def plus_one_frame(self):
        self.execute_cmd_command("a")

    def plus_fifteen_frames(self):
        self.execute_cmd_command("a 15")

    def execute_cmd_command(self, command):
        cmd_window = None
        for window in gw.getWindowsWithTitle("C:\\Windows\\system32\\cmd.exe"):
            cmd_window = window
            break

        if cmd_window:
            cmd_window.activate()
            pyautogui.write(command)
            pyautogui.press('enter')
            cmd_window.minimize()
            pyautogui.hotkey('alt', 'tab')

    def show_previous_lines(self):
        cmd_window = None
        for window in gw.getWindowsWithTitle("C:\\Windows\\system32\\cmd.exe"):
            cmd_window = window
            break

        if cmd_window:
            cmd_window.activate()
            pyautogui.write('f')
            pyautogui.press('enter')

            time.sleep(0.5)

            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')
            cmd_window.minimize()
            pyautogui.hotkey('alt', 'tab')

            copied_text = self.get_output_text()

            lines = copied_text.splitlines()
            if len(lines) >= 2:
                self.current_frame_output.setText(lines[-2])
            else:
                self.current_frame_output.setText("Not enough lines found")

    def get_output_text(self):
        return pyperclip.paste()

    def closeEvent(self, event):
        self.directory_watcher.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomWindow()
    window.show()
    sys.exit(app.exec_())
