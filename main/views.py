import uuid
from decimal import Decimal
from django.db import transaction

from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Customer, Category, Dish, Cart, CartItem, Order, OrderItem, OrderStatusLog
from .serializers import (
    CustomerSerializer, CategorySerializer, DishSerializer, 
    CartSerializer, OrderSerializer
)
from .permissions import IsAdminUserOrReadOnly, IsAdminRole, IsOshpazOrAdmin
from .filters import DishFilter, OrderFilter

from django.http import JsonResponse
from rest_framework.decorators import api_view
from .services import send_telegram_order


@api_view(['POST'])
def create_order(request):
    data = request.data
    telephone = str(data.get('phone') or '').strip()
    ism = str(data.get('customer_name') or '').strip()
    if not telephone or not ism:
        return JsonResponse({'error': 'Ism va telefon raqam kiritilishi shart'}, status=400)

    customer, _ = Customer.objects.get_or_create(
        telefon=telephone, defaults={'ism': ism}
    )
    if customer.ism != ism:
        customer.ism = ism
    customer.telefon = telephone
    customer.save()

    delivery_type = data.get('delivery_type')
    if delivery_type == 'delivery':
        yt = 'manzil'
    elif delivery_type == 'stol':
        yt = 'stol'
    else:
        yt = 'olib_kelish'

    items_data = data.get('items') or []
    if not items_data:
        return JsonResponse({'error': "Savat bo'sh"}, status=400)

    try:
        with transaction.atomic():
            order = Order.objects.create(
                raqam=f"B-{timezone.now():%Y%m%d}-{str(uuid.uuid4().int)[:4]}",
                mijoz=customer,
                holat='yangi',
                yetkazish_turi=yt,
                stol_raqami=data.get('stol_raqami') or None,
                manzil=data.get('address') or '',
                telefon=telephone,
                izoh=data.get('comment') or '',
                yetkazish_narxi=Decimal(str(data.get('delivery_fee') or 0)),
            )
            jami = Decimal('0')
            bot_items = []
            for it in items_data:
                dish_id = it.get('dish')
                soni = int(it.get('quantity') or 1)
                dish = Dish.objects.filter(id=dish_id).first()
                if not dish:
                    continue
                summa = dish.narx * soni
                OrderItem.objects.create(
                    buyurtma=order, taom=dish, taom_nomi=dish.nom,
                    narx=dish.narx, miqdor=soni, summa=summa
                )
                jami += summa
                bot_items.append({
                    'taom_nomi': dish.nom,
                    'miqdor': soni,
                    'narx': dish.narx,
                    'summa': summa,
                })
            order.jami_summa = jami + order.yetkazish_narxi
            order.save()
            OrderStatusLog.objects.create(
                buyurtma=order, eski_holat='-', yangi_holat='yangi', kim=None
            )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    send_telegram_order({
        'raqam': order.raqam,
        'customer_name': customer.ism,
        'phone': telephone,
        'delivery_type': yt,
        'address': data.get('address') or '',
        'comment': data.get('comment') or '',
        'items': bot_items,
        'jami_summa': order.jami_summa,
    })

    return JsonResponse({
        'status': 'ok',
        'order_id': order.id,
        'raqam': order.raqam,
    })

def _is_admin(user):
    return user and (user.is_superuser or user.groups.filter(name='Administrator').exists())


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminRole]

    @action(detail=False, methods=['post'], permission_classes=[])
    def get_or_create_telegram(self, request):
        telegram_id = request.data.get('telegram_id')
        ism = request.data.get('ism', '')
        username = request.data.get('username', '')

        if not telegram_id:
            return Response({'error': 'telegram_id kiritilishi shart'}, status=status.HTTP_400_BAD_REQUEST)

        customer, created = Customer.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={'ism': ism, 'username': username}
        )
        if not created and ism:
            customer.ism = ism
            customer.username = username
            customer.save()

        serializer = self.get_serializer(customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get_queryset(self):
        if _is_admin(self.request.user):
            return Category.objects.all()
        return Category.objects.filter(faolmi=True)


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DishFilter
    search_fields = ['nom', 'tavsif']
    ordering_fields = ['narx', 'yaratilgan']

    def get_queryset(self):
        if _is_admin(self.request.user):
            return Dish.objects.all()
        return Dish.objects.filter(faolmi=True, kategoriya__faolmi=True)


class CartView(APIView):
    
    def get_cart(self, telegram_id):
        try:
            customer = Customer.objects.get(telegram_id=telegram_id)
            cart, _ = Cart.objects.get_or_create(mijoz=customer, faolmi=True)
            return cart, None
        except Customer.DoesNotExist:
            return None, "Mijoz topilmadi"

    def get(self, request):
        cart, error = self.get_cart(request.query_params.get('telegram_id'))
        if error:
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)
        return Response(CartSerializer(cart).data)

    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        dish_id = request.data.get('dish_id')
        miqdor = int(request.data.get('miqdor', 1))

        cart, error = self.get_cart(telegram_id)
        if error:
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)

        try:
            dish = Dish.objects.get(id=dish_id)
        except Dish.DoesNotExist:
            return Response({'error': "Taom topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        if not dish.faolmi or not dish.kategoriya.faolmi:
            return Response({'error': "Ushbu taom hozirda mavjud emas"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(savat=cart, taom=dish)
        if created:
            cart_item.miqdor = min(miqdor, 50)
        else:
            cart_item.miqdor = min(cart_item.miqdor + miqdor, 50)
        cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    def delete(self, request):
        cart, error = self.get_cart(request.data.get('telegram_id'))
        if error:
            return Response({'error': error}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = CartItem.objects.get(savat=cart, taom_id=request.data.get('dish_id'))
            if request.data.get('to_lower', False) and item.miqdor > 1:
                item.miqdor -= 1
                item.save()
            else:
                item.delete()
            return Response(CartSerializer(cart).data)
        except CartItem.DoesNotExist:
            return Response({'error': "Savatda bunday taom yo'q"}, status=status.HTTP_404_NOT_FOUND)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ['yaratilgan', 'id']

    def create(self, request, *args, **kwargs):
        telegram_id = request.data.get('telegram_id')
        try:
            customer = Customer.objects.get(telegram_id=telegram_id)
        except Customer.DoesNotExist:
            return Response({'error': "Mijoz topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        if customer.bloklangan:
            return Response({'error': "Siz bloklangansiz, buyurtma bera olmaysiz!"}, status=status.HTTP_403_FORBIDDEN)

        try:
            cart = Cart.objects.get(mijoz=customer, faolmi=True)
        except Cart.DoesNotExist:
            return Response({'error': "Faol savat topilmadi"}, status=status.HTTP_400_BAD_REQUEST)

        qatorlar = cart.qatorlar.all()
        if not qatorlar.exists():
            return Response({'error': "Bo'sh savatdan buyurtma yaratib bo'lmaydi"}, status=status.HTTP_400_BAD_REQUEST)

        for item in qatorlar:
            if not item.taom.faolmi or not item.taom.kategoriya.faolmi:
                return Response(
                    {'error': f"'{item.taom.nom}' taomi hozirda sotuvda mavjud emas. Savatingizni yangilang."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        bugun = timezone.now().strftime('%Y%m%d')
        unikal_id = str(uuid.uuid4().int)[:4]
        buyurtma_raqami = f"B-{bugun}-{unikal_id}"

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order = serializer.save(
            raqam=buyurtma_raqami,
            mijoz=customer,
            holat='yangi'
        )

        jami_summa = Decimal('0.00')
        for item in qatorlar:
            summa = item.taom.narx * item.miqdor
            OrderItem.objects.create(
                buyurtma=order,
                taom=item.taom,
                taom_nomi=item.taom.nom,
                narx=item.taom.narx,
                miqdor=item.miqdor,
                summa=summa
            )
            jami_summa += summa

        order.jami_summa = jami_summa + order.yetkazish_narxi
        order.save()

        customer.telefon = order.telefon
        customer.save()

        cart.faolmi = False
        cart.save()

        OrderStatusLog.objects.create(
            buyurtma=order,
            eski_holat='-',
            yangi_holat='yangi',
            kim=request.user if request.user.is_authenticated else None
        )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], permission_classes=[IsOshpazOrAdmin])
    def change_status(self, request, pk=None):
        order = self.get_object()
        yangi_holat = request.data.get('holat')
        bekor_sababi = request.data.get('bekor_sababi', '')

        HOLATLAR_TARTIBI = ['yangi', 'tayyorlanmoqda', 'tayyor', 'berildi', 'yetkazildi']
        eski_holat = order.holat

        if yangi_holat == 'bekor_qilindi':
            if eski_holat in ['tayyor', 'berildi', 'yetkazildi']:
                return Response({'error': "Tayyor bo'lgan buyurtmani bekor qilib bo'lmaydi!"}, status=status.HTTP_400_BAD_REQUEST)
            if not bekor_sababi:
                return Response({'error': "Bekor qilish sababi kiritilishi shart!"}, status=status.HTTP_400_BAD_REQUEST)
            order.bekor_sababi = bekor_sababi
            order.yopilgan_vaqti = timezone.now()
        else:
            if eski_holat not in HOLATLAR_TARTIBI or yangi_holat not in HOLATLAR_TARTIBI:
                return Response({'error': "Noto'g'ri holat kiritildi"}, status=status.HTTP_400_BAD_REQUEST)
            
            eski_idx = HOLATLAR_TARTIBI.index(eski_holat)
            yangi_idx = HOLATLAR_TARTIBI.index(yangi_holat)

            if yangi_idx != eski_idx + 1:
                return Response({'error': "Holatlarni o'tkazib yuborish yoki orqaga qaytarish mumkin emas!"}, status=status.HTTP_400_BAD_REQUEST)

            if yangi_holat == 'tayyor':
                order.tayyor_vaqti = timezone.now()
            elif yangi_holat in ['berildi', 'yetkazildi']:
                order.yopilgan_vaqti = timezone.now()

        order.holat = yangi_holat
        order.save()

        OrderStatusLog.objects.create(
            buyurtma=order,
            eski_holat=eski_holat,
            yangi_holat=yangi_holat,
            kim=request.user if request.user.is_authenticated else None
        )

        return Response(OrderSerializer(order).data)


class KitchenQueueView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsOshpazOrAdmin]

    def get_queryset(self):
        return Order.objects.filter(holat__in=['yangi', 'tayyorlanmoqda']).order_by('yaratilgan')


class DailyReportView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        sana = request.query_params.get('sana', timezone.now().strftime('%Y-%m-%d'))
        
        buyurtmalar = Order.objects.filter(
            yaratilgan__date=sana,
            holat__in=['berildi', 'yetkazildi']
        )

        jami_savdo = buyurtmalar.aggregate(Sum('jami_summa'))['jami_summa__sum'] or Decimal('0.00')

        top_taomlar = OrderItem.objects.filter(
            buyurtma__in=buyurtmalar
        ).values('taom_nomi').annotate(
            sotilgan_soni=Sum('miqdor'),
            jami_tushum=Sum('summa')
        ).order_by('-sotilgan_soni')[:5]

        return Response({
            'sana': sana,
            'muvaffaqiyatli_buyurtmalar_soni': buyurtmalar.count(),
            'jami_tushum': jami_savdo,
            'top_taomlar': top_taomlar
        })


def index_view(request):
    return render(request, 'index.html')


def menu_view(request):
    return render(request, 'menu.html')


def cart_view(request):
    return render(request, 'savat.html')


def checkout_view(request):
    return render(request, 'order.html')


def order_success_view(request):
    return render(request, 'ratification.html')


def about_view(request):
    return render(request, 'about.html')