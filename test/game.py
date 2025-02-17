import cv2
import mediapipe as mp
import numpy as np
import random
import os
import time
from math import sqrt
from mediapipe.python.solutions.drawing_utils import DrawingSpec

# Configuración de la cámara
CAMERA = cv2.VideoCapture(1)

# Configuración de velocidades
MOVEMENT_SPEED = 6.0
MIN_CHANGE_INTERVAL = 0.3
MAX_CHANGE_INTERVAL = 1.5
REAPPEAR_DELAY = 1.0  # Tiempo antes de que reaparezca una imagen
INITIAL_DIRECTION = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

# Duración del juego en segundos
GAME_DURATION = 20  

# Diccionario de imágenes
valores = {
    '1.png': 'Rojo',
    '2.png': 'Azul',
    '3.png': 'Amarrillo',
    '4.png': 'Rosa',
    '5.png': 'Verde'
}

class HandDetector:
    def __init__(self, static_image_mode=False, max_num_hands=2, model_complexity=1,
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.draw_spec = self.mp_draw.DrawingSpec(thickness=1, circle_radius=2)

    def find_hands(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                        self.draw_spec, DrawingSpec(color=(255, 0, 0)))
        return img

    def is_hand_closed(self, hand_landmarks):
        # Verificar si la mano está cerrada basándose en la posición de los dedos
        finger_tips = [8, 12, 16, 20]  # Índices de las puntas de los dedos
        thumb_tip = 4
        thumb_base = 2

        # Obtener coordenadas del pulgar
        thumb_tip_pos = hand_landmarks.landmark[thumb_tip]
        thumb_base_pos = hand_landmarks.landmark[thumb_base]

        # Verificar si el pulgar está doblado
        thumb_folded = thumb_tip_pos.x < thumb_base_pos.x

        # Contar dedos doblados
        folded_fingers = 0
        for tip in finger_tips:
            if hand_landmarks.landmark[tip].y > hand_landmarks.landmark[tip - 2].y:
                folded_fingers += 1

        return folded_fingers >= 3 and thumb_folded

    def get_hand_positions(self):
        if not hasattr(self, 'results') or not self.results.multi_hand_landmarks:
            return []

        hand_positions = []
        for hand_landmarks in self.results.multi_hand_landmarks:
            # Usar el punto medio de la palma como posición de la mano
            palm_x = hand_landmarks.landmark[9].x
            palm_y = hand_landmarks.landmark[9].y
            is_closed = self.is_hand_closed(hand_landmarks)
            hand_positions.append((palm_x, palm_y, is_closed))

        return hand_positions

class MovingImage:
    def __init__(self, image, position, direction, images_list, image_name):
        self.images = images_list
        self.current_image_index = 0
        self.image = image
        self.image_name = image_name  # Nombre de la imagen actual
        self.position = list(position)
        self.visible = True
        self.hidden_time = None
        magnitude = sqrt(direction[0]**2 + direction[1]**2)
        self.velocity = [
            direction[0] / magnitude * MOVEMENT_SPEED,
            direction[1] / magnitude * MOVEMENT_SPEED
        ]
        self.size = image.shape[:2]
        self.last_change_time = time.time()
        self.change_interval = random.uniform(MIN_CHANGE_INTERVAL, MAX_CHANGE_INTERVAL)

    def update_image(self):
        if not self.visible:
            if time.time() - self.hidden_time >= REAPPEAR_DELAY:
                self.visible = True
                self.position = [
                    random.randint(0, frame_width - self.size[1]),
                    random.randint(0, frame_height - self.size[0])
                ]
            return

        current_time = time.time()
        if current_time - self.last_change_time >= self.change_interval:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.image = self.images[self.current_image_index]
            self.image_name = list(overlays.keys())[self.current_image_index]  # Actualizar el nombre de la imagen
            self.last_change_time = current_time
            self.change_interval = random.uniform(MIN_CHANGE_INTERVAL, MAX_CHANGE_INTERVAL)

    def check_hand_collision(self, hand_x, hand_y, frame_width, frame_height, is_closed):
        if not self.visible:
            return False

        # Convertir coordenadas normalizadas de la mano a píxeles
        hand_pixel_x = int(hand_x * frame_width)
        hand_pixel_y = int(hand_y * frame_height)

        # Verificar si la mano está dentro del área de la imagen
        image_x1 = self.position[0]
        image_y1 = self.position[1]
        image_x2 = self.position[0] + self.size[1]
        image_y2 = self.position[1] + self.size[0]

        if (image_x1 <= hand_pixel_x <= image_x2 and
                image_y1 <= hand_pixel_y <= image_y2 and
                is_closed):
            self.visible = False
            self.hidden_time = time.time()
            return True
        return False

def load_overlay_images(directory, desired_size=(100, 100)):
    images = {}
    color_files = ['1.png', '2.png', '3.png', '4.png', '5.png']

    try:
        if os.path.isdir(directory):
            for filename in color_files:
                path = os.path.join(directory, filename)
                if os.path.isfile(path):
                    overlay = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                    if overlay is not None:
                        overlay = cv2.resize(overlay, desired_size)
                        if overlay.shape[2] == 3:
                            overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2BGRA)
                        images[filename] = overlay
    except Exception as e:
        print(f"Error cargando imágenes: {e}")

    if len(images) < 5:
        colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255)]
        for i, color in enumerate(colors):
            overlay = np.zeros((desired_size[0], desired_size[1], 4), dtype=np.uint8)
            overlay[:, :, 0] = color[0]
            overlay[:, :, 1] = color[1]
            overlay[:, :, 2] = color[2]
            overlay[:, :, 3] = 255
            images[f'{i+1}.png'] = overlay

    return images

