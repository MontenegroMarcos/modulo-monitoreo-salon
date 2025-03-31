from ultralytics import YOLO
from picamera2 import Picamera2

#picamera solo funciona en Distribuciones de Linux como la de Raspbian (Raspberry)


def count_people(model)-> int:
    """Counts the people that the camera sees
    """
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
    picam2.start()

    frame = picam2.capture_array()
    picam2.close()

    results = model(frame)
    return sum(1 for det in results[0].boxes.cls if int(det) == 0)
    