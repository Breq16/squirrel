import time

import numpy as np
import cv2
import zbar

import trackedqr

class Environment:
    def __init__(self, name="Squirrel LPS"):
        self.name = name

        self.scanner = zbar.Scanner()

        self.frame = 0
        self.objects = {}
        self.reference = None

        self.frame_timestamp = time.time()

    def open(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FPS, 15)

        cv2.namedWindow(self.name)

    def captureImage(self):
        return_code, image = self.cap.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image, gray

    def removeInactiveObjects(self):
        inactive = []
        for data, object in self.objects.items():
            if not object.isActive(self.frame):
                print(f"Removing object {object.name}")
                inactive.append(data)
                if object is self.reference:
                    self.reference = None

        for data in inactive:
            del self.objects[data]

    def showFPS(self, image):
        new_time = time.time()
        frame_time = new_time - self.frame_timestamp
        self.frame_timestamp = new_time

        cv2.putText(image, f"FPS: {int(1/frame_time)}", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0, 255), 3)

    def scanObjects(self, gray):
        results = self.scanner.scan(gray)

        for result in results:
            if result.type == "QR-Code":
                data = result.data
                name = data[1:].decode(errors="ignore")
                if data not in self.objects:
                    print(f"New object {name}")
                    self.objects[data] = trackedqr.TrackedQR(data)

                    if self.objects[data].isReference:
                        if self.reference is None:
                            self.reference = self.objects[data]
                self.objects[data].update(result.position, self.frame)

    def showObjects(self, image):
        for object in self.objects.values():
            corners_array = np.array(object.corners)

            if object.isCurrent(self.frame):
                cv2.polylines(image, [corners_array], True, (0, 0, 255), 2)
            else:
                cv2.polylines(image, [corners_array], True, (128, 128, 128), 2)

            if object.isReference:
                cv2.circle(image, object.corners[0], 10, (0, 0, 255), 2)
                cv2.arrowedLine(image, object.corners[0], object.corners[1], (0, 255, 0), 2)
                cv2.arrowedLine(image, object.corners[0], object.corners[3], (255, 0, 0), 2)
            else:
                centroid = tuple(int(coord) for coord in object.getCentroid())
                frontMidpoint = tuple(int(coord) for coord in object.getFrontMidpoint())
                cv2.circle(image, centroid, 10, (255, 0, 255), 2)
                cv2.arrowedLine(image, centroid, frontMidpoint, (0, 255, 255), 2)

    def getPositions(self, image):
        if self.reference is None:
            return
        pictureToScene, sceneToPicture = self.reference.getTransformMatrices()

        #originInScene = np.array([[10], [10], [1]])
        #originInPicture = np.matmul(sceneToPicture, originInScene)
        #print(originInPicture)
        #cv2.circle(image, (int(originInPicture[0][0]/originInPicture[2][0]), int(originInPicture[1][0]/originInPicture[2][0])), 10, (255, 0, 255), 2)

        for object in self.objects.values():
            if not object.isReference:
                centroid = np.array([[coord] for coord in object.getCentroid()] + [[1]])
                realPosHomo = np.matmul(pictureToScene, centroid)
                realX = realPosHomo[0][0] / realPosHomo[2][0]
                realY = realPosHomo[1][0] / realPosHomo[2][0]
                cv2.putText(image, f"({int(realX)}, {int(realY)})", tuple(int(coord) for coord in object.getCentroid()), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0, 255), 3)

    def update(self):
        image, gray = self.captureImage()

        self.scanObjects(gray)
        self.removeInactiveObjects()

        self.showObjects(image)
        self.getPositions(image)
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
