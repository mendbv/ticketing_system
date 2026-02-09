from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, ProfileConfirmationForm
from .models import User

class StaffUserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'accounts/staff_user_detail.html'
    context_object_name = 'client_user'

    def test_func(self):
        return self.request.user.is_staff

@login_required
def profile_confirmation(request):
    """
    Страница, куда попадает юзер после входа.
    Позволяет проверить данные и сохранить их.
    """
    if request.method == 'POST':
        form = ProfileConfirmationForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('client_dashboard')
    else:
        form = ProfileConfirmationForm(instance=request.user)
    
    return render(request, 'accounts/profile_confirmation.html', {'form': form})