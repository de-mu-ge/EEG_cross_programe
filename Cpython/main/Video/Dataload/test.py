# import cv2
import numpy as np

frame = np.array([480, 640, 3])
width, height = 480, 640


frame = frame[(width - 480) // 2 : (width - 480) // 2 + 480, (height - 640) // 2 : (height - 640) // 2 + 640]

print(frame.shape)