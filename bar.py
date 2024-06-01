# tracking_code_1/code.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import numpy as np
import time
import PoseModule as pm

def run_tracking_bar():
    # Load the Haar Cascade for face detection
    cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    detector = pm.poseDetector()
    count = 0
    dir = 0
    pTime = 0

    class VideoProcessor:
        def recv(self, frame):
            nonlocal count, dir, pTime

            frm = frame.to_ndarray(format="bgr24")
            gray = cv2.cvtColor(frm, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(gray, 1.1, 3)

            # for (x, y, w, h) in faces:
            #     cv2.rectangle(frm, (x, y), (x + w, y + h), (0, 255, 0), 3)

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
            # print("back_angle : " + back_angle)
            color = (255, 0, 255)
            if 95 <= per <= 100 :
                color = (0, 255, 0)
                if dir == 0:
                    count += 0.5
                    dir = 1
            if per <= 5 :
                color = (0, 255, 0)
                if dir == 1:
                    count += 0.5
                    dir = 0

            # Dessiner la barre de progression
            cv2.rectangle(img, (1100, 100), (w-60, h-20), color, 3)
            cv2.rectangle(img, (1100, int(bar)), (w-60, h-20), color, cv2.FILLED)
            cv2.putText(img, f'{int(per)} %', (w-120, 75), cv2.FONT_HERSHEY_PLAIN, 4,
                        color, 4)


            cv2.rectangle(img, (0, 550), (150, 700), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, str(int(count)), (10, h-30), cv2.FONT_HERSHEY_PLAIN, 5,
                        (255, 0, 0), 5)
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, str(int(fps)), (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)

            return av.VideoFrame.from_ndarray(img, format='bgr24')

    st.title("Webcam Face and Pose Detection")

    rtc_configuration = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    webrtc_streamer(key="example", video_processor_factory=VideoProcessor, rtc_configuration=rtc_configuration)

if __name__ == "__main__":
    run_tracking_curls()
