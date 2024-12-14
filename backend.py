from flask import Flask, jsonify, render_template, Response, request
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import math

app = Flask(__name__)
CORS(app)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

camera = cv2.VideoCapture(0)
score = 0
scoring_effect = 0
current_pose_val = 0

def calculate_angle(a, b, c):
    """
    Calculate angle between three points.
    Args:
        a: first point [x, y]
        b: mid point [x, y]
        c: end point [x, y]
    Returns:
        angle in degrees
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360-angle
        
    return angle

POSE_TARGETS = {
    0: {  # Downward Dog
        'left_shoulder': 104.5,
        'left_elbow': 112.4,
        'right_shoulder': 117.8,
        'right_elbow': 162.7,
        'left_hip': 102.3,
        'left_knee': 164.1,
        'right_hip': 29.3,
        'right_knee': 163.6
    },
    1: {  # Tree Pose
        'left_shoulder': 99.5,
        'left_elbow': 171.9,
        'right_shoulder': 87.9,
        'right_elbow': 179.4,
        'left_hip': 167.1,
        'left_knee': 167.7,
        'right_hip': 114.2,
        'right_knee': 57.3
    },
    2: {  # Warrior 1
        'left_shoulder': 140.1,
        'left_elbow': 169.6,
        'right_shoulder': 151.3,
        'right_elbow': 178.7,
        'left_hip': 146.7,
        'left_knee': 115.2,
        'right_hip': 107.0,
        'right_knee': 52.9
    },
    3: {  # Warrior 2
        'left_shoulder': 71.4,
        'left_elbow': 177.3,
        'right_shoulder': 104.4,
        'right_elbow': 176.5,
        'left_hip': 148.8,
        'left_knee': 166.5,
        'right_hip': 125.5,
        'right_knee': 138.4
    }
}

def calculate_pose_score(current_angles, target_pose_val):
    """
    Calculate how well the current pose matches the target pose.
    Returns a score from 1-4:
    1: Poor match (X)
    2: Okay match
    3: Great match
    4: Perfect match
    """
    if target_pose_val not in POSE_TARGETS:
        return 1
    
    target_angles = POSE_TARGETS[target_pose_val]
    
    # Define angle difference thresholds for scoring
    PERFECT_THRESHOLD = 35  # Within 15 degrees
    GREAT_THRESHOLD = 45    # Within 25 degrees
    OKAY_THRESHOLD = 65     # Within 35 degrees
    
    # Calculate differences for each angle
    differences = []
    for joint, target_angle in target_angles.items():
        if joint in current_angles:
            diff = abs(current_angles[joint] - target_angle)
            differences.append(diff)
    
    if not differences:
        return 1
    
    # Calculate average difference
    avg_difference = sum(differences) / len(differences)
    
    # Count how many angles are within thresholds
    angles_within_perfect = sum(1 for diff in differences if diff <= PERFECT_THRESHOLD)
    angles_within_great = sum(1 for diff in differences if diff <= GREAT_THRESHOLD)
    angles_within_okay = sum(1 for diff in differences if diff <= OKAY_THRESHOLD)
    
    total_angles = len(differences)
    
    # Scoring logic
    if angles_within_perfect >= total_angles * 0.75:  # 75% of angles are near perfect
        return 4  # Perfect
    elif angles_within_great >= total_angles * 0.75:  # 75% of angles are great
        return 3  # Great
    elif angles_within_okay >= total_angles * 0.75:   # 75% of angles are okay
        return 2  # Okay
    else:
        return 1  # Poor match

def gen_frames():
    global current_pose_val, scoring_effect
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Flip the frame horizontally for a selfie-view display
        frame = cv2.flip(frame, 1)
        
        # Convert the BGR image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # Make detection
        results = pose.process(image)
        
        # Draw the pose annotation on the image
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.pose_landmarks:
            # Draw pose landmarks
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            # Calculate and display angles for key joints
            # Example: Right elbow angle
            landmarks = results.pose_landmarks.landmark
            
            # Right arm (shoulder, elbow, wrist)
            left_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            left_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            left_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            # Left arm (shoulder, elbow, wrist)
            right_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            right_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            right_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # Right leg (hip, knee, ankle)
            left_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            left_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            left_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

            # Left leg (hip, knee, ankle)
            right_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            right_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            right_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            # Calculate angles for left side
            left_shoulder_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
            left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
            left_hip_angle = calculate_angle(left_hip, left_knee, left_ankle)
            left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)

            # Calculate angles for right side
            right_shoulder_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
            right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
            right_hip_angle = calculate_angle(right_hip, right_knee, right_ankle)
            right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)

            # Display angles on frame
            h, w, c = image.shape

            """
            # Right arm angles
            cv2.putText(image, f'Left Elbow: {int(left_elbow_angle)}deg', 
                        (int(left_elbow[0] * w), int(left_elbow[1] * h) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, f'Left Shoulder: {int(left_shoulder_angle)}deg', 
                        (int(left_shoulder[0] * w), int(left_shoulder[1] * h) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # Right leg angles
            cv2.putText(image, f'Left Hip: {int(left_hip_angle)}deg', 
                        (int(left_hip[0] * w), int(left_hip[1] * h) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, f'Left Knee: {int(left_knee_angle)}deg', 
                        (int(left_knee[0] * w), int(left_knee[1] * h) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # Left arm angles (ensure text positions are flipped correctly)
            cv2.putText(image, f'Right Elbow: {int(right_elbow_angle)}deg', 
                        (int(right_elbow[0] * w), int(right_elbow[1] * h) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, f'Right Shoulder: {int(right_shoulder_angle)}deg', 
                        (int(right_shoulder[0] * w), int(right_shoulder[1] * h) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # Left leg angles
            cv2.putText(image, f'Right Hip: {int(right_hip_angle)}deg', 
                        (int(right_hip[0] * w), int(right_hip[1] * h) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, f'Right Knee: {int(right_knee_angle)}deg', 
                        (int(right_knee[0] * w), int(right_knee[1] * h) - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            """
            
            current_angles = {
                'left_shoulder': left_shoulder_angle,
                'left_elbow': left_elbow_angle,
                'right_shoulder': right_shoulder_angle,
                'right_elbow': right_elbow_angle,
                'left_hip': left_hip_angle,
                'left_knee': left_knee_angle,
                'right_hip': right_hip_angle,
                'right_knee': right_knee_angle
            }

            # Get the current target pose value (you'll need to pass this from the frontend)
            # For testing, you can hardcode a value
            pose_score = calculate_pose_score(current_angles, current_pose_val)

            scoring_effect = pose_score

        ret, buffer = cv2.imencode('.jpg', image)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/current_pose', methods=['POST'])
def update_current_pose():
    global current_pose_val
    try:
        data = request.get_json()
        new_pose_val = data.get('poseValue', 0)
        if isinstance(new_pose_val, (int, float)) and 0 <= new_pose_val <= 3:
            current_pose_val = int(new_pose_val)
            return jsonify({'status': 'success', 'current_pose': current_pose_val})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid pose value'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/get_scoring_effect', methods=['GET'])
def get_scoring_effect():
    global scoring_effect
    return jsonify({'scoringEffect': scoring_effect})

@app.route('/update_score', methods=['POST'])
def update_score():
    global score, scoring_effect
    data = request.get_json()
    scoring_effect = data.get('scoringEffect', 1)
    
    if scoring_effect == 1:
        score -= 50
    elif scoring_effect == 2:
        score += 10
    elif scoring_effect == 3:
        score += 30
    elif scoring_effect == 4:
        score += 50
    
    return jsonify({'score': score, 'scoringEffect': scoring_effect})

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')