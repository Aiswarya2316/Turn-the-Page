from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Buyer, Seller
from .forms import UserRegistrationForm, BuyerRegistrationForm, SellerRegistrationForm
from django.contrib import messages


# Create your views here.
def home(request):
   return render(request,'home.html')


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
    
    return render(request, 'admin/register_seller.html', {'user_form': user_form, 'seller_form': seller_form})


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


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Buyer, Seller
from django.contrib import messages

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")

            # Check if the user is a Seller
            if Seller.objects.filter(user=user).exists():
                return redirect('admin_dashboard')  # Redirect sellers to a custom dashboard
            
            # Otherwise, redirect to buyer home
            return redirect('buyerhome')
        else:
            messages.error(request, "Invalid username or password!")
    
    return render(request, "login.html")



# User Logout
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('login')











# ------------------------------------buyer session--------------------------------------------------#
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q  # ✅ Import Q for OR filtering
from .models import ExchangeRequest

@login_required
def buyerhome(request):
    pending_requests = ExchangeRequest.objects.filter(receiver=request.user, status="pending")

    # Get all completed exchanges involving the logged-in user
    completed_exchanges = ExchangeRequest.objects.filter(
        Q(requester=request.user) | Q(receiver=request.user),
        status="completed"
    )

    # Extract unique exchanged users and books
    exchanged_users = set()
    exchanged_books = []

    for exchange in completed_exchanges:
        if exchange.requester == request.user:
            exchanged_users.add(exchange.receiver)
        else:
            exchanged_users.add(exchange.requester)

        exchanged_books.append({
            'book': exchange.book,
            'with_user': exchange.receiver if exchange.requester == request.user else exchange.requester,
            'date': exchange.created_at
        })

    return render(request, 'buyer/buyerhome.html', {
        'pending_requests': pending_requests,
        'user_name': request.user.username,
        'exchanged_users': exchanged_users,  # Pass exchanged users list
        'exchanged_books': exchanged_books  # Pass exchanged books list
    })





from django.shortcuts import render
from .models import Book

def book_list(request):
    books = Book.objects.all()
    return render(request, 'buyer/book_list.html', {'books': books})




from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Book, ExchangeRequest

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    owner = book.owner  # Get the owner of the book

    if request.method == 'POST':
        if book.owner == request.user:
            messages.error(request, "You cannot exchange your own book.")
        else:
            # Ensure the request goes to the book owner
            existing_request = ExchangeRequest.objects.filter(book=book, requester=request.user, receiver=owner, status="pending").exists()

            if existing_request:
                messages.warning(request, "You have already requested to exchange this book.")
            else:
                ExchangeRequest.objects.create(book=book, requester=request.user, receiver=owner, status="pending")
                messages.success(request, "Exchange request sent to the book owner!")

        return redirect('book_detail', book_id=book_id)

    return render(request, 'buyer/book_details.html', {'book': book, 'owner': owner})



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Book
from .forms import BookForm  # ✅ Import the form

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)  # ✅ Include request.FILES
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user
            book.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'buyer/addbook.html', {'form': form})



from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import ExchangeRequest

@login_required
def manage_exchange_request(request, request_id):
    exchange_request = get_object_or_404(ExchangeRequest, id=request_id)

    if request.user != exchange_request.receiver:  # Ensure only the book owner can approve/reject
        messages.error(request, "You are not authorized to process this request.")
        return redirect('buyerhome')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            exchange_request.status = 'approved'
            exchange_request.book.owner = exchange_request.requester  # Transfer ownership
            exchange_request.book.available = False  # Mark as unavailable after exchange
            exchange_request.book.save()
            exchange_request.status = 'completed'
            messages.success(request, "✅ Exchange approved! Book ownership transferred.")

        elif action == 'reject':
            exchange_request.status = 'rejected'
            messages.error(request, "❌ Exchange request rejected.")

        exchange_request.save()
        return redirect('buyerhome')  # Redirect to home after approval/rejection

    return render(request, 'buyer/manage_exchange.html', {'exchange_request': exchange_request})






# -----------------------------------Admin session-------------------------------------------------#
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Book, ExchangeRequest

@login_required
def admin_dashboard(request):
    # Ensure the user is a seller before granting access
    if not Seller.objects.filter(user=request.user).exists():
        return redirect('buyerhome')  # Redirect unauthorized users

    books = Book.objects.all()  
    exchange_requests = ExchangeRequest.objects.all()  

    return render(request, 'admin/admin_dashboard.html', {
        'books': books,
        'exchange_requests': exchange_requests
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Book

# Simulating a payment gateway (Replace this with Razorpay/Stripe)
def buy_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":
        # Simulate payment success (Replace with actual gateway logic)
        book.available = False  # Mark book as sold
        book.save()
        messages.success(request, f'Payment successful! You have bought "{book.title}".')
        return redirect('payment_success')

    return render(request, 'payment.html', {'book': book})

def payment_success(request):
    return render(request, 'payment_success.html')
