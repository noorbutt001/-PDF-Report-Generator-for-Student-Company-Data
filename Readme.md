# 🐍 PDF Report Generator for Student & Company Data

## 📌 Project Overview
This project is a Python-based PDF Report Generator that automates the creation of professional reports for student and company data. It reads data from CSV and JSON files and generates structured PDF reports using the ReportLab library.

---

## 🎯 Features
✔ Load student data from CSV files  
✔ Load company data from JSON files  
✔ Generate professional PDF reports  
✔ Automatic file saving with unique names  
✔ Clean table-based formatting  
✔ Menu-driven CLI system  
✔ Error handling for missing data  

---

## ⚙️ Technologies Used
- Python 3.x  
- ReportLab (PDF generation)  
- CSV module  
- JSON module  
- OS module  
- Datetime module

pdf_report_generator/
│
├── main.py
├── menu.py
├── data_handler.py
├── pdf_generator.py
│
├── data/
│ ├── students.csv
│ └── company.json
│
├── reports/
└── README.md


---

## 🚀 How to Run

### 1️⃣ Install dependencies
```bash
pip install reportlab
2️⃣ Run the project
python main.py
📥 Input Data Format
CSV Example (Student Data)
name,id,email,course,marks,attendance
Ali,101,ali@gmail.com,BSCS,85,90%
Sara,102,sara@gmail.com,BSSE,92,95%
JSON Example (Company Data)
[
  {
    "name": "Ahmed",
    "id": 1,
    "email": "ahmed@company.com",
    "role": "Developer",
    "performance": "Excellent"
  }
]
📊 Output
PDF reports saved in the reports folder
Each file is named with a timestamp
Clean and structured table format
Professional report layout
🌟 Future Enhancements
GUI version using Tkinter
Add charts and analytics
Password-protected PDFs
Database integration (MySQL)
Bulk report generation
👨‍💻 Author

Python Mini Project – PDF Report Generator System


---
