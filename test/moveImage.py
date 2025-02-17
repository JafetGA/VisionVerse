import cv2
import numpy as np
import random
import os
import time

# Configuración de velocidades
MOVEMENT_SPEED = 5.0  # Velocidad de movimiento de las imágenes
MIN_CHANGE_INTERVAL = 0.3  # Tiempo mínimo entre cambios de imagen
MAX_CHANGE_INTERVAL = 1.5  # Tiempo máximo entre cambios de imagen
INITIAL_DIRECTION = [  # Direcciones posibles de movimiento
    (1, 0),    # Derecha
    (-1, 0),   # Izquierda
    (0, 1),    # Abajo
    (0, -1),   # Arriba
    (1, 1),    # Diagonal abajo-derecha
    (-1, 1),   # Diagonal abajo-izquierda
    (1, -1),   # Diagonal arriba-derecha
    (-1, -1)   # Diagonal arriba-izquierda
]

class MovingImage:
    def __init__(self, image, position, direction, images_list):
        self.images = images_list
        self.current_image_index = 0
        self.image = image
        self.position = list(position)
        # Normalizar el vector de dirección y multiplicar por la velocidad
        magnitude = sqrt(direction[0]**2 + direction[1]**2)
        self.velocity = [
            direction[0] / magnitude * MOVEMENT_SPEED,
            direction[1] / magnitude * MOVEMENT_SPEED
        ]
        self.size = image.shape[:2]
        self.last_change_time = time.time()
        # Intervalo aleatorio individual para cada imagen
        self.change_interval = random.uniform(MIN_CHANGE_INTERVAL, MAX_CHANGE_INTERVAL)

    def update_image(self):
        current_time = time.time()
        if current_time - self.last_change_time >= self.change_interval:
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.image = self.images[self.current_image_index]
            self.last_change_time = current_time
            # Generar nuevo intervalo aleatorio para el siguiente cambio
            self.change_interval = random.uniform(MIN_CHANGE_INTERVAL, MAX_CHANGE_INTERVAL)

def load_overlay_images(directory, desired_size=(100, 100)):
    images = []
    valid_extensions = ['.png', '.jpg', '.jpeg', '.gif']

    try:
        if os.path.isdir(directory):
            for filename in os.listdir(directory):
                if any(filename.lower().endswith(ext) for ext in valid_extensions):
                    path = os.path.join(directory, filename)
                    overlay = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                    if overlay is not None:
                        overlay = cv2.resize(overlay, desired_size)
                        if overlay.shape[2] == 3:
                            overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2BGRA)
                        images.append(overlay)
    except Exception as e:
        print(f"Error cargando imágenes: {e}")

    if not images:
        colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (255,0,255)]
        for color in colors:
            overlay = np.zeros((desired_size[0], desired_size[1], 4), dtype=np.uint8)
            overlay[:, :, 0] = color[0]
            overlay[:, :, 1] = color[1]
            overlay[:, :, 2] = color[2]
            overlay[:, :, 3] = 255
            images.append(overlay)

    return images

def main():
    num_images = 7

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara")
        return

    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo leer el frame")
        return

    height, width = frame.shape[:2]

    overlays = load_overlay_images('../app/static/img/balloons')
    if not overlays:
        print("No se encontraron imágenes. Usando formas de colores.")

    moving_images = []
    image_size = overlays[0].shape[:2]

    for _ in range(num_images):
        x = random.randint(0, width - image_size[1])
        y = random.randint(0, height - image_size[0])

        # Seleccionar una dirección aleatoria de las predefinidas
        direction = random.choice(INITIAL_DIRECTION)

        moving_images.append(MovingImage(
            overlays[0],
            (x, y),
            direction,
            overlays
        ))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_bgra = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

        for img in moving_images:
            # Actualizar posición
            img.position[0] += img.velocity[0]
            img.position[1] += img.velocity[1]

            # Rebotar en los bordes
            if img.position[0] <= 0 or img.position[0] >= width - img.size[1]:
                img.velocity[0] *= -1
            if img.position[1] <= 0 or img.position[1] >= height - img.size[0]:
                img.velocity[1] *= -1

            # Mantener dentro de los límites
            img.position[0] = max(0, min(img.position[0], width - img.size[1]))
            img.position[1] = max(0, min(img.position[1], height - img.size[0]))

            # Actualizar imagen
            img.update_image()

            # Dibujar imagen
            frame_bgra = overlay_image(frame_bgra, img.image,
                                       (int(img.position[0]), int(img.position[1])))

        frame_final = cv2.cvtColor(frame_bgra, cv2.COLOR_BGRA2BGR)
        cv2.imshow('Multiple Moving Images', frame_final)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

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

if __name__ == "__main__":
    from math import sqrt
    main()