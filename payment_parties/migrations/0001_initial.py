# Generated by Django 2.2.6 on 2019-10-19 22:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentParty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('is_self_firm', models.BooleanField(default=False)),
                ('account_details', models.TextField(blank=True)),
            ],
        ),
    ]
