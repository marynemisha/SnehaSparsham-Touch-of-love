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

print("--- Initializing missing Caretaker records ---")
all_caretaker_users = User.objects.filter(role="caretaker")
created_count = 0
for user_ct in all_caretaker_users:
    if not Caretaker.objects.filter(user=user_ct).exists():
        Caretaker.objects.create(user=user_ct, experience=0, approved=True)
        created_count += 1
        print(f"Created record for: {user_ct.fullname}")

print(f"\nDone. Created {created_count} records.")
