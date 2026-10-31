from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('senior', 'Senior Citizen'),
        ('family', 'Family Member'),
        ('caretaker', 'Caretaker'),
    )

    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    )

    # Remove username field
    username = None

    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile = models.ImageField(upload_to="profile/", null=True, blank=True)

    # Health Details
    age = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES,
        null=True,
        blank=True
    )

    # Role & Status
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, default="active")

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname', 'role']

    class Meta:
        db_table = "user"

    def __str__(self):
        return self.fullname




# ===============================
# CARETAKER REQUEST (Admin Approval)
# ===============================
class Caretaker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    
    # New Caretaker Details
    gender = models.CharField(max_length=20, choices=(('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')), null=True, blank=True)
    experience = models.IntegerField(null=True, blank=True, help_text="Years of experience")
    care_type = models.CharField(max_length=50, choices=(('Full-time', 'Full-time'), ('Part-time', 'Part-time')), null=True, blank=True)
    availability = models.CharField(
        max_length=50, 
        choices=(('Full Day', 'Full Day'), ('Day', 'Day'), ('Half Day', 'Half Day')), 
        null=True, 
        blank=True
    )
    services = models.TextField(null=True, blank=True, help_text="Comma-separated list of services")
    assigned_duration = models.CharField(max_length=100, null=True, blank=True, help_text="e.g., 6 Months, 1 Year")
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.user.fullname


# ===============================
# MEDICINE SCHEDULE
# ===============================



# ===============================
# HEALTH RECORD
# ===============================
class HealthRecord(models.Model):
    senior = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'senior'})
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.senior.fullname} - {self.date}"


# ===============================
# EMERGENCY ALERT
# ===============================



# ===============================
# REPORTS (VISIBLE TO ALL ROLES)
# ===============================
class Report(models.Model):
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports",
        limit_choices_to={'role': 'senior'},
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class MedicineSchedule(models.Model):
    TIMING_CHOICES = (
        ('Morning', 'Morning'),
        ('Noon', 'Noon'),
        ('Evening', 'Evening'),
        ('Night', 'Night'),
    )
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'senior'}
    )
    medicine_name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    timing = models.CharField(max_length=20, choices=TIMING_CHOICES, default='Morning')
    time = models.TimeField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.medicine_name} - {self.senior.fullname}"

    


class CareRelation(models.Model):
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="senior_rel",
        limit_choices_to={'role': 'senior'}
    )

    caretaker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="caretaker_rel",
        limit_choices_to={'role': 'caretaker'},
        null=True,
        blank=True
    )

    family = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="family_rel",
        limit_choices_to={'role': 'family'},
        null=True,
        blank=True
    )

    approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.family} → {self.senior}"






    
class HealthVital(models.Model):
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vitals",
        limit_choices_to={'role': 'senior'}
    )
    caretaker = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="health_vitals_added",
    limit_choices_to={'role': 'caretaker'},
    null=True,
    blank=True
)


    blood_pressure = models.CharField(max_length=50)
    heart_rate = models.CharField(max_length=50)
    temperature = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.senior.fullname} - Vital"


class MoodUpdate(models.Model):
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="moods",
        limit_choices_to={'role': 'senior'}
    )
    caretaker = models.ForeignKey(
    User,
    null=True,
    blank=True,
    on_delete=models.CASCADE,
    limit_choices_to={'role': 'caretaker'}
)


    mood = models.CharField(max_length=100)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.senior.fullname} - {self.mood}"


class MedicineStatus(models.Model):
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="medicine_status",
        limit_choices_to={'role': 'senior'}
    )
    caretaker = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name="medicine_updates_added",
    limit_choices_to={'role': 'caretaker'},
    null=True,
    blank=True
)


    medicine_name = models.CharField(max_length=200)
    status = models.CharField(max_length=50)  # Taken / Missed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine_name} - {self.status}"


