# Generated by Django 2.2.6 on 2019-11-05 21:11

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dealers', '0001_initial'),
        ('materials', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loading',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loading_no', models.CharField(max_length=12, unique=True)),
                ('vehicle_details', models.TextField(blank=True)),
                ('extra_info', models.TextField(blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('CR', 'Created'), ('ED', 'Entries Done'), ('DN', 'DN')], default='CR', max_length=2)),
                ('dealer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dealers.Dealer')),
            ],
        ),
        migrations.CreateModel(
            name='LoadingWeight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight_count', models.FloatField(validators=[django.core.validators.MinValueValidator(limit_value=1.0)])),
                ('loading', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='loadings.Loading')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='materials.Material')),
            ],
            options={
                'unique_together': {('material', 'loading')},
            },
        ),
    ]
