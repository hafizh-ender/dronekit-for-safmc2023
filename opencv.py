# First import the library
from disNat import poseEstim, callback
import pyrealsense2 as rs
import cv2

def threshold(x,y):
  if (abs(x) <= 8 and abs(y) <= 8):
    return 1

# idDistArray.get(i)
def changeId(idDistArr, currId):
    # sort tuple idDistArr by distance idDistArr = {id:distanc, id:distance, ...}
    sorted_dict = sorted(idDistArr.items(), key=lambda x: x[1])
    # get the id of the seconde closest marker
    if len(sorted_dict) >= 2:
      id = sorted_dict[1][0]
      return id
    elif (len(sorted_dict) == 1 and sorted_dict[0][0] != currId):
      return sorted_dict[0][0]
    else:
      return None

def arucoFollower(): 
    currId = 0
    lastId = 2
    bannedId = []

    # Declare RealSense pipeline, encapsulating the actual device and sensors
    pipe = rs.pipeline()

    # Build config object and stream everything
    cfg = rs.config()

    # Start streaming with our callback
    pipe.start(cfg, callback)

    try:
      IdDistArr = {}

      # Retreive the stream and intrinsic properties for both cameras
      profiles = pipe.get_active_profile()
      streams = {"left"  : profiles.get_stream(rs.stream.fisheye, 1).as_video_stream_profile(),
              "right" : profiles.get_stream(rs.stream.fisheye, 2).as_video_stream_profile()}

      isNewId = False
      x, y, idDistArr, id, command = poseEstim(currId, bannedId, IdDistArr, streams, isNewId)

      while (currId != lastId) or (currId == lastId and not threshold(x, y)):
          if threshold(x,y):
              bannedId.append(currId)
              print(f"banned id: {bannedId}")
              newId = changeId(idDistArr, currId)

              while newId is None:
                  print("Scanning other aruco markers")
                  isNewId = True
                  x, y, idDistArr, id, command = poseEstim(currId, bannedId, IdDistArr, streams, isNewId)
                  # print(newId)
                  newId = changeId(idDistArr, currId)
                  isNewId = False

              del idDistArr[currId]
              currId = newId

          x, y, idDistArr, id, command = poseEstim(currId, bannedId, IdDistArr, streams, isNewId)

    finally:
      print("Selesai")
      pipe.stop()
if __name__ == "__main__":
  arucoFollower()