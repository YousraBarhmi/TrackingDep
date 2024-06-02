# tracking_code_1/code.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import numpy as np
import time
import PoseModule as pm

def run_tracking_curls():
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
                # Right Arm
                angle1 = detector.findAngle(img, 12, 14, 16)
                # Left Arm
                angle2 = detector.findAngle(img, 11, 13, 15)

                if angle1 is not None and angle2 is not None:
                    per1 = np.interp(angle1, (40, 160), (0, 100))
                    per2 = np.interp(angle2, (40, 160), (0, 100))

                    per = (per1 + per2) / 2
                    bar = np.interp(per, (0, 100), (650, 100))

                    color = (0, 140, 255)
                    if 95 <= per <= 100:
                        color = (0, 255, 0)
                        if dir == 0:
                            count += 0.5
                            dir = 1
                    elif per <= 5:
                        color = (0, 255, 0)
                        if dir == 1:
                            count += 0.5
                            dir = 0

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

                    # Dessiner la barre de progression
                    cv2.rectangle(img, (w-40, 100), (w-20, h-20), color, 3)
                    cv2.rectangle(img, (w-40, int(bar)), (w-20, h-20), color, thickness=cv2.FILLED, lineType=cv2.LINE_AA)

                    cv2.putText(img, f'{int(per)} %', (w-90, 80), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
                    cv2.rectangle(img, (0, 550), (150, 700), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, str(int(count)), (10, h-30), cv2.FONT_HERSHEY_PLAIN, 5, (0, 140, 255), 5)

                    for i, feedback in enumerate(feedback):
                        cv2.putText(img, feedback, (50, 200 + i * 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

            return av.VideoFrame.from_ndarray(img, format='bgr24')

    st.markdown("<h3> Bicep Curls Tracker</h3>", unsafe_allow_html=True)

    rtc_configuration = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    
    webrtc_streamer(key="example", video_processor_factory=VideoProcessor, rtc_configuration=rtc_configuration)

if __name__ == "__main__":
    run_tracking_curls()
