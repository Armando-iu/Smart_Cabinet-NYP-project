from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import socket
import threading
import time
import json
from PIL import Image
import io
import atexit
import base64
from flask_socketio import SocketIO
# from ultralytics import YOLO


scheduler = BackgroundScheduler()
scheduler.start()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

socketio = SocketIO(app)

HEADER_SIZE = 30
client_to_send = {}
last_data_time = None  # Track the time of the last successful data reception

class Hr(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hr = db.Column(db.String(20), nullable=False)
    Date = db.Column(db.String(20), nullable=False)
    Date_ID = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"User('{self.hr}', '{self.Date}', '{self.Date_ID}')"

class Temp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temp = db.Column(db.String(20), unique=False, nullable=False)
    Date = db.Column(db.String(20), unique=False, nullable=False)
    Date_ID = db.Column(db.String(20), unique=False, nullable=False)

    def __repr__(self):
        return f"User('{self.temp}', '{self.Date}', '{self.Date_ID}')"

class Paitent_login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(20), unique=True, nullable=False)
    Username = db.Column(db.String(20), unique=True, nullable=False)
    Password = db.Column(db.String(20), unique=True, nullable=False)
    TwoFA = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.Email}', '{self.Username}', '{self.Password}','{self.TwoFA}')"

class DrLogin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Dr_ID = db.Column(db.String(20), unique=True, nullable=False)
    Dr_name = db.Column(db.String(20), unique=True, nullable=False)
    Dr_IC = db.Column(db.String(20), unique=True, nullable=False)
    TwoFA = db.Column(db.String(20), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.Dr_ID}', '{self.Dr_name}', '{self.Dr_IC}', '{self.TwoFA}')"
 
class Health_report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.String(20), unique=False, nullable=False)
    triglyceride = db.Column(db.String(20), unique=False, nullable=False)
    hdl_c = db.Column(db.String(20), unique=False, nullable=False)
    ldl = db.Column(db.String(20), unique=False, nullable=False)
    chol_hdl = db.Column(db.String(20), unique=False, nullable=False)
    bilirubin = db.Column(db.String(20), unique=False, nullable=False)
    alt = db.Column(db.String(20), unique=False, nullable=False)
    ast = db.Column(db.String(20), unique=False, nullable=False)
    alp = db.Column(db.String(20), unique=False, nullable=False)
    golbulin = db.Column(db.String(20), unique=False, nullable=False)
    protein = db.Column(db.String(20), unique=False, nullable=False)
    albumin = db.Column(db.String(20), unique=False, nullable=False)
    creatinine = db.Column(db.String(20), unique=False, nullable=False)
    potassium = db.Column(db.String(20), unique=False, nullable=False)
    egfr = db.Column(db.String(20), unique=False, nullable=False)
    hba1c = db.Column(db.String(20), unique=False, nullable=False)

    def __repr__(self):
        return f"HealthReport('{self.total}', '{self.triglyceride}', '{self.hdl_c}', '{self.ldl}', '{self.chol_hdl}', '{self.bilirubin}', '{self.alt}', '{self.ast}', '{self.alp}', '{self.golbulin}', '{self.protein}', '{self.albumin}', '{self.creatinine}', '{self.potassium}', '{self.egfr}', '{self.hba1c}')"

class DoctorAdvice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cardiovascular = db.Column(db.String(500), nullable=False)
    glucose = db.Column(db.String(500), nullable=False)
    diet = db.Column(db.String(500), nullable=False)
    exercise = db.Column(db.String(500), nullable=False)
    mental = db.Column(db.String(500), nullable=False)
    respiratory = db.Column(db.String(500), nullable=False)
    digestive = db.Column(db.String(500), nullable=False)
    bone = db.Column(db.String(500), nullable=False)
    immunizations = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"DoctorAdvice('{self.cardiovascular}', '{self.glucose}', '{self.diet}', '{self.exercise}', '{self.mental}', '{self.respiratory}', '{self.digestive}', '{self.bone}',  '{self.immunizations}')"


