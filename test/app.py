import cv2
from hand_detector import HandDetector
cap = cv2.VideoCapture(0)


def hand_detection():
    detector = HandDetector()
    while True:
        success, img = cap.read()
        if not success:
            break
        img = detector.find_hands(img)
        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    hand_detection()