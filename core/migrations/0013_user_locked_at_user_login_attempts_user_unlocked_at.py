# Generated by Django 4.2.6 on 2023-11-21 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_alter_cartao_data_exp'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='locked_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='login_attempts',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='unlocked_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
