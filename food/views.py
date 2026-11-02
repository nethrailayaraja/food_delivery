
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Order


# Food Prices
FOOD_PRICES = {
    # Fast Food & Favorites
    "Cheese Pizza": Decimal("199.00"),
    "Chicken Burger": Decimal("149.00"),
    "French Fries": Decimal("79.00"),
    "Chicken Nuggets": Decimal("159.00"),

    # Indian Main Course
    "Chicken Biryani": Decimal("249.00"),
    "Veg Biryani": Decimal("179.00"),
    "Chicken Fried Rice": Decimal("179.00"),
    "Veg Fried Rice": Decimal("139.00"),

    # Healthy & Fresh Foods
    "Veg Salad": Decimal("99.00"),
    "Chicken Salad": Decimal("149.00"),
    "Avocado Salad": Decimal("179.00"),
    "Vegetable Soup": Decimal("89.00"),
    "Fruit Bowl": Decimal("129.00"),
    "Whole Wheat Sandwich": Decimal("119.00"),

    # Chaat & Street Food
    "Pani Puri": Decimal("60.00"),
    "Samosa Chaat": Decimal("80.00"),
    "Bhel Puri": Decimal("70.00"),
    "Pav Bhaji": Decimal("120.00"),
    "Dahi Puri": Decimal("80.00"),

    # Pasta & Noodles
    "Veg Noodles": Decimal("129.00"),
    "Chicken Noodles": Decimal("169.00"),
    "White Sauce Pasta": Decimal("159.00"),
    "Red Sauce Pasta": Decimal("149.00"),

    # Desserts & Drinks
    "Chocolate Cake": Decimal("99.00"),
    "Brownie": Decimal("109.00"),
    "Ice Cream": Decimal("79.00"),
    "Fresh Lime Soda": Decimal("69.00"),
    "Cold Coffee": Decimal("99.00"),

    # Healthy Drinks
    "Fresh Orange Juice": Decimal("99.00"),
    "Mixed Fruit Smoothie": Decimal("129.00"),
}


# Customer Login
def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(request, "login.html", {
            "error": "Invalid username or password. Please try again."
        })

    return render(request, "login.html")


# Customer Registration
def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if not username or not email or not password1 or not password2:
            return render(request, "register.html", {
                "error": "Please fill in all fields."
            })

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Username already exists. Choose another."
            })

        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {
                "error": "Email already registered. Please log in."
            })

        if password1 != password2:
            return render(request, "register.html", {
                "error": "Passwords do not match."
            })

        if len(password1) < 8:
            return render(request, "register.html", {
                "error": "Password must contain at least 8 characters."
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        return redirect("login")

    return render(request, "register.html")


# Home Page
@login_required(login_url="login")
def home(request):
    return render(request, "home.html")


# Checkout Page
@login_required(login_url="login")
def checkout(request):
    if request.method == "POST":

        customer_name = request.POST.get(
            "customer_name", ""
        ).strip()

        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        payment_method = request.POST.get("payment", "COD")
        submitted_items = request.POST.get("items", "").strip()

        # Check if all details are entered
        if (
            not customer_name
            or not phone
            or not address
            or not submitted_items
        ):
            return render(request, "checkout.html", {
                "error": "Please provide your delivery details and cart items."
            })

        # Calculate total amount using trusted food prices
        total_amount = Decimal("0.00")
        valid_lines = []

        for line in submitted_items.splitlines():
            if not line.strip():
                continue

            try:
                name, price_text = line.rsplit(" - ₹", 1)
                name = name.strip()

                if name not in FOOD_PRICES:
                    raise ValueError("Unknown food item")

                # Use the correct price from the server
                trusted_price = FOOD_PRICES[name]
                total_amount += trusted_price

                valid_lines.append(
                    f"{name} - ₹{trusted_price:.2f}"
                )

            except (ValueError, ArithmeticError):
                return render(request, "checkout.html", {
                    "error": (
                        "Invalid cart item. Please return to the "
                        "menu and try again."
                    )
                })

        # Check if cart is empty
        if not valid_lines:
            return render(request, "checkout.html", {
                "error": "Your cart is empty. Please add food first."
            })

        # Check phone number
        if len(phone) != 10 or not phone.isdigit():
            return render(request, "checkout.html", {
                "error": "Please enter a valid 10-digit phone number."
            })

        # Check payment method
        if payment_method not in ["COD", "UPI", "CARD"]:
            payment_method = "COD"

        # Save the order in database
        order = Order.objects.create(
            user=request.user,
            customer_name=customer_name,
            phone=phone,
            address=address,
            items="\n".join(valid_lines),
            total_amount=total_amount,
            payment_method=payment_method,
        )

        # Go to Order Confirmation Page
        return redirect(
            "order_confirmation",
            order_id=order.id
        )

    return render(request, "checkout.html")


# Order Confirmation Page
@login_required(login_url="login")
def order_confirmation(request, order_id):

    # Only allow the customer who owns the order to view it
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, "order_confirmation.html", {
        "order": order
    })


# Edit Profile
@login_required(login_url="login")
def edit_profile(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()

        if not username or not email:
            return render(request, "edit_profile.html", {
                "error": "Please fill in all fields.",
                "username": username,
                "email": email,
            })

        # Check if another user already has this username
        if User.objects.filter(username=username).exclude(
            id=request.user.id
        ).exists():
            return render(request, "edit_profile.html", {
                "error": "This username is already taken.",
                "username": username,
                "email": email,
            })

        # Check if another user already has this email
        if User.objects.filter(email=email).exclude(
            id=request.user.id
        ).exists():
            return render(request, "edit_profile.html", {
                "error": "This email is already registered.",
                "username": username,
                "email": email,
            })

        # Save updated profile
        request.user.username = username
        request.user.email = email
        request.user.save()

        return redirect("home")

    return render(request, "edit_profile.html", {
        "username": request.user.username,
        "email": request.user.email,
    })


# My Orders Page
@login_required(login_url="login")
def my_orders(request):

    # Show only orders belonging to the logged-in user
    orders = Order.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "my_orders.html", {
        "orders": orders
    })


# Cancel Order
@login_required(login_url="login")
def cancel_order(request, order_id):

    # Only allow the customer who owns the order to cancel it
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # Only Pending and Preparing orders can be cancelled
    if request.method == "POST":
        if order.status in ["Pending", "Preparing"]:
            order.status = "Cancelled"
            order.save()

    return redirect("my_orders")