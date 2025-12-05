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

# ANSI COLORS FOR TERMINAL
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

def generate_realistic_telemetry(scene, elapsed_time):
    """
    Generates telemetry with organic noise and network jitter.
    """
    # 1. Base Confidence (varies by scenario)
    # Emergency detection is usually higher confidence than counting crowded cars
    if scene['ambulance']:
        base_conf = 0.94
    else:
        base_conf = 0.88
        
    # Add random noise (+/- 5%)
    noise = random.uniform(-0.05, 0.04)
    final_conf = min(0.99, max(0.75, base_conf + noise))
    
    # 2. Realistic Latency Calculation
    # Inference (40ms) + Network RTT (80-200ms) + Jitter
    inference_time = random.uniform(0.035, 0.055)
    network_latency = random.uniform(0.080, 0.200)
    total_latency_ms = int((inference_time + network_latency) * 1000)
    
    # 3. Terminal Logging (The "Matrix" Look)
    timestamp = time.strftime("%H:%M:%S", time.localtime())
    
    # Simulate occasional drops in confidence (Occlusion)
    if final_conf < 0.85:
        print(f"{GREY}[{timestamp}]{RESET} WARN: PARTIAL OCCLUSION DETECTED. CONF: {final_conf*100:.1f}%")
    
    if scene['ambulance']:
        # Math Simulation for Coordinates
        y_pos = 0
        dist_m = 0.0
        
        # Map time to position (Front/Middle/Back)
        if 19 <= elapsed_time < 24:   # FRONT
            y_pos = int(random.uniform(410, 440))
            dist_m = random.uniform(1.2, 1.5)
        elif 34 <= elapsed_time < 39: # MIDDLE
            y_pos = int(random.uniform(220, 260))
            dist_m = random.uniform(4.5, 5.2)
        elif 49 <= elapsed_time < 54: # BACK
            y_pos = int(random.uniform(60, 90))
            dist_m = random.uniform(8.5, 9.2)
            
        x_pos = int(random.uniform(310, 330))
        
        # Only print full logs occasionally to keep it readable
        if random.random() > 0.6:
            print(f"{CYAN}[{timestamp}]{RESET} INFERENCE: {total_latency_ms}ms | {RED}CLASS: AMBULANCE{RESET}")
            print(f"   >>> TRACKING ID: #OBJ_01 [x={x_pos}, y={y_pos}]")
            print(f"   >>> DEPTH: {dist_m:.2f}m | PROBABILITY: {final_conf:.4f}")
            
        return f"Loc: {dist_m:.1f}m", f"{final_conf*100:.1f}%", f"{total_latency_ms}ms"
        
    else:
        # Normal Traffic Logs
        if random.random() > 0.7:
            print(f"{CYAN}[{timestamp}]{RESET} INFERENCE: {total_latency_ms}ms | {GREEN}FLOW: STABLE{RESET}")
            print(f"   >>> DENSITY: R1={scene['r1_count']} | R2={scene['r2_count']}")
            
        return "Scanning...", f"{final_conf*100:.1f}%", f"{total_latency_ms}ms"

@app.route('/reset_system')
def reset_system():
    global start_time
    start_time = time.time()
    print(f"\n{RED}*** HARDWARE INTERRUPT: TIMELINE RESET TO 0s ***{RESET}\n")
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
            
    # Calculate the realistic numbers
    loc_str, conf_str, lat_str = generate_realistic_telemetry(current_scene, loop_time)

    return jsonify({
        "time_index": int(loop_time),
        "scene": current_scene['phase_name'],
        "r1": current_scene['r1_count'],
        "r2": current_scene['r2_count'],
        "amb": current_scene['ambulance'],
        "amb_loc": loc_str,
        "decision": current_scene['decision'],
        "servo1": current_scene['servo1'],
        "servo2": current_scene['servo2'],
        "conf": conf_str,    # Now fluctuates nicely
        "latency": lat_str,  # Now varies realistically
        "log": current_scene['log']
    })

# --- FAST VIDEO PASS-THROUGH ---
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
    print(f"{GREEN}>>> CORTEX AI ENGINE ONLINE.{RESET}")
    print(f"{YELLOW}>>> SENSOR CALIBRATION... COMPLETE.{RESET}")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)