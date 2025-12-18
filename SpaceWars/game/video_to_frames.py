import cv2
import os

VIDEO_PATH = "abertura_spacewars.mp4"  # agora direto
OUTPUT_DIR = "intro"
FPS = 30

os.makedirs(OUTPUT_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_PATH)
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_name = f"frame_{frame_count:04d}.png"
    cv2.imwrite(os.path.join(OUTPUT_DIR, frame_name), frame)
    frame_count += 1

cap.release()
print("Frames extraídos com sucesso!")
