# Africa's Talking USSD

The callback is available at:

`POST /api/ussd/callback/`

It accepts Africa's Talking `application/x-www-form-urlencoded` fields:

`sessionId`, `serviceCode`, `phoneNumber`, `networkCode`, and `text`.

## Local setup

1. Install backend dependencies and run migrations:

```powershell
py -3 -m pip install -r backend/requirements.txt
py -3 backend/manage.py migrate
```

2. Configure the environment without committing credentials:

```env
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your-key
AFRICASTALKING_USSD_SERVICE_CODE=*123#
AFRICASTALKING_USSD_CALLBACK_URL=https://YOUR-NGROK-DOMAIN.ngrok-free.app/api/ussd/callback/
USSD_MAX_CALLS_PER_MINUTE=30
```

3. Start Django and expose it through a tunnel, for example:

```powershell
py -3 backend/manage.py runserver 0.0.0.0:8000
ngrok http 8000
```

Register the public callback URL in the Africa's Talking dashboard. The callback returns plain-text `CON` or `END` responses.

## Session and data behavior

- Sessions are stored in `UssdSession` and expire after 15 minutes.
- The participant phone number is the lookup key; registration does not create duplicate users for an existing number.
- Applications, participation status, form responses, and challenges use the existing domain models.
- USSD challenge reports are marked in `audit_history` with `actor: USSD` and `note: Source: USSD`.
- Callback logs retain only a session suffix, phone suffix, and text length.