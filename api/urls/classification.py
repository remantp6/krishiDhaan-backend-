from rest_framework.routers import DefaultRouter

from api.views.classification import ClassificationViewSet

router_classification = DefaultRouter()

router_classification.register("classify", ClassificationViewSet, basename="classification")