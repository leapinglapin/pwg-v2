# Generated by Django 4.2.2 on 2023-06-10 20:00

from django.db import migrations, models
import django.db.models.deletion
import djmoney.models.fields
import wagtail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', wagtail.fields.RichTextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AttributeType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ContainsPieces',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Edition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', wagtail.fields.RichTextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Faction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', wagtail.fields.RichTextField(blank=True, null=True)),
                ('subfaction_models_not_in_parent_faction', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', wagtail.fields.RichTextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', wagtail.fields.RichTextField(blank=True, null=True)),
                ('cost_to_start_currency', djmoney.models.fields.CurrencyField(choices=[('USD', 'US Dollar')], default='USD', editable=False, max_length=3, null=True)),
                ('cost_to_start', djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default_currency='USD', max_digits=19, null=True)),
                ('approximate_cost_of_full_force_currency', djmoney.models.fields.CurrencyField(choices=[('USD', 'US Dollar')], default='USD', editable=False, max_length=3, null=True)),
                ('approximate_cost_of_full_force', djmoney.models.fields.MoneyField(blank=True, decimal_places=2, default_currency='USD', max_digits=19, null=True)),
                ('featured', models.BooleanField(default=False)),
                ('slug', models.SlugField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='GamePiece',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('attributes', models.ManyToManyField(to='game_info.attribute')),
                ('factions', models.ManyToManyField(to='game_info.faction')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='piece', to='game_info.game')),
            ],
        ),
        migrations.CreateModel(
            name='GamePieceVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attributes', models.ManyToManyField(blank=True, to='game_info.attribute')),
                ('piece', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='game_info.gamepiece')),
            ],
        ),
    ]
