# Generated by Django 2.2.5 on 2019-10-10 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challans', '0013_auto_20191010_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challan',
            name='challan_no',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]