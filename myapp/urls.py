from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.home, name="home"),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name="login"),
    path('logout/', views.signout, name="logout"),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve-family/<int:user_id>/', views.approve_family, name='approve_family'),
    path('add-report/', views.add_report, name='add_report'),
    path('view-reports/', views.view_reports, name='view_reports'),
    path('add-medicine/', views.add_medicine, name='add_medicine'),
    path('view-medicine/', views.view_medicine, name='view_medicine'),
    path("edit-report/<int:id>/", views.edit_report, name="edit_report"),
    path("delete-report/<int:id>/", views.delete_report, name="delete_report"),
    path('add-senior/', views.add_senior, name='add_senior'),
    path('senior-details/', views.senior_details, name='senior_details'),
    path("add-vital/", views.add_vital, name="add_vital"),
    path("add-mood/", views.add_mood, name="add_mood"),
    path("add-medicine-status/", views.add_medicine_status, name="add_medicine_status"),
    path("add-visit/", views.add_visit, name="add_visit"),
    path("trigger-emergency/", views.trigger_emergency, name="trigger_emergency"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("family-dashboard/", views.family_dashboard, name="family_dashboard"),
    path("family/senior/<int:senior_id>/", views.family_senior_detail, name="family_senior_detail"),
    path("request-access/<int:senior_id>/", views.request_senior_access, name="request_senior_access"),
    path("senior-dashboard/", views.senior_dashboard, name="senior_dashboard"),
    path("caretaker-dashboard/", views.caretaker_dashboard, name="caretaker_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("access-requests/", views.admin_requests, name="admin_requests"),
    path("approve-access/<int:request_id>/", views.approve_request, name="approve_request"),
    path("add-daily-routine/", views.add_daily_routine, name="add_daily_routine"),
    path("daily-reminders/", views.daily_reminders, name="daily_reminders"),
    path("family-notifications/", views.family_notifications, name="family_notifications"),
    path("mark-notification/<int:notif_id>/", views.mark_notification_read, name="mark_notification_read"),
    path('profl',views.profile , name='profile'),
    path('updatepic', views.update_profile, name='update_profile'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('medicine-tracking/', views.medicine_tracking, name="medicine_tracking"),
    path('diet-monitor/', views.diet_monitor, name="diet_monitor"),
    path('medicine-stock/', views.medicine_stock, name="medicine_stock"),
    path('care-history/', views.care_history, name="care_history"),
    path('feedback/<int:caretaker_id>/', views.caretaker_feedback, name="caretaker_feedback"),
    path('caretaker-details/<int:caretaker_id>/', views.assigned_caretaker_details, name="caretaker_details"),
    path("assign-caretaker/", views.admin_assign_caretaker, name="assign_caretaker"),
    path('admin-all-feedback/<int:caretaker_id>/', views.admin_view_all_feedback, name='admin_view_all_feedback'),
    
    # Leave System
    path("request-leave/", views.request_leave, name="request_leave"),
    path("manage-leave/", views.manage_leave_requests, name="manage_leave"),
    
    # Payment System
    path("payment-dashboard/", views.payment_dashboard, name="payment_dashboard"),
    path("process-payment/", views.process_payment, name="process_payment"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("admin-payments/", views.admin_salary_approval, name="admin_payments"),
    













    

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)