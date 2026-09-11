from django.urls import path , include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    CustomerViewSet, CategoryViewSet, DishViewSet,
    CartView, OrderViewSet, KitchenQueueView, DailyReportView,
    create_order,
    index_view, menu_view, cart_view, checkout_view, order_success_view, about_view,
)

urlpatterns = [
    path('', index_view, name='home'),
    path('menyu/', menu_view, name='menu'),
    path('savat/', cart_view, name='cart'),
    path('buyurtma/', checkout_view, name='checkout'),
    path('tasdiq/', order_success_view, name='order_success'),
    path('biz-haqimizda/', about_view, name='about'),

    path('telegram-order/', create_order, name='telegram-order'),

    path('categories/', CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='category-list'),
    path('categories/<int:pk>/', CategoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='category-detail'),

    path('dishes/', DishViewSet.as_view({'get': 'list', 'post': 'create'}), name='dish-list'),
    path('dishes/<int:pk>/', DishViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='dish-detail'),

    path('orders/', OrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='order-list'),
    path('orders/<int:pk>/', OrderViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='order-detail'),
    path('orders/<int:pk>/change_status/', OrderViewSet.as_view({'patch': 'change_status'}), name='order-change-status'),

    path('customers/get_or_create_telegram/', CustomerViewSet.as_view({'post': 'get_or_create_telegram'}), name='customer-telegram'),
    path('customers/', CustomerViewSet.as_view({'get': 'list', 'post': 'create'}), name='customer-list'),
    path('customers/<int:pk>/', CustomerViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='customer-detail'),

    path('cart/', CartView.as_view(), name='cart-api'),
    path('kitchen/queue/', KitchenQueueView.as_view(), name='kitchen_queue'),
    path('reports/daily/', DailyReportView.as_view(), name='daily_report'),

    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("silk/", include("silk.urls", namespace="silk")),
]



