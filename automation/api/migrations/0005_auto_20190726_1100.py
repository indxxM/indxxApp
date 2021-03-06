# Generated by Django 2.1.10 on 2019-07-26 05:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20190717_1222'),
    ]

    operations = [
        migrations.CreateModel(
            name='Priordays',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sel_cycle_1_day_recon', models.CharField(max_length=20)),
                ('comp_cycle_1_day_recon', models.CharField(max_length=20)),
                ('sel_cycle_2_day_recon', models.CharField(max_length=20)),
                ('prelim_day_recon', models.CharField(max_length=20)),
                ('freeze_day_recon', models.CharField(max_length=20)),
                ('indcommittee_day_recon', models.CharField(max_length=20)),
                ('qc_day_recon', models.CharField(max_length=20)),
                ('announce_day_recon', models.CharField(max_length=20)),
                ('clientcomm_day_recon', models.CharField(max_length=20)),
                ('comm_cal_agent_day_recon', models.CharField(max_length=20)),
                ('freeze_day_rebal', models.CharField(max_length=20)),
                ('qc_day_rebal', models.CharField(max_length=20)),
                ('announce_day_rebal', models.CharField(max_length=20)),
                ('clientcomm_day_rebal', models.CharField(max_length=20)),
                ('comm_cal_agent_day_rebal', models.CharField(max_length=20)),
                ('sel_cycle_2_day_review', models.CharField(max_length=20)),
                ('indcommittee_day_review', models.CharField(max_length=20)),
                ('qc_day_review', models.CharField(max_length=20)),
                ('freeze_day_review', models.CharField(max_length=20)),
                ('announce_day_review', models.CharField(max_length=20)),
                ('clientcomm_day_review', models.CharField(max_length=20)),
                ('comm_cal_agent_day_review', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='registerindex',
            name='QC_Date',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='registerindex',
            name='QC_Date_review',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='ruleslist',
            name='qc_rule',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='ruleslist',
            name='qc_rule_review',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='priordays',
            name='index',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Registerindex'),
        ),
    ]
