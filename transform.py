import numpy as np
import cv2

transformation_matrix = np.array([[-4.62389460e+00, -1.29813687e+01, 5.89744728e+03],
                                 [1.46544756e-01, -2.38574862e+01, 7.06949487e+03],
                                 [4.66759180e-05, -1.00445012e-02, 1.00000000e+00]])

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

def apply_transform(absolute_coords):
    # Convert input coordinates to a numpy array
    input_coordinates_np = np.array([absolute_coords], dtype=np.float32)
    
    # Apply perspective transformation
    output_coordinates_np = cv2.perspectiveTransform(input_coordinates_np, transformation_matrix)

    # Extract the output coordinates from the numpy array
    output_coordinates = output_coordinates_np[0]

    return output_coordinates