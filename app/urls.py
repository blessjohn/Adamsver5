# from django.urls import path

# from . import views

# urlpatterns = [
#     path('', views.home, name='home')
# ]   

from django.contrib.auth import views as auth_views

from django.urls import path
from . import views
from app.views import health

urlpatterns = [
    path(""health/",health),
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
    path('notice_board', views.notice_board_view, name='notice_board'),
    path('rulebook-viewer/', views.rulebook_viewer, name='rulebook_viewer'),
    path('reset_password', views.reset_password, name='reset_password'),
    
    # Policy pages
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    
    path('api/get-user-details/<int:userId>/', views.get_user_details, name='get_user_details'),
    # path('api/user/<int:user_id>/image/<str:image_field>/', views.serve_user_image, name='serve_user_image'),
    path('api/user/<int:user_id>/file/<str:file_field>/', views.serve_user_file, name='serve_user_image'),
    path('media/image/<str:image_name>/', views.serve_image, name='serve_image'),
    path('delete/image/<str:image_name>/', views.delete_image_view, name='delete_image'),
#    path('gallery/edit/<int:image_id>/', views.edit_image_view, name='edit_image'),
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
    
    # Approve/Reject member URLs
    path("api/approve-member/<int:user_id>/", views.approve_member, name="approve_member"),
    path("api/reject-member/<int:user_id>/", views.reject_member, name="reject_member"),
    path("api/change-member-status/<int:user_id>/", views.change_member_status, name="change_member_status"),
    
    # Notice Board URLs
    path("api/get-notices/", views.get_notices, name="get_notices"),
    path("api/add-notice/", views.add_notice, name="add_notice"),
    path("api/update-notice/<int:notice_id>/", views.update_notice, name="update_notice"),
    path("api/delete-notice/<int:notice_id>/", views.delete_notice, name="delete_notice"),
    
    # Contact Messages URLs
    path("api/get-messages/", views.get_messages, name="get_messages"),
    path("api/get-message/<int:message_id>/", views.get_message, name="get_message"),
    path("api/mark-message-read/<int:message_id>/", views.mark_message_read, name="mark_message_read"),
    path("api/reply-message/<int:message_id>/", views.reply_message, name="reply_message"),
    path("api/delete-message/<int:message_id>/", views.delete_message, name="delete_message"),
    
    # Rulebook URLs
    path("api/get-rulebooks/", views.get_rulebooks, name="get_rulebooks"),
    path("api/get-active-rulebook/", views.get_active_rulebook, name="get_active_rulebook"),
    path("api/serve-rulebook-pdf/", views.serve_rulebook_pdf, name="serve_rulebook_pdf"),
    path("api/upload-rulebook/", views.upload_rulebook, name="upload_rulebook"),
    path("api/toggle-rulebook/<int:rulebook_id>/", views.toggle_rulebook, name="toggle_rulebook"),
    path("api/delete-rulebook/<int:rulebook_id>/", views.delete_rulebook, name="delete_rulebook"),
]
