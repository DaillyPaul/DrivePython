from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm 
from .form import CustomUserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import os
from django.conf import settings
from django.core.files.storage import default_storage
from .models import UploadedFile, Folder

# Create your views here.
def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')
    else:
        form = CustomUserCreationForm()
    return render(request, 'inscription.html', {'form': form})

def connexion(request):
    print("Je suis appelé")
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('accueil')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'connexion.html')

@login_required
def acceuil(request):
    # Récupère tous les fichiers uploadés par l'utilisateur connecté
    user_files = UploadedFile.objects.filter(user=request.user)
    user_folders = Folder.objects.filter(user=request.user)
    return render(request, 'accueil.html', {'files': user_files, 'folders': user_folders})

def deconnexion(request):
    logout(request)
    return redirect('connexion')

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']  # Récupère le fichier uploadé
        # Vérifier si la somme des tailles des fichiers de l'utilisateur plus le fichier uploader dépasse la limite de 100 Mo
        user_files = UploadedFile.objects.filter(user=request.user)
        total_size = sum([file.file_size for file in user_files]) + uploaded_file.size
        if total_size > 100 * 1024 * 1024:  # 100 Mo en octets
            messages.error(request, 'La taille totale de vos fichiers dépasse la limite autorisée.')
            return redirect('accueil')

        # Définir le chemin du dossier de destination (par exemple : media/uploads/user_<id>/)
        user_folder = f'user_{request.user.id}'
        destination_folder = os.path.join(settings.MEDIA_ROOT, 'uploads', user_folder)
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # Chemin de sauvegarde complet pour le fichier
        file_path = os.path.join(destination_folder, uploaded_file.name)

        # Enregistre le fichier sur le serveur
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Sauvegarde du fichier dans la base de données avec l'utilisateur
        uploaded_file_instance = UploadedFile(
            user=request.user, 
            file_name=uploaded_file.name, 
            file_path=file_path,
            file_size=uploaded_file.size
        )
        uploaded_file_instance.save()
        user_files = UploadedFile.objects.filter(user=request.user)
        user_folders = Folder.objects.filter(user=request.user)

        # Redirection ou message de succès
        return render(request, 'accueil.html', {'files': user_files, 'folders': user_folders})

    return render(request, 'accueil.html', {'files': user_files, 'folders': user_folders})

def upload_folder(request):
    if request.method == 'POST' and request.FILES.getlist('files'):
        files = request.FILES.getlist('files')  # Récupère tous les fichiers uploadés
        folder_name = request.POST.get('folder_name')  # Récupère le nom du dossier
        # Vérifier si la somme des tailles des fichiers de l'utilisateur plus la taille des fichiers uploader dépasse la limite de 100 Mo
        user_files = UploadedFile.objects.filter(user=request.user)
        total_size = sum([file.file_size for file in user_files]) + sum([file.size for file in files])
        if total_size > 100 * 1024 * 1024:  # 100 Mo en octets
            messages.error(request, 'La taille totale de vos fichiers dépasse la limite autorisée.')
            return redirect('accueil')
        # Définir le dossier utilisateur
        user_folder = f'user_{request.user.id}'
        base_destination_folder = os.path.join(settings.MEDIA_ROOT, 'uploads', user_folder, folder_name)
        folder_destination = os.path.join(settings.MEDIA_ROOT, 'uploads', user_folder)

        # Créer le dossier de destination
        os.makedirs(base_destination_folder, exist_ok=True)
        uploaded_folder_instance = Folder(
                user=request.user,
                folder_name=folder_name,
                folder_path=folder_destination
            )
        uploaded_folder_instance.save()
        # Parcours chaque fichier uploadé
        for uploaded_file in files:
            # Chemin de sauvegarde complet pour chaque fichier
            file_path = os.path.join(base_destination_folder, uploaded_file.name)

            # Enregistre le fichier sur le serveur
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Sauvegarde dans la base de données si nécessaire
            uploaded_file_instance = UploadedFile(
                user=request.user,
                file_name=uploaded_file.name,
                file_path=file_path,
                file_size=uploaded_file.size
            )
            uploaded_file_instance.save()


        user_files = UploadedFile.objects.filter(user=request.user)
        user_folders = Folder.objects.filter(user=request.user)

        # Redirection ou message de succès
        return render(request, 'accueil.html', {'files': user_files, 'folders': user_folders})

    return render(request, 'accueil.html')


def style(request):
    return render(request, 'style.css', content_type='text/css')

def user_files(request):
    # Récupère tous les fichiers uploadés par l'utilisateur connecté
    user_files = UploadedFile.objects.filter(user=request.user)
    
    return render(request, 'user_files.html', {'files': user_files})
