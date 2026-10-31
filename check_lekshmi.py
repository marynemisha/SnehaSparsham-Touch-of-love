import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import User, CareRelation

def check_lekshmi_amma():
    print("Checking Lekshmi Amma...")
    seniors = User.objects.filter(fullname__icontains="lekshmi", role="senior")
    if not seniors.exists():
        print("Lekshmi Amma not found.")
        return

    for senior in seniors:
        print(f"Found Senior: {senior.fullname} (ID: {senior.id})")
        relations = CareRelation.objects.filter(senior=senior)
        if not relations.exists():
            print("  No CareRelations found.")
        else:
            for rel in relations:
                print(f"  Relation ID: {rel.id}")
                print(f"    Family: {rel.family.fullname if rel.family else 'None'}")
                print(f"    Caretaker: {rel.caretaker.fullname if rel.caretaker else 'None'}")
                print(f"    Approved: {rel.approved}")

if __name__ == "__main__":
    check_lekshmi_amma()