class food_nutrition (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(20), nullable=False)
    Energy = db.Column(db.String(20), nullable=False)
    Fat = db.Column(db.String(20), nullable=False)
    sugar = db.Column(db.String(20), nullable=False)
    Fiber = db.Column(db.String(20), nullable=False)
    Protiens = db.Column(db.String(20), nullable=False)
    Salt = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"DoctorAdvice('{self.food_name}', '{self.Energy}', '{self.Fat}', '{self.sugar}', '{self.Fiber}','{self.Protiens}','{self.Salt}')"

@app.route("/")
def User():
    return render_template('User_login_page.html')

@app.route("/Dr")
def Dr():
    return render_template('Dr_login_Page.html')

@app.route('/main_page')
def main_page():
    return render_template('main_page.html')

@app.route("/habit_tracker")
def habit_tracker():
    return render_template('habit_tracker.html')

@app.route("/habit_tracker2")
def habit_tracker2():
    return render_template('habit_tracker2.html')

@app.route("/Health Report")
def Health_Report():
    return render_template('Health Report.html')

@app.route("/cabinet")
def cabinet():
    return render_template('cabinet.html')

@app.route('/health_monitoring')
def hm():
    latest_temp_data = Temp.query.order_by(Temp.Date.desc()).first()
    latest_hr_data = Hr.query.order_by(Hr.Date.desc()).first()
    if latest_temp_data:
        return render_template('health_monitoring.html', temperature=latest_temp_data.temp, date=latest_temp_data.Date, hr=latest_hr_data.hr)
    else:
        return render_template('health_monitoring.html', temperature=None, date=None, hr=None)

@app.route("/health_monitoring SM")
def hm_SM():
    return render_template('health_monitoring SM.html')

@app.route("/health_monitoring O2")
def hm_O2():
    return render_template('health_monitoring O2.html')

@app.route("/health_monitoring HR")
def hm_HR():
    return render_template('health_monitoring HR.html')

@app.route("/health_monitoring BP")
def hm_BP():
    return render_template('health_monitoring BP.html')

@app.route("/paitent_report")
def paitent_report():
    return render_template('paitent_report.html')

@app.route("/paitent_coment")
def paitent_rcoment():
    return render_template('paitent_coment.html')

@app.route('/doctor_comment')
def doctor_commnet():
    return render_template('doctor_comment.html')

@app.route('/get_latest_data')
def get_latest_data():
    latest_temp_data = Temp.query.order_by(Temp.Date.desc()).first()
    latest_hr_data = Hr.query.order_by(Hr.Date.desc()).first()
    if latest_temp_data and latest_hr_data:
        return jsonify(temperature=latest_temp_data.temp, date=latest_temp_data.Date, hr=latest_hr_data.hr)
    else:
        return jsonify(temperature=None, date=None, hr=None)

@app.route('/data_stream')
def data_stream():
    def event_stream():
        with app.app_context():   # Enter the application context
            while True:
                time.sleep(1)
                latest_temp_data = Temp.query.order_by(Temp.Date.desc()).first()
                latest_hr_data = Hr.query.order_by(Hr.Date.desc()).first()
                
                if latest_temp_data:
                    data = {'temperature': latest_temp_data.temp, 'date': latest_temp_data.Date, 'hr': latest_hr_data.hr}
                    yield f"data: {json.dumps(data)}\n\n"

    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    user = Paitent_login.query.filter_by(Email=email, Username=username, Password=password).first()

    if user:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 401

@app.route('/login_dr', methods=['POST'])
def login_dr():
    data = request.get_json()
    dr_id = data.get('dr_id')
    dr_name = data.get('dr_name')
    dr_ic = data.get('dr_ic')
    two_fa = data.get('two_fa')

    user = DrLogin.query.filter_by(Dr_ID=dr_id, Dr_name=dr_name, Dr_IC=dr_ic, TwoFA=two_fa).first()

    if user:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
    
