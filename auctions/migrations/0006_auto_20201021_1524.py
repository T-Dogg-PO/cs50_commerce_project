# Generated by Django 3.1 on 2020-10-21 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_auto_20201021_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctionlisting',
            name='category',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
