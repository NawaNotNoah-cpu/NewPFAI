import cv2


for i in range(10):

    cap = cv2.VideoCapture(i)

    if cap.isOpened():

        ret, frame = cap.read()

        if ret:
            print(f"Camera {i}: WORKING")
        else:
            print(f"Camera {i}: Opens but no frame")

        cap.release()

    else:

        print(f"Camera {i}: unavailable")