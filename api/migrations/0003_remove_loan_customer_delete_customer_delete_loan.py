# Generated by Django 4.2.8 on 2023-12-16 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_alter_customer_current_debt"),
    ]

    operations = [
        migrations.RemoveField(model_name="loan", name="customer",),
        migrations.DeleteModel(name="Customer",),
        migrations.DeleteModel(name="Loan",),
    ]