@app.route('/api/data')
def api_data():
    hr_data = Hr.query.all()
    temp_data = Temp.query.all()
    data = []

    # Create a dictionary with Date_ID as the key for quick lookup
    temp_dict = {temp.Date_ID: temp for temp in temp_data}

    # Loop through hr_data and match with temp_data using Date_ID
    for hr in hr_data:
        temp = temp_dict.get(hr.Date_ID)
        if temp:
            data.append({
                'time': hr.Date,
                'hr': hr.hr,
                'temp': temp.temp
            })

    return jsonify(data)

@app.route('/send_data_request')
def send_data_request_handler():
    # Ensure at least 30 seconds have passed since last data reception
    if last_data_time and (datetime.now() - last_data_time).total_seconds() < 30:
        return "Waiting for 30 seconds after the last data reception."

    send_data_request("bpm")
    send_data_request("temp")

    return "sent"

@app.route('/submit_advice', methods=['POST'])
def submit_advice():
    if request.method == 'POST':
        data = request.form

        # Clear the existing data
        DoctorAdvice.query.delete()

        # Create new advice entry
        new_advice = DoctorAdvice(
            cardiovascular=data.get('cardiovascular', ''),
            glucose=data.get('glucose', ''),
            diet=data.get('diet', ''),
            exercise=data.get('exercise', ''),
            mental=data.get('mental', ''),
            respiratory=data.get('respiratory', ''),
            digestive=data.get('digestive', ''),
            bone=data.get('bone', ''),
            skin=data.get('skin', ''),
            sexual=data.get('sexual', ''),
            immunizations=data.get('immunizations', ''),
            aging=data.get('aging', ''),
            pediatric=data.get('pediatric', '')
        )

        # Add new advice to the session and commit
        db.session.add(new_advice)
        db.session.commit()

        return "Advice submitted successfully", 200

@app.route('/get_advice', methods=['GET'])
def get_advice():
    advice = DoctorAdvice.query.first()
    if advice:
        return jsonify({
            'cardiovascular': advice.cardiovascular,
            'glucose': advice.glucose,
            'diet': advice.diet,
            'exercise': advice.exercise,
            'mental': advice.mental,
            'respiratory': advice.respiratory,
            'digestive': advice.digestive,
            'bone': advice.bone,
            'skin': advice.skin,
            'sexual': advice.sexual,
            'immunizations': advice.immunizations,
            'aging': advice.aging,
            'pediatric': advice.pediatric
        })
    else:
        return "No advice found", 404

def send_data_request(data_type):
    global last_data_time
    
    if not client_to_send:
        return "No client connected"

    for client_addr, client_data in client_to_send.items():
        if len(client_data) >= 2 and b"wch" == client_data[1]:
            print(f"Sending {data_type} request to client {client_addr}")
            client_data[0].send(data_type.encode())
            last_data_time = datetime.now()

    return "sent"

def send_health_report_data_to_client(clientsocket):
    with app.app_context():
        latest_health_report = Health_report.query.order_by(Health_report.id.desc()).first()
        if latest_health_report:
            # Format data as needed and send it to the ESP32
            data_to_send = f"{latest_health_report.total},{latest_health_report.triglyceride},{latest_health_report.hdl_c},..."  # Adjust as per your data structure
            clientsocket.send(bytes(data_to_send, "utf-8"))
        else:
            print("No health report data found.")

@app.route('/img')
def send_img_req():
    for keys in client_to_send.keys():
        print(f"stuff {client_to_send[keys][1]}")
        if b"img" == client_to_send[keys][1]:
            print(f"sending req to {client_to_send[keys][0]}")
            client_to_send[keys][0].send(b"img")
    return "sent"

@app.route('/cab')
def send_led_off():
    for keys in client_to_send.keys():
        print(f"stuff {client_to_send[keys][1]}")
        if b"cab" == client_to_send[keys][1]:
            print(f"sending req to {client_to_send[keys][0]}")
            client_to_send[keys][0].send(b"lof")
    return "sent cab"


