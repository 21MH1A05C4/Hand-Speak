from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
from django.contrib.staticfiles import finders
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from .forms import EmailAuthenticationForm  # Import the custom email login form
from .forms import CustomUserCreationForm  

# Ensure necessary nltk resources are available
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")
nltk.download("wordnet")
nltk.download("stopwords")

# Home Page View
def home_view(request):
    return render(request, "home.html")


# About Page View
def about_view(request):
    return render(request, "about.html")


# Contact Page View
def contact_view(request):
    return render(request, "contact.html")


# Animation View (Requires Login)
@login_required(login_url="login")
def animation_view(request):
    if request.method == "POST":
        text = request.POST.get("sen", "").lower()
        words = word_tokenize(text)
        tagged = nltk.pos_tag(words)

        # Identifying Tenses
        tense = {
            "future": sum(1 for _, tag in tagged if tag == "MD"),
            "present": sum(1 for _, tag in tagged if tag in ["VBP", "VBZ", "VBG"]),
            "past": sum(1 for _, tag in tagged if tag in ["VBD", "VBN"]),
            "present_continuous": sum(1 for _, tag in tagged if tag == "VBG"),
        }

        # Stopwords that will be removed (custom set like the previous code)
        stop_words = set(["mightn't", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn', 'do', "you've", 'off', 'for', "didn't", 'm', 'ain', 'haven', "weren't", 'are', "she's", "wasn't", 'its', "haven't", "wouldn't", 'don', 'weren', 's', "you'd", "don't", 'doesn', "hadn't", 'is', 'was', "that'll", "should've", 'a', 'then', 'the', 'mustn', 'i', 'nor', 'as', "it's", "needn't", 'd', 'am', 'have', 'hasn', 'o', "aren't", "you'll", "couldn't", "you're", "mustn't", 'didn', "doesn't", 'll', 'an', 'hadn', 'whom', 'y', "hasn't", 'itself', 'couldn', 'needn', "shan't", 'isn', 'been', 'such', 'shan', "shouldn't", 'aren', 'being', 'were', 'did', 'ma', 't', 'having', 'mightn', 've', "isn't", "won't"])

        # Removing stopwords and applying lemmatization
        lemmatizer = WordNetLemmatizer()
        filtered_text = []
        for word, tag in tagged:
            if word not in stop_words:
                if tag in ["VBG", "VBD", "VBZ", "VBN", "NN"]:
                    filtered_text.append(lemmatizer.lemmatize(word, pos="v"))
                elif tag in ["JJ", "JJR", "JJS", "RBR", "RBS"]:
                    filtered_text.append(lemmatizer.lemmatize(word, pos="a"))
                else:
                    filtered_text.append(lemmatizer.lemmatize(word))

        words = filtered_text  # Ensure we use the filtered list

        # Adjusting Words Based on Tense
        probable_tense = max(tense, key=tense.get)
        if probable_tense == "past" and tense["past"] >= 1:
            words.insert(0, "Before")
        elif probable_tense == "future" and tense["future"] >= 1:
            if "Will" not in words:
                words.insert(0, "Will")
        elif probable_tense == "present_continuous":
            words.insert(0, "Now")

        # Finding animation files
        final_words = []
        for word in words:
            if not finders.find(f"{word}.mp4"):  # If animation not found, use letters
                final_words.extend(list(word))
            else:
                final_words.append(word)

        return render(request, "animation.html", {"words": final_words, "text": text})

    return render(request, "animation.html")


# Signup View
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            return redirect("home")  # Redirect to home page after signup
    else:
        form = CustomUserCreationForm()

    return render(request, "signup.html", {"form": form})


# Login View (Using EmailAuthenticationForm)
def login_view(request):
    if request.method == "POST":
        form = EmailAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user)
            next_url = request.GET.get("next", "home")
            return redirect(next_url)
    else:
        form = EmailAuthenticationForm()

    return render(request, "login.html", {"form": form})


# Logout View
def logout_view(request):
    logout(request)
    return redirect("home")


# Check User Authentication (AJAX)
def check_authentication(request):
    return JsonResponse({"authenticated": request.user.is_authenticated})