# Generated by Django 4.2.4 on 2023-10-09 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images_rest_api', '0004_alter_customuser_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]