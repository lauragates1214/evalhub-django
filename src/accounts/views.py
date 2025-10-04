from django.contrib import messages
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
)


class LoginView(DjangoLoginView):
    def form_valid(self, form):
        messages.success(self.request, "You have been logged in successfully")
        return super().form_valid(form)


class LogoutView(DjangoLogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out")
        return super().dispatch(request, *args, **kwargs)
