import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration

def main():
    # Add custom CSS
    custom_css = """
    <style>
        /* Set the background color to black */
        .stApp, .MuiBox-root{
            background-color: rgb(3, 20, 38);
        }
        
        /* Style the logo and title */
        .header-container {
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;  /* Set the text color to white */
        }

        .header-container img {
            margin-right: 20px;
        }
        
        .header-container h1, h3 {
            color : white;
            margin: 0;
        }

        hr{
        background-color: white;
        }
        
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    # Add a logo and title to the header
    st.markdown(
        """
        <div class="header-container">
            <img src="data:image/png;base64,{logo}" width="80">
            <h1>FitAI</h1>
        </div>
        <hr>
        """.format(logo=load_logo()),
        unsafe_allow_html=True
    )
    
    # Get the URL query parameters
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
    # Add other conditions for other URL paths if necessary

def load_logo():
    import base64
    with open("logofitai.png", "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
    
if __name__ == "__main__":
    main()
