import sqlite3

conn = sqlite3.connect('DBproject.db')
c = conn.cursor()

# --- WaitingConfirmation ---
c.execute("""
CREATE TABLE IF NOT EXISTS WaitingConfirmation (
    Email VARCHAR(33) PRIMARY KEY UNIQUE,
    Name VARCHAR(20),
    Surname VARCHAR(20),
    Birthplace VARCHAR(40),
    Birthdate DATE,
    Street VARCHAR(50),
    City VARCHAR(35),
    ZIP CHAR,
    TaxCode CHAR(16) UNIQUE,
    Password VARCHAR(30),
    Telephone INTEGER UNIQUE,
    Role VARCHAR(10) CHECK(Role IN ('Patient', 'Specialist', 'Technician')),
    Weight INTEGER,
    Height INTEGER,
    EmergencyContactNumber INTEGER UNIQUE,
    Allergy VARCHAR(80),
    UniqueCode INTEGER,
    MedicalRegistrationCode INTEGER
);
""")
# --- Person ---
c.execute("""
CREATE TABLE IF NOT EXISTS Person (
    ID_Person TEXT PRIMARY KEY,
    Email VARCHAR(40) UNIQUE,
    Name VARCHAR(20) NOT NULL,
    Surname VARCHAR(20) NOT NULL,
    Birthplace VARCHAR(40),
    Birthdate DATE,
    Street VARCHAR(50),
    City VARCHAR(35),
    ZIP INTEGER,
    TaxCode CHAR(16) UNIQUE,
    Password VARCHAR(30),
    Telephone INTEGER UNIQUE,
    CompanyAuthenticationCode INTEGER,
    Role VARCHAR(10) CHECK(Role IN ('Patient', 'Specialist', 'Technician'))
);
""")

# --- Technician ---
c.execute("""
CREATE TABLE IF NOT EXISTS Technician (
    ID_Technician TEXT PRIMARY KEY,
    CompanyAuthenticationCode INTEGER,
    FOREIGN KEY (ID_Technician) REFERENCES Person (ID_Person)
);
""")

# --- Backup ---
c.execute("""
CREATE TABLE IF NOT EXISTS Backup (
    ID_Technician TEXT,
    IP_DBMS TEXT,
    Size INTEGER,
    BackupDate DATE,
    BackupTime TIME,
    Data TEXT,
    StorageName TEXT,
    PRIMARY KEY (ID_Technician, IP_DBMS, BackupDate, BackupTime),
    FOREIGN KEY (ID_Technician) REFERENCES Technician (ID_Technician),
    FOREIGN KEY (IP_DBMS) REFERENCES DBMS (IP_DBMS)
);
""")

# --- DBMS ---
c.execute("""
CREATE TABLE IF NOT EXISTS DBMS (
    IP_DBMS TEXT PRIMARY KEY,
    Type VARCHAR(20),
    Version VARCHAR(40)
);
""")

# --- Ticket ---
c.execute("""
CREATE TABLE IF NOT EXISTS Ticket (
    Code TEXT PRIMARY KEY,
    ID_Person TEXT,
    Title VARCHAR(50),
    Body VARCHAR(200),
    CompilationDate DATE,
    CompilationTime TIME,
    Type VARCHAR(20),
    IsReplied INTEGER DEFAULT 0,             -- 0 = non risposto, 1 = risposto
    Reply TEXT,                              -- risposta del tecnico
    ReplyDate DATE,                          -- data della risposta
    ReplyTime TIME,                          -- ora della risposta
    FOREIGN KEY (ID_Person) REFERENCES Person (ID_Person)
);
""")

# --- NotificationSystem ---
c.execute("""
CREATE TABLE IF NOT EXISTS NotificationSystem(
    Type VARCHAR(20),
    Version VARCHAR(40),
    PRIMARY KEY (Type, Version)
);
""")

