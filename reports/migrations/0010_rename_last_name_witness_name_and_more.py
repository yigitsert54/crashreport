# Generated by Django 5.2.1 on 2025-06-15 18:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0009_damagereport_witness_textfield'),
    ]

    operations = [
        migrations.RenameField(
            model_name='witness',
            old_name='last_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='witness',
            name='first_name',
        ),
    ]
