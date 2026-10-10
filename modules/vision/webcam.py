"""
Webcam detection for PROJECT R1
Phase 8.3 — Detects cameras, handles permissions, captures frames
"""

import cv2
import os

# Permission file — remembers which cameras user allowed
PERMISSION_FILE = "data/webcam_permissions.txt"


def list_cameras(max_check=5):
    """
    Detect available cameras on the system.
    Returns a list of camera indices that work.
    """
    available = []
    for i in range(max_check):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available.append(i)
            cap.release()
    return available


def get_camera_info(index):
    """
    Get basic info about a camera.
    """
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(index)
    if not cap.isOpened():
        return None
    info = {
        "index": index,
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": int(cap.get(cv2.CAP_PROP_FPS)),
    }
    cap.release()
    return info


def load_permissions():
    """Load which camera indices the user has approved."""
    if not os.path.exists(PERMISSION_FILE):
        return set()
    with open(PERMISSION_FILE, "r") as f:
        return {int(line.strip()) for line in f if line.strip().isdigit()}


def save_permission(camera_index):
    """Save a user-approved camera."""
    perms = load_permissions()
    perms.add(camera_index)
    os.makedirs("data", exist_ok=True)
    with open(PERMISSION_FILE, "w") as f:
        for idx in perms:
            f.write(f"{idx}\n")


def is_permitted(camera_index):
    """Check if a camera is already permitted."""
    return camera_index in load_permissions()


def capture_frame(camera_index=0):
    """
    Capture a single frame from the camera.
    Returns the frame as a numpy array, or None on failure.
    """
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    cap.release()
    if ret:
        return frame
    return None


def check_for_new_cameras():
    """
    Check if new cameras have been connected since last scan.
    Returns list of new camera indices (not yet permitted).
    """
    available = list_cameras()
    permitted = load_permissions()
    new_cameras = [idx for idx in available if idx not in permitted]
    return new_cameras