class VisitLog(models.Model):
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="visits",
        limit_choices_to={'role': 'senior'}
    )

    caretaker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="visit_logs_added",
        limit_choices_to={'role': 'caretaker'},
        null=True,
        blank=True
    )

    visitor_name = models.CharField(max_length=100)   # ✅ ADD THIS

    visit_note = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.visitor_name} - {self.senior.fullname}"




class EmergencyAlert(models.Model):
    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="emergencies",
        limit_choices_to={'role': 'senior'}
    )
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="triggered_emergencies",
        null=True,          # ✅ ADD THIS
        blank=True          # ✅ ADD THIS
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Emergency - {self.senior.fullname}"




from django.conf import settings

class DailyRoutine(models.Model):
    senior = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    reminder_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.senior.fullname} - {self.title}"
    


class Notification(models.Model):
    family = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_notifications"
    )

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.family.fullname}"


# ===============================
# MEDICINE TRACKING
# ===============================
class MedicineTracking(models.Model):

    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="medicine_tracking",
        limit_choices_to={'role': 'senior'}
    )

    caretaker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="medicine_tracking_added",
        limit_choices_to={'role': 'caretaker'},
        null=True,
        blank=True
    )

    medicine_name = models.CharField(max_length=200)

    status = models.CharField(
        max_length=20,
        choices=(
            ("Taken", "Taken"),
            ("Not Taken", "Not Taken")
        )
    )

    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine_name} - {self.status}"



# ===============================
# DIET / FOOD MONITORING
# ===============================

class DietPlan(models.Model):

    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="diet_plans",
        limit_choices_to={'role': 'senior'}
    )

    caretaker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="diet_plans_added",
        limit_choices_to={'role': 'caretaker'},
        null=True,
        blank=True
    )

    meal_name = models.CharField(max_length=200)

    meal_status = models.CharField(
        max_length=20,
        choices=(
            ("Given", "Given"),
            ("Skipped", "Skipped")
        )
    )

    special_diet = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.meal_name} - {self.senior.fullname}"


# ===============================
# MEDICINE STOCK
# ===============================

class MedicineStock(models.Model):

    medicine_name = models.CharField(max_length=200)

    quantity = models.IntegerField()

    low_stock_limit = models.IntegerField(default=5)

    updated_at = models.DateTimeField(auto_now=True)

    def is_low(self):
        return self.quantity <= self.low_stock_limit

    def __str__(self):
        return self.medicine_name


# ===============================
# CARE HISTORY
# ===============================

class CareHistory(models.Model):

    senior = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="care_history",
        limit_choices_to={'role': 'senior'}
    )

    event = models.CharField(max_length=200)

    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.senior.fullname} - {self.event}"



# ===============================
# CARETAKER FEEDBACK
# ===============================

class CaretakerFeedback(models.Model):

    caretaker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedback_received",
        limit_choices_to={'role': 'caretaker'}
    )

    given_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedback_provided"
    )

    rating = models.IntegerField()

    feedback = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.caretaker.fullname} - {self.rating}"


# ===============================
# PAYMENTS
# ===============================
class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('Subscription', 'Monthly Subscription'),
        ('Visit', 'Visit-Based Payment'),
        ('Full-Time', 'Full-Time Stay Charge'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved by Admin'),
        ('Paid', 'Paid'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
    )

    family = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments_made")
    senior = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments_for_senior")
    caretaker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="salary_received", null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='Cash')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_paid = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.payment_type} - {self.family.fullname} - {self.status}"

# ===============================
# LEAVE & SUBSTITUTE REQUEST
# ===============================
class LeaveRequest(models.Model):
    REASON_CHOICES = (
        ('Health', 'Health Issue'),
        ('Emergency', 'Personal Emergency'),
        ('Leave', 'Planned Leave'),
    )
    
    STATUS_CHOICES = (
        ('Pending', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    caretaker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="leave_requests")
    senior = models.ForeignKey(User, on_delete=models.CASCADE, related_name="caretaker_leaves", null=True, blank=True)
    
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    substitute_caretaker = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="substitute_assignments",
        limit_choices_to={'role': 'caretaker'}
    )
    
    admin_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.caretaker.fullname} - {self.reason} ({self.status})"






