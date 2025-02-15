from django.urls import path
from .import views
urlpatterns=[
    path('',views.home,name='home'),
    path('buyerhome/',views.buyerhome,name='buyerhome'),
    path('register_seller/',views.register_seller, name='register_seller'),
    path('register_buyer/',views.register_buyer, name='register_buyer'),
    path('login/',views.user_login, name='login'),
    path('logout/',views.user_logout, name='logout'),
    path('book_list/', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('add_book/', views.add_book, name='add_book'),
    path('manage/<int:request_id>/', views.manage_exchange_request, name='manage_exchange'),
]



