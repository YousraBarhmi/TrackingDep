import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import numpy as np
import time
import PoseModule as pm

# Load the Haar Cascade for face detection
cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
detector = pm.poseDetector()

class VideoProcessor:
    def __init__(self):
        self.count = 0
        self.dir = 0
        self.pTime = 0

    def recv(self, frame):
        frm = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, 1.1, 3)

        for (x, y, w, h) in faces:
            cv2.rectangle(frm, (x, y), (x + w, y + h), (0, 255, 0), 3)

        img = detector.findPose(frm, True)
        lmList = detector.findPosition(img, False)

        if len(lmList) != 0:
            feedback = []
            # Right Arm
            angle1 = detector.findAngle(img, 12, 14, 16)
            # Left Arm
            angle2 = detector.findAngle(img, 11, 13, 15)

            if angle1 is not None and angle2 is not None:
                per1 = np.interp(angle1, (40, 160), (0, 100))
                per2 = np.interp(angle2, (40, 160), (0, 100))

                per = (per1 + per2) / 2
                bar = np.interp(per, (0, 100), (650, 100))

                color = (255, 0, 255)
                if 95 <= per <= 100:
                    color = (0, 255, 0)
                    if self.dir == 0:
                        self.count += 0.5
                        self.dir = 1
                elif per <= 5:
                    color = (0, 255, 0)
                    if self.dir == 1:
                        self.count += 0.5
                        self.dir = 0

                if angle1 > 170:
                    feedback.append('Right arm: too high')
                    color = (0, 0, 255)
                elif angle2 > 170:
                    feedback.append('Left arm: too high')
                    color = (0, 0, 255)
                if angle1 < 20:
                    feedback.append('Right arm: too low')
                    color = (0, 0, 255)
                elif angle2 < 20:
                    feedback.append('Left arm: too low')
                    color = (0, 0, 255)
                if feedback:
                    cv2.putText(img, f'{str(feedback)}', (10, 75), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

                cv2.rectangle(img, (1100, 100), (img.shape[1] - 60, img.shape[0] - 20), color, 3)
                cv2.rectangle(img, (1100, int(bar)), (img.shape[1] - 60, img.shape[0] - 20), color, cv2.FILLED)
                cv2.putText(img, f'{int(per)} %', (img.shape[1] - 120, 75), cv2.FONT_HERSHEY_PLAIN, 4, color, 4)
                cv2.rectangle(img, (0, 450), (250, 720), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, str(int(self.count)), (45, img.shape[0] - 40), cv2.FONT_HERSHEY_PLAIN, 15, (255, 0, 0), 25)

        cTime = time.time()
        fps = 1 / (cTime - self.pTime)
        self.pTime = cTime
        cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)

        return av.VideoFrame.from_ndarray(img, format='bgr24')

# Streamlit app layout
st.title("Webcam Face Detection")

# WebRTC configuration for the streamer
rtc_configuration = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# WebRTC streamer with the video processor
webrtc_streamer(key="example", video_processor_factory=VideoProcessor, rtc_configuration=rtc_configuration)
