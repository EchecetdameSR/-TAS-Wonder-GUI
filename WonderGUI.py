import pyautogui
import os
import sys
import json
import pygetwindow as gw
import pyperclip
import time
import keyboard  # Import de la bibliothèque pour gérer le Caps Lock
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QListWidget, QDialog, QLineEdit, QFormLayout, QDialogButtonBox
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


class EditBubbleRNGDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Edit Bubble RNG")
        self.setGeometry(100, 100, 300, 150)

        self.layout = QFormLayout(self)
        self.x_input = QLineEdit(self)
        self.y_input = QLineEdit(self)
        self.layout.addRow("X Value:", self.x_input)
        self.layout.addRow("Y Value:", self.y_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_values(self):
        return self.x_input.text(), self.y_input.text()


class BubbleRNGPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(1700, 20, 200, 40)  # Positionné en haut à droite
        self.setWindowTitle("Bubble RNG")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # Reste toujours en haut
        
        self.setStyleSheet(""" 
            color: rgb(0, 194, 188);
            background-color: #333333;
            font-size: 25px;
            border: 1px solid #444444;
            border-radius:  0px;  # Coins arrondis
            padding: 2px 4px;
        """)
        self.label = QLabel("Bubble RNG: X = ? | Y = ?", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, 200, 40)
        # Appliquer des coins arrondis également au label
        self.label.setStyleSheet(""" 
            background-color: #333333;
            color: rgb(0, 194, 188);
            font-size: 14px;
            border-radius: 0px;
        """)

    def update_values(self, x, y):
        self.label.setText(f"Bubble RNG: X = {x} | Y = {y}")


class CustomWindow(QMainWindow):
    SETTINGS_FILE = ""

    def __init__(self):
        super().__init__()

        self.load_settings()

        self.setWindowTitle("")
        self.setWindowOpacity(1)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setGeometry(15, 555, 400, 100)
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

        # Variables pour Bubble RNG
        self.x_value = None
        self.y_value = None

        # Bubble RNG Page (visible tout le temps)
        self.bubble_rng_page = BubbleRNGPage()
        self.bubble_rng_page.show()

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

        # Ajouter le bouton "Edit Bubble RNG" sous les autres boutons
        edit_rng_button = QPushButton("Edit Bubble RNG")
        edit_rng_button.setStyleSheet("background-color: rgb(0, 194, 188); color: #E5E5E5; font-size: 14px; font-weight: normal; border: 1px solid #444444; border-radius: 5px; padding: 8px 16px;")
        edit_rng_button.clicked.connect(self.open_rng_dialog)
        buttons_layout.addWidget(edit_rng_button)


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

    def open_rng_dialog(self):
        dialog = EditBubbleRNGDialog()
        if dialog.exec_() == QDialog.Accepted:
            x_value, y_value = dialog.get_values()
            try:
                # Essayer de convertir les valeurs en float
                x_value = int(x_value)
                y_value = float(y_value)
                self.x_value = x_value
                self.y_value = y_value
                self.bubble_rng_page.update_values(self.x_value, self.y_value)
                
                # Exécuter la commande "bubbleRNG X Y" dans CMD
                self.execute_cmd_command(f"bubbleRNG {x_value} {y_value}")
            except ValueError:
                self.current_frame_output.setText("Invalid values entered")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomWindow()
    window.show()
    sys.exit(app.exec_())
