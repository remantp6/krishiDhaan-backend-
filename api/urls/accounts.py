from rest_framework.routers import DefaultRouter

from api.views.accounts import (
    UserProfileViewSet, UserHistoryViewSet, ContactUsViewSet
)

router_accounts = DefaultRouter()

router_accounts.register("profile", UserProfileViewSet)
router_accounts.register("history", UserHistoryViewSet)
router_accounts.register("contact", ContactUsViewSet)
