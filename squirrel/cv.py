import time

import zbar
import cv2

import trackedobject
import environment

e = environment.Environment()
e.open()
e.run()
e.close()
