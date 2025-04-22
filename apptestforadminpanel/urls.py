

from django.contrib import admin
from django.urls import path
from views import change_parent_type

urlpatterns = [
	path('admin/change_parent_type', change_parent_type),
    path('admin/', admin.site.urls),
]
