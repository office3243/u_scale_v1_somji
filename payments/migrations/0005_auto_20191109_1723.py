# Generated by Django 2.2.7 on 2019-11-09 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_accounttransaction_serial_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounttransaction',
            name='actr_no',
            field=models.CharField(default='SMP', max_length=7, verbose_name='Payment No'),
        ),
    ]
