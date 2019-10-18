# Generated by Django 2.2.6 on 2019-10-18 19:05

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_wallettransaction_deducted_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallettransaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=9),
        ),
        migrations.CreateModel(
            name='InPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('status', models.CharField(choices=[('PN', 'Pending'), ('DN', 'Done')], default='DN', max_length=2)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.Payment')),
            ],
        ),
    ]