# Generated by Django 3.2.16 on 2022-11-22 19:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
        ('game_info', '0001_initial'),
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventTicketItem',
            fields=[
                ('item_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='shop.item')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='events.event')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('shop.item',),
        ),
        migrations.AddField(
            model_name='event',
            name='edition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='game_info.edition'),
        ),
        migrations.AddField(
            model_name='event',
            name='format',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='game_info.format'),
        ),
        migrations.AddField(
            model_name='event',
            name='game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='game_info.game'),
        ),
    ]
