# Generated by Django 2.2.6 on 2019-10-15 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_accounts', '0003_bankaccount_branch_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankaccount',
            name='account_holder',
            field=models.CharField(default=' ', max_length=128),
            preserve_default=False,
        ),
    ]
