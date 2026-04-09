import re
import os
from flask import Flask, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
from datetime import datetime, timedelta, date
import random
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import json 



from flask_cors import CORS

# ==========================================================
# ✅ APP INIT
# ==========================================================
app = Flask(__name__)
CORS(app)
app.secret_key = "supersecretkey"

# ==========================================================
# ✅ MAIL CONFIG
# ==========================================================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mudesai09@gmail.com' 
app.config['MAIL_PASSWORD'] = 'otffxqwlewzddbbn'
mail = Mail(app)
# ================================
# PHOTO UPLOAD CONFIG
# ================================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==========================================================
# SERVE UPLOADED IMAGES
# ==========================================================
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ==========================================================
# ✅ DATABASE CONNECTION (DB NAME: hydroguard)
# ==========================================================
def get_connection():
    try:
        connection = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="",
            database="hydroguard",
            port=3306,   # ✅ correct port
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return connection
    except Exception as e:
        print("Database connection failed:", e)
        return None
    
# ==========================================================
# ✅ SAFE INT HELPER
# ==========================================================
def _to_int(v, default=None):
    try:
        return int(v)
    except:
        return default

# ==========================================================
# ✅ PASSWORD VALIDATOR
# ==========================================================
def validate_password(password):
    missing = []
    if len(password) < 6:
        missing.append("at least 6 characters")
    if not any(c.islower() for c in password):
        missing.append("one lowercase letter")
    if not any(c.isupper() for c in password):
        missing.append("one uppercase letter")
    if not any(c.isdigit() for c in password):
        missing.append("one numerical digit")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        missing.append("one special character")
    return missing

# ==========================================================
# ✅ BASIC TEST ROUTE
# ==========================================================
@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "success", "message": "HydraGraud backend running ✅"}), 200

# ==========================================================
# ✅ REGISTER
# ==========================================================
# @app.route("/register", methods=["POST"])
# def register():
#     data = request.get_json(silent=True) or {}

#     full_name = data.get("full_name")
#     email = data.get("email")
#     password = data.get("password")
#     confirm_password = data.get("confirm_password")
#     location = data.get("location")   # district
#     role_input = data.get("role") or "citizen"

#     if not full_name or not email or not password or not confirm_password or not location:
#         return jsonify({"status": "error", "message": "All fields are required"}), 400

#     # Normalize role for DB ENUM: 'Citizen' -> 'citizen', 'Health Worker' -> 'health_worker'
#     role = role_input.lower().replace(" ", "_")
#     if role not in ["citizen", "health_worker", "admin"]:
#         role = "citizen"

#     if not re.match(r"^[A-Za-z\s]+$", full_name):
#         return jsonify({"status": "error", "message": "Full name must contain only letters and spaces"}), 400

#     email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
#     if not re.match(email_pattern, email):
#         return jsonify({"status": "error", "message": "Invalid email format"}), 400

#     missing_requirements = validate_password(password)
#     if missing_requirements:
#         return jsonify({
#             "status": "error",
#             "message": f"Password must contain: {', '.join(missing_requirements)}"
#         }), 400

#     if password != confirm_password:
#         return jsonify({"status": "error", "message": "Passwords do not match"}), 400

#     conn = get_connection()
#     if not conn:
#         return jsonify({"status": "error", "message": "DB connection failed"}), 500

#     try:
#         with conn.cursor() as cursor:

#             # Check if email already exists
#             cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
#             existing_user = cursor.fetchone()

#             if existing_user:
#                 return jsonify({"status": "error", "message": "Mail already registered"}), 409

#             hashed_password = generate_password_hash(password)

#             # Insert new user
#             cursor.execute("""
#                 INSERT INTO users
#                 (full_name, email, password_hash, role, assigned_district)
#                 VALUES (%s, %s, %s, %s, %s)
#             """, (full_name, email, hashed_password, role, location))

#             conn.commit()

#         return jsonify({"status": "success", "message": "User registered successfully"}), 201

#     finally:
#         conn.close()
# 1. AUTHENTICATION
# @app.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()

#     full_name = data.get('full_name')
#     email = data.get('email')
#     password = data.get('password')
#     district = data.get('district')
#     role = data.get('role', 'citizen')

#     # ✅ Validation
#     if not all([full_name, email, password, district]):
#         return jsonify({"status": "error", "message": "All fields are required"}), 400

#     # 🔐 Hash password
#     hashed_password = generate_password_hash(password)

#     conn = get_connection()
#     cursor = conn.cursor()

#     try:
#         # ✅ Check if email already exists
#         cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
#         if cursor.fetchone():
#             return jsonify({"status": "error", "message": "Email already exists"}), 409

#         # ✅ Insert user (FIXED)
#         cursor.execute("""
#             INSERT INTO users (full_name, email, password_hash, role, district)
#             VALUES (%s, %s, %s, %s, %s)
#         """, (full_name, email, hashed_password, role.lower(), district))

#         conn.commit()

#         return jsonify({
#             "status": "success",
#             "message": "User registered successfully"
#         }), 201

#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         }), 500

#     finally:
#         cursor.close()
#         conn.close()
# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()

#     email = data.get('email')
#     password = data.get('password')

#     if not email or not password:
#         return jsonify({
#             "status": "error",
#             "message": "Email and password are required"
#         }), 400

