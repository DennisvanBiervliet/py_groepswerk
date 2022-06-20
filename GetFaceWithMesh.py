import cv2
import mediapipe as mp
from mediapipe.python.solutions.face_mesh import FaceMesh
import os
from deepface import DeepFace
from datetime import datetime


# Alle objecten initialiseren
face_cascade = cv2.CascadeClassifier("static/haarcascade_frontalface_default.xml")
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
cap = cv2.VideoCapture(0)


def process_image(mesh: FaceMesh, copy_image: bool = True):
    # Webcam lezen en beeld selecteren
    success, image = cap.read()

    if copy_image:
        frame = image.copy()
    else:
        frame = None

    # Beeld van rgb naar bgr voor open cv, bewerkbaar maken
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = mesh.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Facemesh construeren en op beeld tekenen
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            mp_drawing.draw_landmarks(image, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION,
                                      mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                                      mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
                                      )

    return image, frame


# Code om beeld te generen dat leesbaar/toonbaar is op html site
def gen_frames():
    with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
        while True:
            image, frame = process_image(mesh=face_mesh, copy_image=True)

            # Beeld omzetten in grijswaarden om beter te kunnen lezen
            gray = cv2.cvtColor(frame,
                                cv2.COLOR_BGR2GRAY)

            result = DeepFace.analyze(frame, actions=tuple(['emotion']), enforce_detection=False)

            # Happiness-score en dominante emotie genereren
            emotion = result["emotion"]["happy"]
            dominant_emotion = result["dominant_emotion"]

            txt1 = f"Happiness score = {emotion/10:.2f}"
            txt2 = f"Dominant emotion = {dominant_emotion}"

            # Happiness-score en dominante emotie tonen op beeld
            text_depth = 50

            for text in txt1, txt2:
                cv2.putText(image, text, (50, text_depth), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 0, 255), 3
                text_depth += 30

            # Proces beëindigen
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
            ret, buffer = cv2.imencode('.jpg', image)
            image = buffer.tobytes()

            yield (b'--image\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n')

        cv2.destroyAllWindows()


# Functie om een opname (still) van het beeld van camera met facemesh te maken
def capture(username):
    # Filename genereren zodat het opgeslagen kan worden
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    path = os.path.join('static', f'{username}_{now}.jpg')

    with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
        while True:
            success, image = cap.read()
            image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = face_mesh.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(image, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION,
                                              mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                                              mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
                                              )

            cv2.imwrite(path, image)
            break

    return path, now


# Analyseer de emotie data van opname en return voor weergave
def analyze(path):
    image_path = cv2.imread(path)
    analysis = DeepFace.analyze(image_path, actions=tuple(['emotion']), enforce_detection=False)
    result = analysis["emotion"]

    for emo, value in result.items():
        result[emo] = round(value/10, 2)

    score = analysis["emotion"]["happy"]

    return result, score
