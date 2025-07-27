import os
import cv2

# --- SETUP ---

# CHANGE THIS TO YOUR IMAGE FOLDER PATH
image_folder = r'C:\Users\codyr\Downloads\7_23_2025'
video_name = 'walkthrough.mp4'
fps = 2  # = 0.5 seconds per image

# --- GATHER FILES ---
valid_ext = ('.jpg', '.jpeg', '.png')
images = sorted([f for f in os.listdir(image_folder) if f.lower().endswith(valid_ext)])

if not images:
    raise Exception("No images found in the folder!")

# --- GET VIDEO SETTINGS FROM FIRST IMAGE ---
first_img_path = os.path.join(image_folder, images[0])
frame = cv2.imread(first_img_path)
if frame is None:
    raise Exception("Could not read first image.")
height, width, _ = frame.shape

# --- INITIALIZE VIDEO WRITER ---
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

# --- WRITE IMAGES TO VIDEO ---
for img_file in images:
    img_path = os.path.join(image_folder, img_file)
    frame = cv2.imread(img_path)
    if frame is not None and frame.shape[:2] == (height, width):
        video.write(frame)
    else:
        print(f"Skipping {img_file} due to size mismatch or read error.")

video.release()
print(f"🎉 Done! Video saved as: {video_name}")
