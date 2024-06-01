# tracking_code_1/code.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration
import av
import cv2
import numpy as np
import time
import PoseModule as pm

def run_tracking_katt():
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


            img = detector.findPose(frm, True)
            (h, w) = img.shape[:2]

            lmList = detector.findPosition(img, False)

            if len(lmList) != 0:
                feedback = []

                shoulder_angle = detector.findAngle(img, 23, 11, 13)
                elbow_angle = detector.findAngle(img, 11, 13, 15)
                back_angle = detector.findAngle(img, 11, 23, 25)
                knee_angle = detector.findAngle(img, 23, 25, 27)

                per_shoulder = np.interp(shoulder_angle, (15, 75), (0, 100))
                per_elbow = np.interp(elbow_angle, (150, 175), (0, 100))
                per_back = np.interp(back_angle, (60, 170), (0, 100))
                per_knee = np.interp(knee_angle, (110, 175), (0, 100))
                per = (per_back + per_knee + per_shoulder + per_elbow) / 4
                
                bar = np.interp(per, (0, 100), (650, 100))

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
                cv2.rectangle(img, (w-40, 100), (w-20, h-20), color, 3)
                cv2.rectangle(img, (w-40, int(bar)), (w-20, h-20), color, thickness=cv2.FILLED, lineType=cv2.LINE_AA)

                cv2.putText(img, f'{int(per)} %', (w-90, 80), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)
                cv2.rectangle(img, (0, 550), (150, 700), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, str(int(count)), (10, h-30), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 5)

                if 10 < per < 17:
                    if per_shoulder > 5:
                        feedback.append(f"Shoulder angle too high: {int(shoulder_angle)}")
                    if per_back > 5:
                        feedback.append(f"Back angle too high: {int(back_angle)}")
                    if per_knee > 5:
                        feedback.append(f"Knee angle too high: {int(knee_angle)}")
                    if per_elbow > 5:
                        feedback.append(f"Elbow angle too high: {int(elbow_angle)}")
                    cv2.putText(img, "Adjust your knee angle!", (50, 150), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
                elif per > 80:
                    if per_shoulder < 95:
                        feedback.append(f"Shoulder angle too low: {int(shoulder_angle)}")
                    if per_back < 95:
                        feedback.append(f"Back angle too low: {int(back_angle)}")
                    if per_knee < 95:
                        feedback.append(f"Knee angle too low: {int(knee_angle)}")
                    if per_elbow < 95:
                        feedback.append(f"Elbow angle too low: {int(elbow_angle)}")
                    cv2.putText(img, "Great job!", (50, 150), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

                for i, feedback in enumerate(feedback):
                    cv2.putText(img, feedback, (50, 200 + i * 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
            return av.VideoFrame.from_ndarray(img, format='bgr24')

    st.title("Webcam Face and Pose Detection")

    rtc_configuration = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

    webrtc_streamer(key="example", video_processor_factory=VideoProcessor, rtc_configuration=rtc_configuration)

if __name__ == "__main__":
    run_tracking_katt()
