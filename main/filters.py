import django_filters
from .models import Dish, Order

class DishFilter(django_filters.FilterSet):
    min_narx = django_filters.NumberFilter(field_name="narx", lookup_expr='gte')
    max_narx = django_filters.NumberFilter(field_name="narx", lookup_expr='lte')
    kategoriya = django_filters.NumberFilter(field_name="kategoriya__id")

    class Meta:
        model = Dish
        fields = ['kategoriya', 'faolmi', 'min_narx', 'max_narx']


class OrderFilter(django_filters.FilterSet):
    sanadan = django_filters.DateTimeFilter(field_name="yaratilgan", lookup_expr='gte')
    sanagach = django_filters.DateTimeFilter(field_name="yaratilgan", lookup_expr='lte')

    class Meta:
        model = Order
        fields = ['holat', 'yetkazish_turi', 'mijoz', 'sanadan', 'sanagach']