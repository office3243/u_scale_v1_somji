# Generated by Django 2.2.6 on 2019-10-19 22:36

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('materials', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('parties', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Challan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('challan_no', models.PositiveIntegerField(blank=True, null=True)),
                ('vehicle_details', models.CharField(blank=True, max_length=128, null=True)),
                ('weights_amount', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=9)),
                ('extra_charges', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=9, verbose_name='Kata Charges')),
                ('round_amount', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=4)),
                ('total_amount', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=9)),
                ('image', models.ImageField(blank=True, null=True, upload_to='payments/')),
                ('extra_info', models.TextField(blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_entries_done', models.BooleanField(default=False)),
                ('is_reports_done', models.BooleanField(default=False)),
                ('is_rates_assigned', models.BooleanField(default=False)),
                ('is_payed', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('PN', 'Pending'), ('DN', 'Done')], default='PN', max_length=2)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('party', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parties.Party')),
            ],
        ),
        migrations.CreateModel(
            name='Weight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_weight', models.FloatField(default=0.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('rate_per_unit', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=9)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('PN', 'Pending'), ('DN', 'Done')], default='PN', max_length=2)),
                ('challan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='challans.Challan')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='materials.Material')),
            ],
            options={
                'unique_together': {('challan', 'material')},
            },
        ),
        migrations.CreateModel(
            name='WeightEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry', models.FloatField(validators=[django.core.validators.MinValueValidator(0.1)])),
                ('weight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='challans.Weight')),
            ],
            options={
                'verbose_name_plural': 'Weight Entries',
            },
        ),
        migrations.CreateModel(
            name='ReportWeight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight_count', models.FloatField(default=0.0)),
                ('report_type', models.CharField(choices=[('RP', 'Report'), ('RT', 'Return')], max_length=2)),
                ('status', models.CharField(choices=[('PN', 'Pending'), ('DN', 'Done')], default='PN', max_length=2)),
                ('reported_on', models.DateTimeField(blank=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('weight', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='challans.Weight')),
            ],
        ),
    ]
