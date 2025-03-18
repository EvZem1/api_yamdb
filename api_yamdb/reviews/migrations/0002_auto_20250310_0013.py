# Generated by Django 3.2 on 2025-03-09 21:13

from django.db import migrations, models
import reviews.validators


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('id',), 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.TextField(blank=True, verbose_name='биография'),
        ),
        migrations.AlterField(
            model_name='user',
            name='confirmation_code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='код подтверждения'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(blank=True, choices=[('user', 'user'), ('admin', 'admin'), ('moderator', 'moderator')], default='user', max_length=20, verbose_name='роль'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[reviews.validators.validate_username]),
        ),
    ]
