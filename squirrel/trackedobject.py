

class TrackedObject:
    def __init__(self, name=None, size=None, data=None):
        if data:
            self.size = data[0]
            self.name = data[1:].decode(errors="ignore")
        else:
            self.name = name
            self.size = size

        self.lastSeen = 0
        self.corners = None

    def update(self, corners, frame):
        self.lastSeen = frame
        self.corners = corners

    def isActive(self, frame, threshold=5):
        return frame - self.lastSeen < threshold
