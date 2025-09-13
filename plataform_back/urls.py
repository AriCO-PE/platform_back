from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/students/", include("students.urls")), 
    path("api/ranking/", include("ranking.urls")), 
    path("api/courses/", include("courses.urls")),
    path("api/grades/", include("grades.urls")),  
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
