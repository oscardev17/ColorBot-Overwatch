# ================================== #
# This program was created by Oscar  #
# ================================== #

import cv2
from mss import mss
import numpy as np

class Grabber:
    def __init__(self) -> None:
        self.upper = np.array([157, 255, 255], np.uint8)

    def find_dimensions(self, scale,witdh,height):
        oworegion = (int(witdh/2-witdh/scale/2),int(height/2-height/scale/2),int(witdh/2+witdh/scale/2),int(height/2+height/scale/2))
        x,y,width,height = oworegion
        self.box_middle_x = int((width-x)/2)
        self.box_middle_y = int((height-y)/2)
        self.dimensions = oworegion

    def process_frame(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        processed = cv2.inRange(hsv, self.lower, self.upper)
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, np.ones((10, 10), np.uint8))
        dilatation_size = 2
        dilation_shape = cv2.MORPH_RECT
        element = cv2.getStructuringElement(dilation_shape, (2 * dilatation_size + 1, 2 * dilatation_size + 1),
                                    (dilatation_size, dilatation_size))
        processed = cv2.dilate(processed, element)
        return processed
    
    def detect_contours(self, frame, minimum_size):
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        large_contours = []
        if len(contours) != 0:
            for i in contours:
                if cv2.contourArea(i) > minimum_size:
                    large_contours.append(i)
        return large_contours

    def scale_contour(self,cnt, scale:float):
        M = cv2.moments(cnt)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])

        cnt_norm = cnt - [cx, cy]
        cnt_scaled = cnt_norm * scale
        cnt_scaled = cnt_scaled + [cx, cy]
        cnt_scaled = cnt_scaled.astype(np.int32)

        return cnt_scaled

    def on_target(self, contour):
        for c in contour:
            cont = self.scale_contour(c,0.85)
            test = cv2.pointPolygonTest(cont,(self.box_middle_x,self.box_middle_y),False)
            if test >= 0:
                return True
        return False
    
    def compute_centroid(self, contour):
        c = max(contour, key=cv2.contourArea)
        rectangle = np.int0(cv2.boxPoints(cv2.minAreaRect(c)))
        new_box = []
        for point in rectangle:
            point_x = point[0]
            point_y = point[1]
            new_box.append([round(point_x, -1), round(point_y, -1)])
        M = cv2.moments(np.array(new_box))
        if M['m00']:
            TwT_x = (M['m10'] / M['m00'])
            TwT_y = (M['m01'] / M['m00'])
            x = -(self.box_middle_x - TwT_x)
            y = -(self.box_middle_y - TwT_y)
            return [], x, y
