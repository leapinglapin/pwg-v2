# Generated by Django 4.2.2 on 2023-06-10 20:00

import address.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('discount_codes', '0003_initial'),
        ('realaddress', '0001_initial'),
        ('address', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('partner', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
        ('checkout', '0001_initial'),
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkoutline',
            name='item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.item'),
        ),
        migrations.AddField(
            model_name='checkoutline',
            name='paid_in_cart',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lines_paid', to='checkout.cart'),
        ),
        migrations.AddField(
            model_name='checkoutline',
            name='partner_at_time_of_submit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='partner.partner'),
        ),
        migrations.AddField(
            model_name='checkoutline',
            name='submitted_in_cart',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lines_submitted', to='checkout.cart'),
        ),
        migrations.AddField(
            model_name='cart',
            name='billing_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='checkout.billingaddress'),
        ),
        migrations.AddField(
            model_name='cart',
            name='delivery_address',
            field=address.models.AddressField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='delivery_address', to='address.address'),
        ),
        migrations.AddField(
            model_name='cart',
            name='discount_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='discount_codes.discountcode'),
        ),
        migrations.AddField(
            model_name='cart',
            name='old_billing_address',
            field=address.models.AddressField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='billing_address', to='address.address'),
        ),
        migrations.AddField(
            model_name='cart',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='carts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cart',
            name='partner_transactions',
            field=models.ManyToManyField(blank=True, to='partner.partnertransaction'),
        ),
        migrations.AddField(
            model_name='cart',
            name='payment_partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payment_partner', to='partner.partner'),
        ),
        migrations.AddField(
            model_name='cart',
            name='pickup_partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pickup_partner', to='partner.partner'),
        ),
        migrations.AddField(
            model_name='cart',
            name='shipping_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='checkout.shippingaddress'),
        ),
        migrations.AddField(
            model_name='cart',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sites.site'),
        ),
        migrations.AddField(
            model_name='billingaddress',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='realaddress.realcountry', verbose_name='Country'),
        ),
    ]
