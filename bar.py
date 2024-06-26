# tracking_code_1/code.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import numpy as np
import time
import PoseModule as pm
import gc

def run_tracking_bar():
    detector = pm.poseDetector()
    count = 0
    dir = 0
    pTime = 0

    class VideoProcessor:
        def recv(self, frame):
            nonlocal count, dir, pTime

            frm = frame.to_ndarray(format="bgr24")
            gray = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)

            img = detector.findPose(frm, True)
            (h, w) = img.shape[:2]
            lmList = detector.findPosition(img, False)

            if len(lmList) != 0:
                feedback = []
                # Calcul des angles
                back_angle = detector.findAngle(img, 12, 24, 26)
                knee_angle = detector.findAngle(img, 24, 26, 28)

                # Interpoler les valeurs d'angle pour le pourcentage et la barre de progression
                per1 = np.interp(back_angle, (65, 170), (0, 100))
                per2 = np.interp(knee_angle, (65, 165), (0, 100))
                bar = np.interp(back_angle, (70, 170), (650, 100))

                per = (per1 + per2) / 2
                color = (0, 140, 255)
                if 95 <= per <= 100:
                    color = (0, 255, 0)
                    if dir == 0:
                        count += 0.5
                        dir = 1
                if per <= 5:
                    color = (0, 255, 0)
                    if dir == 1:
                        count += 0.5
                        dir = 0

                # Dessiner la barre de progression
                cv2.rectangle(img, (w-40, 100), (w-20, h-20), color, 3)
                cv2.rectangle(img, (w-40, int(bar)), (w-20, h-20), color, thickness=cv2.FILLED, lineType=cv2.LINE_AA)
                cv2.putText(img, f'{int(per)} %', (w-90, 80), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

                cv2.rectangle(img, (0, 550), (150, 700), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, str(int(count)), (10, h-30), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)

                # Ajouter des retours
                if back_angle > 170:
                    feedback.append('Back: too straight')
                    color = (0, 0, 255)
                if knee_angle > 165:
                    feedback.append('Knees: too straight')
                    color = (0, 0, 255)
                if back_angle < 65:
                    feedback.append('Back: too bent')
                    color = (0, 0, 255)
                if knee_angle < 65:
                    feedback.append('Knees: too bent')
                    color = (0, 0, 255)

                for i, feedback in enumerate(feedback):
                        cv2.putText(img, feedback, (50, 200 + i * 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

                # Dessiner la barre de progression
                cv2.rectangle(img, (w-40, 100), (w-20, h-20), color, 3)
                cv2.rectangle(img, (w-40, int(bar)), (w-20, h-20), color, thickness=cv2.FILLED, lineType=cv2.LINE_AA)

                cv2.putText(img, f'{int(per)} %', (w-90, 80), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
                cv2.rectangle(img, (0, 550), (150, 700), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, str(int(count)), (10, h-30), cv2.FONT_HERSHEY_PLAIN, 5, (0, 140, 255), 5)
            return av.VideoFrame.from_ndarray(img, format='bgr24')

    st.markdown("<h3> Squat Tracker</h3>", unsafe_allow_html=True)

    rtc_configuration = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    webrtc_streamer(key="example", video_processor_factory=VideoProcessor, rtc_configuration=rtc_configuration)

    # Manually trigger garbage collection to free memory
    gc.collect()

if __name__ == "_main_":
    run_tracking_bar()