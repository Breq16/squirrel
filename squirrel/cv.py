import time

import zbar
import cv2

camera = cv2.VideoCapture(0)

cv2.namedWindow("Squirrel LPS")

scanner = zbar.Scanner()

last_frame = time.time()

while True:
    code, image = camera.read()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    results = scanner.scan(gray)

    for result in results:
        print(result)
        if result.type == "QR-Code":
            for point in result.position:
                cv2.circle(image, point, 10, (0, 0, 255), 2)

    new_time = time.time()
    frame_time = new_time - last_frame
    last_frame = new_time

    cv2.putText(image, f"FPS: {int(1/frame_time)}", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0, 255), 3)

    preview = cv2.resize(image, (640, 480))
    cv2.imshow("Squirrel LPS", preview)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
