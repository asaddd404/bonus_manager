from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='core/login.html', redirect_authenticated_user=True, extra_context={'next': '/dashboard/'}), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
    path('', include('core.urls')),
]