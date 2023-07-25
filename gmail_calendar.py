import csv
import datetime
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


year = datetime.datetime.today().year  # año actual
month = 7  # Julio
INITIAL_DATE = datetime.datetime(year, month, 1, 18, 0)  # Fecha de inicio 1 de Julio 18hs de año corriente

# ID del calendario de Google al que quieras agregar las citas
CALENDAR_ID = "######@group.calendar.google.com"


def autheticate():
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "gmail_credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)

    service = build("calendar", "v3", credentials=creds)

    return service


def create_event(service, calendar_id, date,  name, email):
    event = {
        "summary": f"Guardia {name}",
        "description": f"Esta es una cita diaria para el correo electrónico {email}",
        "start": {
            "dateTime": date.isoformat(),
            "timeZone": "America/Buenos_Aires",
        },
        "end": {
            "dateTime": (
                date + datetime.timedelta(hours=15)  # se suman 15 horas para terminar a las 9hs del día siguiente
            ).isoformat(),
            "timeZone": "America/Buenos_Aires",
        },
        "attendees": [
            {"email": email},
        ],
    }

    service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f"Cita creada el día {date.isoformat()} para {name} - {email}")


def calendar_week(service):
    """
        Genera citas para días de semana a partir de listado csv
    """

    print("*** CREANDO ROTACIÓN DE DIAS DE SEMANA ***")
    actual_date = INITIAL_DATE
    with open("mails_list.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            email = row["Email"]
            name = row["Name"]

            if actual_date.weekday() == 5:
                actual_date += datetime.timedelta(days=2)  # Saltea fin de semana

            if actual_date.weekday() < 5:  # Verifica si es un día de semana (lunes a viernes), 5 y 6 (Sábado y Domingo)
                create_event(service, CALENDAR_ID, actual_date, name, email)

            actual_date += datetime.timedelta(days=1)
            time.sleep(1)  # Retraso para evitar exceder los límites de la API


def calendar_weekend(service):
    """
        Genera citas para fines de semana a partir de listado csv
    """

    print("*** CREANDO ROTACIÓN DE FINES DE SEMANA ***")
    actual_date = INITIAL_DATE
    with open("mails_list.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        inverted_rows = rows[::-1]

        for row in inverted_rows:
            email = row["Email"]
            name = row["Name"]

            while actual_date.weekday() < 5:  # Busca el proximo fin de semana
                actual_date += datetime.timedelta(days=1)

            if actual_date.weekday() >= 5:  # Es fin de semana
                create_event(service, CALENDAR_ID, actual_date, name, email)
                actual_date += datetime.timedelta(days=1)  # Saltea fin de semana

            time.sleep(1)  # Retraso para evitar exceder los límites de la API


if __name__ == "__main__":
    service = autheticate()
    calendar_week(service)
    calendar_weekend(service)
