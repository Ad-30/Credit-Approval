# Generated by Django 4.2.8 on 2023-12-16 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="current_debt",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
