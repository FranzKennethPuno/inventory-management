# Generated by Django 4.2.20 on 2025-03-21 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_pantryitem_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='pantryitem',
            name='last_used_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
