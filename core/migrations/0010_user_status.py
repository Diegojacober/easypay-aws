# Generated by Django 4.2.6 on 2023-11-21 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_conta_transferencias_realizadas_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='status',
            field=models.CharField(default='Em Aprovação', max_length=20),
        ),
    ]
