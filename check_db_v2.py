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

print("--- User Count by Role ---")
from django.db.models import Count
role_counts = User.objects.values('role').annotate(total=Count('id'))
for rc in role_counts:
    print(f"Role: {rc['role']}, Total: {rc['total']}")

print("\n--- Caretakers Detail ---")
caretakers = User.objects.filter(role='caretaker')
for c in caretakers:
    print(f"ID: {c.id}, Fullname: {c.fullname}, Status: {c.status}, is_active: {c.is_active}, is_staff: {c.is_staff}")

print("\n--- Caretaker Model Records ---")
ct_records = Caretaker.objects.all()
for ct in ct_records:
    print(f"User: {ct.user.fullname}, Approved: {ct.approved}, CareType: {ct.care_type}")
