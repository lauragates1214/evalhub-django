from django.contrib import messages
from django.contrib.auth.views import LoginView as DjangoLoginView


class LoginView(DjangoLoginView):
    def form_valid(self, form):
        messages.success(self.request, "You have been logged in successfully")
        return super().form_valid(form)