def overlay_image(background, foreground, position):
    bh, bw = background.shape[:2]
    fh, fw = foreground.shape[:2]
    x, y = position

    x = max(0, min(x, bw - fw))
    y = max(0, min(y, bh - fh))

    alpha = foreground[:, :, 3] / 255.0

    for c in range(3):
        background[y:y+fh, x:x+fw, c] = background[y:y+fh, x:x+fw, c] * (1 - alpha) + \
                                        foreground[:, :, c] * alpha

    return background

def main():
    global frame_width, frame_height, overlays


    cap = CAMERA
    detector = HandDetector()

    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara")
        return

    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo leer el frame")
        return

    frame_height, frame_width = frame.shape[:2]

    overlays = load_overlay_images('app/static/img/balloons')
    if not overlays:
        print("No se encontraron imágenes. Usando formas de colores.")

    moving_images = []
    image_size = list(overlays.values())[0].shape[:2]
    captured_count = {filename: 0 for filename in overlays.keys()}  # Contadores para cada imagen

    for filename, overlay in overlays.items():
        x = random.randint(0, frame_width - image_size[1])
        y = random.randint(0, frame_height - image_size[0])
        direction = random.choice(INITIAL_DIRECTION)
        moving_images.append(MovingImage(overlay, (x, y), direction, list(overlays.values()), filename))

    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = detector.find_hands(frame)
        hand_positions = detector.get_hand_positions()

        frame_bgra = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

        for img in moving_images:
            if img.visible:
                img.position[0] += img.velocity[0]
                img.position[1] += img.velocity[1]

                if img.position[0] <= 0 or img.position[0] >= frame_width - img.size[1]:
                    img.velocity[0] *= -1
                if img.position[1] <= 0 or img.position[1] >= frame_height - img.size[0]:
                    img.velocity[1] *= -1

                img.position[0] = max(0, min(img.position[0], frame_width - img.size[1]))
                img.position[1] = max(0, min(img.position[1], frame_height - img.size[0]))

                for hand_x, hand_y, is_closed in hand_positions:
                    if img.check_hand_collision(hand_x, hand_y, frame_width, frame_height, is_closed):
                        captured_count[img.image_name] += 1
                        break

            img.update_image()

            if img.visible:
                frame_bgra = overlay_image(frame_bgra, img.image,
                                           (int(img.position[0]), int(img.position[1])))

        # Mostrar contador de imágenes capturadas
        frame_final = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)

        cv2.imshow('Hand Interaction with Images', frame_final)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Verificar si el tiempo del juego ha terminado
        if time.time() - start_time >= GAME_DURATION:
            break

    cap.release()
    cv2.destroyAllWindows()

    # Imprimir el número de imágenes capturadas en consola
    for filename, count in captured_count.items():
        print(f"{valores[filename]}: {count}")

if __name__ == "__main__":
    frame_width = 0
    frame_height = 0
    main()