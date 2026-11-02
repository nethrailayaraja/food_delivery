
from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    # Show these details in the Admin Order list
    list_display = (
        'id',
        'user',
        'customer_name',
        'phone',
        'total_amount',
        'payment_method',
        'status',
        'created_at',
    )

    # Allow quick editing of order status
    list_editable = (
        'status',
    )

    # Search orders by customer details
    search_fields = (
        'customer_name',
        'phone',
        'user__username',
    )

    # Filter options in the sidebar
    list_filter = (
        'payment_method',
        'status',
        'created_at',
    )

    # Show newest orders first
    ordering = (
        '-created_at',
    )