# Django http and shortcuts import
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
# From Contrib
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from sign_in.views import SignInUserLogIn
# Django User
from django.contrib.auth.models import User


# App Forms
from accounts.forms import RegisterForm, UserForm, ProfileCreationForm, ProfileSettingsForm


def login_view(request):
    """
    Login view function takes no arguemnt if supplied username and password
    matches then request will authenticate with login and return with User context
    """
    if request.method == 'POST':
        form = UserForm()
        if form.is_valid():
            # Will not throw error because input have value=""
            username = request.POST['username']
            password = request.POST['password']

        # Check the user in database or return
            try:
                user = User.objects.get(username=username)
                user = authenticate(username=username, password=password)
                if user:
                    # Password matching and user found with authenticate
                    login(request, user)
                    return HttpResponseRedirect(reverse('frontend:home'))
            except:
                messages.error(request, "User not found")
                return redirect(SignInUserLogIn, {'form': form})
        else:
            # Password wrong
            messages.error(request, 'Username or Password is wrong')
            return render(request, 'accounts/sign_in.html', {'form': form})
    return render(request, 'accounts/sign_in.html')


def logout_view(request):
    """ Remove user from the request """
    logout(request)
    return HttpResponseRedirect(reverse("frontend:home"))