def predict(model_path , image):
  model = YOLO(model_path)
  predict_results = model.predict(image, imgsz = 640 , conf = 0.6 , save = True)
  for r in predict_results:
    boxes = r.boxes  # Boxes object for bbox outputs

    predicted_food = boxes.cls.tolist()
    predicted_start_end = boxes.xyxy.tolist()
    predicted_conf = boxes.conf.tolist()

    all_items = {
                "Nutella":0,
                "Pepsi":0 ,
                "Pringles":0
                }
    for i in range(len(predicted_food)):
        # 1 loop for every trash in predicted trash
        print(f"predicted_food: {predicted_food[i]}")
        if predicted_food[i] == 0:
          all_items["Nutella"] += 1
        elif predicted_food[i] == 1:
          all_items["Pepsi"] += 1
        elif predicted_food[i] == 2:
          all_items["Pringles"] += 1
        print(f"predicted_conf: {predicted_conf[i]}")
        print(f"predicted_start_end: {predicted_start_end[i]}")
    return all_items
    print("trust the sacue")

# made by armando
def send_cardio_doctors_advice(clientsocket):
    with app.app_context():
        # Query all health reporsts from the database
        all_doctors_adv = DoctorAdvice.query
        
        if all_doctors_adv:
            # Prepare a list to store CSV formatted strings of each health report
            data_to_send = []

            for report in all_doctors_adv:
                # Format each health report as CSV
                report_data = ",".join([
                    str(report.cardiovascular),
                ])
                print(f"report_data {report_data}")
                data_to_send = report_data

            # Join all health reports into a single string with newline separators
            data_to_send = "crd" + data_to_send # Ensure the final message ends with a newline
            print(data_to_send)
            print("Sending health report data:", data_to_send)
            # clientsocket.send(data_to_send.encode("utf-8"))  # Ensure data is encoded before sending

            print('sent')
        else:
            print("No health report data found.")

def send_glucose_doctors_advice(clientsocket):
    with app.app_context():
        # Query all health reporsts from the database
        all_doctors_adv = DoctorAdvice.query
        
        if all_doctors_adv:
            # Prepare a list to store CSV formatted strings of each health report
            data_to_send = []

            for report in all_doctors_adv:
                # Format each health report as CSV
                report_data = ",".join([
                    str(report.glucose),
                ])
                print(f"report_data glc {report_data}")
                data_to_send = report_data

            # Join all health reports into a single string with newline separators
            data_to_send = "glc" + data_to_send # Ensure the final message ends with a newline
            print(data_to_send)
            print("Sending health report data:", data_to_send)
            # clientsocket.send(data_to_send.encode("utf-8"))  # Ensure data is encoded before sending

            print('sent')
        else:
            print("No health report data found.")

def send_diet_doctors_advice(clientsocket):
    with app.app_context():
        # Query all health reporsts from the database
        all_doctors_adv = DoctorAdvice.query
        
        if all_doctors_adv:
            # Prepare a list to store CSV formatted strings of each health report
            data_to_send = []

            for report in all_doctors_adv:
                # Format each health report as CSV
                report_data = ",".join([
                    str(report.diet),
                ])
                print(f"report_data diet {report_data}")
                data_to_send = report_data

            # Join all health reports into a single string with newline separators
            data_to_send = "dit" + data_to_send # Ensure the final message ends with a newline
            print(data_to_send)
            print("Sending health report data:", data_to_send)
            # clientsocket.send(data_to_send.encode("utf-8"))  # Ensure data is encoded before sending

            print('sent')
        else:
            print("No health report data found.")

def send_exercise_doctors_advice(clientsocket):
    with app.app_context():
        # Query all health reporsts from the database
        all_doctors_adv = DoctorAdvice.query
        
        if all_doctors_adv:
            # Prepare a list to store CSV formatted strings of each health report
            data_to_send = []

            for report in all_doctors_adv:
                # Format each health report as CSV
                report_data = ",".join([
                    str(report.exercise),
                ])
                print(f"report_data exercise {report_data}")
                data_to_send = report_data

            # Join all health reports into a single string with newline separators
            data_to_send = "exr" + data_to_send # Ensure the final message ends with a newline
            print(data_to_send)
            print("Sending health report data:", data_to_send)
            # clientsocket.send(data_to_send.encode("utf-8"))  # Ensure data is encoded before sending

            print('sent')
        else:
            print("No health report data found.")

