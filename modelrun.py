from collections import defaultdict
import cv2
from ultralytics import YOLO
from dataclasses import dataclass
import math
import json
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
output_video_path = 'output.mp4'
fourcc = cv2.VideoWriter_fourcc(*'H264')
output_video = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

# Store the track history
track_history = defaultdict(lambda: [])

#logs all car objects
allcars = {}

#logs all the movements of the bots
robotlog = defaultdict(lambda: [])

#class car to keep permanent track of robots
@dataclass
class Car():
    #X position in Video
    x: int
    #Y position in Video
    y: int
    #Class type, Blu or Red
    cls: int
    #ID's
    carid: int
    #Dirty if tracking has been lost [no id]
    dirty: bool = False
    
# Loop through the video frames
Fuck = True
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

        # Creating car objects for consitent re-identification
        if  len(allcars) < 6:
            allcars.clear()
            for i in range(len(boxes)):
                #print( Car(int(boxes[i][0].int()), int(boxes[i][1].int()), clss[i]))
                allcars[track_ids[i]] =  Car(int(boxes[i][0].int()), int(boxes[i][1].int()), clss[i], len(allcars))
                #print(type(allcars[track_ids[i]]))

        #unsure
        elif len(boxes) < len(allcars):
            for car in allcars.values():
                car.dirty = True
            for tid in track_ids:
                if allcars.get(tid):
                    allcars[tid].dirty = False

        #sid when you pull from the git please update these comments
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
                    killcar = allcars.pop(m)
                    allcars[track_ids[i]] = Car(int(boxes[i][0].int()), int(boxes[i][1].int()), clss[i], killcar.carid)
                except ZeroDivisionError as e:
                    print(e)

        for box, track_id in zip(boxes, track_ids):
            #update bounding boxes
            x, y, w, h = box
            allcars[track_id].x = int(x)
            allcars[track_id].y = int(y)
            track = track_history[track_id]
            track.append((float(x), float(y)))  # X, Y center point

            # Retain only the last 30 points for a history of 30 frames
            track = track[-30:]

        for car in allcars.values():
            #annotates the frame
            robotlog[car.carid].append((car.x, car.y))
            cv2.putText(annotated_frame,str(car.carid), 
                    (int(car.x), int(car.y)),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1,
                    (0, 255,255), thickness=2
            )

        # Display the annotated frame
        cv2.imshow("YOLOv8 Tracking", annotated_frame)
        output_video.write(annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

converted_dict = dict(robotlog)

json_filename = 'output.json'
with open(json_filename, 'w') as json_file:
    json.dump(converted_dict, json_file, indent=2)

output_video.release()
cap.release()
cv2.destroyAllWindows()