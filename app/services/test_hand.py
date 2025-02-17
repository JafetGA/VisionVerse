import cv2
from hand_detection import HandDetector

cap = cv2.VideoCapture(1)  # Use 0 if this is your primary camera
want_to_draw = True

def hand_detection():
    # Initialize detector
    detector = HandDetector()

    # Basic usage (just get coordinates)
    while True:
        success, img = cap.read()
        if not success:
            break
            
        # Get hand detection results
        detection_results = detector.find_hands(img)
        
        if detection_results['coordinates']:
            # Get coordinates and hand types
            for idx, hand_coords in enumerate(detection_results['coordinates']):
                hand_type = detection_results['hand_types'][idx]
                
                # Convert to pixel coordinates if needed
                pixel_coords = detector.get_pixel_coordinates(
                    hand_coords, 
                    detection_results['image_shape']
                )
                
                # Use the coordinates as needed
                print(f"{hand_type} Hand coordinates:", pixel_coords)
        
        # Optionally draw the hands
        if want_to_draw:
            img_with_drawings = detector.draw_hands(img, detection_results)
            cv2.imshow("Image", img_with_drawings)
        else:
            cv2.imshow("Image", img)
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    hand_detection()