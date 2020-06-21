import time

import numpy as np
import cv2
import zbar

import trackedobject

class Environment:
    def __init__(self, name="Squirrel LPS"):
        self.name = name

        self.scanner = zbar.Scanner()

        self.frame = 0
        self.objects = {}

        self.frame_timestamp = time.time()

    def open(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        cv2.namedWindow(self.name)

    def captureImage(self):
        return_code, image = self.cap.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image, gray

    def removeInactiveObjects(self):
        inactive = []
        for name, object in self.objects.items():
            if not object.isActive(self.frame):
                inactive.append(name)

        for name in inactive:
            print(f"Removing object {name}")
            del self.objects[name]

    def showFPS(self, image):
        new_time = time.time()
        frame_time = new_time - self.frame_timestamp
        self.frame_timestamp = new_time

        cv2.putText(image, f"FPS: {int(1/frame_time)}", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0, 255), 3)

    def scanObjects(self, gray):
        results = self.scanner.scan(gray)

        for result in results:
            if result.type == "QR-Code":
                name = result.data.decode(errors="ignore")
                if name not in self.objects:
                    print(f"New object {name}")
                    self.objects[name] = trackedobject.TrackedObject(name=name)
                self.objects[name].update(result.position, self.frame)

    def showObjects(self, image):
        for object in self.objects.values():
            cv2.circle(image, object.corners[0], 10, (0, 0, 255), 2)
            cv2.circle(image, object.corners[1], 10, (0, 0, 255), 2)
            corners_array = np.array(object.corners)
            cv2.polylines(image, [corners_array], True, (0, 0, 255), 2)

    def update(self):
        image, gray = self.captureImage()

        self.scanObjects(gray)
        self.removeInactiveObjects()

        self.showObjects(image)
        self.showFPS(image)

        cv2.imshow(self.name, image)
        self.frame += 1

    def run(self):
        while True:
            self.update()
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    def close(self):
        self.cap.release()
        cv2.destroyWindow(self.name)
