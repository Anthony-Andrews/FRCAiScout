import numpy as np
import cv2
import json

def calculate_matrix():
    with open('transformpoint.json', 'r') as json_file:
        jsondata = json.load(json_file)
    # Convert the source points to numpy array

    # Define destination points based on the output resolution
    src_points_np = np.array(jsondata["src_points"], dtype=np.float32)
    dst_points = np.array([[0, 0], [jsondata["output_width"] - 1, 0], [jsondata["output_width"] - 1, jsondata["output_height"] - 1], [0, jsondata["output_height"] - 1]],
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
transformation_matrix = calculate_matrix()
def apply_transform(absolute_coords):
    # Convert input coordinates to a numpy array
    input_coordinates_np = np.array([absolute_coords], dtype=np.float32)
    
    # Apply perspective transformation
    output_coordinates_np = cv2.perspectiveTransform(input_coordinates_np, transformation_matrix)

    # Extract the output coordinates from the numpy array
    output_coordinates = output_coordinates_np[0]

    return output_coordinates