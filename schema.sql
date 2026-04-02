-- HydroGuard Database Schema
-- Target RDBMS: MySQL

CREATE DATABASE IF NOT EXISTS hydroguard_db;
USE hydroguard_db;

-- 1. Users Table (Citizens, Health Workers, Admins)
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('citizen', 'health_worker', 'admin') NOT NULL,
    phone_number VARCHAR(20) NULL,
    assigned_district VARCHAR(100) NULL, -- Specifically for Health Workers
    hw_id_code VARCHAR(50) NULL, -- E.g., HW-2024-0042
    otp VARCHAR(10) NULL,
    otp_expiry TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Water Sources Table (For logging all physical community water sources)
CREATE TABLE IF NOT EXISTS water_sources (
    source_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL, -- e.g. 'Community Well'
    type ENUM('well', 'public_tap', 'river', 'lake', 'other') NOT NULL,
    district_zone VARCHAR(100) NOT NULL, -- e.g. 'Central District, Zone A'
    latitude DECIMAL(10, 8) NULL,
    longitude DECIMAL(11, 8) NULL,
    status ENUM('safe', 'moderate', 'unsafe', 'pending_test') DEFAULT 'pending_test',
    last_tested_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Citizen Water Issue Reports Table
CREATE TABLE IF NOT EXISTS citizen_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    citizen_id INT NOT NULL,
    source_id INT NULL, -- Can be NULL if the citizen reported a completely new unknown location
    location_desc VARCHAR(255) NULL, -- Manual entry if source_id is null
    issue_type VARCHAR(100) NOT NULL, -- e.g. 'Contamination', 'Dry well'
    description TEXT,
    photo_url VARCHAR(255) NULL,
    status ENUM('new', 'viewed', 'forwarded_to_admin', 'resolved') DEFAULT 'new',
    risk_level ENUM('low', 'moderate', 'high') DEFAULT 'moderate',
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_citizen FOREIGN KEY (citizen_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_report_source FOREIGN KEY (source_id) REFERENCES water_sources(source_id) ON DELETE SET NULL
);

-- 4. Health Worker Patient Cases Table 
CREATE TABLE IF NOT EXISTS patient_cases (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    health_worker_id INT NOT NULL,
    patient_name VARCHAR(150) NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    location VARCHAR(255) NOT NULL, -- Auto-detected or manually entered
    symptoms JSON NOT NULL, -- Array of selected symptoms e.g. '["Fever", "Vomiting", "Diarrhea"]'
    other_symptoms TEXT NULL,
    severity ENUM('Mild', 'Moderate', 'Severe') NOT NULL,
    disease_type VARCHAR(100) NULL, -- E.g. Cholera, Typhoid (Added after diagnosis)
    status ENUM('Active', 'Resolved', 'Fatal') DEFAULT 'Active',
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_health_worker FOREIGN KEY (health_worker_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 5. System Alerts Table
CREATE TABLE IF NOT EXISTS system_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    severity ENUM('Info', 'Warning', 'Critical') NOT NULL,
    target_audience ENUM('All', 'Citizens', 'Health Workers') DEFAULT 'All',
    issued_by INT NULL, -- Admin who issued the alert
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_admin_issuer FOREIGN KEY (issued_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- 6. User Notification Preferences (Optional/Extensional based on Profile screen)
CREATE TABLE IF NOT EXISTS user_preferences (
    pref_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    receive_citizen_reports BOOLEAN DEFAULT TRUE,
    receive_admin_alerts BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_user_pref FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