#     conn = get_connection()
#     cursor = conn.cursor()

#     try:
#         # ✅ FIXED QUERY (MySQL style)
#         cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
#         user = cursor.fetchone()

#         # 🔐 Check password
#         if user and check_password_hash(user['password_hash'], password):
#             return jsonify({
#                 "status": "success",
#                 "message": "Login successful",
#                 "user": {
#                     "user_id": user["user_id"],
#                     "full_name": user["full_name"],
#                     "email": user["email"],
#                     "role": user["role"],
#                     "district": user["district"]
#                 }
#             }), 200

#         return jsonify({
#             "status": "error",
#             "message": "Invalid credentials"
#         }), 401

#     finally:
#         cursor.close()
#         conn.close()
# ✅ REGISTER
# ==========================================================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    district = data.get('district')
    role = data.get('role', 'citizen').lower()

    # ✅ Required fields
    if not all([full_name, email, password, confirm_password, district]):
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    # ✅ Name validation
    if not re.match(r"^[A-Za-z\s]+$", full_name):
        return jsonify({"status": "error", "message": "Invalid full name"}), 400

    # ✅ Email validation
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
        return jsonify({"status": "error", "message": "Invalid email format"}), 400

    # ✅ Password validation
    missing = validate_password(password)
    if missing:
        return jsonify({
            "status": "error",
            "message": f"Password must contain: {', '.join(missing)}"
        }), 400

    # ✅ Confirm password
    if password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ✅ Check existing email
        cursor.execute("SELECT user_id FROM users WHERE LOWER(email)=LOWER(%s)", (email,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Email already exists"}), 409

        hashed_password = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO users (full_name, email, password_hash, role, district)
            VALUES (%s, %s, %s, %s, %s)
        """, (full_name, email.lower(), hashed_password, role, district))

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "User registered successfully"
        }), 201

    finally:
        cursor.close()
        conn.close()


# ==========================================================
# ✅ LOGIN
# ==========================================================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and password required"
        }), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ✅ Case-insensitive email
        cursor.execute("SELECT * FROM users WHERE LOWER(email)=LOWER(%s)", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            return jsonify({
                "status": "success",
                "message": "Login successful",
                "user": {
                    "user_id": user["user_id"],
                    "full_name": user["full_name"],
                    "email": user["email"],
                    "role": user["role"],
                    "district": user["district"]
                }
            }), 200

        return jsonify({
            "status": "error",
            "message": "Invalid credentials"
        }), 401

    finally:
        cursor.close()
        conn.close()


# ==========================================================
# ✅ SEND OTP (NEW API)
# ==========================================================
@app.route('/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"status": "error", "message": "Email required"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"status": "error", "message": "Email not registered"}), 404

        # ✅ Generate OTP
        otp = random.randint(100000, 999999)
        expiry = datetime.now() + timedelta(minutes=5)

        # ✅ Store OTP
        cursor.execute("""
            UPDATE users 
            SET otp=%s, otp_expiry=%s 
            WHERE email=%s
        """, (otp, expiry, email))

        conn.commit()

        # ✅ Send email
        msg = Message("Your OTP Code",
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])

        msg.body = f"Your OTP is {otp}. It expires in 5 minutes."

        mail.send(msg)

        return jsonify({
            "status": "success",
            "message": "OTP sent successfully"
        })

    finally:
        cursor.close()
        conn.close()


# ==========================================================
# ✅ RESET PASSWORD
# ==========================================================
# @app.route('/reset-password', methods=['POST'])
# def reset_password():
#     data = request.get_json()

#     email = data.get('email')
#     otp = data.get('otp')
#     new_password = data.get('new_password')
#     confirm_password = data.get('confirm_password')

#     if not all([email, otp, new_password, confirm_password]):
#         return jsonify({"status": "error", "message": "All fields required"}), 400

#     if new_password != confirm_password:
#         return jsonify({"status": "error", "message": "Passwords do not match"}), 400

#     # ✅ Password validation
#     missing = validate_password(new_password)
#     if missing:
#         return jsonify({
#             "status": "error",
#             "message": f"Password must contain: {', '.join(missing)}"
#         }), 400

#     conn = get_connection()
#     cursor = conn.cursor()

#     try:
#         cursor.execute("""
#             SELECT otp, otp_expiry 
#             FROM users 
#             WHERE email=%s
#         """, (email,))

#         user = cursor.fetchone()

#         if not user:
#             return jsonify({"status": "error", "message": "User not found"}), 404

#         # ✅ OTP check
#         if str(user["otp"]) != str(otp):
#             return jsonify({"status": "error", "message": "Invalid OTP"}), 400

#         if user["otp_expiry"] < datetime.now():
#             return jsonify({"status": "error", "message": "OTP expired"}), 400

#         # ✅ Update password
#         hashed_password = generate_password_hash(new_password)

#         cursor.execute("""
#             UPDATE users 
#             SET password_hash=%s, otp=NULL, otp_expiry=NULL 
#             WHERE email=%s
#         """, (hashed_password, email))

#         conn.commit()

#         return jsonify({
#             "status": "success",
#             "message": "Password reset successful"
#         })

#     finally:
#         cursor.close()
#         conn.close()

# ==========================================================
@app.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json(silent=True) or {}

        email = data.get('email')
        otp = data.get('otp')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        # ✅ Validate input
        if not all([email, otp, new_password, confirm_password]):
            return jsonify({
                "status": "error",
                "message": "All fields are required"
            }), 400

        if new_password != confirm_password:
            return jsonify({
                "status": "error",
                "message": "Passwords do not match"
            }), 400

        # ✅ Password strength check
        missing = validate_password(new_password)
        if missing:
            return jsonify({
                "status": "error",
                "message": f"Password must contain: {', '.join(missing)}"
            }), 400

        conn = get_connection()
        if not conn:
            return jsonify({
                "status": "error",
                "message": "Database connection failed"
            }), 500

        cursor = conn.cursor()

        # ✅ Fetch user + OTP
        cursor.execute("""
            SELECT otp, otp_expiry 
            FROM users 
            WHERE LOWER(email)=LOWER(%s)
        """, (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404

        # ✅ OTP validation
        if str(user.get("otp")) != str(otp):
            return jsonify({
                "status": "error",
                "message": "Invalid OTP"
            }), 400

        # ✅ Expiry check
        if not user.get("otp_expiry") or user["otp_expiry"] < datetime.now():
            return jsonify({
                "status": "error",
                "message": "OTP expired"
            }), 400

        # ✅ Hash new password
        hashed_password = generate_password_hash(new_password)

        # ✅ Update password & clear OTP
        cursor.execute("""
            UPDATE users 
            SET password_hash=%s, otp=NULL, otp_expiry=NULL 
            WHERE LOWER(email)=LOWER(%s)
        """, (hashed_password, email))

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Password reset successful"
        }), 200

    except Exception as e:
        print("RESET PASSWORD ERROR:", e)
        return jsonify({
            "status": "error",
            "message": "Server error"
        }), 500

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
# ==========================================================
# ==========================================================
# CITIZEN CHECK WATER SOURCE WITH RISK ANALYSIS
# ==========================================================

# @app.route('/citizen/check-water', methods=['POST'])
# def citizen_check_water():

#     data = request.get_json()

#     citizen_id = data.get("citizen_id")
#     water_source_type = data.get("water_source_type")
#     appearance = data.get("appearance")
#     smell = data.get("smell")
#     taste = data.get("taste")
#     symptoms = data.get("symptoms")

#     conn = get_connection()

#     if conn is None:
#         return jsonify({
#             "status": "error",
#             "message": "Database connection failed"
#         })

#     cursor = conn.cursor()

#     # check citizen exists
#     cursor.execute("SELECT user_id FROM users WHERE user_id=%s", (citizen_id,))
#     user = cursor.fetchone()

#     if not user:
#         return jsonify({
#             "status": "error",
#             "message": "Citizen not found"
#         })

#     # risk logic
#     risk_level = "low"

#     if appearance in ["Very Muddy", "Yellow or Brown Color", "Floating Particles / Dirt"]:
#         risk_level = "moderate"

#     if smell == "Strong Bad Smell":
#         risk_level = "high"

#     if taste in ["Salty", "Bitter", "Metallic / Strange Taste"]:
#         risk_level = "moderate"

#     if symptoms in ["Diarrhea", "Vomiting", "Multiple People Sick"]:
#         risk_level = "high"

#     try:

#         query = """
#         INSERT INTO citizen_water_check
#         (citizen_id, water_source_type, water_appearance, water_smell, water_taste, health_symptoms, risk_level)
#         VALUES (%s,%s,%s,%s,%s,%s,%s)
#         """

#         cursor.execute(query, (
#             citizen_id,
#             water_source_type,
#             appearance,
#             smell,
#             taste,
#             symptoms,
#             risk_level
#         ))

#         conn.commit()

#         return jsonify({
#             "status": "success",
#             "risk_level": risk_level
#         })

#     except Exception as e:

#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         })

#     finally:
#         conn.close()
# Citizen Check Water API
# ------------------------

# ==========================================================
# CITIZEN WATER SOURCE CHECK
# ==========================================================
@app.route('/citizen/water-check', methods=['POST'])
def citizen_water_check():
    try:
        data = request.get_json()

        citizen_id = data.get("citizen_id")
        source_type = data.get("source_type")
        appearance = data.get("appearance")
        smell = data.get("smell")
        taste = data.get("taste")
        symptoms = data.get("symptoms")

        conn = get_connection()
        cursor = conn.cursor()

        # Risk logic
        risk_level = "low"

        if appearance in ["Very Muddy", "Yellow or Brown Color", "Floating Particles / Dirt"]:
            risk_level = "high"

        if smell == "Strong Bad Smell":
            risk_level = "high"

        if taste in ["Bitter", "Metallic / Strange Taste"]:
            risk_level = "medium"

        if symptoms in ["Diarrhea", "Vomiting", "Multiple People Sick"]:
            risk_level = "high"

        cursor.execute("""
        INSERT INTO citizen_water_check
        (citizen_id, water_source_type, water_appearance, water_smell, water_taste, health_symptoms)
        VALUES (%s,%s,%s,%s,%s,%s)
        """,(citizen_id, source_type, appearance, smell, taste, symptoms))

        conn.commit()

        return jsonify({
            "status": "success",
            "riskLevel": risk_level
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })
# ==========================================================
# CITIZEN REPORT ISSUE
# ==========================================================
# @app.route('/citizen/report', methods=['POST'])
# def report_issue():
#     try:
#         data = request.get_json()

#         citizen_id = data.get("citizenId")
#         water_source = data.get("waterSource")
#         issue_type = data.get("issueType")
#         description = data.get("description")
#         photo_url = data.get("photoUrl", "")

#         # Validate required fields (description and photoUrl are optional)
#         if not citizen_id or not water_source or not issue_type:
#             return jsonify({
#                 "status": "error",
#                 "message": "Missing required fields"
#             }), 400

#         conn = get_connection()
#         cursor = conn.cursor()

#         risk_level = "low"

#         # Insert report
#         cursor.execute("""
#         INSERT INTO citizen_reports
#         (citizen_id, location_desc, issue_type, description, photo_url, risk_level, reported_at, status)
#         VALUES (%s,%s,%s,%s,%s,%s,NOW(),'new')
#         """, (
#             citizen_id,
#             water_source,
#             issue_type,
#             description,
#             photo_url,
#             risk_level
#         ))

#         conn.commit()

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "status": "success",
#             "message": "Report submitted successfully"
#         })

#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         })
# @app.route('/citizen/report', methods=['POST'])
# def report_issue():
#     try:
#         data = request.get_json()

#         citizen_id = data.get("citizenId")
#         water_source = data.get("waterSource")
#         issue_type = data.get("issueType")
#         description = data.get("description")
#         photo_url = data.get("photoUrl", "")

#         if not citizen_id or not water_source or not issue_type:
#             return jsonify({
#                 "status": "error",
#                 "message": "Missing required fields"
#             }), 400

#         conn = get_connection()
#         cursor = conn.cursor()

#         # ✅ FIX 1: correct column name (assigned_district)
#         cursor.execute(
#             "SELECT assigned_district FROM users WHERE user_id=%s AND role='citizen'",
#             (citizen_id,)
#         )
#         citizen = cursor.fetchone()

#         if not citizen:
#             return jsonify({
#                 "status": "error",
#                 "message": "Citizen not found"
#             }), 404

#         # ✅ FIX 2: DictCursor → use key, not index
#         citizen_district = citizen["assigned_district"]

#         risk_level = "low"

#         # ✅ Insert report WITH district
#         cursor.execute("""
#         INSERT INTO citizen_reports
#         (citizen_id, district, location_desc, issue_type, description, photo_url, risk_level, reported_at, status)
#         VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),'new')
#         """, (
#             citizen_id,
#             citizen_district,
#             water_source,
#             issue_type,
#             description,
#             photo_url,
#             risk_level
#         ))

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify({
#             "status": "success",
#             "message": "Report submitted successfully"
#         })

#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         })
@app.route('/citizen/report', methods=['POST'])
def report_issue():
    try:
        data = request.get_json(silent=True) or {}

        citizen_id = data.get("citizenId")
        water_source = data.get("waterSource")
        issue_type = data.get("issueType")
        description = data.get("description")
        photo_url = data.get("photoUrl", "")

        # ✅ Validate input
        if not citizen_id or not water_source or not issue_type:
            return jsonify({
                "status": "error",
                "message": "Missing required fields"
            }), 400

        # ✅ Get DB connection
        conn = get_connection()
        if not conn:
            return jsonify({
                "status": "error",
                "message": "Database connection failed"
            }), 500

        cursor = conn.cursor()

        # ✅ Get citizen district (UPDATED: use 'district')
        cursor.execute(
            "SELECT district FROM users WHERE user_id=%s AND role='citizen'",
            (citizen_id,)
        )
        citizen = cursor.fetchone()

        if not citizen:
            return jsonify({
                "status": "error",
                "message": "Citizen not found"
            }), 404

        citizen_district = citizen.get("district")

        # ✅ Check if district exists
        if not citizen_district:
            return jsonify({
                "status": "error",
                "message": "Citizen district not set"
            }), 400

        risk_level = "low"

        # ✅ Insert report (make sure 'district' column exists)
        cursor.execute("""
        INSERT INTO citizen_reports
        (citizen_id, district, location_desc, issue_type, description, photo_url, risk_level, reported_at, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),'new')
        """, (
            citizen_id,
            citizen_district,
            water_source,
            issue_type,
            description,
            photo_url,
            risk_level
        ))

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Report submitted successfully"
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass
# =============================================
# ==========================================================
# DELETE CITIZEN ACCOUNT
# ==========================================================
@app.route('/citizen/delete-account', methods=['POST'])
def delete_citizen_account():
    try:
        data = request.get_json()

        user_id = data.get("user_id")
        confirm_delete = data.get("confirm_delete")

        if not user_id or not confirm_delete:
            return jsonify({
                "status": "error",
                "message": "user_id and confirm_delete required"
            }), 400

        conn = get_connection()
        cursor = conn.cursor()

        # Check if citizen exists
        cursor.execute(
            "SELECT user_id FROM users WHERE user_id=%s AND role='citizen'",
            (user_id,)
        )
        citizen = cursor.fetchone()

        if not citizen:
            return jsonify({
                "status": "error",
                "message": "Citizen not found"
            }), 404

        # Delete citizen account
        cursor.execute(
            "DELETE FROM users WHERE user_id=%s",
            (user_id,)
        )

        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Account deleted successfully"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })
# ==========================================================
# ✅ CREATE NEW CASE FOR HEALTH WORKER
# ==========================================================
@app.route('/healthworker/create-case', methods=['POST'])
def create_case():
    data = request.get_json()

    patient_name = data.get("patient_name")
    age = data.get("age")
    gender = data.get("gender")
    location = data.get("location")
    symptoms = data.get("symptoms")  # this can be a list
    risk_level = data.get("risk_level")
    health_worker_id = data.get("health_worker_id")

    # Convert symptoms list to JSON string
    import json
    symptoms_json = json.dumps(symptoms)

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO patient_cases
    (patient_name, age, gender, location, symptoms, risk_level, health_worker_id)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query,(
        patient_name,
        age,
        gender,
        location,
        symptoms_json,  # ✅ JSON string
        risk_level,
        health_worker_id
    ))

    conn.commit()

    case_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "message":"Case created successfully",
        "case_id":case_id
    })
#=========================================================
#Health worker water source
#=========================================================
@app.route('/healthworker/add-water-source', methods=['POST'])
def add_water_source():

    data = request.get_json()

    case_id = data.get("case_id")
    water_type = data.get("water_type")
    source = data.get("source")
    appearance = data.get("appearance")
    treatment_method = data.get("treatment_method")
    risk_level = data.get("risk_level")

    conn = get_connection()
    cursor = conn.cursor()

    # Step 1: Check if case_id exists
    cursor.execute("SELECT case_id FROM patient_cases WHERE case_id=%s", (case_id,))
    case = cursor.fetchone()

    if not case:
        cursor.close()
        conn.close()
        return jsonify({
            "status": "error",
            "message": "Invalid case_id. Patient case does not exist."
        })

    # Step 2: Insert water source details
    query = """
    INSERT INTO water_source_details
    (case_id, water_type, source, appearance, treatment_method, risk_level)
    VALUES (%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, (case_id, water_type, source, appearance, treatment_method, risk_level))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Report submitted successfully"
    })
@app.route('/health-worker/notifications', methods=['GET'])
def health_worker_notifications():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ✅ Get logged-in health worker ID (example using query param or token)
        health_worker_id = request.args.get("user_id")

        # ✅ Step 1: Get health worker district
        cursor.execute("""
            SELECT district FROM users 
            WHERE user_id = %s AND role = 'health_worker'
        """, (health_worker_id,))
        
        worker = cursor.fetchone()

        if not worker:
            return jsonify({
                "status": "error",
                "message": "Health worker not found"
            }), 404

        worker_district = worker["district"]

        # ✅ Step 2: Fetch reports only from same district
        query = """
    SELECT 
    cr.report_id,
    u.full_name AS citizen_name,
    cr.location_desc,
    cr.issue_type,
    cr.description,
    cr.photo_url,
    cr.risk_level,
    cr.status,
    cr.reported_at
FROM citizen_reports cr
JOIN users u ON cr.citizen_id = u.user_id
WHERE cr.district = %s
ORDER BY cr.reported_at DESC
"""

        cursor.execute(query, (worker_district,))
        rows = cursor.fetchall()

        reports = []

        for r in rows:
            reports.append({
                "report_id": r["report_id"],
                "citizen_name": r["citizen_name"],
                "location": r["location_desc"],
                "issue_type": r["issue_type"],
                "description": r["description"],
                "photo_url": r["photo_url"],
                "risk_level": r["risk_level"],
                "status": r["status"],
                "reported_at": str(r["reported_at"])
            })

        conn.close()

        return jsonify({
            "status": "success",
            "district": worker_district,
            "reports": reports
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
# # ==========================================================
# # HEALTH WORKER - GET CITIZEN REPORT NOTIFICATIONS
# # ==========================================================
# @app.route('/health-worker/notifications', methods=['GET'])
# def health_worker_notifications():
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()

#         query = """
#         SELECT 
#             cr.report_id,
#             u.full_name AS citizen_name,
#             cr.location_desc,
#             cr.issue_type,
#             cr.description,
#             cr.photo_url,
#             cr.risk_level,
#             cr.status,
#             cr.reported_at
#         FROM citizen_reports cr
#         JOIN users u ON cr.citizen_id = u.user_id
#         ORDER BY cr.reported_at DESC
#         """

#         cursor.execute(query)
#         rows = cursor.fetchall()

#         reports = []

#         for r in rows:
#             reports.append({
#                 "report_id": r["report_id"],
#                 "citizen_name": r["citizen_name"],
#                 "location": r["location_desc"],
#                 "issue_type": r["issue_type"],
#                 "description": r["description"],
#                 "photo_url": r["photo_url"],
#                 "risk_level": r["risk_level"],
#                 "status": r["status"],
#                 "reported_at": str(r["reported_at"])
#             })

#         conn.close()

#         return jsonify({
#             "status": "success",
#             "reports": reports
#         })

#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         }), 500
#==========================================================
#health worker reports
#==========================================================
# @app.route('/healthworker/reports', methods=['POST'])
# def get_reports():
#     try:
#         data = request.get_json()
#         health_worker_id = data.get("user_id")

#         if not health_worker_id:
#             return jsonify({
#                 "status": "error",
#                 "message": "user_id required"
#             }), 400

#         conn = get_connection()
#         cursor = conn.cursor()

#         # ✅ FIX 1: correct column name
#         cursor.execute(
#             "SELECT assigned_district FROM users WHERE user_id=%s AND role='health_worker'",
#             (health_worker_id,)
#         )
#         worker = cursor.fetchone()

#         if not worker:
#             return jsonify({
#                 "status": "error",
#                 "message": "Health worker not found"
#             }), 404

#         # ✅ FIX 2: DictCursor → use key
#         worker_district = worker["assigned_district"]

#         # ✅ Fetch ONLY same district reports
#         cursor.execute("""
#         SELECT * FROM citizen_reports
#         WHERE district = %s
#         """, (worker_district,))

#         reports = cursor.fetchall()

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "status": "success",
#             "reports": reports
#         })

#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         })
# ==========================================================
# ---------------- Admin: Fetch Patient Cases ----------------
@app.route("/admin/patient-cases", methods=["GET"])
def admin_patient_cases():
    severity_filter = request.args.get("severity", "").lower()  # optional filter

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT
                    case_id,
                    patient_name,
                    age,
                    gender,
                    location,
                    symptoms,
                    disease_type,
                    severity,
                    status
                FROM patient_cases
            """

            params = ()
            # Apply severity filter if provided
            if severity_filter in ("mild", "moderate", "severe", "low", "high"):
                query += " WHERE LOWER(severity)=%s"
                params = (severity_filter,)

            query += " ORDER BY case_id DESC"
            cursor.execute(query, params)
            cases = cursor.fetchall()

            # Format cases for Android frontend
            formatted_cases = []
            for case in cases:
                formatted_cases.append({
                    "caseId": case["case_id"],
                    "patientName": case["patient_name"],
                    "age": case["age"],
                    "gender": case["gender"],
                    "location": case["location"],
                    "symptoms": case["symptoms"],
                    "diseaseType": case["disease_type"],
                    "severity": case["severity"],
                    "status": case["status"]
                })

        return jsonify({"status": "success", "cases": formatted_cases})

    finally:
        conn.close()


# ==========================================================
# HEALTH WORKER PROFILE
# ==========================================================
# ==========================================================
# DELETE ACCOUNT API
# ==========================================================
# @app.route('/delete-account', methods=['POST'])
# def delete_account():
#     try:
#         data = request.get_json()

#         user_id = data.get("user_id")

#         if not user_id:
#             return jsonify({
#                 "status": "error",
#                 "message": "user_id is required"
#             }), 400

#         conn = get_connection()
#         cursor = conn.cursor()

#         # Check user exists
#         cursor.execute("SELECT user_id FROM users WHERE user_id=%s", (user_id,))
#         user = cursor.fetchone()

#         if not user:
#             return jsonify({
#                 "status": "error",
#                 "message": "User not found"
#             }), 404

#         # Delete user
#         cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
#         conn.commit()

#         conn.close()

#         return jsonify({
#             "status": "success",
#             "message": "Account deleted successfully"
#         })

#     except Exception as e:
#         return jsonify({
#             "status": "error",
#             "message": str(e)
#         }), 500

# ================= Admin Login API =================
# ================= Admin Login API =================
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and password required"
        }), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ✅ Correct MySQL query
        cursor.execute(
    "SELECT * FROM users WHERE LOWER(email)=LOWER(%s) AND role='admin'",
    (email,)
        )
        admin = cursor.fetchone()

        # ✅ Correct password check
        if admin and check_password_hash(admin['password_hash'], password):
            return jsonify({
                "status": "success",
                "message": "Admin login successful",
                "admin": {
                    "admin_id": admin['user_id'],
                    "full_name": admin['full_name'],
                    "email": admin['email']
                }
            }), 200

        return jsonify({
            "status": "error",
            "message": "Invalid admin credentials"
        }), 401

    finally:
        cursor.close()
        conn.close()

#==============================================   

# ==============================================
# API: Get report details by report_id
# ==============================================
@app.route("/report/<int:report_id>", methods=["GET"])
def get_report_details(report_id):
    conn = get_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            query = """
                SELECT 
                    r.report_id,
                    u.full_name AS citizen_name,
                    r.district AS location,
                    r.location_desc AS water_source,
                    r.issue_type AS incident_type,
                    r.risk_level,
                    r.reported_at AS report_date,
                    r.status AS report_status,
                    r.description,
                    r.photo_url AS photo_path
                FROM citizen_reports r
                JOIN users u ON r.citizen_id = u.user_id
                WHERE r.report_id = %s
            """
            cursor.execute(query, (report_id,))
            report = cursor.fetchone()
            if report and report['report_date']:
                report['report_date'] = str(report['report_date'])

            if not report:
                return jsonify({"status": "error", "message": "Report not found"}), 404

            return jsonify({"status": "success", "report": report}), 200
    except Exception as e:
        print("Error fetching report:", e)
        return jsonify({"status": "error", "message": "Server error"}), 500
    finally:
        conn.close()

# ==============================================
# API: Update report status
# ==============================================
@app.route("/report/<int:report_id>/status", methods=["POST"])
def update_report_status(report_id):
    data = request.get_json()
    new_status = data.get("status")

    if not new_status:
        return jsonify({"status": "error", "message": "Status is required"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            # First check if the report exists
            cursor.execute("SELECT report_id FROM citizen_reports WHERE report_id = %s", (report_id,))
            if not cursor.fetchone():
                return jsonify({"status": "error", "message": "Report not found"}), 404

            # Update the status
            cursor.execute(
                "UPDATE citizen_reports SET status = %s WHERE report_id = %s",
                (new_status, report_id)
            )
            conn.commit()
            return jsonify({"status": "success", "message": f"Report status updated to {new_status}"}), 200
    except Exception as e:
        print("Error updating report status:", e)
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

#Admin summary reports
# ==========================================================
# ADMIN SUMMARY REPORTS
# ==========================================================
@app.route("/admin/summary-reports", methods=["GET"])
def admin_summary_reports():

    conn = get_connection()

    if not conn:
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500

    try:
        with conn.cursor() as cursor:

            query = """
                SELECT
                    disease_type,
                    COUNT(*) AS case_count
                FROM patient_cases
                GROUP BY disease_type
                ORDER BY case_count DESC
            """

            cursor.execute(query)

            reports = cursor.fetchall()

        return jsonify({
            "status": "success",
            "reports": reports
        }), 200

    finally:
        conn.close()
#Health worker Cases
@app.route('/health-worker/cases', methods=['GET'])
def health_worker_cases():
    """
    Get all cases for the logged-in health worker
    Optional: filter by district or risk_level
    """
    # For now, assume all cases are returned
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            query = """
            SELECT 
                report_id,
                citizen_id,
                source_id,
                location_desc,
                issue_type,
                description,
                photo_path,
                risk_level,
                created_at
            FROM citizen_reports
            ORDER BY created_at DESC
            """
            cursor.execute(query)
            data = cursor.fetchall()

        return jsonify({
            "status": "success",
            "cases": data
        })

    finally:
        conn.close()

# ==========================================================
# ✅ UPDATE USER PROFILE
# ==========================================================
@app.route("/update-profile", methods=["POST"])
def update_profile():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    full_name = data.get("full_name", "").strip()

    if not user_id or not full_name:
        return jsonify({"status":"error","message":"User ID and full name are required"}), 400

    # Validate name: only letters and spaces
    if not re.match(r"^[A-Za-z\s]+$", full_name):
        return jsonify({"status":"error","message":"Full name must contain only letters and spaces"}), 400

    conn = get_connection()
    if not conn:
        return jsonify({"status":"error","message":"DB connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET full_name=%s WHERE user_id=%s",
                (full_name, user_id)
            )
            conn.commit()

        return jsonify({"status":"success","message":"Profile updated successfully"}), 200

    finally:
        conn.close()

# ==========================================================
# ✅ CHANGE PASSWORD FOR LOGGED-IN USERS
# ==========================================================
@app.route("/change-password", methods=["POST"])
def change_password():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not user_id or not old_password or not new_password or not confirm_password:
        return jsonify({"status":"error","message":"All fields are required"}), 400

    if new_password != confirm_password:
        return jsonify({"status":"error","message":"New passwords do not match"}), 400

    missing_requirements = validate_password(new_password)
    if missing_requirements:
        return jsonify({
            "status":"error",
            "message": f"Password must contain: {', '.join(missing_requirements)}"
        }), 400

    conn = get_connection()
    if not conn:
        return jsonify({"status":"error","message":"DB connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            # Fetch current password hash
            cursor.execute("SELECT password_hash FROM users WHERE user_id=%s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"status":"error","message":"User not found"}), 404

            if not check_password_hash(user["password_hash"], old_password):
                return jsonify({"status":"error","message":"Old password is incorrect"}), 401

            # Update with new password hash
            hashed_password = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE users SET password_hash=%s WHERE user_id=%s",
                (hashed_password, user_id)
            )
            conn.commit()

        return jsonify({"status":"success","message":"Password changed successfully"}), 200

    finally:
        conn.close()

# @app.route('/get-hw-patient-cases/<int:user_id>', methods=['GET'])
# def get_hw_patient_cases(user_id):
#     try:
#         print("✅ API HIT:", user_id)

#         conn = get_connection()
#         cursor = conn.cursor()

#         cursor.execute("""
#             SELECT 
#                 case_id,
#                 patient_name,
#                 symptoms,
#                 location,
#                 status
#             FROM patient_cases
#             WHERE health_worker_id = %s
#         """, (user_id,))

#         rows = cursor.fetchall()
#         print("ROWS:", rows)

#         cases = []
#         for row in rows:
#             # ✅ SAFE ACCESS (NO UNPACK ERROR)
#             cases.append({
#                 "caseId": row[0],
#                 "patientName": row[1],
#                 "symptoms": row[2],
#                 "location": row[3],
#                 "status": row[4]
#             })

#         cursor.close()
#         conn.close()

#         return {
#             "status": "success",
#             "cases": cases
#         }

#     except Exception as e:
#         print("ERROR:", e)
#         return {
#             "status": "error",
#             "message": str(e)
#         }
@app.route('/get-hw-patient-cases/<int:user_id>', methods=['GET'])
def get_hw_patient_cases(user_id):
    try:
        print("API USER_ID:", user_id)   # ✅ DEBUG

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT case_id, patient_name, symptoms, location, status
            FROM patient_cases
            WHERE health_worker_id = %s
        """, (user_id,))

        rows = cursor.fetchall()

        # Format for Android app (camelCase keys and success status)
        formatted_cases = []
        for row in rows:
            formatted_cases.append({
                "caseId": row.get("case_id"),
                "patientName": row.get("patient_name"),
                "symptoms": row.get("symptoms"),
                "location": row.get("location"),
                "status": row.get("status")
            })

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "cases": formatted_cases
        })

    except Exception as e:
        print("GET HW CASES ERROR:", e)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
# @app.route('/update-status/<int:case_id>', methods=['PUT'])
# def update_case_status(case_id):
#     try:
#         data = request.get_json()
#         status = data.get('status')   # "Completed"

#         conn = get_connection()
#         cursor = conn.cursor()

#         cursor.execute("""
#             UPDATE patient_cases 
#             SET status = %s 
#             WHERE case_id = %s
#         """, (status, case_id))   # ✅ directly store "Completed"

#         conn.commit()

#         return jsonify({
#             "status": "success",
#             "message": "Status updated"
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)})
# @app.route('/update-status/<int:case_id>', methods=['PUT'])
# def update_case_status(case_id):
#     try:
#         data = request.get_json()
#         status = data.get('status')

