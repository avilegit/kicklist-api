from django.urls import path,include
from rest_framework.routers import DefaultRouter

from shoes import views

router = DefaultRouter()
router.register('tags', views.TagViewSet)
router.register('characteristics', views.CharacteristicViewSet)
router.register('shoes', views.ShoeViewSet)

app_name = 'shoes'

urlpatterns = [
    path('', include(router.urls))
]