# --- Notification ---
c.execute("""
CREATE TABLE IF NOT EXISTS Notification (
    ID_Person TEXT,
    NS_Version TEXT,
    NS_Type TEXT,
    Type VARCHAR(20),
    Title VARCHAR(50),
    Body VARCHAR(200),
    CompilationDate DATE,
    CompilationTime TIME,
    IsRead INTEGER DEFAULT 0,
    ID_Visit TEXT,
    PRIMARY KEY (ID_Person, CompilationDate, CompilationTime),
    FOREIGN KEY (ID_Person) REFERENCES Person (ID_Person),
    FOREIGN KEY (NS_Version) REFERENCES NotificationSystem (Version),
    FOREIGN KEY (NS_Type) REFERENCES NotificationSystem (Type),
    FOREIGN KEY (ID_Visit) REFERENCES Visit (ID_Visit)
);
""")

#Chat
c.execute("""
CREATE TABLE IF NOT EXISTS ChatMessages (
    ID_Message TEXT PRIMARY KEY,
    SenderID TEXT NOT NULL,
    ReceiverID TEXT NOT NULL,
    MessageBody TEXT NOT NULL,
    CompilationDate DATE,
    CompilationTime TIME,
    IsRead INTEGER DEFAULT 0,
    FOREIGN KEY (SenderID) REFERENCES Person(ID_Person),
    FOREIGN KEY (ReceiverID) REFERENCES Person(ID_Person)
);
""")

# --- Patient ---
c.execute("""
CREATE TABLE IF NOT EXISTS Patient (
    ID_Patient TEXT PRIMARY KEY,
    ID_Specialist TEXT,
    Weight INTEGER,
    Height INTEGER,
    Allergy VARCHAR(80),
    EmergencyContactNumber INTEGER UNIQUE,
    FOREIGN KEY (ID_Patient) REFERENCES Person (ID_Person),
    FOREIGN KEY (ID_Specialist) REFERENCES Person (ID_Person)
);
""")

# --- Specialist ---
c.execute("""
CREATE TABLE IF NOT EXISTS Specialist (
    ID_Specialist TEXT PRIMARY KEY,
    MedicalRegistrationCode INTEGER,
    FOREIGN KEY (ID_Specialist) REFERENCES Person (ID_Person)
);
""")

# --- AssociationUniqueCode ---
c.execute("""
CREATE TABLE IF NOT EXISTS AssociationUniqueCode (
    UniqueCode INTEGER PRIMARY KEY,
    Email VARCHAR(33),
    ID_Specialist TEXT,
    FOREIGN KEY (Email) REFERENCES WaitingConfirmation (Email),
    FOREIGN KEY (ID_Specialist) REFERENCES Specialist (ID_Specialist)
);
""")

# --- Note ---
c.execute("""
CREATE TABLE IF NOT EXISTS Note (
    ID_Person TEXT,
    Title VARCHAR(50),
    Body VARCHAR(200),
    CompilationDate DATE,
    CompilationTime TIME,
    ExamType VARCHAR(20),
    PRIMARY KEY (ID_Person, CompilationDate, CompilationTime),
    FOREIGN KEY (ID_Person) REFERENCES Person (ID_Person)
);
""")

# --- Visit ---
c.execute("""
CREATE TABLE IF NOT EXISTS Visit (
    ID_Visit TEXT PRIMARY KEY,
    ID_Patient TEXT,
    ID_Specialist TEXT,
    Type VARCHAR(20),
    Place VARCHAR(30),
    Annotation VARCHAR(200),
    VisitDate DATE,
    VisitTime TIME,
    FOREIGN KEY (ID_Patient) REFERENCES Patient (ID_Patient),
    FOREIGN KEY (ID_Specialist) REFERENCES Specialist (ID_Specialist)
);
""")

