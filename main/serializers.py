from decimal import Decimal
from rest_framework import serializers
from .models import Customer, Category, Dish, Cart, CartItem, Order, OrderItem, OrderStatusLog


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'telegram_id', 'ism', 'username', 'telefon', 'bloklangan', 'yaratilgan']
        read_only_fields = ['id', 'yaratilgan']


class CategorySerializer(serializers.ModelSerializer):
    # Frontend uchun 'name' va 'nom' ikkalasini ham uzatamiz
    name = serializers.CharField(source='nom', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'nom', 'name', 'slug', 'tartib', 'faolmi']


class DishSerializer(serializers.ModelSerializer):
    kategoriya_nomi = serializers.ReadOnlyField(source='kategoriya.nom')
    
    # Frontend (data.js) kutayotgan inglizcha nomlarni alias qilib ulab qo'yamiz
    name = serializers.CharField(source='nom', read_only=True)
    price = serializers.DecimalField(source='narx', max_digits=10, decimal_places=2, read_only=True)
    category = serializers.PrimaryKeyRelatedField(source='kategoriya', read_only=True)

    class Meta:
        model = Dish
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    taom_nomi = serializers.ReadOnlyField(source='taom.nom')
    taom_narxi = serializers.ReadOnlyField(source='taom.narx')
    taom_faolmi = serializers.ReadOnlyField(source='taom.faolmi')
    jami_narx = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'taom', 'taom_nomi', 'taom_narxi', 'taom_faolmi', 'miqdor', 'jami_narx']

    def get_jami_narx(self, obj):
        return obj.taom.narx * obj.miqdor


class CartSerializer(serializers.ModelSerializer):
    qatorlar = CartItemSerializer(many=True, read_only=True)
    jami_summa = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'mijoz', 'faolmi', 'qatorlar', 'jami_summa', 'yangilangan']

    def get_jami_summa(self, obj):
        return sum(item.taom.narx * item.miqdor for item in obj.qatorlar.all())


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'taom', 'taom_nomi', 'narx', 'miqdor', 'summa']


class OrderStatusLogSerializer(serializers.ModelSerializer):
    kim_nomi = serializers.ReadOnlyField(source='kim.username')

    class Meta:
        model = OrderStatusLog
        fields = ['id', 'eski_holat', 'yangi_holat', 'kim_nomi', 'vaqt']


class OrderSerializer(serializers.ModelSerializer):
    qatorlar = OrderItemSerializer(many=True, read_only=True)
    tarix = OrderStatusLogSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'raqam', 'mijoz', 'holat', 'yetkazish_turi', 'stol_raqami', 
            'manzil', 'telefon', 'izoh', 'jami_summa', 'yetkazish_narxi', 
            'yaratilgan', 'tayyor_vaqti', 'yopilgan_vaqti', 'bekor_sababi',
            'qatorlar', 'tarix'
        ]
        read_only_fields = ['id', 'raqam', 'jami_summa', 'yaratilgan', 'tayyor_vaqti', 'yopilgan_vaqti']

    def validate(self, attrs):
        yetkazish_turi = attrs.get('yetkazish_turi')
        if yetkazish_turi == 'stol' and not attrs.get('stol_raqami'):
            raise serializers.ValidationError({'stol_raqami': "Stolda yetkazish uchun stol raqami ko'rsatilishi shart."})
        if yetkazish_turi == 'manzil' and not attrs.get('manzil'):
            raise serializers.ValidationError({'manzil': "Yetkazib berish uchun manzil kiritilishi shart."})
        return attrs