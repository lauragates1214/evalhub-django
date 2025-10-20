"""
AI Assistance Note:
This module was developed using AI tools (Claude, VS Code AI) for:
- Initial test case generation following TDD patterns
- Debugging and interpreting test failures
- Explaining Django/htmx concepts and patterns
All architecture and design decisions and final implementations are my own work.
"""

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
