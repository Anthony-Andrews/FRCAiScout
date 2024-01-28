from collections import defaultdict
import cv2
import json
import numpy as np
from ultralytics import YOLO
from dataclasses import dataclass
import math

# Load YOLOv8 model
model = YOLO('LargeBumperModel.pt')

# Path to video file
video_path = 'cuttest.mp4'

# Path to transformation JSON:
#json_file_path = 'C:/Users/antho/Desktop/frCV/Q90.json'

# Field overlay image 2560 x 1240
overlay = cv2.imread('/Users/cheese/Downloads/fieldS.png')
video_overlay = False

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

# with open(json_file_path, 'r') as json_file:
#     points = json.load(json_file)

# # Setup variables read from JSON
# src_points = points['src_points']
output_width = 2560
output_height = 1240

def calculate_matrix(src_points, output_width, output_height):
    # Convert the source points to numpy array
    src_points_np = np.array(src_points, dtype=np.float32)

    # Define destination points based on the output resolution
    src_points = np.array([[528, 302], [1477, 302], [1889, 523], [117, 496]], dtype=np.float32)
    dst_points = np.array([[0, 0], [output_width - 1, 0], [output_width - 1, output_height - 1], [0, output_height - 1]],
                                   dtype=np.float32)

    print("src_points_np before transformation:", src_points_np)

    # Calculate the perspective transformation matrix using cv2.getPerspectiveTransform
    transformation_matrix = cv2.getPerspectiveTransform(src_points_np, dst_points)

    print("transformation_matrix:", transformation_matrix)

    # Apply transformation to source points for visualization
    transformed_points = cv2.perspectiveTransform(np.array([src_points_np]), transformation_matrix)
    transformed_points = transformed_points[0]

    print("transformed_points:", transformed_points)

    return transformation_matrix

# transformation_matrix = calculate_matrix(src_points, output_width, output_height) the calculated_matrix is bugged so here the matrix is hardcoded:

transformation_matrix = np.array([[-4.62389460e+00, -1.29813687e+01, 5.89744728e+03],
                                  [1.46544756e-01, -2.38574862e+01, 7.06949487e+03],
                                  [4.66759180e-05, -1.00445012e-02, 1.00000000e+00]])

def apply_transform(absolute_coords):
    # Convert input coordinates to a numpy array
    input_coordinates_np = np.array([absolute_coords], dtype=np.float32)
    
    # Apply perspective transformation
    output_coordinates_np = cv2.perspectiveTransform(input_coordinates_np, transformation_matrix)

    # Extract the output coordinates from the numpy array
    output_coordinates = output_coordinates_np[0]

    return output_coordinates

# matrix test case:
#absolute_coords = [[1520, 343]]
#result = apply_transform(absolute_coords)
#print(result)

# Ensure frame_transformed and overlay have the same size
overlay_resized = cv2.resize(overlay, (width, height))

allcars = {}
currcars = 6
@dataclass
class Car():
    x: int
    y: int
    #class, blue or red
    cls: int
    #dirty means lost track [no id]
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

        frame_transformed = cv2.warpPerspective(frame, transformation_matrix, (output_width, output_height))

        if video_overlay:
            # Ensure frame_transformed and overlay have the same size
            overlay_resized = cv2.resize(overlay, (frame_transformed.shape[1], frame_transformed.shape[0]))

            # Blend the transformed frame with the overlay (50% opacity)
            blended_frame = cv2.addWeighted(frame_transformed, 0.5, overlay_resized, 0.5, 0)

            # Blend the transformed frame with the overlay (50% opacity)
            field_opacity = 0.37
            field_frame = cv2.addWeighted(frame_transformed, 0.5 - field_opacity, overlay_resized, field_opacity, 0)
        else:
            # Ensure frame_transformed and overlay have the same size
            field_frame = cv2.resize(overlay, (frame_transformed.shape[1], frame_transformed.shape[0]))

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

            # Draw the tracking lines
            if len(track) > 1:
                points = np.array(track, dtype=np.int32).reshape((-1, 2))  # Reshape to (N, 2)
                q_points = apply_transform(points)  # Apply perspective transformation
                q_points = q_points.astype(np.int32)  # Ensure the points are integers
                cv2.polylines(field_frame, [q_points], isClosed=False, color=(0, 0, 0), thickness=5)
        print(allcars)
        for car in allcars.values():
            cv2.putText(annotated_frame,str(car), 
                    (int(car.x), int(car.y)), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1,
                    (255, 0,0), thickness=3
            )

        cv2.imshow("Walmart Zebra Motionworks:", field_frame)

        # Save the current blended frame to the video.
        #output_video.write(field_frame)

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