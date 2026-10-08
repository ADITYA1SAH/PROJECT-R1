"""
RAF Face App — connected to brain
"""

import sys
import math
import random
import io
import os
import contextlib

# Add project root to path so we can import `core` and `modules`
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush


# =========================
# COLORS
# =========================
BG_COLOR = QColor(20, 30, 70)
EYE_COLOR = QColor(0, 245, 225)
MOUTH_COLOR = QColor(0, 245, 225)
GLASSES_COLOR = QColor(0, 245, 225)
GLASSES_LENS = QColor(0, 245, 225, 20)


class RAFFace(QWidget):
    """RAF's face with smooth blink + talking animation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)

        self.breath_phase = 0.0
        self.expression = "happy"
        self.time = 0.0

        self.micro_offset_x = 0.0
        self.micro_offset_y = 0.0

        # Blink (smooth eased)
        self.blink_state = "open"     # "open", "closing", "opening"
        self.blink_progress = 0.0
        self.eye_blink = 0.0

        # Speaking animation
        self.is_speaking = False
        self.mouth_open = 0.0
        self.mouth_phase = 0.0

        # Timers
        self.timer = QTimer()
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)

        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._start_blink)
        self.blink_timer.start(random.randint(2500, 5000))

    def _animate(self):
        self.time += 0.016
        self.breath_phase += 0.03
        if self.breath_phase > math.tau:
            self.breath_phase -= math.tau

        self.micro_offset_x = math.sin(self.time * 3.7) * 0.8
        self.micro_offset_y = math.cos(self.time * 2.3) * 0.8

        # Smooth blink (eased)
        speed = 0.08

        if self.blink_state == "closing":
            self.blink_progress += speed
            if self.blink_progress >= 1.0:
                self.blink_progress = 1.0
                self.blink_state = "opening"
            eased = 1 - (1 - self.blink_progress) ** 2
            self.eye_blink = eased

        elif self.blink_state == "opening":
            self.blink_progress -= speed
            if self.blink_progress <= 0.0:
                self.blink_progress = 0.0
                self.blink_state = "open"
            eased = self.blink_progress ** 1.5
            self.eye_blink = eased

        # Speaking → mouth moves
        if self.is_speaking:
            self.mouth_phase += 0.35
            raw = (math.sin(self.mouth_phase) + math.sin(self.mouth_phase * 1.7)) / 2
            self.mouth_open = (raw + 1) / 2
        else:
            self.mouth_open += (0.0 - self.mouth_open) * 0.15

        self.update()

    def _start_blink(self):
        if self.blink_state == "open":
            self.blink_state = "closing"
            self.blink_progress = 0.0
        self.blink_timer.start(random.randint(2500, 5000))

    def set_expression(self, expression):
        self.expression = expression

    def set_speaking(self, speaking):
        self.is_speaking = speaking

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        painter.fillRect(self.rect(), BG_COLOR)

        cx = self.width() / 2 + self.micro_offset_x
        cy = self.height() / 2 + self.micro_offset_y
        breath = 1.0 + math.sin(self.breath_phase) * 0.02

        # Eyes
        eye_w = self.width() * 0.07
        eye_h = self.height() * 0.30 * breath
        eye_y = cy - eye_h - 20
        eye_spacing = self.width() * 0.18
        eye_squeeze = 1.0 - self.eye_blink

        for eye_x in [cx - eye_spacing, cx + eye_spacing]:
            painter.setBrush(QBrush(QColor(0, 245, 225, 40)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(
                QRectF(eye_x - eye_w, eye_y - 10, eye_w * 2, eye_h * eye_squeeze + 20),
                eye_w, eye_w
            )
            eye_rect = QRectF(eye_x - eye_w / 2, eye_y, eye_w, eye_h * eye_squeeze)
            painter.setBrush(QBrush(EYE_COLOR))
            painter.drawRoundedRect(eye_rect, eye_w / 2, eye_w / 2)

        # Glasses
        frame_w = eye_w + 30
        frame_h = eye_h + 30
        frame_y = eye_y - 15

        painter.setBrush(QBrush(GLASSES_LENS))
        painter.setPen(QPen(GLASSES_COLOR, 4))
        for eye_x in [cx - eye_spacing, cx + eye_spacing]:
            frame_rect = QRectF(eye_x - frame_w / 2, frame_y, frame_w, frame_h * eye_squeeze)
            painter.drawRoundedRect(frame_rect, 15, 15)

        bridge_y = frame_y + frame_h / 2
        painter.setPen(QPen(GLASSES_COLOR, 4))
        painter.drawLine(
            int(cx - eye_spacing + frame_w / 2), int(bridge_y),
            int(cx + eye_spacing - frame_w / 2), int(bridge_y)
        )
        painter.drawLine(
            int(cx - eye_spacing - frame_w / 2), int(bridge_y),
            int(cx - eye_spacing - frame_w / 2 - 30), int(bridge_y - 5)
        )
        painter.drawLine(
            int(cx + eye_spacing + frame_w / 2), int(bridge_y),
            int(cx + eye_spacing + frame_w / 2 + 30), int(bridge_y - 5)
        )

        # Mouth
        mouth_w = self.width() * 0.22
        mouth_h_base = self.height() * 0.10
        mouth_x = cx - mouth_w / 2
        mouth_y = cy + 40

        if self.is_speaking or self.mouth_open > 0.05:
            # Open oval mouth (talking)
            open_h = mouth_h_base * (0.4 + self.mouth_open * 1.2)
            painter.setBrush(QBrush(MOUTH_COLOR))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                QPointF(cx, mouth_y + mouth_h_base / 2),
                mouth_w * 0.5,
                open_h
            )
        else:
            mouth_h = self.height() * 0.18

            if self.expression == "happy":
                painter.setBrush(QBrush(MOUTH_COLOR))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(
                    QRectF(mouth_x, mouth_y, mouth_w, mouth_h),
                    mouth_w / 2, mouth_w / 2
                )
                painter.setBrush(QBrush(BG_COLOR))
                painter.drawRect(QRectF(mouth_x - 3, mouth_y - 3, mouth_w + 6, mouth_h / 2))

            elif self.expression == "curious":
                painter.setBrush(QBrush(MOUTH_COLOR))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(
                    QPointF(cx, mouth_y + mouth_h / 2),
                    mouth_w * 0.35,
                    mouth_h * 0.5
                )

            elif self.expression == "thinking":
                painter.setPen(QPen(MOUTH_COLOR, 10))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawLine(
                    int(cx - mouth_w / 2), int(mouth_y + mouth_h / 2),
                    int(cx + mouth_w / 2), int(mouth_y + mouth_h / 2)
                )

            elif self.expression == "sad":
                painter.setBrush(QBrush(MOUTH_COLOR))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(
                    QRectF(mouth_x, mouth_y - 15, mouth_w, mouth_h),
                    mouth_w / 2, mouth_w / 2
                )
                painter.setBrush(QBrush(BG_COLOR))
                painter.drawRect(QRectF(
                    mouth_x - 3,
                    mouth_y + mouth_h / 2 - 15,
                    mouth_w + 6,
                    mouth_h / 2 + 15
                ))


class RAFApp(QMainWindow):
    """Main RAF window — connected to brain."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RAF — Revolutionary Artificial Friend")
        self.setGeometry(100, 100, 700, 900)
        self.setStyleSheet("background-color: #141e46;")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("RAF")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #00F5E1; font-size: 28px; font-weight: bold;")
        layout.addWidget(title)

        self.face = RAFFace()
        layout.addWidget(self.face, stretch=1)

        self.caption = QLabel("Hey Aditya! I'm RAF.")
        self.caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.caption.setStyleSheet("color: #ffffff; font-size: 16px; padding: 12px;")
        self.caption.setWordWrap(True)
        layout.addWidget(self.caption)

        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Type a message...")
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #16213e;
                color: #ffffff;
                border: 2px solid #0f3460;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #00F5E1; }
        """)
        self.input.returnPressed.connect(self.send_message)

        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #00F5E1; color: #000000;
                border: none; border-radius: 10px;
                padding: 10px 20px; font-weight: bold;
            }
            QPushButton:hover { background-color: #00c4b8; }
        """)
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)

        bottom = QHBoxLayout()

        history_btn = QPushButton("📜 History")
        history_btn.setStyleSheet(self._btn_style())
        history_btn.clicked.connect(self.show_history)
        bottom.addWidget(history_btn)

        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setStyleSheet(self._btn_style())
        settings_btn.clicked.connect(self.show_settings)
        bottom.addWidget(settings_btn)

        mode_btn = QPushButton("🌐 Mode")
        mode_btn.setStyleSheet(self._btn_style())
        mode_btn.clicked.connect(self.switch_mode)
        bottom.addWidget(mode_btn)

        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setStyleSheet(self._btn_style())
        clear_btn.clicked.connect(self.clear_chat)
        bottom.addWidget(clear_btn)

        layout.addLayout(bottom)

    def _btn_style(self):
        return """
            QPushButton {
                background-color: #16213e;
                color: #a0a0a0;
                border: 1px solid #0f3460;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0f3460;
                color: #00F5E1;
            }
        """

    def send_message(self):
        text = self.input.text().strip()
        if not text:
            return

        self.caption.setText(f"You: {text}")
        self.input.clear()

        self.face.set_expression("thinking")
        QApplication.processEvents()

        try:
            response = self._process_with_raf(text)
        except Exception as e:
            response = f"(brain error: {e})"

        if response:
            self.caption.setText(f"RAF: {response}")
            try:
                self.face.set_expression(self._detect_expression(response))
            except Exception:
                self.face.set_expression("happy")
            try:
                self._speak(response)
            except Exception as e:
                print(f"Speak error: {e}")
        else:
            self.caption.setText("RAF: (no response)")

    def _process_with_raf(self, text):
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                from core.brain import process_command
                process_command(text)
        except Exception as e:
            return f"(error: {e})"

        output = buffer.getvalue().strip()

        if "RAF:" in output:
            response = output.split("RAF:")[-1].strip()
        else:
            response = output.strip()

        lines = [
            l for l in response.split("\n")
            if not l.strip().startswith(("🔍", "⚠️", "⚡", "[PostHog]", "100%", "0%"))
        ]
        response = " ".join(lines).strip()

        if "🔧" in response:
            response = response.split("🔧")[-1].strip()

        return response

    def _detect_expression(self, response):
        r = response.lower()
        if any(w in r for w in ["sorry", "sad", "unfortunately"]):
            return "sad"
        if any(w in r for w in ["hmm", "thinking", "let me"]):
            return "thinking"
        if any(w in r for w in ["interesting", "curious", "wow"]):
            return "curious"
        return "happy"

    def _speak(self, text):
        """Speak text in a background thread so UI stays responsive."""
        import threading

        def worker():
            try:
                self.face.set_speaking(True)
                from modules.voice.voice import speak
                speak(text)
            except Exception as e:
                print(f"TTS error: {e}")
            finally:
                self.face.set_speaking(False)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def show_history(self):
        try:
            from modules.conversation.context import get_recent_history
            history = get_recent_history(10)
            if not history:
                self.caption.setText("No conversation history yet.")
                return
            lines = []
            for msg in history[-5:]:
                role = msg.get("role", "?")
                content = msg.get("content", "")[:60]
                lines.append(f"{role}: {content}")
            self.caption.setText("\n".join(lines))
        except Exception as e:
            self.caption.setText(f"History error: {e}")

    def show_settings(self):
        try:
            from modules.modes.mode import get_mode_config
            mode = get_mode_config()
            self.caption.setText(f"Mode: {mode['name']} | Settings coming soon")
        except Exception:
            self.caption.setText("Settings coming soon")

    def switch_mode(self):
        try:
            from modules.modes.mode import get_mode_config, set_mode
            current = get_mode_config()["name"].lower().replace(" mode", "")
            modes = ["normal", "professional", "idle", "emergency"]
            idx = (modes.index(current) + 1) % len(modes)
            new_mode = modes[idx]
            set_mode(new_mode)
            self.caption.setText(f"Mode switched to: {new_mode.title()}")
        except Exception as e:
            self.caption.setText(f"Mode error: {e}")

    def clear_chat(self):
        self.caption.setText("Cleared. Ready for new chat.")


def main():
    app = QApplication(sys.argv)
    window = RAFApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()