import cv2
import streamlit as st
from ultralytics import YOLO
import streamlink
import numpy as np
import time

def get_stream_url(youtube_url):
    try:
        session = streamlink.Streamlink()
        session.set_option("http-headers", {"User-Agent": "Mozilla/5.0"})

        # Load cookies exported from a logged-in YouTube browser session
        # (e.g. via the "Get cookies.txt LOCALLY" browser extension)
        import http.cookiejar
        cj = http.cookiejar.MozillaCookieJar("youtube_cookies.txt")
        cj.load(ignore_discard=True, ignore_expires=True)
        session.http.cookies.update({c.name: c.value for c in cj})

        streams = session.streams(youtube_url)
        if not streams:
            return None
        return streams.get('360p', streams['best']).url
    except Exception as e:
        st.error(f"Streamlink could not open URL: {e}")
        return None
        

def main():
    st.set_page_config(page_title="YOLOv8 Streamlink", layout="wide")
    st.title("🚀 YOLOv8 YouTube Live Detection")

    youtube_url = st.text_input("YouTube URL", "https://www.youtube.com/watch?v=j-hH64410UM")
    
    # Use session state to track the running process
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False

    col1, col2 = st.columns(2)
    start_btn = col1.button("Start Detection")
    stop_btn = col2.button("Stop")

    if start_btn:
        st.session_state.is_running = True
    if stop_btn:
        st.session_state.is_running = False

    video_placeholder = st.empty()

    if st.session_state.is_running:
        model = YOLO("yolov8n.pt")
        stream_url = get_stream_url(youtube_url)
        
        if stream_url:
            # Force FFMPEG backend to stop the CAP_IMAGES error
            cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
            
            while st.session_state.is_running:
                ret, frame = cap.read()
                if not ret:
                    st.warning("Stream disconnected. Attempting to reconnect...")
                    break
                
                # Resize to reduce CPU usage
                frame = cv2.resize(frame, (640, 360))
                
                # Run YOLO Inference
                results = model(frame, conf=0.4, verbose=False)
                annotated = results[0].plot()
                
                # Update UI
                video_placeholder.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), channels="RGB")
                
                # Yield control to Streamlit
                time.sleep(0.01)

            cap.release()
        else:
            st.error("Could not extract stream. The IP might be rate-limited.")

if __name__ == "__main__":
    main()
