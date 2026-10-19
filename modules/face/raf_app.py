"""
RAF Face App — Stable pyttsx3 version with working presence detection.
"""

import sys
import math
import random
import io
import os
import contextlib
import cv2
import threading
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSlot
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# =========================
# COLORS
# =========================
BG_COLOR = QColor(20, 30, 70)
EYE_COLOR = QColor(0, 245, 225)
MOUTH_COLOR = QColor(0, 245, 225)
GLASSES_COLOR = QColor(0, 245, 225)
GLASSES_LENS = QColor(0, 245, 225, 20)

class RAFFace(QWidget):
    """RAF's face with glasses and natural animations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)

        self.breath_phase = 0.0
        self.expression = "happy"
        self.time = 0.0

        self.micro_offset_x = 0.0
        self.micro_offset_y = 0.0

        # Smooth blink
        self.blink_state = "open"     
        self.blink_progress = 0.0
        self.eye_blink = 0.0

        # Speaking animation
        self.is_speaking = False
        self.speak_timer = 0
        self.word_timer = 0
        self.target_mouth = 0.0
        self.mouth_open = 0.0

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

        # Smooth blink
        speed = 0.10
        if self.blink_state == "closing":
            self.blink_progress += speed
            if self.blink_progress >= 1.0:
                self.blink_progress = 1.0
                self.blink_state = "opening"
            self.eye_blink = math.sin((self.blink_progress * math.pi) / 2)
        elif self.blink_state == "opening":
            self.blink_progress -= speed
            if self.blink_progress <= 0.0:
                self.blink_progress = 0.0
                self.blink_state = "open"
            self.eye_blink = math.sin((self.blink_progress * math.pi) / 2)

        # Speaking (Word-to-Word simulation)
        if self.speak_timer > 0:
            self.speak_timer -= 1
            if self.word_timer <= 0:
                self.target_mouth = random.choice([0.2, 0.6, 1.0])
                self.word_timer = random.randint(5, 10)
            else:
                self.word_timer -= 1
            self.mouth_open += (self.target_mouth - self.mouth_open) * 0.3
        else:
            self.is_speaking = False
            self.mouth_open += (0.0 - self.mouth_open) * 0.15

        self.update()

    def _start_blink(self):
        if self.blink_state == "open":
            self.blink_state = "closing"
            self.blink_progress = 0.0
        self.blink_timer.start(random.randint(2500, 5000))

    def set_expression(self, expression):
        self.expression = expression

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
            eye_rect = QRectF(eye_x - eye_w / 2, eye_y, eye_w, eye_h * eye_squeeze)
            painter.setBrush(QBrush(EYE_COLOR))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(eye_rect, eye_w / 2, eye_w / 2)

        # Glasses (Fixed size — NO squish)
        frame_w = eye_w + 30
        frame_h = eye_h + 30
        frame_y = eye_y - 15

        painter.setBrush(QBrush(GLASSES_LENS))
        painter.setPen(QPen(GLASSES_COLOR, 4))
        for eye_x in [cx - eye_spacing, cx + eye_spacing]:
            frame_rect = QRectF(eye_x - frame_w / 2, frame_y, frame_w, frame_h)
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
                painter.drawRoundedRect(QRectF(mouth_x, mouth_y, mouth_w, mouth_h), mouth_w / 2, mouth_w / 2)
                painter.setBrush(QBrush(BG_COLOR))
                painter.drawRect(QRectF(mouth_x - 3, mouth_y - 3, mouth_w + 6, mouth_h / 2))
            elif self.expression == "curious":
                painter.setBrush(QBrush(MOUTH_COLOR))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(cx, mouth_y + mouth_h / 2), mouth_w * 0.35, mouth_h * 0.5)
            elif self.expression == "thinking":
                painter.setPen(QPen(MOUTH_COLOR, 10))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawLine(int(cx - mouth_w / 2), int(mouth_y + mouth_h / 2), int(cx + mouth_w / 2), int(mouth_y + mouth_h / 2))
            elif self.expression == "sad":
                painter.setBrush(QBrush(MOUTH_COLOR))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRectF(mouth_x, mouth_y - 15, mouth_w, mouth_h), mouth_w / 2, mouth_w / 2)
                painter.setBrush(QBrush(BG_COLOR))
                painter.drawRect(QRectF(mouth_x - 3, mouth_y + mouth_h / 2 - 15, mouth_w + 6, mouth_h / 2 + 15))

class RAFApp(QMainWindow):
    """Main RAF window — stable pyttsx3 version with presence."""

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

        # Presence Detection
        self.last_presence_greet = 0
        self.presence_thread = threading.Thread(target=self._presence_loop, daemon=True)
        self.presence_thread.start()

    def _presence_loop(self):
        try:
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
        except ImportError:
            print("⚠️ MediaPipe not installed.")
            return

        model_path = "data/blaze_face_short_range.tflite"
        if not os.path.exists(model_path):
            import urllib.request
            os.makedirs("data", exist_ok=True)
            print("⬇️ Downloading face detection model...")
            urllib.request.urlretrieve(
                "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite",
                model_path
            )
            print("✅ Model downloaded.")

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceDetectorOptions(base_options=base_options)
        detector = vision.FaceDetector.create_from_options(options)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("⚠️ Webcam not available for presence detection.")
            return

        print("👀 Presence detection started (Tasks API).")

        while True:
            ret, frame = cap.read()
            if ret:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                detection_result = detector.detect(mp_image)

                if detection_result.detections:
                    now = time.time()
                    if now - self.last_presence_greet > 30:
                        self.last_presence_greet = now
                        from PyQt6.QtCore import QMetaObject, Qt
                        QMetaObject.invokeMethod(self, "on_presence_detected", Qt.ConnectionType.QueuedConnection)
            time.sleep(1)

    @pyqtSlot()
    def on_presence_detected(self):
        if not self.face.is_speaking:
            self.face.set_expression("happy")
            greeting = "Hey Aditya! I see you there."
            self.caption.setText(f"RAF: {greeting}")
            self._speak(greeting)

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
        """Speak text in a background thread and animate mouth for the right duration."""
        import threading

        char_count = len(text)
        estimated_seconds = max(1.0, char_count / 15.0)
        
        self.face.speak_timer = int(estimated_seconds * 60)

        def worker():
            try:
                from modules.voice.voice import speak
                speak(text)
            except Exception as e:
                print(f"TTS error: {e}")
            finally:
                self.face.speak_timer = 0
                self.face.is_speaking = False

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