from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='UssdSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(db_index=True, max_length=120, unique=True)),
                ('phone_number', models.CharField(db_index=True, max_length=30)),
                ('service_code', models.CharField(blank=True, max_length=30)),
                ('network_code', models.CharField(blank=True, max_length=80)),
                ('state', models.CharField(choices=[('MENU', 'Main menu'), ('REGISTER_NAME', 'Registration name'), ('REGISTER_LOCATION', 'Registration location'), ('REGISTER_EDUCATION', 'Registration education'), ('REGISTER_SKILLS', 'Registration skills'), ('REGISTER_INTERESTS', 'Registration interests'), ('OPPORTUNITIES', 'Opportunity list'), ('OPPORTUNITY_DETAIL', 'Opportunity detail'), ('OPPORTUNITY_APPLY', 'Opportunity application'), ('PROGRAMME', 'Programme menu'), ('CHECKIN', 'Monitoring check-in'), ('CHECKIN_CHALLENGE', 'Check-in challenge'), ('CHECKIN_CATEGORY', 'Check-in challenge category'), ('CHALLENGE', 'Challenge menu'), ('PROFILE', 'Profile menu'), ('PROFILE_LOCATION', 'Profile location'), ('PROFILE_EDUCATION', 'Profile education'), ('PROFILE_SKILLS', 'Profile skills'), ('PROFILE_INTERESTS', 'Profile interests')], default='MENU', max_length=40)),
                ('temporary_data', models.JSONField(blank=True, default=dict)),
                ('completed', models.BooleanField(default=False)),
                ('expires_at', models.DateTimeField(db_index=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'indexes': [models.Index(fields=['phone_number', 'completed'], name='ussd_ussdse_phone_n_1f1e50_idx')],
            },
        ),
    ]