#         if not status:
#             return jsonify({"error": "Status is missing"}), 400

#         conn = get_connection()
#         cursor = conn.cursor()

#         cursor.execute("""
#             UPDATE patient_cases 
#             SET status = %s 
#             WHERE case_id = %s
#         """, (status, case_id))

#         conn.commit()

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "status": "success",
#             "message": "Status updated successfully"
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
# @app.route('/update-status/<int:case_id>', methods=['PUT'])
# def update_case_status(case_id):
#     try:
#         data = request.get_json()
#         status = data.get('status')

#         if not status:
#             return jsonify({"error": "Status is missing"}), 400

#         conn = get_connection()
#         cursor = conn.cursor()

#         cursor.execute("""
#             UPDATE patient_cases 
#             SET status = %s 
#             WHERE case_id = %s
#         """, (status, case_id))

#         conn.commit()

#         print("ROWS AFFECTED:", cursor.rowcount)  # DEBUG

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "status": "success",
#             "message": "Status updated successfully"
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
# @app.route('/update-status/<int:case_id>', methods=['PUT'])
# def update_case_status(case_id):
#     try:
#         # ❌ remove this (optional)
#         # data = request.get_json()
#         # status = data.get('status')

#         # ✅ force completed
#         status = "completed"

#         conn = get_connection()
#         cursor = conn.cursor()