def send_mental_doctors_advice(clientsocket):
    with app.app_context():
        # Query all health reporsts from the database
        all_doctors_adv = DoctorAdvice.query
        
        if all_doctors_adv:
            # Prepare a list to store CSV formatted strings of each health report
            data_to_send = []

            for report in all_doctors_adv:
                # Format each health report as CSV
                report_data = ",".join([
                    str(report.mental),
                ])
                print(f"report_data mental {report_data}")
                data_to_send = report_data

            # Join all health reports into a single string with newline separators
            data_to_send = "mtl" + data_to_send # Ensure the final message ends with a newline
            print(data_to_send)
            print("Sending health report data:", data_to_send)
            # clientsocket.send(data_to_send.encode("utf-8"))  # Ensure data is encoded before sending

            print('sent')
        else:
            print("No health report data found.")

def send_respiratory_doctors_advice(clientsocket):
    with app.app_context():
        # Query all health reporsts from the database
        all_doctors_adv = DoctorAdvice.query
        if all_doctors_adv:
            # Prepare a list to store CSV formatted strings of each health report
            data_to_send = []

            for report in all_doctors_adv:
                # Format each health report as CSV
                report_data = ",".join([
                    str(report.respiratory),
                ])
                print(f"report_data respr {report_data}")
                data_to_send = report_data

            # Join all health reports into a single string with newline separators
            data_to_send = "rsp" + data_to_send # Ensure the final message ends with a newline
            print(data_to_send)
            print("Sending health report data:", data_to_send)
            # clientsocket.send(data_to_send.encode("utf-8"))  # Ensure data is encoded before sending

            print('sent')
        else:
            print("No health report data found.")

def send_digestive_doctors_advice(clientsocket):
    with app.app_context():
        # Query all health reporsts from the database
        all_doctors_adv = DoctorAdvice.query
        
        if all_doctors_adv:
            # Prepare a list to store CSV formatted strings of each health report
            data_to_send = []

            for report in all_doctors_adv:
                # Format each health report as CSV
                report_data = ",".join([
                    str(report.digestive),
                ])
                print(f"report_data dig {report_data}")
                data_to_send = report_data

            # Join all health reports into a single string with newline separators
            data_to_send = "dig" + data_to_send # Ensure the final message ends with a newline
            print(data_to_send)
            print("Sending health report data:", data_to_send)
            # clientsocket.send(data_to_send.encode("utf-8"))  # Ensure data is encoded before sending

            print('sent')
        else:
            print("No health report data found.")

def send_bone_doctors_advice(clientsocket):
    with app.app_context():
        # Query all health reporsts from the database
        all_doctors_adv = DoctorAdvice.query
        
        if all_doctors_adv:
            # Prepare a list to store CSV formatted strings of each health report
            data_to_send = []

            for report in all_doctors_adv:
                # Format each health report as CSV
                report_data = ",".join([
                    str(report.bone),
                ])
                print(f"report_data bone {report_data}")
                data_to_send = report_data

            # Join all health reports into a single string with newline separators
            data_to_send = "bne" + data_to_send # Ensure the final message ends with a newline
            print(data_to_send)
            print("Sending health report data:", data_to_send)
            # clientsocket.send(data_to_send.encode("utf-8"))  # Ensure data is encoded before sending

            print('sent')
        else:
            print("No health report data found.")

