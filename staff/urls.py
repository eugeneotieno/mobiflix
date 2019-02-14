from django.conf.urls import url,include
from django.contrib import admin
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token,refresh_jwt_token

urlpatterns = [
#list a movie..upload
path('admin/content/upload',views.UploadContent.as_view()),
path('admin/content/delete/<int:id>/', views.UploadContentDetailView.as_view()),
path('admin/content/update/<int:id>/', views.UploadContentDetailView.as_view()),

path('admin/category/list/',views.ContentCategory.as_view()),
path('admin/category/item/',views.ContentCategoryDetailView.as_view()),


#token
path('api/v1/login/', obtain_jwt_token),
path('api/v1/refresh/', refresh_jwt_token),

#refresh



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
