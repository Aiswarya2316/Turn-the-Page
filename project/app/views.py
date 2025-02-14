from django.shortcuts import render

# Create your views here.
def home(request):
   return render(request,'home.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Buyer, Seller
from .forms import UserRegistrationForm, BuyerRegistrationForm, SellerRegistrationForm
from django.contrib import messages

# Register as Seller
def register_seller(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        seller_form = SellerRegistrationForm(request.POST)
        if user_form.is_valid() and seller_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            seller = seller_form.save(commit=False)
            seller.user = user
            seller.save()
            messages.success(request, "Seller registered successfully! You can log in now.")
            return redirect('login')
    else:
        user_form = UserRegistrationForm()
        seller_form = SellerRegistrationForm()
    
    return render(request, 'seller/register_seller.html', {'user_form': user_form, 'seller_form': seller_form})

# Register as Buyer
def register_buyer(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        buyer_form = BuyerRegistrationForm(request.POST)
        if user_form.is_valid() and buyer_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            buyer = buyer_form.save(commit=False)
            buyer.user = user
            buyer.save()
            messages.success(request, "Buyer registered successfully! You can log in now.")
            return redirect('login')
    else:
        user_form = UserRegistrationForm()
        buyer_form = BuyerRegistrationForm()
    
    return render(request, 'buyer/register_buyer.html', {'user_form': user_form, 'buyer_form': buyer_form})

# User Login
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('buyerhome')  # Change this to your homepage or dashboard
        else:
            messages.error(request, "Invalid username or password!")
    
    return render(request, "login.html")

# User Logout
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')











from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Book, ExchangeRequest
from .forms import BookForm, ExchangeRequestForm

def book_list(request):
    books = Book.objects.filter(available=True)
    return render(request, 'buyer/book_list.html', {'books': books})

@login_required
def book_detail(request, book_id):
    book = Book.objects.get(id=book_id)
    if request.method == 'POST':
        # Handle exchange request
        ExchangeRequest.objects.create(book=book, requester=request.user)
        return redirect('book_list')
    return render(request, 'buyer/book_details.html', {'book': book})

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user
            book.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'buyer/addbook.html', {'form': form})



def buyerhome(request):
    return render(request,'buyer/buyerhome.html')

