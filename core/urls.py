from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.views import CustomRegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    re_path(r'^rest-auth/', include('dj_rest_auth.urls')),
    path('rest-auth/registration/', CustomRegisterView.as_view(), name='rest_register')
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from api.urls.accounts import router_accounts
from api.urls.classification import router_classification

urlpatterns += [
    re_path(r'^accounts/', include(router_accounts.urls)),
    re_path(r'^classification/', include(router_classification.urls)),
]