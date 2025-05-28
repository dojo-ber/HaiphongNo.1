# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
# Create your views here.

# Register-Seite
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # wird beim erflogreicher Registrierung in login.html angezeigt
            messages.success(request, 'Konto wurde erfolgreich erstellt! Du kannst dich jetzt einloggen.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# extra view für das Logout, ACHTUNG! Keine richtige Seite sondern dient nur für die zusätzliche Nachricht!
def custom_logout(request):
    logout(request)
    messages.success(request, "Erfolgreich abgemeldet!") # wird angezeigt, siehe startingscreen.html
    return redirect('start')

# dahboard view,kann man nur zugreifen, wenn man angelmeldet ist
@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html', {'user': request.user})
