from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password

# Create your views here.

def home(request):
    return render(request, 'index.html')


def register(request):
    if request.method == "POST":
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        age = request.POST.get('age')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        blood_group = request.POST.get('blood_group')
        role = request.POST.get('role')
        # Independent senior registration is now allowed
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        profile = request.FILES.get('profile')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')

        user = User.objects.create_user(
            email=email,
            password=password,
            fullname=fullname,
            age=age if age else None,
            weight=weight if weight else None,
            height=height if height else None,
            blood_group=blood_group,
            role=role,
            address=address,
            phone=phone,
            profile=profile
        )

        # If role is caretaker, initialize the Caretaker model record
        if role == 'caretaker':
            experience = request.POST.get('experience')
            availability_list = request.POST.getlist('availability')
            availability = ", ".join(availability_list)
            services_list = request.POST.getlist('services')
            services = ", ".join(services_list)
            
            Caretaker.objects.create(
                user=user,
                experience=experience if experience else 0,
                availability=availability,
                services=services,
                approved=True # Auto-approve for now based on project flow or False if admin must approve
            )

        messages.success(request, "Registration Successful")
        return redirect('login')

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Role Based Redirect
            if user.role == "admin":
                return redirect("admin_dashboard")
            elif user.role == "caretaker":
                return redirect("caretaker_dashboard")
            elif user.role == "family":
                return redirect("family_dashboard")
            elif user.role == "senior":
                return redirect("senior_dashboard")
            
            return redirect("home")

        else:
            messages.error(request, "Invalid Email or Password")

    return render(request, "login.html")


def signout(request):
    logout(request)
    # messages.success(request,'User successfully logged out')
    return redirect('home')


from django.shortcuts import  get_object_or_404

from django.contrib.auth.decorators import login_required


# ===============================
# ADMIN DASHBOARD
# ===============================
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')

    low_stocks = [s for s in MedicineStock.objects.all() if s.is_low()]

    context = {
        'caretakers': Caretaker.objects.all(),
        'families': User.objects.filter(role='family'),
        'alerts': EmergencyAlert.objects.all(),
        'reports': Report.objects.all(),
        'low_stocks': low_stocks
    }
    return render(request, 'admin_dashboard.html', context)