def send_immunizations_doctors_advice(clientsocket):
    with app.app_context():
        # Query all health reporsts from the database
        all_doctors_adv = DoctorAdvice.query
        
        if all_doctors_adv:
            # Prepare a list to store CSV formatted strings of each health report
            data_to_send = []

            for report in all_doctors_adv:
                # Format each health report as CSV
                report_data = ",".join([
                    str(report.immunizations),
                ])
                print(f"report_data immu {report_data}")
                data_to_send = report_data

            # Join all health reports into a single string with newline separators
            data_to_send = "imm" + data_to_send # Ensure the final message ends with a newline
            print(data_to_send)
            print("Sending health report data:", data_to_send)
            # clientsocket.send(data_to_send.encode("utf-8"))  # Ensure data is encoded before sending

            print('sent')
        else:
            print("No health report data found.")
#

def socket_listener(clientsocket):
    def largest_fb(client_to_send):
        have_fbsize = False
        highest = STD_FB
        for key in client_to_send.keys():
            try:
                if highest < client_to_send[key][3]:
                    highest = client_to_send[key][3]
                    have_fbsize = True
            except:
                continue
        if have_fbsize == False:
            return STD_FB
        elif have_fbsize:
            return highest
        
    def check_new_client(client_to_send ,remote_addr ):
        for keys in client_to_send.keys():
            if remote_addr == keys and b"new~" in data:
                print("inning")
                id = data[4:]
                client_to_send[remote_addr].extend([id , True , STD_FB])
                client_to_send[remote_addr][0].send(b"start")
                print(f"client made {client_to_send}")
                return True
        return False

    def find_clients_id(client_to_send ,remote_addr):
        for keys in client_to_send.keys():
            if remote_addr == keys: 
                id = client_to_send[keys][1]
                print(f"received id: {id}") 
                return id
    
    print("start")
    STD_FB = 2048
    send_again = False
    while True:
        fb_size = largest_fb(client_to_send)
        data = clientsocket.recv(fb_size)
        print(f"data {data}")
        remote_addr = clientsocket.getpeername()
        
        if check_new_client(client_to_send ,remote_addr) == False:
            id = find_clients_id(client_to_send ,remote_addr)
            if b"size-" in data: # size declaration
                client_to_send[remote_addr][3] = int(data[5:].decode("utf-8"))

                client_to_send[remote_addr][0].send(b"send")
                print(f"size declaration by {remote_addr}")
            elif b"img" == id:
                print(len(data))
                img = Image.open(io.BytesIO(data))  
                pic_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}food.jpg"
                pic_name = "/Users/Sanjeev/Desktop/IOT sys project/static/images/" + pic_name
                img.save(pic_name)
                item = predict("/Users/Sanjeev/Desktop/IOT sys project/best.pt" , img)
                img.show()  
                b64_ = base64.b64encode(io.BytesIO(data).getvalue()).decode("utf-8")
                socketio.emit("ESP32_pics", b64_)
                send_led_off()
       
            elif b"wch" == id:
                try:
                    received_data = data.decode("utf-8").split(",")
                    print("Received data:", received_data)


                    if len(received_data) == 2:
                        value, data_type = received_data
 
                        with app.app_context():
                            current_time = datetime.now()
                            formatted_date = current_time.strftime("%d %b %H:%M:%S")
                            date_id = current_time.strftime("%Y%m%d") + str(Hr.query.filter_by(Date_ID=current_time.strftime("%Y%m%d")).count() + 1)

                            if data_type == 'bpm':
                                new_hr = Hr(hr=value, Date=formatted_date, Date_ID=date_id)
                                db.session.add(new_hr)
                                db.session.commit()
                                print("BPM Data committed to the database.")
                            elif data_type == 'temp':
                                new_temp = Temp(temp=value, Date=formatted_date, Date_ID=date_id)
                                db.session.add(new_temp)
                                db.session.commit()
                                print("Temperature Data committed to the database.")

                            elif data_type == 'rep':
                                print("Received command: rep")
                                send_health_report_data_to_client(clientsocket)

                            elif data_type == 'a':
                                print("Received command: a")
                                send_health_report_data_to_client(clientsocket)

                            elif data_type == 'b':
                                print("Received command: b")
                                send_health_report_data_to_client(clientsocket)

                            elif data_type == 'c':
                                print("Received command: c")
                                send_health_report_data_to_client(clientsocket)

                            elif data_type == 'd':
                                print("Received command: d")
                                send_health_report_data_to_client(clientsocket)

                            elif data_type == 'e':
                                print("Received command: e")
                                send_health_report_data_to_client(clientsocket)

                            elif data_type == 'f':
                                print("Received command: f")
                                send_health_report_data_to_client(clientsocket)

                            elif data_type == 'g':
                                print("Received command: g")
                                send_health_report_data_to_client(clientsocket)

                            elif data_type == 'h':
                                print("Received command: h")
                                send_health_report_data_to_client(clientsocket)

                            elif data_type == 'i':
                                print("Received command: i")
                                send_health_report_data_to_client(clientsocket)

                except Exception as e:
                    print("Error processing data:", e)
            
            elif b"cab" == id: 
                print(data[4:].decode("utf-8"))
                if b"aft" in data[:4]:
                    print("after")
                    send_img_req()
                elif b"bfr" in data[:4]:
                    print("before")

