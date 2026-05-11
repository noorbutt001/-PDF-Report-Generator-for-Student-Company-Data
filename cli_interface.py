"""Professional CLI interface"""

from pathlib import Path
from data.data_manager import DataManager
from reports.student_report import StudentReportGenerator
from reports.employee_report import EmployeeReportGenerator
from config.logger_config import get_logger

logger = get_logger(__name__)

class CLIInterface:
    """Enterprise CLI interface"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.student_gen = StudentReportGenerator()
        self.employee_gen = EmployeeReportGenerator()
    
    def run(self) -> None:
        """Main CLI loop"""
        self._display_banner()
        
        while True:
            choice = input("\n> Select option (1-5): ").strip()
            
            if choice == "1":
                self._student_menu()
            elif choice == "2":
                self._employee_menu()
            elif choice == "5":
                print("👋 Goodbye!")
                break
    
    def _display_banner(self) -> None:
        """Display CLI banner"""
        print("=" * 60)
        print("🐍 PDF REPORT GENERATOR - Professional Edition v2.0")
        print("=" * 60)
    
    def _student_menu(self) -> None:
        """Student report menu"""
        print("\n📚 STUDENT REPORTS")
        print("1. Add Student")
        print("2. Generate Report")
        print("3. Back")
        
        choice = input("> ").strip()
        if choice == "1":
            self._add_student()
        elif choice == "2":
            self._generate_student_report()
    
    def _employee_menu(self) -> None:
        """Employee report menu"""
        print("\n👔 EMPLOYEE REPORTS")
        print("1. Add Employee")
        print("2. Generate Report")
        print("3. Back")
        
        choice = input("> ").strip()
        if choice == "1":
            self._add_employee()
        elif choice == "2":
            self._generate_employee_report()
    
    def _add_student(self) -> None:
        """Add student record"""
        try:
            student = {
                "name": input("Name: "),
                "id": input("ID: "),
                "email": input("Email: "),
                "course": input("Course: "),
                "gpa": float(input("GPA: ") or 3.0),
                "attendance": int(input("Attendance: ") or 80),
            }
            
            if self.data_manager.add_record(student):
                print("✓ Student added")
            else:
                print("✗ Failed to add student")
        
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"✗ Error: {e}")
    
    def _add_employee(self) -> None:
        """Add employee record"""
        try:
            emp = {
                "name": input("Name: "),
                "id": input("ID: "),
                "email": input("Email: "),
                "department": input("Department: "),
                "position": input("Position: "),
                "salary": float(input("Salary: ") or 50000),
                "performance_rating": float(input("Rating: ") or 3.0),
            }
            
            if self.data_manager.add_record(emp):
                print("✓ Employee added")
            else:
                print("✗ Failed to add employee")
        
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"✗ Error: {e}")
    
    def _generate_student_report(self) -> None:
        """Generate student report"""
        records = self.data_manager.get_records()
        if not records:
            print("✗ No records loaded")
            return
        
        try:
            file_path = self.student_gen.generate(records[0])
            print(f"✓ Report generated: {file_path}")
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"✗ Error: {e}")
    
    def _generate_employee_report(self) -> None:
        """Generate employee report"""
        records = self.data_manager.get_records()
        if not records:
            print("✗ No records loaded")
            return
        
        try:
            file_path = self.employee_gen.generate(records[0])
            print(f"✓ Report generated: {file_path}")
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"✗ Error: {e}")