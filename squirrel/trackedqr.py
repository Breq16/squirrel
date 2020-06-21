import numpy as np

class TrackedQRType:
    # Code Type
    MASK_TYPE = 0x80
    REFERENCE = 0x00
    TARGET = 0x80
    # Code Plane
    MASK_PLANE = 0x60
    PLANE_XY = 0x00
    PLANE_XZ = 0x20
    PLANE_YZ = 0x40
    # Code Preference
    MASK_PREFERENCE = 0x10
    PRIMARY = 0x00
    SECONDARY = 0x10
    # Code Size
    MASK_SIZE = 0x0F
    SIZES_CM = {  # loosely based off E6 series
        0x0: 1.0,
        0x1: 1.5,
        0x2: 2.0,
        0x3: 3.0,
        0x4: 5.0,
        0x5: 7.0,
        0x6: 10,
        0x7: 15,
        0x8: 20,
        0x9: 30,
        0xA: 50,
        0xB: 70,
        0xC: 100,
    }

class TrackedQR:
    def __init__(self, data):
        self.type_code = data[0]
        self.name = data[1:].decode(errors="ignore")

        self.size = TrackedQRType.SIZES_CM[self.type_code & TrackedQRType.MASK_SIZE]
        self.isReference = self.type_code & TrackedQRType.MASK_TYPE == TrackedQRType.REFERENCE

        self.lastSeen = 0
        self.corners = None

    def update(self, corners, frame):
        self.lastSeen = frame
        self.corners = corners

    def isActive(self, frame, threshold=15):
        return frame - self.lastSeen <= threshold

    def isCurrent(self, frame, threshold=0):
        return frame - self.lastSeen <= threshold

    def getCentroid(self):
        if self.corners is None:
            return

        def getCentroidTriangle(a, b, c):
            x = (a[0] + b[0] + c[0]) / 3
            y = (a[1] + b[1] + c[1]) / 3
            return (x, y)

        centroids = (getCentroidTriangle(self.corners[0], self.corners[1], self.corners[2]),
                     getCentroidTriangle(self.corners[0], self.corners[1], self.corners[3]),
                     getCentroidTriangle(self.corners[0], self.corners[2], self.corners[3]),
                     getCentroidTriangle(self.corners[1], self.corners[2], self.corners[3]))

        def lineLineIntersection(a, b, c, d):
            ab = np.linalg.det(np.array([a, b]))
            cd = np.linalg.det(np.array([c, d]))
            abx = np.linalg.det(np.array([[a[0], 1], [b[0], 1]]))
            cdx = np.linalg.det(np.array([[c[0], 1], [d[0], 1]]))
            aby = np.linalg.det(np.array([[a[1], 1], [b[1], 1]]))
            cdy = np.linalg.det(np.array([[c[1], 1], [d[1], 1]]))

            xnum = np.linalg.det(np.array([[ab, abx], [cd, cdx]]))
            ynum = np.linalg.det(np.array([[ab, aby], [cd, cdy]]))
            denom = np.linalg.det(np.array([[abx, aby], [cdx, cdy]]))

            return (xnum / denom, ynum / denom)

        centroid = lineLineIntersection(centroids[0], centroids[2], centroids[1], centroids[3])
        return centroid

    def getFrontMidpoint(self):
        x = (self.corners[0][0] + self.corners[3][0]) / 2
        y = (self.corners[0][1] + self.corners[3][1]) / 2
        return (x, y)

    def getTransformMatrices(self):
        def mapBasisToPoints(points):
            homoPoints = [np.array([[point[0]], [point[1]], [1]]) for point in points]

            threePoints = np.concatenate(homoPoints[:3], axis=1)

            coefficients = np.matmul(np.linalg.inv(threePoints), homoPoints[3])

            scaled = np.matmul(threePoints, np.array([[coefficients[0][0], 0, 0],
                                                      [0, coefficients[1][0], 0],
                                                      [0, 0, coefficients[2][0]]]))
            return scaled

        sceneCorners = ((0, 0), (0, self.size), (self.size, self.size), (self.size, 0))

        basisToPicture = mapBasisToPoints(self.corners)
        basisToScene = mapBasisToPoints(sceneCorners)

        pictureToScene = np.matmul(basisToScene, np.linalg.inv(basisToPicture))
        sceneToPicture = np.matmul(basisToPicture, np.linalg.inv(basisToScene))

        pictureToScene /= pictureToScene[2][2]
        sceneToPicture /= sceneToPicture[2][2]

        return pictureToScene, sceneToPicture
