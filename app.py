# app.py
import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration

def main():
    # Obtenir les paramètres de la requête
    url = st.query_params
    current_path = url.get("path", "")

    if current_path == "BicepCurl":
        from curls import run_tracking_curls
        run_tracking_curls()
    elif current_path == "Squat":
        from bar import run_tracking_bar
        run_tracking_bar()
    elif current_path == "KettlebellSwing":
        from katt import run_tracking_katt
        run_tracking_katt()
    # Ajoutez d'autres conditions pour d'autres chemins URL si nécessaire

if __name__ == "__main__":
    main()
