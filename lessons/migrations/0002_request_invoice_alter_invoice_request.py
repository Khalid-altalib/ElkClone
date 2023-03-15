# Generated by Django 4.1.4 on 2022-12-14 12:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='invoice',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='request.masterInvoice+', to='lessons.invoice'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='request',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='invoice.masterRequest+', to='lessons.request'),
        ),
    ]