# --- Prescription ---
c.execute("""
CREATE TABLE IF NOT EXISTS Prescription (
    ID_Prescription TEXT PRIMARY KEY,
    ID_Patient TEXT,
    ID_Specialist TEXT,
    IP_SS INTEGER,
    Type VARCHAR(50),
    Title VARCHAR(50),
    Body VARCHAR(200),
    CompilationDate DATE,
    CompilationTime TIME,
    FOREIGN KEY (ID_Patient) REFERENCES Patient (ID_Patient),
    FOREIGN KEY (ID_Specialist) REFERENCES Specialist (ID_Specialist),
    FOREIGN KEY (IP_SS) REFERENCES SS_Middleware (IP_SS)
);
""")

# --- EHR ---
c.execute("""
CREATE TABLE IF NOT EXISTS EHR (
    ID_Patient TEXT,
    IP_SS INTEGER,
    ID_Specialist TEXT,
    URL TEXT,
    PRIMARY KEY (ID_Patient, IP_SS, ID_Specialist),
    FOREIGN KEY (ID_Patient) REFERENCES Patient (ID_Patient),
    FOREIGN KEY (ID_Specialist) REFERENCES Specialist (ID_Specialist),
    FOREIGN KEY (IP_SS) REFERENCES SS_Middleware (IP_SS)
);
""")

# --- SS_Middleware ---
c.execute("""
CREATE TABLE IF NOT EXISTS SS_Middleware (
    IP_SS INTEGER PRIMARY KEY,
    Owner VARCHAR(50),
    Version VARCHAR(20)
);
""")

# --- AutomaticData ---
c.execute("""
CREATE TABLE IF NOT EXISTS AutomaticData (
    ID_AutomaticData TEXT PRIMARY KEY,
    UDI INTEGER,
    ID_Patient TEXT,
    Name VARCHAR(50),
    UnitOfMeasure VARCHAR(10),
    Value REAL,
    CompilationDate DATE,
    CompilationTime TIME,
    FOREIGN KEY (ID_Patient) REFERENCES Patient (ID_Patient),
    FOREIGN KEY (UDI) REFERENCES ExternalDevice (UDI)
);
""")

# --- ManualData ---
c.execute("""
CREATE TABLE IF NOT EXISTS ManualData (
    ID_ManualData TEXT PRIMARY KEY,
    ID_Visit TEXT,
    BloodPressure VARCHAR(10),
    OxygenSaturation VARCHAR(10),
    Weight VARCHAR(10),
    VisitNote VARCHAR(200),
    CompilationDate DATE,
    CompilationTime TIME,
    FOREIGN KEY (ID_Visit) REFERENCES Visit (ID_Visit)
);
""")

# --- ExternalDevice ---
c.execute("""
CREATE TABLE IF NOT EXISTS ExternalDevice (
    UDI INTEGER PRIMARY KEY,
    Producer VARCHAR(50),
    ID_Patient TEXT,
    FOREIGN KEY (ID_Patient) REFERENCES Patient (ID_Patient)
);
""")

# --- Questionnaire ---
c.execute("""
CREATE TABLE IF NOT EXISTS Questionnaire (
    ID_Filled TEXT PRIMARY KEY,
    ID_Patient TEXT NOT NULL,
    TemplateID TEXT NOT NULL,
    TemplateName TEXT,
    Frequency TEXT,
    Score INTEGER,
    CompilationDate DATE,
    CompilationTime TIME,
    FOREIGN KEY (ID_Patient) REFERENCES Patient (ID_Patient)
);
""")

# --- QuestionnaireAnswer ---
c.execute("""
CREATE TABLE IF NOT EXISTS QuestionnaireAnswer (
    ID_Filled TEXT,
    QuestionIndex INTEGER,
    Answer TEXT,
    PRIMARY KEY (ID_Filled, QuestionIndex),
    FOREIGN KEY (ID_Filled) REFERENCES Questionnaire (ID_Filled)
);
""")

# Commit(confirm) changes
conn.commit()

# Close connection
conn.close()