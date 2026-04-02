CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('citizen', 'health_worker', 'admin') NOT NULL,
    phone_number VARCHAR(20) NULL,
    assigned_district VARCHAR(100) NULL,
    hw_id_code VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
-- CREATE TABLE IF NOT EXISTS water_sources (
--     source_id INT AUTO_INCREMENT PRIMARY KEY,
--     name VARCHAR(150) NOT NULL, 
--     type ENUM('well', 'public_tap', 'river', 'lake', 'other') NOT NULL,
--     district_zone VARCHAR(100) NOT NULL, 
--     latitude DECIMAL(10, 8) NULL,
--     longitude DECIMAL(11, 8) NULL,
--     status ENUM('safe', 'moderate', 'unsafe', 'pending_test') DEFAULT 'pending_test',
--     last_tested_date TIMESTAMP NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );
CREATE TABLE IF NOT EXISTS water_sources (
    source_id INT AUTO_INCREMENT PRIMARY KEY,
    source_name VARCHAR(150),
    source_type VARCHAR(100),
    village VARCHAR(150),
    contamination_level ENUM('low','moderate','high') DEFAULT 'low',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- CREATE TABLE IF NOT EXISTS citizen_reports (
--     report_id INT AUTO_INCREMENT PRIMARY KEY,
--     citizen_id INT NOT NULL,
--     source_id INT NULL, 
--     location_desc VARCHAR(255) NULL, 
--     issue_type VARCHAR(100) NOT NULL, 
--     description TEXT,
--     photo_url VARCHAR(255) NULL,
--     status ENUM('new', 'viewed', 'forwarded_to_admin', 'resolved') DEFAULT 'new',
--     risk_level ENUM('low', 'moderate', 'high') DEFAULT 'moderate',
--     reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--     CONSTRAINT fk_citizen FOREIGN KEY (citizen_id) REFERENCES users(user_id) ON DELETE CASCADE,
--     CONSTRAINT fk_report_source FOREIGN KEY (source_id) REFERENCES water_sources(source_id) ON DELETE SET NULL
-- );
CREATE TABLE citizen_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    citizen_id INT NOT NULL,
    source_id INT DEFAULT NULL,
    location_desc VARCHAR(255),
    issue_type VARCHAR(100) NOT NULL,
    description TEXT,
    photo_url VARCHAR(255),
    status ENUM('new','viewed','forwarded_to_admin','resolved') DEFAULT 'new',
    risk_level ENUM('low','moderate','high') DEFAULT 'moderate',
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (citizen_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES water_sources(source_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS patient_cases (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    health_worker_id INT NOT NULL,
    patient_name VARCHAR(150) NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    location VARCHAR(255) NOT NULL,
    symptoms JSON NOT NULL, 
    other_symptoms TEXT NULL,
    severity ENUM('Mild', 'Moderate', 'Severe') NOT NULL,
    disease_type VARCHAR(100) NULL, 
    status ENUM('Active', 'Resolved', 'Fatal') DEFAULT 'Active',
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_health_worker FOREIGN KEY (health_worker_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS system_notifications (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    severity ENUM('Info', 'Warning', 'Critical') NOT NULL,
    target_audience ENUM('All', 'Citizens', 'Health Workers') DEFAULT 'All',
    issued_by INT NULL, 
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_admin_issuer FOREIGN KEY (issued_by) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS user_preferences (
    pref_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    receive_citizen_reports BOOLEAN DEFAULT TRUE,
    receive_admin_alerts BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_user_pref FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE water_checks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    citizen_id INT,
    source_type VARCHAR(100),
    appearance VARCHAR(100),
    smell VARCHAR(100),
    taste VARCHAR(100),
    symptoms VARCHAR(100),
    risk_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE water_source_details (
id INT AUTO_INCREMENT PRIMARY KEY,
case_id INT,
water_type VARCHAR(100),
source VARCHAR(100),
appearance VARCHAR(100),
treatment VARCHAR(100),
risk_level VARCHAR(20),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (case_id) REFERENCES patient_cases(id) ON DELETE CASCADE
);

CREATE TABLE health_workers (
    worker_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    assigned_district VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
