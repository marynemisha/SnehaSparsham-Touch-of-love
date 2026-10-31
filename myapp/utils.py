from .models import CareRelation

def get_assigned_senior(user):
    relation = CareRelation.objects.filter(family=user).first()
    return relation.senior if relation else None
