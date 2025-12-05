import time
import json
import cv2
import numpy as np
from flask import Flask, render_template, jsonify, Response, request
import random

app = Flask(__name__)

# GLOBAL STATE
start_time = time.time()
script_data = {}
current_frame = None

# ANSI COLORS 
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
GREY = "\033[90m"
RESET = "\033[0m"

def load_script():
    global script_data
    with open('simulation_script.json', 'r') as f:
        script_data = json.load(f)

load_script()

def simulate_ai_math(scene, elapsed_time):
    """
    Generates realistic looking coordinates and confidence scores
    instead of just printing text.
    """
    # 1. Random Processing Time (Simulate GPU Lag)
    inference_time = random.uniform(0.018, 0.042)
    
    # 2. Header Log
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    print(f"{GREY}[{timestamp}]{RESET} GPU_0: YOLOv8n inference completed in {inference_time*1000:.1f}ms")

    # 3. Simulate Coordinate Logic
    if scene['ambulance']:
        # Simulate different positions based on the specific time in the loop
        # We know specific times map to Front/Middle/Back based on your scenario
        
        y_pos = 0
        dist_m = 0.0
        
        # LOGIC MAP based on your 54s script
        if 19 <= elapsed_time < 24:
            # FRONT (Close to camera, high Y value)
            y_pos = int(random.uniform(400, 450)) 
            dist_m = random.uniform(1.2, 1.8)
        elif 34 <= elapsed_time < 39:
            # MIDDLE
            y_pos = int(random.uniform(200, 250))
            dist_m = random.uniform(4.0, 5.5)
        elif 49 <= elapsed_time < 54:
            # BACK (Far from camera, low Y value)
            y_pos = int(random.uniform(50, 100))
            dist_m = random.uniform(8.0, 9.5)
            
        x_pos = int(random.uniform(300, 340)) # Roughly centered horizontally
        
        # PRINT THE "CALCULATION"
        print(f"   {RED}>>> OBJECT_DETECTED: CLASS_ID 1 (AMBULANCE){RESET}")
        print(f"   >>> BBOX_COORDS: [x={x_pos}, y={y_pos}, w=60, h=120]")
        print(f"   >>> CENTROID_CALC: ({x_pos+30}, {y_pos+60})")
        print(f"   >>> DEPTH_ESTIMATION: {dist_m:.2f} meters")
        print(f"   {CYAN}>>> LOGIC TRIGGER: PREEMPTION_PROTOCOL_INITIATED{RESET}")
        
        return f"Loc: {dist_m:.1f}m (y={y_pos})"
    
    elif "RESET" in scene['phase_name']:
        print(f"   {YELLOW}>>> SCENE_CHANGE: Re-initializing Tracker...{RESET}")
        print(f"   >>> BACKGROUND_SUBTRACTION: Calibrating...")
        return "Calibrating..."
        
    else:
        # Normal Traffic Math
        total_cars = scene['r1_count'] + scene['r2_count']
        density = (total_cars / 20) * 100 # Fake density calc
        print(f"   {GREEN}>>> OBJECTS_DETECTED: {total_cars} VEHICLES{RESET}")
        print(f"   >>> LANE_DENSITY: {density:.1f}% Saturation")
        print(f"   >>> DECISION_MATRIX: {scene['decision']} PRIORITY")
        return "Scanning..."

    print("-" * 50)

# --- ROUTES ---

@app.route('/reset_system')
def reset_system():
    global start_time
    start_time = time.time()
    print(f"\n{RED}*** HARDWARE INTERRUPT RECEIVED: SYSTEM ZEROED ***{RESET}\n")
    return jsonify({"status": "system_reset"})

@app.route('/')
def phone(): return render_template('phone.html')

@app.route('/monitor')
def monitor(): return render_template('monitor.html')

@app.route('/report')
def report(): return render_template('report.html')

@app.route('/telemetry')
def telemetry():
    elapsed = (time.time() - start_time)
    loop_time = elapsed % script_data['loop_duration']
    
    current_scene = script_data['timeline'][0]
    for scene in script_data['timeline']:
        if scene['start'] <= loop_time < scene['end']:
            current_scene = scene
            break
            
    # Run the "Math Simulator" to print logs
    # We only print every ~500ms to avoid flooding
    if random.random() > 0.5:
        log_output = simulate_ai_math(current_scene, loop_time)
    else:
        # Just generate the string for the dashboard without printing
        log_output = "Processing..." 

    return jsonify({
        "time_index": int(loop_time),
        "scene": current_scene['phase_name'],
        "r1": current_scene['r1_count'],
        "r2": current_scene['r2_count'],
        "amb": current_scene['ambulance'],
        "amb_loc": log_output, # Send the calculated math to dashboard
        "decision": current_scene['decision'],
        "servo1": current_scene['servo1'],
        "servo2": current_scene['servo2'],
        "conf": f"{random.uniform(98.5, 99.9):.1f}%",
        "latency": f"{random.uniform(12, 18):.0f}ms"
    })

# --- VIDEO PASS-THROUGH ---
@app.route('/upload', methods=['POST'])
def upload():
    global current_frame
    try:
        file = request.files['frame']
        file_bytes = file.read()
        npimg = np.frombuffer(file_bytes, np.uint8)
        current_frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        return "ok"
    except: return "error"

def gen_frames():
    while True:
        if current_frame is not None:
            try:
                ret, buffer = cv2.imencode('.jpg', current_frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
                frame = buffer.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except: pass
        time.sleep(0.05)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print(f"{GREEN}>>> NEURAL ENGINE INITIALIZED.{RESET}")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)