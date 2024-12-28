import sys
import os
import pygetwindow as gw
import pyautogui
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QRect, QEvent
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QSizePolicy
from PyQt5.QtGui import QIcon

script_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(script_dir, "..", "img", "wonder-flower.png")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bubble RNG")
        self.setGeometry(1566, 75, 250, 600)  
        self.setWindowOpacity(0.7)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QIcon(icon_path))
        self.setStyleSheet(""" 
            color: rgb(0, 194, 188);
            background-color: #333333;
            font-size: 18px;
            border: 5px solid #444444;
            border-radius: 10px;  
            padding: 2px 4px;
        """)

        main_groupbox = QGroupBox(self)
        main_groupbox.setStyleSheet(""" 
            QGroupBox {
                border: 2px solid #ffffff; 
                border-radius: 15px;
                padding: 10px;
                background-color: #333333;
            }
        """)

        main_layout = QVBoxLayout()
        title_label = QLabel("Bubble RNG", self)
        title_label.setStyleSheet(""" 
            color: #ffffff;
            background-color: #333333;
            font-size: 16px;
            font-weight: bold;
            border-radius: 5px;
            padding: 5px;
            border: 2px solid #ffffff; 
        """)
        title_label.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(title_label)

        self.sliders = []
        self.labels = []
        self.value_labels = []

        bubble_names = [
            "X phase offset",
            "Y phase offset",
            "Period",
            "Magnitude",
            "X velocity",
            "Y velocity",
            "Alive time"
        ]

        for i in range(7):
            bubble_group = QGroupBox()
            bubble_group.setStyleSheet(""" 
                QGroupBox {
                    border: 2px solid white;
                    border-radius: 10px;
                    padding: 5px;
                    background-color: #444444;
                }
                QGroupBox:title {
                    color: #ffffff;
                    background-color: #333333;
                    font-size: 16px;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)

            bubble_layout = QVBoxLayout()
            bubble_name_layout = QHBoxLayout()
            bubble_name_label = QLabel(bubble_names[i], self)  
            bubble_name_label.setStyleSheet("color: rgb(255, 255, 255); font-size: 16px; font-weight: bold;")
            value_label = QLabel(f"Value: 0.00", self)
            value_label.setStyleSheet("color: rgb(255, 255, 255); font-size: 14px;")
            bubble_name_layout.addWidget(bubble_name_label)
            bubble_name_layout.addWidget(value_label)
            slider = QSlider(Qt.Horizontal)  
            slider.setRange(0, 100)  
            slider.setTickPosition(QSlider.TicksBelow) 
            slider.setTickInterval(1) 
            slider.setStyleSheet(""" 
                    QSlider::handle:horizontal {
                        background-color: #ffffff;
                        width: 12px;  
                        height: 25px;   
                        margin-top: -12px;  
                        margin-bottom: -12px;
                    } 
                    QSlider::groove:horizontal {
                        border: 1px solid #ffffff; 
                        background: rgba(255, 255, 255, 150); 
                        height: 10px; 
                    }
                """)

            slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            slider.setFixedHeight(25)  
            slider.valueChanged.connect(lambda value, label=value_label: label.setText(f"Value: {value/100:.2f}"))
            slider.sliderReleased.connect(lambda i=i, slider=slider: self.send_to_cmd(i, slider.value() / 100.0))  

            bubble_layout.addLayout(bubble_name_layout)  
            bubble_layout.addWidget(slider) 
            bubble_group.setLayout(bubble_layout)
            main_layout.addWidget(bubble_group)

            self.sliders.append(slider)
            self.labels.append(bubble_names[i])  
            self.value_labels.append(value_label)

        main_groupbox.setLayout(main_layout)

        instruction_label = QLabel("You have to click on the slider for it to work", self)
        instruction_label.setStyleSheet("""
            color: rgb(255, 255, 255);
            font-size: 14px;
            border: 2px solid #ffffff; 
            text-align: center;
            padding: 10px;
            font-weight: bold;
        """)
        instruction_label.setAlignment(Qt.AlignCenter)

        window_layout = QVBoxLayout()
        window_layout.addWidget(main_groupbox)
        window_layout.addWidget(instruction_label)  
        self.setLayout(window_layout)

    def send_to_cmd(self, bubble_index, value):
        cmd_text = f"bubbleRNG {bubble_index + 1} {value:.2f}"
        self.execute_cmd(cmd_text)

    def execute_cmd(self, cmd_text):
        cmd_window = None
        for window in gw.getWindowsWithTitle("C:\\Program Files\\Python312\\python.exe"):
            cmd_window = window
            break

        if cmd_window:
            cmd_window.activate()  
            pyautogui.write(cmd_text)  
            pyautogui.press('enter')  
            cmd_window.minimize()  


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
