# Generated by Django 2.2.6 on 2019-10-21 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loadings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='loading',
            name='status',
            field=models.CharField(choices=[('CR', 'Created'), ('ED', 'Entries Done'), ('DN', 'DN')], default='CR', max_length=2),
        ),
    ]