# ===============================
# APPROVE FAMILY
# ===============================
@login_required
def approve_family(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.status = "approved"
    user.save()
    return redirect('admin_dashboard')


# ===============================
# ADD REPORT
# ===============================
@login_required
def add_report(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        senior_id = request.POST.get('senior')
        
        senior = None
        if senior_id:
            senior = get_object_or_404(User, id=senior_id, role='senior')
            
        Report.objects.create(title=title, description=description, senior=senior)
        return redirect('admin_dashboard')

    seniors = User.objects.filter(role='senior')
    return render(request, 'add_report.html', {'seniors': seniors})


# ===============================
# VIEW REPORTS (FILTERED BY ROLE)
# ===============================
@login_required
def view_reports(request):
    user = request.user
    if user.role == 'admin':
        reports = Report.objects.all().order_by('-created_at')
    elif user.role == 'senior':
        reports = Report.objects.filter(senior=user).order_by('-created_at')
    elif user.role == 'caretaker':
        assigned_senior_ids = CareRelation.objects.filter(caretaker=user, approved=True).values_list('senior_id', flat=True)
        reports = Report.objects.filter(senior_id__in=assigned_senior_ids).order_by('-created_at')
    elif user.role == 'family':
        assigned_senior_ids = CareRelation.objects.filter(family=user, approved=True).values_list('senior_id', flat=True)
        reports = Report.objects.filter(senior_id__in=assigned_senior_ids).order_by('-created_at')
    else:
        reports = Report.objects.none()
        
    return render(request, 'view_reports.html', {'reports': reports})

@login_required
def edit_report(request, id):
    report = get_object_or_404(Report, id=id)

    if request.user.role != "admin":
        return redirect("view_reports")

    if request.method == "POST":
        report.title = request.POST.get("title")
        report.description = request.POST.get("description")
        report.save()
        return redirect("view_reports")

    return render(request, "edit_report.html", {"report": report})


# Delete Health Record
@login_required
def delete_report(request, id):
    report = get_object_or_404(Report, id=id)

    if request.user.role == "admin":
        report.delete()

    return redirect("view_reports")


from django.contrib.auth.decorators import login_required
from django.contrib import messages

# ===============================
# ADD MEDICINE (ADMIN)
# ===============================
@login_required
def add_medicine(request):
    if not request.user.is_superuser:
        return redirect('home')

    seniors = User.objects.filter(role='senior')

    if request.method == "POST":
        senior_id = request.POST.get('senior')
        medicine_name = request.POST.get('medicine_name')
        dosage = request.POST.get('dosage')
        time = request.POST.get('time')
        notes = request.POST.get('notes')

        senior = User.objects.get(id=senior_id)

        MedicineSchedule.objects.create(
            senior=senior,
            medicine_name=medicine_name,
            dosage=dosage,
            time=time,
            notes=notes
        )

        messages.success(request, "Medicine schedule added successfully!")
        return redirect('add_medicine')

    return render(request, 'add_medicine.html', {'seniors': seniors})


# ===============================
# VIEW MEDICINE (ALL ROLES)
# ===============================
@login_required
def view_medicine(request):
    user = request.user
    if user.role == 'admin':
        medicines = MedicineSchedule.objects.all()
    elif user.role == 'senior':
        medicines = MedicineSchedule.objects.filter(senior=user)
    elif user.role == 'caretaker':
        assigned_senior_ids = CareRelation.objects.filter(caretaker=user, approved=True).values_list('senior_id', flat=True)
        medicines = MedicineSchedule.objects.filter(senior_id__in=assigned_senior_ids)
    elif user.role == 'family':
        assigned_senior_ids = CareRelation.objects.filter(family=user, approved=True).values_list('senior_id', flat=True)
        medicines = MedicineSchedule.objects.filter(senior_id__in=assigned_senior_ids)
    else:
        medicines = MedicineSchedule.objects.none()

    return render(request, 'view_medicine.html', {'medicines': medicines})


def get_assigned_senior(user):
    if user.role == "senior":
        return user

    relation = CareRelation.objects.filter(caretaker=user).first()
    if relation:
        return relation.senior

    return None

@login_required
def add_senior(request):
    if request.user.role not in ['admin', 'caretaker']:
        return redirect('dashboard')
    
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        age = request.POST.get('age')
        weight = request.POST.get('weight')
        height = request.POST.get('height')
        blood_group = request.POST.get('blood_group')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        profile = request.FILES.get('profile')
        password = request.POST.get('password')
        
        if not password:
             # Fallback to random if not provided, though template should require it
             password = User.objects.make_random_password()
        
        try:
            senior = User.objects.create_user(
                email=email,
                password=password,
                fullname=fullname,
                age=age if age else None,
                weight=weight if weight else None,
                height=height if height else None,
                blood_group=blood_group,
                address=address,
                phone=phone,
                profile=profile,
                role='senior'
            )
            
            # If a caretaker adds them, automatically create a CareRelation
            if request.user.role == 'caretaker':
                CareRelation.objects.create(senior=senior, caretaker=request.user, approved=True)
            
            return redirect('senior_details')
        except Exception as e:
            return render(request, 'add_senior.html', {'error': str(e)})

    return render(request, 'add_senior.html')


@login_required
def senior_details(request):
    if request.user.role != "caretaker":
        return redirect("home")

    # Get all seniors assigned to this caretaker
    relations = CareRelation.objects.filter(caretaker=request.user, approved=True).select_related('senior')

    from datetime import date, datetime
    today = date.today()
    now_time = datetime.now().time()
    
    seniors_data = []
    for rel in relations:
        senior = rel.senior
        
        # Medicine Reminders Logic
        schedules = MedicineSchedule.objects.filter(senior=senior)
        taken_today = MedicineStatus.objects.filter(
            senior=senior, 
            created_at__date=today, 
            status="Taken"
        ).values_list('medicine_name', flat=True)
        
        medicine_reminders = []
        for sch in schedules:
            is_taken = sch.medicine_name in taken_today
            
            # Automated Reporting for Overdue
            is_overdue = not is_taken and sch.time < now_time
            
            if is_overdue:
                # Check if we already reported this today
                if not Report.objects.filter(senior=senior, title__icontains=f"Missed: {sch.medicine_name}", created_at__date=today).exists():
                    Report.objects.create(
                        senior=senior,
                        title=f"Missed: {sch.medicine_name}",
                        description=f"Overdue medication alert: {sch.medicine_name} was scheduled for {sch.time} ({sch.timing}) but has not been recorded as taken."
                    )
                
            medicine_reminders.append({
                "id": sch.id,
                "name": sch.medicine_name,
                "dosage": sch.dosage,
                "timing": sch.timing,
                "time": sch.time,
                "is_taken": is_taken,
                "is_overdue": is_overdue
            })

        seniors_data.append({
            "senior": senior,
            "vitals": HealthVital.objects.filter(senior=senior).order_by("-created_at"),
            "moods": MoodUpdate.objects.filter(senior=senior).order_by("-created_at"),
            "medicine_history": MedicineStatus.objects.filter(senior=senior).order_by("-created_at")[:10],
            "medicine_reminders": medicine_reminders,
            "diet_plans": DietPlan.objects.filter(senior=senior).order_by("-created_at"),
            "visits": VisitLog.objects.filter(senior=senior).order_by("-created_at"),
            "emergencies": EmergencyAlert.objects.filter(senior=senior)
        })

    context = {
        "seniors_data": seniors_data,
        "today_date": today
    }

    return render(request, "senior_details.html", context)



from django.http import HttpResponse


@login_required
def add_vital(request):

    if request.user.role != "caretaker":
        return redirect("home")

    relation = CareRelation.objects.filter(caretaker=request.user).first()

    if not relation:
        messages.error(request, "No senior assigned.")
        return redirect("home")

    senior = relation.senior

    if request.method == "POST":

        blood_pressure = request.POST.get("blood_pressure")
        heart_rate = request.POST.get("heart_rate")
        temperature = request.POST.get("temperature")

        HealthVital.objects.create(
            senior=senior,
            caretaker=request.user,
            blood_pressure=blood_pressure,
            heart_rate=heart_rate,
            temperature=temperature
        )

        messages.success(request, "Vital added successfully.")
        return redirect("senior_details")   # or home

    return render(request, "add_vital.html")




@login_required
def add_mood(request):

    if request.method == "POST":
        mood = request.POST.get("mood")

        if request.user.role == "senior":
            MoodUpdate.objects.create(
                senior=request.user,
                mood=mood
            )

        elif request.user.role == "caretaker":
            relation = CareRelation.objects.filter(
                caretaker=request.user
            ).first()

            if relation:
                MoodUpdate.objects.create(
                    senior=relation.senior,
                    caretaker=request.user,
                    mood=mood
                )

        return redirect("home")

    return render(request, "add_mood.html")



@login_required
def add_medicine_status(request):

    if request.user.role != "caretaker":
        return redirect("home")

    relation = CareRelation.objects.filter(
        caretaker=request.user
    ).first()

    if not relation:
        return redirect("home")

    if request.method == "POST":
        medicine_name = request.POST.get("medicine_name")
        status = request.POST.get("status")

        # Record Status
        MedicineStatus.objects.create(
            senior=relation.senior,
            caretaker=request.user,
            medicine_name=medicine_name,
            status=status
        )

        # Stock Management
        if status == "Taken":
            stock = MedicineStock.objects.filter(medicine_name__iexact=medicine_name).first()
            if stock:
                stock.quantity -= 1
                stock.save()
                
                # Check for low stock alert
                if stock.is_low():
                    # Create a notification for the caretaker
                    Report.objects.create(
                        senior=relation.senior,
                        title=f"Refill Needed: {medicine_name}",
                        description=f"Stock for {medicine_name} is low ({stock.quantity} left). Please refill as soon as possible."
                    )
            
            # Send Notification to Family Member if exists
            if relation.family:
                Notification.objects.create(
                    family=relation.family,
                    message=f"Medication '{medicine_name}' was successfully given to {relation.senior.fullname}."
                )

        return redirect("senior_details")

    context = {
        'initial_medicine': request.GET.get('medicine', '')
    }

    return render(request, "add_medicine_status.html", context)




@login_required
def add_visit(request):

    if request.user.role != "caretaker":
        return redirect("home")

    relation = CareRelation.objects.filter(
        caretaker=request.user
    ).first()

    if not relation:
        return redirect("home")

    if request.method == "POST":

        visitor_name = request.POST.get("visitor_name")
        visit_note = request.POST.get("visit_note")

        VisitLog.objects.create(
            senior=relation.senior,
            caretaker=request.user,
            visitor_name=visitor_name,   # ✅ NOW VALID
            visit_note=visit_note
        )

        return redirect("senior_details")

    return render(request, "add_visit.html")




@login_required
def trigger_emergency(request):
    user = request.user
    senior_id = request.GET.get('senior') or request.POST.get('senior_id')
    senior = None

    if user.role == "senior":
        senior = user
    elif user.role == "caretaker":
        if senior_id:
            senior = get_object_or_404(User, id=senior_id, role="senior")
            # Verify caretaker is assigned to this senior
            if not CareRelation.objects.filter(caretaker=user, senior=senior, approved=True).exists():
                return HttpResponseForbidden("Not authorized for this senior.")
        else:
            # Default to first assigned senior
            relation = CareRelation.objects.filter(caretaker=user, approved=True).first()
            if relation:
                senior = relation.senior
    
    if not senior:
        return redirect("dashboard")

    if request.method == "POST":
        message = request.POST.get("message")

        EmergencyAlert.objects.create(
            senior=senior,
            message=message,
            triggered_by=user,
        )

        # Send notification to approved families
        families = CareRelation.objects.filter(senior=senior, approved=True)

        for relation in families:
            if relation.family:
                Notification.objects.create(
                    family=relation.family,
                    message=f"🚨 Emergency Alert from {senior.fullname} (Triggered by {user.fullname}): {message}"
                )

        if user.role == "caretaker":
             messages.success(request, f"Emergency alert triggered for {senior.fullname}")
             return redirect("senior_details")
        return redirect("senior_dashboard")

    return render(request, "trigger_emergency.html", {"senior": senior})





@login_required
def dashboard(request):

    if request.user.role == "admin":
        return redirect("admin_dashboard")

    elif request.user.role in ["senior", "caretaker", "family"]:
        return redirect("senior_details")

    else:
        return redirect("home")



from .utils import get_assigned_senior

@login_required
def family_dashboard(request):

    if request.user.role != "family":
        return redirect("dashboard")

    if request.user.email == 'neethu@gmail.com':
        all_seniors = User.objects.filter(role="senior", fullname__icontains='Lekshmi Amma')
    else:
        all_seniors = User.objects.filter(role="senior")

    approved_relations = CareRelation.objects.filter(
        family=request.user,
        approved=True
    )
    approved_senior_ids = approved_relations.values_list("senior_id", flat=True)

    # Get relations with related senior and caretaker info
    relations = approved_relations.select_related('senior', 'caretaker')
    
    # Store relations in a dictionary for easy access by senior id
    # This relation primarily tracks the family's approved access status
    senior_relations = {rel.senior_id: rel for rel in relations}

    # Find any approved caretaker assignments for these seniors across all relations
    caretaker_relations = CareRelation.objects.filter(
        senior_id__in=approved_senior_ids,
        approved=True,
        caretaker__isnull=False
    ).select_related('caretaker')
    
    # Store caretakers in a dictionary for easy template lookup: senior_id -> caretaker
    senior_caretakers = {rel.senior_id: rel.caretaker for rel in caretaker_relations}

    context = {
        "all_seniors": all_seniors,
        "approved_senior_ids": approved_senior_ids,
        "senior_relations": senior_relations,
        "senior_caretakers": senior_caretakers
    }

    return render(request, "family_dashboard.html", context)



@login_required
def senior_dashboard(request):

    if request.user.role != "senior":
        return redirect("dashboard")

    senior = request.user
    
    # Get assigned caretaker for this senior
    assigned_caretaker = None
    # Look for any approved relation that has a caretaker assigned to this senior
    caretaker_rel = CareRelation.objects.filter(senior=senior, approved=True, caretaker__isnull=False).first()
    if caretaker_rel:
        assigned_caretaker = caretaker_rel.caretaker

    context = {
        "senior": senior,
        "medicines": MedicineSchedule.objects.filter(senior=senior),
        "moods": MoodUpdate.objects.filter(senior=senior).order_by("-created_at"),
        "emergencies": EmergencyAlert.objects.filter(senior=senior).order_by("-created_at"),
        "assigned_caretaker": assigned_caretaker
    }

    return render(request, "senior_dashboard.html", context)



from .models import CareRelation



def caretaker_dashboard(request):
    seniors = CareRelation.objects.filter(
        caretaker=request.user
    ).select_related("senior")

    return render(request, "caretaker_dashboard.html", {
        "seniors": seniors
    })



from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

def family_senior_detail(request, senior_id):

    senior = get_object_or_404(User, id=senior_id, role="senior")

    relation = CareRelation.objects.filter(
        family=request.user,
        senior=senior,
        approved=True
    ).first()

    if not relation:
        return HttpResponseForbidden("You are not approved to view this senior.")
        
    # Get assigned caretaker for this senior from any approved relation
    caretaker_rel = CareRelation.objects.filter(senior=senior, approved=True, caretaker__isnull=False).first()
    assigned_caretaker = caretaker_rel.caretaker if caretaker_rel else None

    # Fetch Tracking and Reports
    medicine_history = MedicineStatus.objects.filter(senior=senior).order_by("-created_at")[:15]
    reports = Report.objects.filter(senior=senior).order_by("-created_at")[:20]

    return render(request, "family_senior_detail.html", {
        "senior": senior,
        "medicines": MedicineSchedule.objects.filter(senior=senior),
        "vitals": HealthVital.objects.filter(senior=senior).order_by("-created_at")[:5],
        "moods": MoodUpdate.objects.filter(senior=senior).order_by("-created_at")[:5],
        "assigned_caretaker": assigned_caretaker,
        "medicine_history": medicine_history,
        "reports": reports
    })


@login_required
def request_senior_access(request, senior_id):

    if request.user.role != "family":
        return redirect("dashboard")

    senior = User.objects.get(id=senior_id, role="senior")

    relation, created = CareRelation.objects.get_or_create(
        senior=senior,
        family=request.user
    )

    if created:
        messages.success(request, "Request sent to admin for approval.")
    else:
        messages.warning(request, "You have already requested this senior.")

    return redirect("family_dashboard")


@login_required
def admin_requests(request):

    if request.user.role != "admin":
        return redirect("dashboard")

    pending_requests = CareRelation.objects.filter(approved=False)

    return render(request, "admin_requests.html", {
        "requests": pending_requests
    })


@login_required
def approve_request(request, request_id):

    if request.user.role != "admin":
        return redirect("dashboard")

    relation = CareRelation.objects.get(id=request_id)
    relation.approved = True
    relation.save()

    return redirect("admin_requests")


from datetime import datetime

@login_required
def add_daily_routine(request):

    if request.user.role != "admin":
        return redirect("dashboard")

    seniors = User.objects.filter(role="senior")

    if request.method == "POST":
        senior_id = request.POST.get("senior")
        title = request.POST.get("title")
        description = request.POST.get("description")
        reminder_time = request.POST.get("reminder_time")

        senior = User.objects.get(id=senior_id)

        DailyRoutine.objects.create(
            senior=senior,
            title=title,
            description=description,
            reminder_time=reminder_time
        )

        messages.success(request, "Routine added successfully.")
        return redirect("add_daily_routine")

    return render(request, "add_daily_routine.html", {"seniors": seniors})




@login_required
def daily_reminders(request):
    user = request.user
    senior_id = request.GET.get('senior')
    senior = None

    if user.role == "senior":
        senior = user
    elif user.role == "caretaker":
        if senior_id:
            senior = get_object_or_404(User, id=senior_id, role="senior")
        else:
            relation = CareRelation.objects.filter(caretaker=user, approved=True).first()
            if relation:
                senior = relation.senior
    
    if not senior:
         return redirect("dashboard")

    now = datetime.now().time()

    reminders = DailyRoutine.objects.filter(
        senior=senior,
        reminder_time__lte=now
    ).order_by("reminder_time")

    return render(request, "daily_reminders.html", {
        "reminders": reminders,
        "senior": senior
    })



@login_required
def family_notifications(request):

    if request.user.role != "family":
        return redirect("dashboard")

    notifications = Notification.objects.filter(
        family=request.user
    ).order_by("-created_at")

    return render(request, "family_notifications.html", {
        "notifications": notifications
    })



@login_required
def mark_notification_read(request, notif_id):

    notification = Notification.objects.get(id=notif_id)

    if notification.family == request.user:
        notification.is_read = True
        notification.save()

    return redirect("family_notifications")



def profile(request):
    users = request.user
    return render(request, 'profile.html', {'data': users})

def update_profile(request):
    user = request.user
    if request.method == "POST":
        profile = request.FILES.get('profile')
        if profile:
            user.profile = profile
            user.save()
            messages.success(request, "Profile picture updated successfully!")
            return redirect('home')
    return render(request, "update_profile.html", {"user": user})






def admin_panel(request):
    # Only allow admin users
    if not request.user.is_authenticated or request.user.role != 'admin':
        return redirect('admin:login')  # redirect to Django admin login

    seniors = User.objects.filter(role='senior')
    family_members = User.objects.filter(role='family')
    reports = Report.objects.all().order_by('-created_at')

    # Get caretakers and calculate their average rating and feedback
    caretakers = User.objects.filter(role='caretaker')
    caretaker_data = []

    for c in caretakers:
        feedbacks = CaretakerFeedback.objects.filter(caretaker=c).order_by('-created_at')
        if feedbacks.exists():
            avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
        else:
            avg_rating = 0
            
        caretaker_data.append({
            'user': c,
            'avg_rating': round(avg_rating, 1),
            'feedbacks': feedbacks[:3]  # Show recent 3 feedbacks
        })

    medicines = MedicineSchedule.objects.all().order_by('-id')[:5]

    context = {
        'seniors': seniors,
        'caretaker_data': caretaker_data,
        'family_members': family_members,
        'reports': reports,
        'medicines': medicines,
    }
    return render(request, 'admin_panel.html', context)


@login_required
def admin_view_all_feedback(request, caretaker_id):
    if request.user.role != 'admin':
        return redirect('dashboard')
    
    caretaker = get_object_or_404(User, id=caretaker_id, role='caretaker')
    feedbacks = CaretakerFeedback.objects.filter(caretaker=caretaker).order_by('-created_at')
    
    if feedbacks.exists():
        avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
    else:
        avg_rating = 0
        
    return render(request, 'admin_all_feedback.html', {
        'caretaker': caretaker,
        'feedbacks': feedbacks,
        'avg_rating': round(avg_rating, 1)
    })



@login_required
def medicine_tracking(request):
    user = request.user
    role = user.role
    
    records = None
    relation = None
    
    if role == "caretaker":
        relation = CareRelation.objects.filter(caretaker=user, approved=True).first()
        if not relation:
            messages.error(request, "No senior assigned.")
            return redirect("home")
            
        if request.method == "POST":
            medicine = request.POST.get("medicine_name")
            status = request.POST.get("status")
    
            MedicineStatus.objects.create(
                senior=relation.senior,
                caretaker=user,
                medicine_name=medicine,
                status=status
            )

            # Stock Management
            if status == "Taken":
                stock = MedicineStock.objects.filter(medicine_name__iexact=medicine).first()
                if stock:
                    stock.quantity -= 1
                    stock.save()
                    
                    # Check for low stock alert
                    if stock.is_low():
                        # Create a report for the admin/caretaker to see
                        Report.objects.create(
                            senior=relation.senior,
                            title=f"Refill Needed: {medicine}",
                            description=f"Stock for {medicine} is low ({stock.quantity} left). Please refill as soon as possible."
                        )
            messages.success(request, "Medicine tracking updated.")
            return redirect("medicine_tracking")
            
        records = MedicineStatus.objects.filter(senior=relation.senior).order_by("-created_at")

    elif role == "senior":
        records = MedicineStatus.objects.filter(senior=user).order_by("-created_at")
        
    elif role == "family":
        relations = CareRelation.objects.filter(family=user, approved=True)
        if relations.exists():
            senior_ids = relations.values_list('senior_id', flat=True)
            records = MedicineStatus.objects.filter(senior_id__in=senior_ids).order_by("-created_at")
        else:
            records = MedicineStatus.objects.none()
            
    elif role == "admin":
        records = MedicineStatus.objects.all().order_by("-created_at")
        
    else:
        return redirect("home")

    return render(request, "medicine_tracking.html", {
        "records": records,
        "role": role
    })


@login_required
def diet_monitor(request):
    user = request.user
    role = user.role
    
    meals = None
    relation = None
    
    if role.lower() == "caretaker":
        senior_id = request.GET.get('senior')
        all_relations = CareRelation.objects.filter(caretaker=user, approved=True).select_related('senior')
        
        if senior_id:
            relation = all_relations.filter(senior_id=senior_id).first()
        else:
            relation = all_relations.first()

        if relation:
            if request.method == "POST":
                meal = request.POST.get("meal_name")
                status = request.POST.get("status")
                special = request.POST.get("special_diet")
        
                DietPlan.objects.create(
                    senior=relation.senior,
                    caretaker=user,
                    meal_name=meal,
                    meal_status=status,
                    special_diet=special
                )
                messages.success(request, f"Diet log added for {relation.senior.fullname} successfully.")
                return redirect(f"/diet-monitor/?senior={relation.senior.id}")
                
            meals = DietPlan.objects.filter(senior=relation.senior).order_by("-created_at")
        else:
            meals = None

    elif role.lower() == "senior":
        meals = DietPlan.objects.filter(senior=user).order_by("-created_at")
        
    elif role.lower() == "family":
        relations = CareRelation.objects.filter(family=user, approved=True)
        if relations.exists():
            senior_ids = relations.values_list('senior_id', flat=True)
            meals = DietPlan.objects.filter(senior_id__in=senior_ids).order_by("-created_at")
        else:
            meals = DietPlan.objects.none()
            
    elif role.lower() == "admin":
        meals = DietPlan.objects.all().order_by("-created_at")
        all_relations = None # Not used/needed in same way for admin
    else:
        return redirect("home")

    return render(request, "diet_monitor.html", {
        "meals": meals,
        "role": role,
        "relation": relation,
        "all_relations": all_relations if role.lower() == "caretaker" else None
    })

    return render(request, "diet_monitor.html", {
        "meals": meals,
        "role": role,
        "relation": relation
    })


@login_required
def medicine_stock(request):
    # Determine role
    user = request.user
    role = user.role

    # Admins can see and add stocks
    if role == "admin":
        if request.method == "POST":
            name = request.POST.get("medicine_name")
            qty = request.POST.get("quantity")
            low_stock = request.POST.get("low_stock_limit", 5)
            
            # Update existing or create new
            stock, created = MedicineStock.objects.get_or_create(
                medicine_name=name,
                defaults={'quantity': qty, 'low_stock_limit': low_stock}
            )
            if not created:
                stock.quantity = int(stock.quantity) + int(qty)
                stock.save()
                
            messages.success(request, "Medicine stock updated successfully.")
            return redirect("medicine_stock")

    # Admins, families, and caretakers can view stocks.
    # We will assume global stock for the facility in this design, so everyone can see it.
    elif role not in ["caretaker", "family", "senior"]:
        return redirect("home")

    stocks = MedicineStock.objects.all().order_by("medicine_name")

    return render(request, "medicine_stock.html", {
        "stocks": stocks,
        "role": role
    })


@login_required
def care_history(request):
    user = request.user
    role = user.role
    
    senior = None
    
    if role == "senior":
        senior = user
    elif role == "caretaker":
        relation = CareRelation.objects.filter(caretaker=user, approved=True).first()
        if relation:
            senior = relation.senior
    elif role == "family":
        relation = CareRelation.objects.filter(family=user, approved=True).first()
        if relation:
            senior = relation.senior
    elif role == "admin":
        # For admin, we could show all history, or require a senior ID. Let's redirect to dashboard for now if accessed directly without senior context.
        return redirect("admin_dashboard")
        
    if not senior:
        messages.error(request, "No senior assigned to view history.")
        return redirect("home")

    # Aggregate records
    history_events = []
    
    # Care History
    for ch in CareHistory.objects.filter(senior=senior):
        history_events.append({
            'type': 'Care Event',
            'title': ch.event,
            'description': ch.description,
            'date': ch.created_at,
            'icon': '📝'
        })

    # Reports/Alerts
    for report in Report.objects.filter(senior=senior):
        history_events.append({
            'type': 'Report',
            'title': report.title,
            'description': report.description,
            'date': report.created_at,
            'icon': '📋'
        })
        
    # Vitals
    for hv in HealthVital.objects.filter(senior=senior):
        history_events.append({
            'type': 'Vitals',
            'title': 'Vitals Recorded',
            'description': f"BP: {hv.blood_pressure}, HR: {hv.heart_rate}, Temp: {hv.temperature}",
            'date': hv.created_at,
            'icon': '❤️'
        })
        
    # Moods
    for mood in MoodUpdate.objects.filter(senior=senior):
        history_events.append({
            'type': 'Mood',
            'title': f"Mood: {mood.mood}",
            'description': mood.note,
            'date': mood.created_at,
            'icon': '😊'
        })
        
    # Diet
    for diet in DietPlan.objects.filter(senior=senior):
        history_events.append({
            'type': 'Diet',
            'title': f"Meal: {diet.meal_name} - {diet.meal_status}",
            'description': diet.special_diet if diet.special_diet else "No special notes.",
            'date': diet.created_at,
            'icon': '🍲'
        })
        
    # Medicine Status
    for med in MedicineStatus.objects.filter(senior=senior):
        history_events.append({
            'type': 'Medicine',
            'title': f"Medicine: {med.medicine_name}",
            'description': f"Status: {med.status}",
            'date': med.created_at,
            'icon': '💊'
        })
        
    # Visit Logs
    for visit in VisitLog.objects.filter(senior=senior):
        history_events.append({
            'type': 'Visit',
            'title': f"Visitor: {visit.visitor_name}",
            'description': visit.visit_note,
            'date': visit.created_at,
            'icon': '🚪'
        })

    # Sort descending by date
    history_events.sort(key=lambda x: x['date'], reverse=True)

    return render(request, "care_history.html", {
        "history": history_events,
        "senior": senior
    })


@login_required
def caretaker_feedback(request, caretaker_id):
    user = request.user
    if user.role not in ["family", "senior"]:
        return redirect("home")

    caretaker = get_object_or_404(User, id=caretaker_id, role="caretaker")

    if request.method == "POST":
        rating = request.POST.get("rating")
        feedback = request.POST.get("feedback")

        CaretakerFeedback.objects.create(
            caretaker=caretaker,
            given_by=user,
            rating=rating,
            feedback=feedback
        )

        messages.success(request, "Thank you for your feedback!")
        if user.role == "family":
            return redirect("family_dashboard")
        else:
            return redirect("senior_dashboard")

    return render(request, "caretaker_feedback.html", {
        "caretaker": caretaker
    })


@login_required
def assigned_caretaker_details(request, caretaker_id):
    caretaker_user = get_object_or_404(User, id=caretaker_id, role="caretaker")
    # Using filter().first() instead of get_object_or_404 because not all caretakers 
    # might have the extended Caretaker details record initialized.
    caretaker_details = Caretaker.objects.filter(user=caretaker_user).first()

    # Check permission
    has_permission = False
    
    if request.user.role == "senior":
        has_permission = CareRelation.objects.filter(senior=request.user, caretaker=caretaker_user, approved=True).exists()
    elif request.user.role == "family":
        shared_seniors = CareRelation.objects.filter(family=request.user, approved=True).values_list('senior_id', flat=True)
        has_permission = CareRelation.objects.filter(senior_id__in=shared_seniors, caretaker=caretaker_user, approved=True).exists()
    elif request.user.role == "admin":
        has_permission = True
        
    if not has_permission:
        messages.error(request, "You do not have permission to view this caretaker's details.")
        return redirect("dashboard")

    return render(request, "caretaker_details.html", {
        "caretaker_user": caretaker_user,
        "caretaker_details": caretaker_details
    })

@login_required
def admin_assign_caretaker(request):
    if request.user.role != "admin":
        return redirect("dashboard")

    if request.method == "POST":
        senior_id = request.POST.get("senior_id")
        caretaker_id = request.POST.get("caretaker_id")
        
        if senior_id and caretaker_id:
            senior = get_object_or_404(User, id=senior_id, role="senior")
            caretaker = get_object_or_404(User, id=caretaker_id, role="caretaker")
            
            # Check if an assignment already exists
            relation, created = CareRelation.objects.get_or_create(
                senior=senior,
                caretaker=caretaker,
                defaults={'approved': True}
            )
            
            if not created:
                # If editing existing, ensure it's approved
                relation.approved = True
                relation.save()
                messages.warning(request, f"Caretaker {caretaker.fullname} was already assigned to {senior.fullname}.")
            else:
                messages.success(request, f"Successfully assigned {caretaker.fullname} to {senior.fullname}.")
            
            return redirect("assign_caretaker")
        else:
            messages.error(request, "Please select both a Senior and a Caretaker.")

    # Get all seniors
    seniors = User.objects.filter(role="senior")
    
    # Get caretakers and ensure they have a Caretaker model record
    all_caretaker_users = User.objects.filter(role="caretaker")
    for user_ct in all_caretaker_users:
        if not Caretaker.objects.filter(user=user_ct).exists():
            Caretaker.objects.create(user=user_ct, experience=0, approved=True)
            
    caretakers = User.objects.filter(role="caretaker", status="active")
    
    # Get active assignments
    assignments = CareRelation.objects.filter(approved=True).select_related('senior', 'caretaker')
    
    return render(request, "admin_assign_caretaker.html", {
        "seniors": seniors,
        "caretakers": caretakers,
        "assignments": assignments
    })


# ===============================
# LEAVE SYSTEM
# ===============================

@login_required
def request_leave(request):
    role = request.user.role
    if role != 'caretaker':
        return redirect('home')
    
    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        # Find which senior they are currently assigned to in CareRelation
        relation = CareRelation.objects.filter(caretaker=request.user, approved=True).first()
        senior = relation.senior if relation else None

        LeaveRequest.objects.create(
            caretaker=request.user,
            senior=senior,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        messages.success(request, "Leave request submitted successfully. Waiting for admin approval.")
        return redirect('request_leave')

    # Fetch history for the logged-in caretaker
    leave_history = LeaveRequest.objects.filter(caretaker=request.user).order_by('-created_at')

    return render(request, "request_leave.html", {
        'role': role,
        'leave_history': leave_history
    })

@login_required
def manage_leave_requests(request):
    role = request.user.role
    if role != 'admin':
        return redirect('home')

    leaves = LeaveRequest.objects.all().order_by('-created_at')
    available_caretakers = User.objects.filter(role='caretaker', status='active')

    if request.method == "POST":
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action') # 'Approved' or 'Rejected'
        admin_note = request.POST.get('admin_note')
        sub_id = request.POST.get('substitute_id')

        leave = get_object_or_404(LeaveRequest, id=leave_id)
        leave.status = action
        leave.admin_note = admin_note
        
        if sub_id:
            sub = get_object_or_404(User, id=sub_id, role='caretaker')
            leave.substitute_caretaker = sub
        
        leave.save()
        messages.success(request, f"Leave request for {leave.caretaker.fullname} {action}.")
        return redirect('manage_leave')

    return render(request, "manage_leave.html", {
        "leaves": leaves,
        "available_caretakers": available_caretakers,
        'role': role
    })


# ===============================
# PAYMENT SYSTEM
# ===============================

@login_required
def payment_dashboard(request):
    role = request.user.role
    if role != 'family':
        return redirect('home')
    
    # Get relations to see who to pay for
    relations = CareRelation.objects.filter(family=request.user, approved=True)
    payments = Payment.objects.filter(family=request.user).order_by('-date_created')

    return render(request, "family_payments.html", {
        "relations": relations,
        "payments": payments,
        'role': role
    })

@login_required
def process_payment(request):
    if request.user.role != 'family':
        return redirect('home')

    if request.method == "POST":
        relation_id = request.POST.get('relation_id')
        amount = request.POST.get('amount')
        payment_type = request.POST.get('payment_type')
        payment_method = request.POST.get('payment_method') or 'Cash'
        
        relation = get_object_or_404(CareRelation, id=relation_id, family=request.user)
        
        Payment.objects.create(
            family=request.user,
            senior=relation.senior,
            caretaker=relation.caretaker, # This is already nullable in models
            amount=amount,
            payment_type=payment_type,
            payment_method=payment_method,
            status='Approved' if payment_method != 'Cash' else 'Pending'
        )
        return redirect('payment_success')

@login_required
def payment_success(request):
    return render(request, "payment_success.html", {'role': request.user.role})

@login_required
def admin_salary_approval(request):
    role = request.user.role
    if role != 'admin':
        return redirect('home')

    payments = Payment.objects.all().order_by('-date_created')

    if request.method == "POST":
        payment_id = request.POST.get('payment_id')
        status = request.POST.get('status')
        
        payment = get_object_or_404(Payment, id=payment_id)
        payment.status = status
        if status == 'Paid':
            import datetime
            payment.date_paid = datetime.datetime.now()
        payment.save()
        
        messages.success(request, f"Payment status updated to {status}.")
        return redirect('admin_payments')

    return render(request, "admin_payments.html", {"payments": payments, 'role': role})



