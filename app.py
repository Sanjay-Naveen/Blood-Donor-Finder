from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ✅ MongoDB Atlas Connection
uri = "mongodb+srv://sanjaynaveen477:9025879408@cluster0.an0tz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
try:
    client = MongoClient(uri)  # Connect to MongoDB Atlas
    db = client["Sanjaynaveen"]  # Database Name
    student_collection = db["Sanjay"]  # Collection Name
    print("[INFO] Connected to MongoDB Atlas successfully!")
except Exception as e:
    print("[ERROR] Failed to connect to MongoDB Atlas:", str(e))

# ✅ Email Configuration
SENDER_EMAIL = "sanjaynaveen477@gmail.com"
SENDER_PASSWORD = " "  # Store in environment variables for security

def send_email(receiver_email, student_name):
    """Function to send an email notification"""
    subject = "Urgent: Blood Donation Request"
    body = f"""
    Dear {student_name},

    We are urgently looking for blood donors, and your blood type matches the requirement.
    If you're available, please contact us as soon as possible.

    Thank you for your support!

    Regards,
    Sanjay Naveen.R
    """

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        return False

# ✅ Add a Student (POST)
@app.route("/add_student", methods=["POST"])
def add_student():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        name = data.get("name")
        roll_no = data.get("roll_no")
        phone = data.get("phone")
        department = data.get("department")
        blood_group = data.get("blood_group")
        email = data.get("email")

        if not all([name, roll_no, phone, department, blood_group, email]):
            return jsonify({"error": "Missing fields"}), 400

        student_data = {
            "name": name,
            "roll_no": roll_no,
            "phone": phone,
            "department": department,
            "blood_group": blood_group,
            "email": email
        }

        student_collection.insert_one(student_data)  # Store in MongoDB Atlas
        print(f"[INFO] Student {name} added to MongoDB Atlas!")
        return jsonify({"message": "Student added successfully!"}), 201
    except Exception as e:
        print("[ERROR] Failed to add student:", str(e))
        return jsonify({"error": "Internal Server Error"}), 500

# ✅ Get All Students (GET)
@app.route("/get_students", methods=["GET"])
def get_students():
    try:
        students = list(student_collection.find({}, {"_id": 0}))  # Fetch all students
        print(f"[INFO] Retrieved {len(students)} students from MongoDB Atlas.")
        return jsonify(students)
    except Exception as e:
        print("[ERROR] Failed to fetch students:", str(e))
        return jsonify({"error": "Internal Server Error"}), 500

# ✅ Delete student by roll_no
@app.route('/delete_student/<roll_no>', methods=['DELETE'])
def delete_student(roll_no):
    print(f"Received request to delete roll_no: {roll_no}")  # Debugging
    result = student_collection.delete_one({"roll_no": str(roll_no)})  

    if result.deleted_count > 0:
        print(f"Deleted student: {roll_no}")  # Debugging
        return jsonify({"message": f"Student with roll_no {roll_no} deleted successfully!"})
    else:
        print("Student not found!")  # Debugging
        return jsonify({"message": "Student not found!"}), 404

# ✅ Send Email to a Student (POST)
@app.route("/send_email", methods=["POST"])
def send_mail():
    try:
        data = request.json
        student_name = data.get("name")

        # Find student in MongoDB
        student = student_collection.find_one({"name": student_name}, {"_id": 0, "email": 1})

        if not student:
            return jsonify({"message": "Student email not found"}), 404

        receiver_email = student["email"]

        if send_email(receiver_email, student_name):
            return jsonify({"message": f"Email sent to {student_name} ({receiver_email})"}), 200
        else:
            return jsonify({"message": "Failed to send email"}), 500
    except Exception as e:
        print("[ERROR] Email sending error:", str(e))
        return jsonify({"error": "Internal Server Error"}), 500

# ✅ Test Route (Home Route for Deployment Check)
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Flask API is running with MongoDB Atlas & Email System!"})

# ✅ Run Flask App
if __name__ == "__main__":
    print("🔥 Flask server starting...")
    app.run(debug=False, host="0.0.0.0", port=5000)  # Adjusted for production environment

from flask import render_template

@app.route('/')
def login():
    return render_template('login.html')  # Show login page

@app.route('/search')
def search():
    return render_template('search.html')  # Show search page

@app.route('/aboutus')
def aboutus():   
    return render_template('aboutus.html')  # Show about us page



