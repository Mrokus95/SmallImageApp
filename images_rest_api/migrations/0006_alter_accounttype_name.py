# Generated by Django 4.2.4 on 2023-10-11 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('images_rest_api', '0005_alter_customuser_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounttype',
            name='name',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]