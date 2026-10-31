import os
import django
import sys

# Add the project directory to sys.path
project_path = r'c:\Users\amrut\Desktop\Snehasparsham\myproject'
sys.path.append(project_path)

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Initialize Django
django.setup()

from myapp.models import User, Caretaker

print("--- User roles ---")
roles = User.objects.values_list('role', flat=True).distinct()
print(f"Roles found: {list(roles)}")

print("\n--- Caretakers check ---")
caretakers = User.objects.filter(role='caretaker')
print(f"Total caretakers in User table: {caretakers.count()}")
for c in caretakers:
    print(f"ID: {c.id}, Fullname: {c.fullname}, Status: {c.status}")

print("\n--- Caretaker model check ---")
ct_records = Caretaker.objects.all()
print(f"Total records in Caretaker table: {ct_records.count()}")
for ct in ct_records:
    print(f"User ID: {ct.user.id}, Experience: {ct.experience}, Approved: {ct.approved}")
