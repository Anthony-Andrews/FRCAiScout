import numpy as np
import cv2
import json
from PIL import Image

image = Image.open("fieldS.png")
width, height = image.size

with open('transformpoint.json', 'r') as json_file:
    jsondata = json.load(json_file)
src_points = np.array(jsondata["src_points"], dtype=np.float32)
dst_points = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)
# Compute the perspective transformation matrix
perspectivematrix = cv2.getPerspectiveTransform(src_points, dst_points)

def position_correct(positions):
    positions_array = np.array(positions, dtype=np.float32)
    positions_homogeneous = np.hstack((positions_array, np.ones((positions_array.shape[0], 1), dtype=np.float32)))
    warped_positions_homogeneous = cv2.perspectiveTransform(positions_homogeneous.reshape(1, -1, 3), perspectivematrix)
    warped_positions = warped_positions_homogeneous[0, :, :2]
    return warped_positions

#calibrating the perspective matrix

"""image = cv2.imread("calibrater.jpg")
overlay_image = cv2.imread('fieldS.png')
warped_image = cv2.warpPerspective(image, perspectivematrix, (width, height))
alpha = 0.3
overlay_image = cv2.addWeighted(overlay_image, alpha, np.zeros_like(overlay_image), 1 - alpha, 0)
result = cv2.addWeighted(warped_image, 1, overlay_image, 1, 0)
cv2.imwrite('calibrateout.jpg', result)
print("done")"""
