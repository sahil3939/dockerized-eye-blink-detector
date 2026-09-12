from flask import Flask, render_template
from flask_sock import Sock

import cv2
import mediapipe as mp
import numpy as np
import base64
import json
import time

from blink_detector import calculate_ear


# ==============================
# Flask Application
# ==============================

app = Flask(__name__)
sock = Sock(app)


# ==============================
# MediaPipe Face Mesh
# ==============================

mp_face_mesh = mp.solutions.face_mesh


# Eye landmark indices
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]


# Blink detection threshold
EAR_THRESHOLD = 0.23


# ==============================
# Home Page
# ==============================

@app.route("/")
def index():

    return render_template("index.html")


# ==============================
# WebSocket Endpoint
# ==============================

@sock.route("/ws")
def websocket(ws):

    print("================================")
    print("WebSocket client connected")
    print("================================")

    # ==============================
    # Blink variables
    # ==============================

    blink_count = 0
    blink_state = False

    last_blink_time = time.time()

    # Prevent repeated notifications
    notification_sent = False


    try:

        # ==============================
        # MediaPipe Face Mesh
        # ==============================

        with mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as face_mesh:

            # ==============================
            # Main processing loop
            # ==============================

            while True:

                # ==============================
                # Receive frame from browser
                # ==============================

                data = ws.receive()

                if data is None:

                    print("Client disconnected.")

                    break


                print("Frame received.")


                # ==============================
                # Decode incoming image
                # ==============================

                try:

                    if isinstance(data, str):

                        # Remove data URL prefix
                        if "," in data:

                            data = data.split(",", 1)[1]


                        # Base64 decode
                        image_bytes = base64.b64decode(data)

                    else:

                        image_bytes = data


                except Exception as e:

                    print(
                        "Base64 decoding error:",
                        e
                    )

                    continue


                # ==============================
                # Convert bytes to NumPy
                # ==============================

                np_array = np.frombuffer(
                    image_bytes,
                    dtype=np.uint8
                )


                # ==============================
                # Decode JPEG
                # ==============================

                frame = cv2.imdecode(
                    np_array,
                    cv2.IMREAD_COLOR
                )


                if frame is None:

                    print(
                        "Could not decode image."
                    )

                    continue


                print(
                    f"Frame decoded: "
                    f"{frame.shape[1]}x{frame.shape[0]}"
                )


                # ==============================
                # Frame dimensions
                # ==============================

                h, w, _ = frame.shape


                # ==============================
                # Convert BGR → RGB
                # ==============================

                rgb = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )


                # ==============================
                # MediaPipe processing
                # ==============================

                results = face_mesh.process(rgb)


                # Default EAR
                ear = 0.0


                # ==============================
                # Face detected
                # ==============================

                if results.multi_face_landmarks:

                    face_landmarks = (
                        results.multi_face_landmarks[0]
                    )


                    # --------------------------
                    # Eye coordinate arrays
                    # --------------------------

                    left_eye = []
                    right_eye = []


                    # ==============================
                    # LEFT EYE
                    # ==============================

                    for idx in LEFT_EYE:

                        lm = face_landmarks.landmark[idx]

                        x = int(lm.x * w)
                        y = int(lm.y * h)

                        left_eye.append([x, y])


                        cv2.circle(
                            frame,
                            (x, y),
                            3,
                            (0, 255, 0),
                            -1
                        )


                    # ==============================
                    # RIGHT EYE
                    # ==============================

                    for idx in RIGHT_EYE:

                        lm = face_landmarks.landmark[idx]

                        x = int(lm.x * w)
                        y = int(lm.y * h)

                        right_eye.append([x, y])


                        cv2.circle(
                            frame,
                            (x, y),
                            3,
                            (0, 255, 0),
                            -1
                        )


                    # ==============================
                    # Convert to NumPy
                    # ==============================

                    left_eye = np.array(
                        left_eye
                    )

                    right_eye = np.array(
                        right_eye
                    )


                    # ==============================
                    # Calculate EAR
                    # ==============================

                    left_ear = calculate_ear(
                        left_eye
                    )

                    right_ear = calculate_ear(
                        right_eye
                    )


                    ear = (
                        left_ear +
                        right_ear
                    ) / 2.0


                    # ==============================
                    # Blink Detection
                    # ==============================

                    if ear < EAR_THRESHOLD:

                        if not blink_state:

                            blink_state = True


                    else:

                        if blink_state:

                            blink_count += 1

                            blink_state = False

                            # Reset blink timer
                            last_blink_time = time.time()


                            # Allow a new notification
                            notification_sent = False


                # ==============================
                # Time since last blink
                # ==============================

                elapsed = (
                    time.time()
                    -
                    last_blink_time
                )


                # ==============================
                # Notification Logic
                # ==============================

                notification = False


                # User has not blinked for
                # more than 5 seconds
                if (
                    elapsed > 5
                    and not notification_sent
                ):

                    notification = True

                    notification_sent = True


                    print(
                        "WARNING: No blink detected "
                        "for more than 5 seconds."
                    )


                # ==============================
                # Reset notification state
                # ==============================

                if elapsed <= 5:

                    notification_sent = False


                # ==============================
                # Draw Blink Count
                # ==============================

                cv2.putText(
                    frame,
                    f"Blink Count: {blink_count}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )


                # ==============================
                # Draw EAR
                # ==============================

                cv2.putText(
                    frame,
                    f"EAR: {ear:.2f}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 0, 0),
                    2
                )


                # ==============================
                # Draw Last Blink Time
                # ==============================

                cv2.putText(
                    frame,
                    f"Last Blink: {elapsed:.1f}s",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )


                # ==============================
                # Display Notification Status
                # ==============================

                if elapsed > 5:

                    cv2.putText(
                        frame,
                        "BLINK REMINDER!",
                        (20, 165),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 255),
                        3
                    )


                # ==============================
                # Encode processed frame
                # ==============================

                success, buffer = cv2.imencode(
                    ".jpg",
                    frame,
                    [
                        cv2.IMWRITE_JPEG_QUALITY,
                        70
                    ]
                )


                if not success:

                    print(
                        "JPEG encoding failed."
                    )

                    continue


                # ==============================
                # Convert image to Base64
                # ==============================

                encoded = base64.b64encode(
                    buffer
                ).decode("utf-8")


                # ==============================
                # Create WebSocket response
                # ==============================

                response = {

                    "image": encoded,

                    "blink_count":
                        blink_count,

                    "ear":
                        round(
                            float(ear),
                            2
                        ),

                    "last_blink":
                        round(
                            float(elapsed),
                            1
                        ),

                    "notification":
                        notification
                }


                # ==============================
                # Send response to browser
                # ==============================

                ws.send(
                    json.dumps(response)
                )


                print(
                    "Processed frame sent."
                )


    # ==============================
    # WebSocket Error
    # ==============================

    except Exception as e:

        print(
            "================================"
        )

        print(
            "WEBSOCKET ERROR:"
        )

        print(
            repr(e)
        )

        print(
            "================================"
        )


    # ==============================
    # Connection closed
    # ==============================

    finally:

        print(
            "WebSocket connection closed."
        )


# ==============================
# Run Flask
# ==============================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )