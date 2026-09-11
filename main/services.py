import requests
from django.conf import settings
from decimal import Decimal

from .models import Dish


def send_telegram_order(order_data):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    text = "📦 <b>Yangi buyurtma!</b>\n\n"
    if order_data.get('raqam'):
        text += f"🧾 <b>Raqam:</b> {order_data['raqam']}\n"
    text += f"👤 <b>Mijoz:</b> {order_data.get('customer_name')}\n"
    text += f"📞 <b>Tel:</b> {order_data.get('phone')}\n"

    turlar = {
        'delivery': 'Yetkazib berish',
        'manzil': 'Yetkazib berish',
        'pickup': 'Olib ketish',
        'olib_kelish': 'Olib kelish',
        'stol': 'Stolda',
    }
    del_type = turlar.get(order_data.get('delivery_type'), order_data.get('delivery_type', '—'))
    text += f"🚚 <b>Turi:</b> {del_type}\n"

    if order_data.get('delivery_type') in ('delivery', 'manzil') and order_data.get('address'):
        text += f"📍 <b>Manzil:</b> {order_data.get('address')}\n"
    if order_data.get('comment'):
        text += f"💬 <b>Izoh:</b> {order_data.get('comment')}\n"

    text += "\n🛒 <b>Taomlar:</b>\n"

    dish_names_cache = {}

    def dish_name_va_narx(dish_id):
        if dish_id is None:
            return None, None
        if dish_id not in dish_names_cache:
            dish = Dish.objects.filter(id=dish_id).first()
            dish_names_cache[dish_id] = (dish.nom if dish else None, dish.narx if dish else None)
        return dish_names_cache[dish_id]

    jami = Decimal('0')
    for item in order_data.get('items', []):
        nom = item.get('taom_nomi')
        narx = item.get('narx')
        miqdor = item.get('miqdor') or item.get('quantity') or 1
        summa = item.get('summa')

        if not nom or not narx:
            db_nom, db_narx = dish_name_va_narx(item.get('dish'))
            nom = nom or db_nom or f"ID: {item.get('dish')}"
            narx = narx or db_narx

        if summa is None:
            try:
                summa = (Decimal(str(narx)) if narx else Decimal('0')) * Decimal(str(miqdor))
            except Exception:
                summa = Decimal('0')

        try:
            jami += Decimal(str(summa))
        except Exception:
            pass

        text += f"• {nom} — {miqdor} ta — {summa:,} so'm\n".replace(',', ' ')

    if order_data.get('jami_summa'):
        jami = Decimal(str(order_data['jami_summa']))

    text += f"\n💰 <b>Jami:</b> {jami:,.0f} so'm".replace(',', ' ')

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram Bot xatoligi: {e}")