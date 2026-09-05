from django.contrib import admin
from .models import Customer, Category, Dish, Cart, CartItem, Order, OrderItem, OrderStatusLog


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('taom_nomi', 'narx', 'miqdor', 'summa')


class OrderStatusLogInline(admin.TabularInline):
    model = OrderStatusLog
    extra = 0
    readonly_fields = ('eski_holat', 'yangi_holat', 'kim', 'vaqt')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('ism', 'telegram_id', 'telefon', 'bloklangan', 'yaratilgan')
    list_filter = ('bloklangan',)
    search_fields = ('ism', 'telegram_id', 'telefon')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('nom', 'slug', 'tartib', 'faolmi')
    list_editable = ('tartib', 'faolmi')
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom', 'kategoriya', 'narx', 'faolmi']
    list_filter = ['kategoriya', 'faolmi']
    search_fields = ['nom', 'tavsif']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'mijoz', 'faolmi', 'yangilangan')
    list_filter = ('faolmi',)
    inlines = [CartItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('raqam', 'mijoz', 'holat', 'yetkazish_turi', 'jami_summa', 'yaratilgan')
    list_filter = ('holat', 'yetkazish_turi', 'yaratilgan')
    search_fields = ('raqam', 'telefon', 'mijoz__ism')
    inlines = [OrderItemInline, OrderStatusLogInline]


@admin.register(OrderStatusLog)
class OrderStatusLogAdmin(admin.ModelAdmin):
    list_display = ('buyurtma', 'eski_holat', 'yangi_holat', 'kim', 'vaqt')
    readonly_fields = ('buyurtma', 'eski_holat', 'yangi_holat', 'kim', 'vaqt')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False