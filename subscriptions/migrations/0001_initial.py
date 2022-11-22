# Generated by Django 3.2.16 on 2022-11-22 19:59

import datetime
from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields
import wagtail.core.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
        ('digitalitems', '0003_downloads_added_from_digital_pack'),
        ('packs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriberDiscount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price_multiplier', models.DecimalField(decimal_places=2, max_digits=3)),
                ('start_month', models.DateField()),
                ('day_of_month_start', models.IntegerField()),
                ('day_of_month_end', models.IntegerField(help_text='Inclusive of the day')),
                ('repeat', models.BooleanField()),
                ('paused', models.BooleanField(default=False)),
                ('last_month_before_pause', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriberList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_method', models.CharField(max_length=40)),
                ('start_date', models.DateField(default=datetime.date.today)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionCampaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', wagtail.core.fields.RichTextField()),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('error_details', models.TextField()),
                ('payment_status', models.CharField(choices=[('Paid', 'PAID'), ('Processing', 'PROCESSING'), ('Payment Error', 'ERROR'), ('Unpaid', 'UNPAID')], default='UNPAID', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionItem',
            fields=[
                ('item_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='shop.item')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('shop.item',),
        ),
        migrations.CreateModel(
            name='SubscriptionTier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tier_name', models.CharField(default='Follower', max_length=100)),
                ('external_name', models.CharField(max_length=100, null=True)),
                ('price_currency', djmoney.models.fields.CurrencyField(choices=[('USD', 'US Dollar')], default='XYZ', editable=False, max_length=3)),
                ('price', djmoney.models.fields.MoneyField(decimal_places=2, max_digits=19, null=True)),
                ('default_price_currency', djmoney.models.fields.CurrencyField(choices=[('USD', 'US Dollar')], default='XYZ', editable=False, max_length=3)),
                ('default_price', djmoney.models.fields.MoneyField(decimal_places=2, max_digits=19, null=True)),
                ('limit', models.IntegerField(blank=True, default=None, null=True)),
                ('allow_on_site_subscriptions', models.BooleanField(default=False)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tiers', to='subscriptions.subscriptioncampaign')),
            ],
            options={
                'ordering': ['tier_name'],
            },
        ),
        migrations.CreateModel(
            name='SubscriptionProduct',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='shop.product')),
                ('month', models.DateField()),
                ('tier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='subscriptions.subscriptiontier')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('shop.product',),
        ),
        migrations.CreateModel(
            name='SubscriptionPack',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('pledges_from', models.DateTimeField()),
                ('pledges_to', models.DateTimeField()),
                ('token_quantity', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('require_multiple_months', models.BooleanField(default=False)),
                ('number_of_months', models.IntegerField(blank=True, null=True)),
                ('require_exact_months', models.BooleanField(default=False)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='packs', to='subscriptions.subscriptioncampaign')),
                ('contents', models.ManyToManyField(blank=True, related_name='subscription_packs', to='digitalitems.DigitalItem')),
                ('pack', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='packs.digitalpack')),
                ('pack_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.productimage')),
                ('tier_req', models.ManyToManyField(to='subscriptions.SubscriptionTier')),
            ],
        ),
    ]
