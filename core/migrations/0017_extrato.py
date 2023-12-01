# Generated by Django 4.2.6 on 2023-12-01 17:01

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_alter_emprestimo_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Extrato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tipo', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('conta', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='extrato', to='core.conta')),
            ],
        ),
    ]
