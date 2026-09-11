from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_customer_telegram_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dish',
            name='tayyorlanish_vaqti',
        ),
        migrations.RenameField(
            model_name='dish',
            old_name='yangilasgan',
            new_name='yangilangan',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='yopingan_vaqti',
            new_name='yopilgan_vaqti',
        ),
        migrations.AlterField(
            model_name='dish',
            name='nom',
            field=models.CharField(max_length=200, verbose_name='Taom nomi'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='tavsif',
            field=models.TextField(blank=True, verbose_name='Tavsif'),
        ),
        migrations.AlterField(
            model_name='dish',
            name='tayyorlash_vaqti',
            field=models.PositiveSmallIntegerField(default=15, verbose_name='Taom tayyorlash vaqti (daq)'),
        ),
        migrations.AlterField(
            model_name='order',
            name='holat',
            field=models.CharField(choices=[('yangi', 'Yangi'), ('tayyorlanmoqda', 'Tayyorlanmoqda'), ('tayyor', 'Tayyor'), ('berildi', 'Berildi'), ('yetkazildi', 'Yetkazildi'), ('bekor_qilindi', 'Bekor qilindi')], db_index=True, default='yangi', max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='yetkazish_turi',
            field=models.CharField(choices=[('stol', 'Stolda'), ('manzil', 'Yetkazib berish'), ('olib_kelish', 'Olib kelish')], max_length=12, verbose_name='Yetkazish turi'),
        ),
        migrations.AlterField(
            model_name='order',
            name='stol_raqami',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Stol raqami'),
        ),
        migrations.AlterField(
            model_name='order',
            name='tayyor_vaqti',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Tayyor vaqti'),
        ),
        migrations.AlterField(
            model_name='order',
            name='yopilgan_vaqti',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Yopilgan vaqti'),
        ),
    ]