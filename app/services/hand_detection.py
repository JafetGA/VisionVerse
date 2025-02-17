import cv2
import mediapipe as mp
from mediapipe.python.solutions.drawing_utils import DrawingSpec
from typing import List, Tuple, Optional, Dict, Any

class HandDetector:
    def __init__(self, static_image_mode=False, max_num_hands=2, model_complexity=1, 
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initialize the HandDetector with MediaPipe Hands.
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
    def find_hands(self, img) -> Dict[str, Any]:
        """
        Detect hands in the image and return their landmark coordinates.
        
        Args:
            img: Input image in BGR format
            
        Returns:
            Dictionary containing:
            - 'coordinates': List of hand landmarks coordinates (21 points with x, y, z)
            - 'hand_types': List of hand classifications (Left/Right)
            - 'landmarks': Raw MediaPipe landmark objects for drawing
            - 'image_shape': Tuple of image height and width
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        
        all_hands = []
        hand_types = []
        raw_landmarks = []
        
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Get hand coordinates
                hand_points = []
                for landmark in hand_landmarks.landmark:
                    x, y, z = landmark.x, landmark.y, landmark.z
                    hand_points.append((x, y, z))
                
                all_hands.append(hand_points)
                raw_landmarks.append(hand_landmarks)
                
                # Get hand type (Left/Right)
                if results.multi_handedness:
                    hand_type = results.multi_handedness[idx].classification[0].label
                    hand_types.append(hand_type)
        
        return {
            'coordinates': all_hands,
            'hand_types': hand_types if hand_types else None,
            'landmarks': raw_landmarks,
            'image_shape': img.shape[:2]  # (height, width)
        }
    
    @staticmethod
    def draw_hands(img, detection_result: Dict[str, Any], 
                  landmarks_color=(255, 0, 0), connections_color=(0, 255, 0),
                  thickness=1, circle_radius=2):
        """
        Draw hand landmarks and connections on the image.
        
        Args:
            img: Input image
            detection_result: Dictionary returned by find_hands()
            landmarks_color: Color for landmark points (BGR format)
            connections_color: Color for connections between landmarks (BGR format)
            thickness: Thickness of drawn lines
            circle_radius: Radius of landmark circles
            
        Returns:
            Image with drawings
        """
        img_copy = img.copy()
        
        if detection_result['landmarks']:
            mp_draw = mp.solutions.drawing_utils
            mp_hands = mp.solutions.hands
            
            landmarks_style = DrawingSpec(
                color=landmarks_color,
                thickness=thickness,
                circle_radius=circle_radius
            )
            connections_style = DrawingSpec(
                color=connections_color,
                thickness=thickness
            )
            
            for hand_landmarks in detection_result['landmarks']:
                mp_draw.draw_landmarks(
                    img_copy,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    landmarks_style,
                    connections_style
                )
        
        return img_copy
    
    @staticmethod
    def get_pixel_coordinates(coordinates: List[Tuple[float, float, float]], 
                            image_shape: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Convert normalized coordinates to pixel coordinates.
        
        Args:
            coordinates: List of normalized (x, y, z) coordinates
            image_shape: Tuple of (height, width)
            
        Returns:
            List of pixel coordinates (x, y)
        """
        height, width = image_shape
        pixel_coords = []
        
        for x, y, _ in coordinates:
            pixel_x = int(x * width)
            pixel_y = int(y * height)
            pixel_coords.append((pixel_x, pixel_y))
            
        return pixel_coords