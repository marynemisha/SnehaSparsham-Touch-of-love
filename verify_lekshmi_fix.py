import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from myapp.models import User, CareRelation

def verify_lekshmi_fix():
    print("Verifying Lekshmi Amma fix...")
    
    lekshmi = User.objects.get(fullname__icontains="lekshmi", role="senior")
    reena = User.objects.get(fullname__icontains="reena", role="family")
    
    # 1. Verify view logic (Simulate family_dashboard logic)
    approved_relations = CareRelation.objects.filter(family=reena, approved=True)
    approved_senior_ids = approved_relations.values_list("senior_id", flat=True)
    
    caretaker_relations = CareRelation.objects.filter(
        senior_id__in=approved_senior_ids,
        approved=True,
        caretaker__isnull=False
    ).select_related('caretaker')
    
    senior_caretakers = {rel.senior_id: rel.caretaker for rel in caretaker_relations}
    
    if lekshmi.id in senior_caretakers:
        print(f"SUCCESS: Found caretaker {senior_caretakers[lekshmi.id].fullname} for Lekshmi Amma in Reena's dashboard data.")
    else:
        print("FAILURE: Caretaker NOT found for Lekshmi Amma in Reena's dashboard data.")

    # 2. Verify senior_detail logic
    relation_with_caretaker = CareRelation.objects.filter(senior=lekshmi, approved=True, caretaker__isnull=False).first()
    if relation_with_caretaker and relation_with_caretaker.caretaker:
        print(f"SUCCESS: Found caretaker {relation_with_caretaker.caretaker.fullname} for Lekshmi Amma's detail view.")
    else:
        print("FAILURE: Caretaker NOT found for Lekshmi Amma's detail view.")

if __name__ == "__main__":
    verify_lekshmi_fix()
