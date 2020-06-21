import time

import zbar
import cv2

import trackedobject

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 30)
fps = int(cap.get(5))
print("fps:", fps)

cv2.namedWindow("Squirrel LPS")

scanner = zbar.Scanner()

last_frame = time.time()

objects = {}
frame = 0

while True:
    code, image = cap.read()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    results = scanner.scan(gray)

    for result in results:
        print(result)
        if result.type == "QR-Code":
            name = result.data.decode(errors="ignore")
            if name not in objects:
                objects[name] = trackedobject.TrackedObject(name=name)
            objects[name].update(result.position, frame)

    dead_objects = []
    for name, object in objects.items():
        if not object.isActive(frame):
            dead_objects.append(name)

    for name in dead_objects:
        del objects[name]

    new_time = time.time()
    frame_time = new_time - last_frame
    last_frame = new_time

    cv2.putText(image, f"FPS: {int(1/frame_time)}", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0, 255), 3)

    #preview = cv2.resize(image, (640, 480))
    cv2.imshow("Squirrel LPS", image)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    frame += 1

cap.release()
cv2.destroyAllWindows()
