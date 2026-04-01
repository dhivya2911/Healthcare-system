from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, session
from database import get_db_connection, init_db

app = Flask(__name__)
app.secret_key = "healthcare_secret"

init_db()
# HOME
@app.route("/")
def index():
    return render_template("index.html")

# LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user"] = username
            session["role"] = user["role"]
            if user["role"] == "admin":
                return redirect("/dashboard")
            elif user["role"] == "doctor":
                return redirect("/doctor_dashboard")
            else:
                return redirect("/user_dashboard")
        else:
            return "Invalid username or password"
    return render_template("login.html")

# REGISTER
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])  # ✅ hash once

        conn = get_db_connection()
        existing_user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        if existing_user:
            conn.close()
            return "Username already exists. Try another username."
        #patient
        conn.execute(
            "INSERT INTO users(username,password,role) VALUES(?,?,?)",
            (username, password, "patient")
        )
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

# DASHBOARDS
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    conn = get_db_connection()
    total_patients = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    total_doctors = conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
    total_appointments = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    conn.close()
    return render_template(
        "dashboard.html",
        total_patients=total_patients,
        total_doctors=total_doctors,
        total_appointments=total_appointments
    )

# PATIENT CRUD
@app.route("/add_patient", methods=["GET","POST"])
def add_patient():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        disease = request.form["disease"]
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO patients(name,age,disease,username) VALUES(?,?,?,?)",
            (name,age,disease,name)
        )
        conn.commit()
        conn.close()
        return redirect("/view_patients")
    return render_template("add_patient.html")

@app.route("/view_patients")
def view_patients():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    conn = get_db_connection()
    patients = conn.execute(
        "SELECT * FROM patients"
    ).fetchall()
    conn.close()
    return render_template("view_patients.html", patients=patients)

@app.route("/edit_patient/<int:id>", methods=["GET","POST"])
def edit_patient(id):
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    conn = get_db_connection()
    patient = conn.execute(
        "SELECT * FROM patients WHERE id=?",
        (id,)
    ).fetchone()
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        disease = request.form["disease"]
        conn.execute(
            "UPDATE patients SET name=?,age=?,disease=? WHERE id=?",
            (name,age,disease,id)
        )
        conn.commit()
        conn.close()
        return redirect("/view_patients")
    conn.close()
    return render_template("edit_patient.html", patient=patient)

@app.route("/delete_patient/<int:id>")
def delete_patient(id):
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM patients WHERE id=?",
        (id,)
    )
    conn.commit()
    conn.close()
    return redirect("/view_patients")

# DOCTOR CRUD
@app.route("/add_doctor", methods=["GET","POST"])
def add_doctor():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    if request.method == "POST":
        name = request.form["name"]
        specialization = request.form["specialization"]
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        conn = get_db_connection()
        #  Check if username already exists
        existing_user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()
        if existing_user:
            conn.close()
            return "Username already exists"

        # Create login for doctor
        conn.execute(
            "INSERT INTO users(username,password,role) VALUES(?,?,?)",
            (username, password, "doctor")
        )
        # Store doctor details
        conn.execute(
            "INSERT INTO doctors(name,specialization,username) VALUES(?,?,?)",
            (name, specialization, username)
        )
        conn.commit()
        conn.close()
        return redirect("/view_doctors")
    return render_template("add_doctor.html")

@app.route("/view_doctors")
def view_doctors():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    conn = get_db_connection()
    doctors = conn.execute(
        "SELECT * FROM doctors"
    ).fetchall()
    conn.close()
    return render_template("view_doctors.html", doctors=doctors)

@app.route("/edit_doctor/<int:id>", methods=["GET","POST"])
def edit_doctor(id):
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    conn = get_db_connection()
    doctor = conn.execute(
        "SELECT * FROM doctors WHERE id=?",
        (id,)
    ).fetchone()
    if request.method == "POST":
        name = request.form["name"]
        specialization = request.form["specialization"]
        conn.execute(
            "UPDATE doctors SET name=?,specialization=? WHERE id=?",
            (name,specialization,id)
        )
        conn.commit()
        conn.close()
        return redirect("/view_doctors")
    conn.close()
    return render_template("edit_doctor.html", doctor=doctor)

@app.route("/delete_doctor/<int:id>")
def delete_doctor(id):
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM doctors WHERE id=?",
        (id,)
    )
    conn.commit()
    conn.close()
    return redirect("/view_doctors")

