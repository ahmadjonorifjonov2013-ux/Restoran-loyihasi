from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q

User = get_user_model()


class Customer(models.Model):
    id = models.BigAutoField(primary_key=True)
    telegram_id = models.BigIntegerField(unique=True, db_index=True, verbose_name="Telegram ID")
    ism = models.CharField(max_length=100, verbose_name="Ism")
    username = models.CharField(max_length=64, blank=True, verbose_name="Username")
    telefon = models.CharField(max_length=20, blank=True, verbose_name="Telefon raqam")
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    bloklangan = models.BooleanField(default=False)
    yaratilgan = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"

    def __str__(self):
        return f"{self.ism} ({self.telegram_id})"



class Category(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nomi")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    tartib = models.PositiveSmallIntegerField(default=0)
    faolmi = models.BooleanField(default=True)


    class Meta:
        ordering = ['tartib', 'nom']
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.nom

class Dish(models.Model):
    kategoriya = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="Taomlar")
    nom = models.CharField(max_length=200 , verbose_name="Taom nomi")
    tavsif= models.TextField(blank=True, verbose_name="Tavsi")
    narx = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Narx (so'm)"
    )
    rasm = models.ImageField(upload_to="Taomlar/", null=True, blank=True, verbose_name="Rasm")
    tayyorlash_vaqti = models.PositiveSmallIntegerField(default=15,verbose_name="Taom tayyorlash vaqti(daq)")
    faolmi = models.BooleanField(default=True, verbose_name="Faolmi")
    yaratilgan = models.DateTimeField(auto_now_add=True)
    yangilasgan = models.DateTimeField(auto_now=True)
    tayyorlanish_vaqti = models.IntegerField(default=15)


    class Meta:
        unique_together = ('kategoriya', 'nom')
        verbose_name = "Taom"
        verbose_name_plural = "Taomlar"

    def __str__(self):
        return f"{self.nom} - {self.narx} so'm"

class Cart(models.Model):
    mijoz = models.ForeignKey(Customer, on_delete=models.CASCADE)
    faolmi = models.BooleanField(default=True, verbose_name="Faolmi")
    yaratilgan = models.DateTimeField(auto_now_add=True)
    yangilangan = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['mijoz'], 
                condition=Q(faolmi=True), 
                name='bitta_faol_savat'
            )
        ]
        verbose_name = "Savat"
        verbose_name_plural = "Savatlar"

    def __str__(self):
        return f"Savat #{self.id} - {self.mijoz.ism}"


class CartItem (models.Model):
    savat = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="Qatorlar")
    taom = models.ForeignKey(Dish, on_delete=models.CASCADE, verbose_name="Taom")
    miqdor = models.PositiveSmallIntegerField(
        default=1, 
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        verbose_name="Miqdor"
    )
    qoshilgan = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('savat', 'taom')
        verbose_name = "Savat Qatori"
        verbose_name_plural = "Savat Qatorlari"

    def __str__(self):
        return f"{self.taom.nom} x {self.miqdor}"

class Order (models.Model):
    HOLATLAR = (
        ('yangi', 'Yangi'),
        ('tayyorlanmoqda', 'Tayyorlanmoqda'),
        ('tayyor', 'Tayyor'),
        ('berildi', 'Berildi'),
        ('yetkazildi', 'Yetkazildi'),
        ('bekor_qilindi', 'Bekor qilindi'),
    )
    YETKAZISH_TURI = (
        ('stol', 'Stolda'),
        ('manzil', 'Yetkazib berish'),
    )
    raqam = models.CharField(max_length=16, unique=True, db_index=True)
    mijoz = models.ForeignKey(Customer, on_delete=models.CASCADE)
    holat = models.CharField(max_length=20, choices=HOLATLAR,default="Yangi", db_index=True)
    yetkazish_turi = models.CharField(max_length=10, choices=YETKAZISH_TURI, verbose_name="Yetgazish turi")
    stol_raqami = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Stol raaqami")
    manzil = models.CharField(max_length=300, blank=True, verbose_name="Manzil")
    telefon = models.CharField(max_length=20,verbose_name="Telefon")
    izoh = models.TextField(blank=True, verbose_name="Izoh")
    jami_summa = models.DecimalField(max_digits=12 , decimal_places=2, default=0, verbose_name="Jami summa")
    yetkazish_narxi = models.DecimalField(max_digits=10, decimal_places=2, default=0 , verbose_name="Yetkazish narxi")
    yaratilgan = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Yaratilgan vaqti")
    tayyor_vaqti = models.DateTimeField(null=True, blank=True, verbose_name="Tayyor vaqti ")
    yopingan_vaqti = models.DateTimeField(null=True,blank=True, verbose_name="Yopilgan vaqati")
    bekor_sababi = models.CharField(max_length=300, blank=True, verbose_name="Bekor sababi")


    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"

    def clean(self):
        if self.yetkazish_turi == 'stol' and not self.stol_raqami:
            raise ValidationError({'stol_raqami': "Stolda yetkazish uchun stol raqami ko'rsatilishi shart."})
        if self.yetkazish_turi == 'manzil' and not self.manzil:
            raise ValidationError({'manzil': "Yetkazib berish uchun manzil kiritilishi shart."})

    def __str__(self):
        return f"Buyurtma {self.raqam} ({self.get_holat_display()})"



class OrderItem(models.Model):
    buyurtma = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='qatorlar', verbose_name="Buyurtma")
    taom = models.ForeignKey(
        Dish, null=True, blank=True, on_delete=models.SET_NULL, related_name='buyurtma_qatorlari', verbose_name="Taom"
    )
    taom_nomi = models.CharField(max_length=120, verbose_name="Taom nomi (Nusxa)")
    narx = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Dona narxi (Nusxa)")
    miqdor = models.PositiveSmallIntegerField(verbose_name="Miqdor")
    summa = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Summa")

    class Meta:
        verbose_name = "Buyurtma Qatori"
        verbose_name_plural = "Buyurtma Qatorlari"

    def __str__(self):
        return f"{self.taom_nomi} x {self.miqdor}"


class OrderStatusLog(models.Model):
    buyurtma = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tarix', verbose_name="Buyurtma")
    eski_holat = models.CharField(max_length=20, verbose_name="Eski holat")
    yangi_holat = models.CharField(max_length=20, verbose_name="Yangi holat")
    kim = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Kim tomonidan")
    vaqt = models.DateTimeField(auto_now_add=True, verbose_name="Vaqt")

    class Meta:
        verbose_name = "Buyurtma Holati Tarixi"
        verbose_name_plural = "Buyurtma Holatlari Tarixi"

    def __str__(self):
        return f"{self.buyurtma.raqam}: {self.eski_holat} -> {self.yangi_holat}"