#         cursor.execute("""
#             UPDATE patient_cases 
#             SET status = %s 
#             WHERE case_id = %s
#         """, (status, case_id))

#         conn.commit()

#         print("ROWS AFFECTED:", cursor.rowcount)

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "status": "success",
#             "message": "Marked as completed"
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
    
@app.route('/update-case-status/<int:case_id>', methods=['PUT'])
def update_case_status(case_id):
    try:
        data = request.get_json(force=True)
        status = data.get('status')

        conn = get_connection()
        cursor = conn.cursor()

        query = "UPDATE patient_cases SET status = %s WHERE case_id = %s"
        values = (status, case_id)

        cursor.execute(query, values)
        conn.commit()

        print("Updated:", case_id, status)
        print("Rows:", cursor.rowcount)

        cursor.close()
        conn.close()

        return jsonify({"status": "success"})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"status": "error", "message": str(e)})
    
# @app.route('/admin/get-all-cases', methods=['GET'])
# def get_all_cases():
#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT case_id, patient_name, status 
#         FROM patient_cases
#     """)

#     rows = cursor.fetchall()

#     return jsonify(rows)
@app.route('/admin/get-all-cases', methods=['GET'])
def get_all_cases():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT case_id, patient_name, status 
        FROM patient_cases
    """)

    rows = cursor.fetchall()

    cases = []
    for row in rows:
        cases.append({
    "case_id": row["case_id"],
    "patient_name": row["patient_name"],
    "status": row["status"]
    })

    cursor.close()
    conn.close()

    return jsonify({"status": "success", "cases": cases})

# @app.route("/citizen-reports/<int:user_id>", methods=["GET"])
# def get_citizen_reports(user_id):
#     conn = get_connection()
#     if conn is None:
#         return jsonify({"status": "error", "message": "Database connection failed"}), 500

#     try:
#         cursor = conn.cursor()

#         query = """
#         SELECT report_id,
#                user_id,
#                issue_type AS issueType,
#                location_desc,
#                description,
#                photo_url AS photoUrl,
#                status,
#                risk_level AS riskLevel,
#                reported_at
#         FROM citizen_reports
#         WHERE user_id = %s
#         ORDER BY reported_at DESC
#         """
#         cursor.execute(query, (user_id,))
#         reports = cursor.fetchall()  # Already dicts thanks to DictCursor

#         cursor.close()
#         conn.close()

#         return jsonify({
#             "status": "success",
#             "reports": reports
#         })

#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/citizen-reports", methods=["GET"])
def get_citizen_reports():
    conn = get_connection()
    if conn is None:
        return jsonify({"status": "error", "message": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        query = """
        SELECT report_id,
               user_id,
               issue_type AS issueType,
               location_desc,
               description,
               photo_url AS photoUrl,
               status,
               risk_level AS riskLevel,
               reported_at
        FROM citizen_reports
        ORDER BY reported_at DESC
        """
        cursor.execute(query)

        reports = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "reports": reports
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
# ==========================================================
#  RUN SERVER
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port = 5000, debug = True)