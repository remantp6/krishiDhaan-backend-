from django.contrib import admin
from django.urls import path, re_path, include

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    re_path(r'^rest-auth/', include('dj_rest_auth.urls')),
]
