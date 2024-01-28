from collections import defaultdict
import cv2
import json
import numpy as np
from ultralytics import YOLO
from dataclasses import dataclass
import math
import transform

# Load YOLOv8 model
model = YOLO('LargeBumperModel.pt')

# Path to video file
video_path = 'cuttest.mp4'

# Open the video
cap = cv2.VideoCapture(video_path)

# Retrieve video properties for setting up VideoWriter
fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Create VideoWriter object with full path
output_video_path = 'a.mp4'
fourcc = cv2.VideoWriter_fourcc(*'H264')
output_video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

# Store the track history
track_history = defaultdict(lambda: [])

output_width = 2560
output_height = 1240

allcars = {}
currcars = 6
@dataclass
class Car():
    #X position in Video
    x: int
    #Y position in Video
    y: int
    #Class type, Blu or Red
    cls: int
    #Dirty if tracking has been lost [no id]
    dirty: bool = False

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    ret, frame = cap.read()

    if ret:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True, conf=0.3, iou=0.5, tracker="bytetrack.yaml", device="mps", max_det=6)

        # Get the boxes and track IDs
        boxes = results[0].boxes.xywh.cpu()
        clss = results[0].boxes.cls.int().cpu().tolist()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        
        # Visualize the results on the frame
        annotated_frame = frame

        # Plot the tracks
        if  len(allcars) < 6:
            allcars.clear()
            for i in range(len(boxes)):
                print( Car(int(boxes[i][0].int()), int(boxes[i][1].int()), clss[i]))
                allcars[track_ids[i]] =  Car(int(boxes[i][0].int()), int(boxes[i][1].int()), clss[i])
                print(type(allcars[track_ids[i]]))
        elif len(boxes) < len(allcars):
            currcars = len(boxes)
            for car in allcars.values():
                car.dirty = True
            for tid in track_ids:
                if allcars.get(tid):
                    allcars[tid].dirty = False
        for i in range(len(track_ids)):
            if allcars.get(track_ids[i]):
                pass
            else:
                distances = {}
                for j in range(len(allcars)):
                    car = list(allcars.values())[j]
                    if not car.dirty or not car.cls == clss[i]:
                        continue
                    distances[list(allcars.keys())[j]] = math.sqrt((boxes[i][0] - car.x)**2 + (boxes[i][1] - car.y)**2)
                try:
                    m = list(distances.keys())[list(distances.values()).index(min(distances.values()))]
                    allcars.pop(m)
                    allcars[track_ids[i]] = Car(int(boxes[i][0].int()), int(boxes[i][1].int()), clss[i])
                    currcars += 1
                except ZeroDivisionError as e:
                    print(e)
        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box
            allcars[track_id].x = int(x)
            allcars[track_id].y = int(y)
            track = track_history[track_id]
            track.append((float(x), float(y)))  # x, y center point

            # Retain only the last 30 points for a history of 30 frames
            track = track[-30:]

        print(allcars)
        for car in allcars.values():
            cv2.putText(annotated_frame,str(car), 
                    (int(car.x), int(car.y)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1,
                    (255, 0,0), thickness=3
            )

        # Display the annotated frame
        cv2.imshow("YOLOv8 Tracking", annotated_frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break

# Release the video writer and capture objects
output_video.release()
cap.release()
cv2.destroyAllWindows()

# Check if the video was saved successfully
if not output_video.isOpened():
    print("Error: Video not written successfully.")
else:
    print("Video saved successfully.")