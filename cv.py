import cv2
import mediapipe as mp
import numpy as np
import os

def calculate_angle(a, b, c):
    """Calculate angle between three points."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360-angle
        
    return angle

def analyze_pose(image_path):
    """Analyze pose in an image and return joint angles."""
    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not read image: {image_path}")
        return None
    
    # Convert to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process image
    results = pose.process(image_rgb)
    
    if not results.pose_landmarks:
        print(f"No pose detected in: {image_path}")
        return None
    
    # Get landmarks
    landmarks = results.pose_landmarks.landmark
    
    # Extract coordinates for joints
    joints = {
        # Left side (from image perspective)
        'left_shoulder': [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
        'left_elbow': [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y],
        'left_wrist': [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y],
        'left_hip': [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y],
        'left_knee': [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y],
        'left_ankle': [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                       landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y],
        
        # Right side (from image perspective)
        'right_shoulder': [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y],
        'right_elbow': [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y],
        'right_wrist': [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y],
        'right_hip': [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                      landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y],
        'right_knee': [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y],
        'right_ankle': [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
    }
    
    # Calculate angles
    angles = {
        # Arms
        'left_shoulder': calculate_angle(joints['left_hip'], joints['left_shoulder'], 
                                       joints['left_elbow']),
        'left_elbow': calculate_angle(joints['left_shoulder'], joints['left_elbow'], 
                                     joints['left_wrist']),
        'right_shoulder': calculate_angle(joints['right_hip'], joints['right_shoulder'], 
                                        joints['right_elbow']),
        'right_elbow': calculate_angle(joints['right_shoulder'], joints['right_elbow'], 
                                      joints['right_wrist']),
        
        # Legs
        'left_hip': calculate_angle(joints['left_shoulder'], joints['left_hip'], 
                                  joints['left_knee']),
        'left_knee': calculate_angle(joints['left_hip'], joints['left_knee'], 
                                   joints['left_ankle']),
        'right_hip': calculate_angle(joints['right_shoulder'], joints['right_hip'], 
                                   joints['right_knee']),
        'right_knee': calculate_angle(joints['right_hip'], joints['right_knee'], 
                                    joints['right_ankle'])
    }
    
    pose.close()
    return angles

def main():
    # Specify your image folder path
    image_folder = "./public/poses"  # Update this path
    
    # Process each image in the folder
    for filename in os.listdir(image_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, filename)
            print(f"\nAnalyzing {filename}:")
            
            angles = analyze_pose(image_path)
            if angles:
                print("\nArm angles:")
                print(f"Left Shoulder: {angles['left_shoulder']:.1f}°")
                print(f"Left Elbow: {angles['left_elbow']:.1f}°")
                print(f"Right Shoulder: {angles['right_shoulder']:.1f}°")
                print(f"Right Elbow: {angles['right_elbow']:.1f}°")
                
                print("\nLeg angles:")
                print(f"Left Hip: {angles['left_hip']:.1f}°")
                print(f"Left Knee: {angles['left_knee']:.1f}°")
                print(f"Right Hip: {angles['right_hip']:.1f}°")
                print(f"Right Knee: {angles['right_knee']:.1f}°")

if __name__ == "__main__":
    main()