
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from food import views


urlpatterns = [
    # Admin page
    path('admin/', admin.site.urls),

    # Foodie Home Page
    path('', views.home, name='home'),

    # Checkout Page
    path('checkout/', views.checkout, name='checkout'),

    # Order Confirmation Page
    path(
        'order-confirmation/<int:order_id>/',
        views.order_confirmation,
        name='order_confirmation'
    ),

 # My Orders Page
path('my-orders/', views.my_orders, name='my_orders'),

# Cancel Order
path(
    'cancel-order/<int:order_id>/',
    views.cancel_order,
    name='cancel_order'
),

    # User authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Passkey authentication
    path(
        'webauthn/',
        include(
            'django_otp_webauthn.urls',
            namespace='otp_webauthn'
        )
    ),
]