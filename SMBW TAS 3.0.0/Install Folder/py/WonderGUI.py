import shutil
import pexpect
import pyautogui
import os
import sys
import pygetwindow as gw
import pyperclip
import time
import subprocess
import ctypes
import keyboard
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QListWidget, QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QKeyEvent

# Path configuration for icons and scripts
script_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(script_dir, "..", "img", "wonder-flower.png")

# Directory watcher thread
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
        self.exec_()  

    def on_change(self, event):
        self.directory_changed.emit()

    def stop(self):
        self.observer.stop()
        self.observer.join()

class PlayerInfoPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(770, 20, 1130, 50) 
        self.setWindowTitle("SMBW TAS - Player Information")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowOpacity(0.7)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet(""" 
            color: rgb(0, 194, 188);
            background-color: #333333;
            font-size: 18px;
            border-radius: 10px;  
            padding: 2px 4px;
        """)

        self.playerInfo_output = QLabel("Player Info will be shown here", self)
        self.playerInfo_output.setAlignment(Qt.AlignCenter)
        self.playerInfo_output.setGeometry(0, 0, 1130, 45)  
        self.playerInfo_output.setStyleSheet(""" 
            background-color: #444444;
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            border-radius: 10px;  
            border: 2px solid white;
            padding: 10px;
        """)

    def update_player_info(self, player_info):
        self.playerInfo_output.setText(player_info)

class CustomWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SMBW TAS - Main")
        self.playerInfoPage = PlayerInfoPage()
        self.playerInfoPage.show()

        self.setWindowOpacity(0.7)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(15, 615, 400, 100)

        self.scripts_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'Scripts')
        print(f"Chemin des scripts: {self.scripts_folder}")

        self.initial_values = {i: "0" for i in range(1, 9)}

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        container = QWidget()
        container.setStyleSheet(""" 
            background-color: #333333;
            border: none; 
            border-radius: 30px;
            padding: 1px;
        """)
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)

        self.add_buttons(container_layout)
        self.add_scripts_list(container_layout)

        current_frame_container = QWidget()
        current_frame_container.setStyleSheet(""" 
            background-color: #333333;
            padding: 10px;
            border: none;
        """)

        self.current_frame_output = QLabel("No Previous Line found")
        self.current_frame_output.setStyleSheet(""" 
            background-color: #333333;
            padding: 5px;
            border-radius: 8px;
            color: #E5E5E5;
            border: 1px solid white;
        """)

        current_frame_container_layout = QVBoxLayout()
        current_frame_container_layout.addWidget(self.current_frame_output)
        current_frame_container.setLayout(current_frame_container_layout)

        container_layout.addWidget(current_frame_container)
        main_layout.addWidget(container)

        self.load_scripts()

        self.directory_watcher = DirectoryWatcher(self.scripts_folder)
        self.directory_watcher.directory_changed.connect(self.refresh_scripts_list)
        self.directory_watcher.start()

    def add_buttons(self, layout):
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_container.setLayout(buttons_layout)

        run_button = QPushButton("Run Script")
        run_button.setStyleSheet(self.button_style())
        run_button.clicked.connect(self.run_script)
        buttons_layout.addWidget(run_button)

        stop_button = QPushButton("Stop Script")
        stop_button.setStyleSheet(self.button_style())
        stop_button.clicked.connect(self.stop_script)
        buttons_layout.addWidget(stop_button)

        pause_button = QPushButton("Pause Game")
        pause_button.setStyleSheet(self.button_style())
        pause_button.clicked.connect(self.pause_game)
        buttons_layout.addWidget(pause_button)

        playerInfo_button = QPushButton("Player Information")
        playerInfo_button.setStyleSheet(self.button_style())
        playerInfo_button.clicked.connect(self.show_playerInfo)
        buttons_layout.addWidget(playerInfo_button)

        frames_buttons_row = QWidget()
        frames_buttons_layout = QHBoxLayout()
        frames_buttons_row.setLayout(frames_buttons_layout)

        plus_15_button = QPushButton("+15 Frames")
        plus_15_button.setStyleSheet(self.button_style())
        plus_15_button.clicked.connect(self.plus_fifteen_frames)
        frames_buttons_layout.addWidget(plus_15_button)

        plus_1_button = QPushButton("+1 Frame")
        plus_1_button.setStyleSheet(self.button_style())
        plus_1_button.clicked.connect(self.plus_one_frame)
        frames_buttons_layout.addWidget(plus_1_button)

        current_frame_button = QPushButton("Current Frame")
        current_frame_button.setStyleSheet(self.button_style())
        current_frame_button.clicked.connect(self.show_previous_lines)
        frames_buttons_layout.addWidget(current_frame_button)

        buttons_layout.addWidget(frames_buttons_row)

        layout.addWidget(buttons_container)

    def add_scripts_list(self, layout):
        scripts_section = QWidget()
        scripts_section.setStyleSheet(""" 
            background-color: #333333;
            border: none;
            border-radius: 8px;
            padding: 10px;
        """)
        scripts_layout = QVBoxLayout()
        scripts_section.setLayout(scripts_layout)

        self.scripts_list = QListWidget()
        self.scripts_list.setStyleSheet(""" 
            background-color: #222222;
            color: #E5E5E5;
            border-radius: 10px;
            padding: 8px;
            font-size: 13px;
            border: 1px solid white;
        """)
        scripts_layout.addWidget(self.scripts_list)
        layout.addWidget(scripts_section)

    def load_scripts(self):
        self.scripts_list.clear()
        try:
            for file_name in os.listdir(self.scripts_folder):
                if file_name.endswith(".stas"):
                    self.scripts_list.addItem(file_name)
        except FileNotFoundError:
            print("Le dossier des scripts n'a pas été trouvé.")

    def refresh_scripts_list(self):
        self.load_scripts()

    def show_playerInfo(self):

        self.execute_cmd_command('p')

        copied_text = self.get_output_text()
        lines = copied_text.splitlines()

        if len(lines) >= 2:
            player_info = lines[-2]  
            self.playerInfoPage.update_player_info(player_info)
        else:

            self.playerInfoPage.update_player_info("Not enough Player Information")

    def show_previous_lines(self):
        self.execute_cmd_command('f')

        copied_text = self.get_output_text()
        lines = copied_text.splitlines()

        if len(lines) >= 2:
            self.current_frame_output.setText(lines[-2])
        else:

            self.current_frame_output.setText("Not enough lines found")

    def run_script(self):
        selected_item = self.scripts_list.currentItem()
        if selected_item:

            selected_item_text = selected_item.text()
            file_name = selected_item.text()
            source_file = os.path.join(self.scripts_folder, file_name)
            destination_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)

            try:
                shutil.copy(source_file, destination_file)
                print(f"Fichier copié : {destination_file}")
            except Exception as e:
                print(f"Erreur lors de la copie du fichier : {e}")
                return

            command = f"start {file_name}"  
            self.execute_cmd_command(command)

            try:
                if os.path.exists(destination_file):
                    os.remove(destination_file)
                    print(f"Fichier supprimé : {destination_file}")
            except Exception as e:
                print(f"Erreur lors de la suppression du fichier : {e}")

            for index in range(self.scripts_list.count()):
                item = self.scripts_list.item(index)
                if item.text() == selected_item_text:
                    self.scripts_list.setCurrentItem(item)
                    break

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
        for window in gw.getWindowsWithTitle("C:\\Program Files\\Python312\\python.exe"):
            cmd_window = window
            break

        if cmd_window:
            cmd_window.activate()
            pyautogui.write(command)
            pyautogui.press('enter')
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.hotkey('ctrl', 'c')
            cmd_window.minimize()
            pyautogui.hotkey('alt', 'tab')

    def get_output_text(self):
        return pyperclip.paste()

    def button_style(self):
        return """
            QPushButton {
                color: #ffffff;
                background-color: #333333;
                font-size: 16px;
                border-radius: 5px;
                padding: 8px;
                border: 2px solid white;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomWindow()
    window.show()
    sys.exit(app.exec_())
