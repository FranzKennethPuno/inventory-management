# Generated by Django 4.2.20 on 2025-03-21 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_userpreferences'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='cuisines',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='dietary_restrictions',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
