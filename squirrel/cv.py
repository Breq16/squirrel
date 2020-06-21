import io

from PIL import Image
import numpy as np
import zbar
import cv2
import picamera

camera = picamera.PiCamera()
camera.resolution = (320, 240)
camera.sharpness = 100
#camera.framerate = 1
#camera.shutter_speed = 100
camera_stream = io.BytesIO()

cv2.namedWindow("Squirrel LPS")

scanner = zbar.Scanner()

while True:
    image = np.empty((320 * 240 * 3,), dtype=np.uint8)
    camera.capture(image, "bgr")
    image = image.reshape((240, 320, 3))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    results = scanner.scan(gray)

    for result in results:
        print(result)
        if result.type == "QR-Code":
            for point in result.position:
                cv2.circle(image, point, 10, (0, 0, 255), 2)

    cv2.imshow("Squirrel LPS", image)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
