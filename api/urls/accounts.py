from rest_framework.routers import DefaultRouter

from api.views.accounts import (
    SentOtpViewSet , UserLoginSignUpViewSet, UserProfileViewSet, 
    # User3stepFormViewset,
    # UsersListViewSet, UserActiveDeactiveViewSet
)

router_accounts = DefaultRouter()

router_accounts.register("profile", UserProfileViewSet)
# router_accounts.register("send-otp", SentOtpViewSet, basename="send-otp")
router_accounts.register("authenticate", UserLoginSignUpViewSet, basename="authenticate")
# router_accounts.register("3-step-form", User3stepFormViewset, basename="3-step-form")

# router_accounts.register("all-users", UsersListViewSet, basename="all-users")
# router_accounts.register("user-status-change", UserActiveDeactiveViewSet, basename="all-users")
