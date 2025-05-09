from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PortfolioViewSet,
    AboutSectionViewSet,
    EducationViewSet,
    SkillViewSet,
    ProjectViewSet,
    CertificateViewSet,
    PortfolioCommentViewSet
)

router = DefaultRouter()
router.register(r'portfolios', PortfolioViewSet, basename='portfolio')
router.register(r'about', AboutSectionViewSet, basename='about')
router.register(r'education', EducationViewSet, basename='education')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'certificates', CertificateViewSet, basename='certificate')
router.register(r'comments', PortfolioCommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
] 