# Generated by Django 4.2.20 on 2025-03-21 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0015_alter_recipe_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='pantryitem',
            name='category',
            field=models.CharField(choices=[('Dairy', 'Dairy'), ('Meat', 'Meat'), ('Vegetables', 'Vegetables'), ('Grains', 'Grains'), ('Fruits', 'Fruits'), ('Others', 'Others')], default='Others', max_length=100),
        ),
    ]
