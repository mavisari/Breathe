import sqlite3

# Create a connection to database
conn = sqlite3.connect('DBproject.db')
c = conn.cursor()

# --- WaitingConfirmation ---
data_patient = [
    ("alex@gmail.com", "Alex", "Bianchi", "Milano", "1942-09-30", "Via Largo Oreste 5", "Milano", "20133", "BNCLXA42P30F205N", "pizzarossa", "+39256789123", "Patient", 90, 183, "+39345678911", "Pollen", 2223, None)
]
c.executemany("INSERT INTO WaitingConfirmation (Email, Name, Surname, Birthplace, Birthdate, Street, City, ZIP, TaxCode, Password, Telephone, Role, Weight, Height, EmergencyContactNumber, Allergy, UniqueCode, MedicalRegistrationCode) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data_patient)

data_specialist = [
    ('marco.bianchi@medicmail.it', "Marco", "Bianchi", "Torino", "1978-11-02", "Corso Vittorio Emanuele II 87", "Torino", "10128", "BNCMRC78S02L219Y", "MedicoSecure789", "+393472345678", "Specialist", None, None, "+39345678912", None, None, 892173)
]
c.executemany("INSERT INTO WaitingConfirmation (Email, Name, Surname, Birthplace, Birthdate, Street, City, ZIP, TaxCode, Password, Telephone, Role, Weight, Height, EmergencyContactNumber, Allergy, UniqueCode, MedicalRegistrationCode) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data_specialist)

# --- Person ---
data_person = [
    ("P0000", "alice@gmail.com", "Alice", "Rossi", "Pescara", "1955-05-08", "Via Madonna 14", "Pescara", "65129", "RSSLCA55E48G482Z", "fragola25", "3912345675", "Patient", ""),
    ("P0001", "roberto@gmail.com", "Roberto", "Fumagalli", "Viterbo", "1948-05-05", "Via Francesco Borgatti 18", "Roma", "00128", "FMGRRT48E05M082L", "8giuggiola8", "39234567891", "Patient", ""),
    ("S0003", "elena.verdi@clinicmail.it", "Elena", "Verdi", "Napoli", "1985-07-24", "Via Posillipo 101", "Napoli", "80123", "VRDLNE85L64F839U", "ClinicaTop_2024", "393493210987", "Specialist",""),
    ("T0005", "luca.romani@techmail.it", "Luca", "Romani", "Genova", "1992-02-11", "Via XX Settembre 33", "Genova", "16121", "RMLLCU92B11D969A", "TechPass456!", "393477654321", "Technician", "98234"),
    ("T0006", "sara.martini@biolab.it", "Sara", "Martini", "Bologna", "1988-10-05", "Via delle Scienze 45", "Bologna", "40126", "MRTSRA88R45A944F", "BioTech2024#", "393496789012", "Technician", "76509")
]
c.executemany("INSERT INTO Person (ID_Person, Email, Name, Surname, Birthplace, Birthdate, Street, City, ZIP, TaxCode, Password, Telephone, Role, CompanyAuthenticationCode) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data_person)
              
# --- Technician ---
technicians = [
    ("T0005", "98234"),
    ("T0006", "76509")
]
c.executemany("INSERT INTO Technician (ID_Technician, CompanyAuthenticationCode) VALUES (?, ?)", technicians)

# --- Backup ---
backups = [
    ('T0005', '192168110', 2048, '2025-05-08', '14:30:00', 'backup_data_001.bak', "Cloud A"),
    ('T0006', '192168110', 1024, '2025-05-07', '09:15:00', 'backup_data_002.bak', "Cloud B")
]
c.executemany("INSERT INTO Backup (ID_Technician, IP_DBMS, Size, BackupDate, BackupTime, Data, StorageName) VALUES (?, ?, ?, ?, ?, ?, ?)", backups)

# --- DBMS ---
dbms_entries = [
    ('192168110', 'MySQL', '8.0.33')
]
c.executemany("INSERT INTO DBMS (IP_DBMS, Type, Version) VALUES (?, ?, ?)", dbms_entries)

# --- Ticket ---
ticket_data = [
    ("TK0000", "P0000", "Problem with the chat", "I can't contact the specialist.", "2025-05-08", "08:45:00", "Assistance", 0, None, None, None),
    ("TK0001", "S0003", "Error compilation", "Error inserting note.", "2025-05-08", "11:30:00", "App", 0, None, None, None)
]
c.executemany("INSERT INTO Ticket (Code, ID_Person, Title, Body, CompilationDate, CompilationTime, Type, IsReplied, Reply, ReplyDate, ReplyTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", ticket_data)

# --- NotificationSystem ---
notification_system_data = [
    ("Usual", "v1.0")]
c.executemany("INSERT OR IGNORE INTO NotificationSystem (Type, Version) VALUES (?, ?)", notification_system_data)

# --- Patient ---
data_patient_table = [
    ("P0000", "S0003", 80, 165, "3989198278", "Strawberries"),
    ("P0001", "S0003", 76, 178, "39345678913", "Pollen")
]
c.executemany("INSERT INTO Patient (ID_Patient, ID_Specialist, Weight, Height, EmergencyContactNumber, Allergy) VALUES (?, ?, ?, ?, ?, ?)", data_patient_table)

# --- Specialist ---
data_specialist_table = [
    ("S0003", 735462)
]
c.executemany("INSERT INTO Specialist (ID_Specialist, MedicalRegistrationCode) VALUES (?, ?)", data_specialist_table)

# --- AssociationUniqueCode ---
association_data = [
    (2223, "alex@gmail.com", "S0003"),
    (9845, "alice@gmail.com", "S0003")
]
c.executemany("INSERT INTO AssociationUniqueCode (UniqueCode, Email, ID_Specialist) VALUES (?, ?, ?)", association_data)

# --- Note ---
note_data = [
    ("S0003", "Routine visit", "All parameters normal. Patient in good health.", "2025-05-10", "12:00:00", "Routine visit"),
    ("S0003", "PSG", "Polysomnography completed, no significant anomalies.", "2025-05-12", "09:00:00", "PSG"),
    ("P0000", "Routine visit", "Mild hypertension detected, follow up in 3 months.", "2025-05-10", "12:00:00", "Routine visit")
]
c.executemany("INSERT OR IGNORE INTO Note (ID_Person, Title, Body, CompilationDate, CompilationTime, ExamType) VALUES (?, ?, ?, ?, ?, ?)", note_data)

# --- ExternalDevice ---
external_device_data = [
    (1001, "Withings", "P0000"),
    (1002, "Withings", "P0001")
]
c.executemany("INSERT INTO ExternalDevice (UDI, Producer, ID_Patient) VALUES (?, ?, ?)", external_device_data)

# --- AutomaticData ---
automatic_data = [
    ("AD00000", 1001, "P0000", "Heart Rate", "bpm", 72, "2025-05-08", "10:00:00"),
    ("AD00001", 1002, "P0001", "Heart Rate", "bpm", 80, "2025-05-08", "10:15:00")
]
c.executemany("INSERT INTO AutomaticData (ID_AutomaticData, UDI, ID_Patient, Name, UnitOfMeasure, Value, CompilationDate, CompilationTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", automatic_data)

# --- Visit --- (PRIMA delle ManualData!)
visit_data = [
    ("V0001", "P0000", "S0003", "Check-up", "Naples Clinic", "All normal", "2025-05-07", "09:30:00"),
    ("V0002", "P0001", "S0003", "Follow-up", "Rome Clinic", "All normal", "2025-05-06", "11:00:00")
]
c.executemany("INSERT INTO Visit (ID_Visit, ID_Patient, ID_Specialist, Type, Place, Annotation, VisitDate, VisitTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", visit_data)

# --- ManualData ---
manual_data = [
    ("MD00000", "V0001", "120/80", "92%", "72 kg", "All normal", "2025-05-07", "09:35:00"),
    ("MD00001", "V0002", "110/70", "97%", "65", "All normal", "2025-05-06", "11:05:00")
]
c.executemany("INSERT INTO ManualData (ID_ManualData, ID_Visit, BloodPressure, OxygenSaturation, Weight, VisitNote, CompilationDate, CompilationTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", manual_data)

# --- EHR ---
ehr_data = [
    ("P0000", 101001, "S0003", "https://ehr.abruzzo.it/P0000"),
]
c.executemany("INSERT INTO EHR (ID_Patient, IP_SS, ID_Specialist, URL) VALUES (?, ?, ?, ?)", ehr_data)

# --- Prescription ---
prescription_data = [
    ("PR0000", "P0000", "S0003", 101001, "Medication", "Paracetamol 500mg", "Take every 8 hours", "2025-05-07", "09:40:00"),
]
c.executemany("INSERT INTO Prescription (ID_Prescription, ID_Patient, ID_Specialist, IP_SS, Type, Title, Body, CompilationDate, CompilationTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", prescription_data)

# --- SS_Middleware ---
ss_middleware_data = [
    (101001, "AbruzzoRegion", "1.0.0"),
    (101002, "LazioRegion", "1.2.5")
]
c.executemany("INSERT INTO SS_Middleware (IP_SS, Owner, Version) VALUES (?, ?, ?)", ss_middleware_data)

# --- Questionnaire ---
compiled = [
    ("PSQI_15_2024-04-01", "P0000", "PSQI", "Pittsburgh Sleep Quality Index", "Monthly", 3, "2024-04-01", "10:30:00"),
    ("PROMIS_15_2024-05-01", "P0000", "PROMIS", "PROMIS Global Health", "Quarterly", 3, "2024-05-01", "11:00:00"),
    ("Berlin_15_2024-05-05", "P0000", "Berlin", "Berlin Questionnaire", "Once", 3, "2024-05-05", "09:45:00")
]
c.executemany("INSERT INTO Questionnaire (ID_Filled, ID_Patient, TemplateID, TemplateName, Frequency, Score, CompilationDate, CompilationTime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", compiled)

# --- QuestionnaireAnswer ---
answers = [
    ("PSQI_15_2024-04-01", 0, "9-11 PM"),
    ("PSQI_15_2024-04-01", 1, "15-30 min"),
    ("PSQI_15_2024-04-01", 2, "Fairly good"),
    ("PROMIS_15_2024-05-01", 0, "Good"),
    ("PROMIS_15_2024-05-01", 1, "Sometimes"),
    ("PROMIS_15_2024-05-01", 2, "Moderately"),
    ("Berlin_15_2024-05-05", 0, "Yes"),
    ("Berlin_15_2024-05-05", 1, "No"),
    ("Berlin_15_2024-05-05", 2, "Yes")
]
c.executemany("INSERT INTO QuestionnaireAnswer (ID_Filled, QuestionIndex, Answer) VALUES (?, ?, ?)", answers)

# --- Notification (deve essere DOPO le visite, per poterle collegare!) ---
notification_data = [
    # (ID_Person, NS_Version, NS_Type, Type, Title, Body, CompilationDate, CompilationTime, IsRead, ID_Visit)
    ("S0003", "v1.0", "Usual", "Calendar", "New appointment", "You have a new appointment scheduled.", "2025-05-15", "10:00:00", 0, None),
    ("S0003", "v1.0", "Usual", "Calendar", "Event added", "A new calendar event has been added.", "2025-05-15", "12:00:00", 1, None),
    ("S0003", "v1.0", "Usual", "Assistance", "Ticket solved", "Your support ticket has been solved by the technician.", "2025-05-15", "17:00:00", 0, None),
    ("P0000", "v1.0", "Usual", "Contact", "New Message", "Good evening Alice.", "2025-05-10", "09:00:00", 0, None),
    ("P0000", "v1.0", "Usual", "Assistance", "Ticket solved", "Your support ticket has been solved by the technician.", "2025-05-15", "15:00:00", 0, None)
]
c.executemany("INSERT OR IGNORE INTO Notification (ID_Person, NS_Version, NS_Type, Type, Title, Body, CompilationDate, CompilationTime, IsRead, ID_Visit) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", notification_data)

# Commit changes
conn.commit()
conn.close()