def send_health_report_data_to_client(clientsocket):
    with app.app_context():
        # Query all health reports from the database
        all_health_reports = Health_report.query.all()
        
        if all_health_reports:
            # Prepare a list to store CSV formatted strings of each health report
            data_to_send = []

            for report in all_health_reports:
                # Format each health report as CSV
                report_data = ",".join([
                    str(report.total),
                    str(report.triglyceride),
                    str(report.hdl_c),
                    str(report.ldl),
                    str(report.chol_hdl),
                    str(report.bilirubin),
                    str(report.alt),
                    str(report.ast),
                    str(report.alp),
                    str(report.golbulin),
                    str(report.protein),
                    str(report.albumin),
                    str(report.creatinine),
                    str(report.potassium),
                    str(report.egfr),
                    str(report.hba1c)
                ])
                data_to_send.append(report_data)

            # Join all health reports into a single string with newline separators
            data_to_send_str = "hrx" + "\n".join(data_to_send) # Ensure the final message ends with a newline
            
            print("Sending health report data:", data_to_send_str)
            clientsocket.send(data_to_send_str.encode("utf-8"))  # Ensure data is encoded before sending
            # data b'10,2,5,15,84,42,63,36,92,61,74,83,46,92,30,83\n'
            print('sent')
        else:
            print("No health report data found.")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()

def close_socket():
    s.close()


def socket_connector():
    while True:
        clientsocket, address = s.accept()
        if clientsocket.getpeername() not in client_to_send.keys():
            client_to_send[clientsocket.getpeername()] = [clientsocket]
            print(client_to_send)
            print(f"Connection from {address}, {clientsocket}")
            connection_estab = "id pls"
            connection_estab = f"{len(connection_estab):<{HEADER_SIZE}}" + connection_estab
            clientsocket.send(bytes(connection_estab, "utf-8"))
        
        listener = threading.Thread(target=socket_listener, args=(clientsocket,))
        listener.start()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist

    # s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    # s.bind(("192.168.0.100" , 5001))
    # s.listen(5)
    # connector = threading.Thread(target=socket_connector)
    
    # print("connection done")
    # connector.start()
    
    # scheduler.add_job(send_data_request_handler, 'interval', seconds=5)  # Adjust timing here
    '''
     line 410 - 625. all the params thr are suppose to be client socket. But the id to send is the param's name
    i.e cardio's id is crd
    '''

    send_cardio_doctors_advice("crd")
    send_glucose_doctors_advice("glc")
    send_diet_doctors_advice("dit")
    send_exercise_doctors_advice("exr")
    send_mental_doctors_advice("mtl")
    send_respiratory_doctors_advice("rsp")
    send_digestive_doctors_advice("dig")
    send_bone_doctors_advice("bne")
    send_immunizations_doctors_advice("imm")
    socketio.run(app)  # Changed port to 5004

    # socketio.run(app, host = "192.168.0.100")