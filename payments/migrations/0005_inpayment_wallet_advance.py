# Generated by Django 2.2.6 on 2019-10-19 13:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parties', '0002_auto_20191018_1943'),
        ('payments', '0004_inpayment_gateway'),
    ]

    operations = [
        migrations.AddField(
            model_name='inpayment',
            name='wallet_advance',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='parties.WalletAdvance'),
        ),
    ]