from django.contrib import admin
from .models import User, Complaints, Announcement, OTP

admin.site.register(User)
# admin.site.register(Complaints)
admin.site.register(Announcement)
# admin.site.register(OTP)


# from django.contrib import admin

admin.site.site_header = "ADAMS Admin Panel"  # Appears at the top of the admin panel
admin.site.site_title = "Admin Panel"  # Appears in the browser tab title
# admin.site.index_title = "Welcome to Your Admin Panel"  # Appears on the admin index page