# APPOINTMENT CRUD
@app.route("/add_appointment", methods=["GET","POST"])
def add_appointment():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    conn = get_db_connection()
    patients = conn.execute("SELECT * FROM patients").fetchall()
    doctors = conn.execute("SELECT * FROM doctors").fetchall()
    if request.method == "POST":
        patient_id = request.form["patient_id"]
        doctor_id = request.form["doctor_id"]
        date = request.form["date"]
        conn.execute(
            "INSERT INTO appointments(patient_id,doctor_id,date) VALUES(?,?,?)",
            (patient_id,doctor_id,date)
        )
        conn.commit()
        conn.close()
        return redirect("/view_appointments")
    conn.close()
    return render_template(
        "add_appointment.html",
        patients=patients,
        doctors=doctors
    )

@app.route("/view_appointments")
def view_appointments():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    conn = get_db_connection()
    appointments = conn.execute("""
    SELECT appointments.id,
    patients.name AS patient_name,
    doctors.name AS doctor_name,
    appointments.date
    FROM appointments
    JOIN patients ON appointments.patient_id = patients.id
    JOIN doctors ON appointments.doctor_id = doctors.id
    """).fetchall()
    conn.close()
    return render_template(
        "view_appointments.html",
        appointments=appointments
    )

@app.route("/edit_appointment/<int:id>", methods=["GET","POST"])
def edit_appointment(id):
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    conn = get_db_connection()
    appointment = conn.execute(
        "SELECT * FROM appointments WHERE id=?",
        (id,)
    ).fetchone()
    patients = conn.execute("SELECT * FROM patients").fetchall()
    doctors = conn.execute("SELECT * FROM doctors").fetchall()
    if request.method == "POST":
        patient_id = request.form["patient_id"]
        doctor_id = request.form["doctor_id"]
        date = request.form["date"]
        conn.execute(
            "UPDATE appointments SET patient_id=?, doctor_id=?, date=? WHERE id=?",
            (patient_id, doctor_id, date, id)
        )
        conn.commit()
        conn.close()
        return redirect("/view_appointments")
    conn.close()
    return render_template(
        "edit_appointment.html",
        appointment=appointment,
        patients=patients,
        doctors=doctors
    )

@app.route("/delete_appointment/<int:id>")
def delete_appointment(id):
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM appointments WHERE id=?",
        (id,)
    )
    conn.commit()
    conn.close()
    return redirect("/view_appointments")

@app.route("/medical_records")
def medical_records():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/login")
    conn = get_db_connection()
    records = conn.execute("""
        SELECT appointments.id, patients.name, patients.age, patients.disease,
               doctors.name AS doctor, 
               appointments.date
        FROM appointments
        JOIN patients ON appointments.patient_id = patients.id
        JOIN doctors ON appointments.doctor_id = doctors.id
    """).fetchall()
    conn.close()
    return render_template("medical_records.html", records=records)

@app.route("/doctor_dashboard")
def doctor_dashboard():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "doctor":
        return redirect("/login")
    conn = get_db_connection()
    appointments = conn.execute("""
        SELECT appointments.id,
               appointments.date,
               patients.name AS patient,
               patients.disease
        FROM appointments
        JOIN patients ON appointments.patient_id = patients.id
        JOIN doctors ON appointments.doctor_id = doctors.id
        WHERE doctors.username = ?
    """, (session["user"],)).fetchall()
    conn.close()
    return render_template("doctor_dashboard.html", appointments=appointments)

@app.route("/user_dashboard")
def user_dashboard():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "patient":
        return redirect("/login")
    conn = get_db_connection()
    appointments = conn.execute("""
        SELECT appointments.id,
               appointments.date,
               doctors.name AS doctor,
               doctors.specialization
        FROM appointments
        JOIN doctors ON appointments.doctor_id = doctors.id
        JOIN patients ON appointments.patient_id = patients.id
        WHERE patients.username = ?
    """, (session["user"],)).fetchall()
    conn.close()
    return render_template("user_dashboard.html", appointments=appointments)

@app.route("/book_appointment", methods=["GET","POST"])
def book_appointment():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "patient":
        return redirect("/login")
    conn = get_db_connection()
    patient = conn.execute(
        "SELECT id FROM patients WHERE username = ?",
        (session["user"],)
    ).fetchone()
    if not patient:
        conn.close()
        return "❌ Patient not found"
    if request.method == "POST":
        doctor_id = request.form["doctor_id"]
        date = request.form["date"]
        conn.execute(
            "INSERT INTO appointments(patient_id, doctor_id, date) VALUES (?,?,?)",
            (patient["id"], doctor_id, date)
        )
        conn.commit()
        conn.close()
        return redirect("/user_dashboard")
    doctors = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()
    return render_template("book_appointment.html", doctors=doctors)
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)