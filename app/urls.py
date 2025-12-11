# from django.urls import path

# from . import views

# urlpatterns = [
#     path('', views.home, name='home')
# ]   

from django.contrib.auth import views as auth_views

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user_view, name='register'),
    path('registration/', views.get_registration, name='registration'),
    path("update-user/<int:user_id>", views.update_user_view, name="update_user"),
    path('delete-user/<int:user_id>', views.delete_user_view, name='delete_user'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout_view, name='logout'),
    path('', views.home_page_view, name='home'),
    path('add-announcement/', views.add_announcement, name='add_announcement'),
    path('delete-announcement/<int:announcement_id>/', views.delete_announcement, name='delete_announcement'),
    path('gallery/', views.render_gallery, name='gallery'),
    path('upload/', views.upload_image_view, name='upload_view'),
    path('qr-code/<int:user_id>/', views.generate_qr_code, name='generate-qr-code'),
    path('validate-qr/', views.validate_qr_code, name='validate_qr_code'),
    path('get-scanner/', views.render_qr_scanner, name='get-scanner'),
    path('under-development/', views.render_maintanance_page, name='under-development'),

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend_otp/', views.resend_otp, name='resend_otp'),
    path('contact/', views.contact_view, name='contact'),

    path('admin_panel', views.admin_panel, name='admin_panel'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('reset_password', views.reset_password, name='reset_password'),
    path('api/get-user-details/<int:userId>/', views.get_user_details, name='get_user_details'),
    # path('api/user/<int:user_id>/image/<str:image_field>/', views.serve_user_image, name='serve_user_image'),
    path('api/user/<int:user_id>/file/<str:file_field>/', views.serve_user_file, name='serve_user_image'),
    path('media/image/<str:image_name>/', views.serve_image, name='serve_image'),
    path('delete/image/<str:image_name>/', views.delete_image_view, name='delete_image'),
    path("api/update-user-status/<int:user_id>/", views.update_user_status, name="update_user_status"),
    path("about-us/", views.render_about_us, name="about_us"),
    path("contact-us", views.render_contact_us, name="contact_us"),
    
    # Category change request URLs
    path("api/request-category-change/", views.request_category_change, name="request_category_change"),
    path("api/get-category-change-requests/", views.get_category_change_requests, name="get_category_change_requests"),
    path("api/approve-reject-category-change/<int:request_id>/", views.approve_reject_category_change, name="approve_reject_category_change"),
    
    # Category management URLs
    path("api/get-category-members/", views.get_category_members, name="get_category_members"),
    path("api/export-category-members/", views.export_category_members, name="export_category_members"),
    path("api/send-bulk-email/", views.send_bulk_email, name="send_bulk_email"),
    
    # Registration reports URL
    path("api/download-registrations/", views.download_registrations, name="download_registrations"),
]
