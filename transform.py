import numpy as np
import cv2
import json
from PIL import Image


image = Image.open("fieldS.png")
width, height = image.size

with open('transformpoint.json', 'r') as transform_json:
    transform = json.load(transform_json)
web_points = transform["src_points"]
width = transform["vid_width"]
height = transform["vid_height"]

sorted_points = sorted(web_points, key=lambda p: (p[0], p[1]))

result_points = [sorted_points[1], sorted_points[2], sorted_points[3], sorted_points[0]]

scaled_points = [[point[0] * width, point[1] * height] for point in result_points]
print(scaled_points)
src_points = np.array(scaled_points, dtype=np.float32)
dst_points = np.array([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]], dtype=np.float32)
# Compute the perspective transformation matrix
perspectivematrix = cv2.getPerspectiveTransform(src_points, dst_points)

def position_correct(points):
    points_array = np.array([points], dtype=np.float32)
    output = cv2.perspectiveTransform(points_array, perspectivematrix)
    return output

with open('unmodout.json', 'r') as unmod_json:
    unmod = json.load(unmod_json)
#converted output dictionary
finalout = {}
json_out = 'output.json'
for i in range(6):
    finalout[str(i)] = position_correct(unmod[str(i)])
with open(json_out, 'w') as output_json:
    json.dump(finalout, output_json, indent=2)
#calibrating the perspective matrix
"""
image = cv2.imread("calibrater.jpg")
overlay_image = cv2.imread('fieldS.png')
warped_image = cv2.warpPerspective(image, perspectivematrix, (width, height))
alpha = 0.3
#overlay_image = cv2.addWeighted(overlay_image, alpha, np.zeros_like(overlay_image), 1 - alpha, 0)
#result = cv2.addWeighted(warped_image, 1, overlay_image, 1, 0)
cv2.imwrite('calibrateout.jpg', warped_image)
print("done")
"""