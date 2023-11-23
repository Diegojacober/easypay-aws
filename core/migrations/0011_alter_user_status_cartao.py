# Generated by Django 4.2.6 on 2023-11-21 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_user_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.CharField(default='Em Análise', max_length=20),
        ),
        migrations.CreateModel(
            name='Cartao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('cvv', models.CharField(max_length=3)),
                ('numero', models.CharField(max_length=16)),
                ('data_exp', models.DateField()),
                ('limite', models.DecimalField(decimal_places=2, max_digits=5)),
                ('tipo', models.CharField(max_length=255)),
                ('conta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cartoes', to='core.conta')),
            ],
        ),
    ]