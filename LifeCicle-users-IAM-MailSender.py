import boto3
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
###############################
# Lambda para enviar notificaciones por correo electrónico
# a los usuarios IAM inactivos durante más de 90 días.
# Utiliza SES para enviar correos electrónicos
# con formato HTML en el cuerpo del mensaje, utilizando MIMEText y MIMEMultipart.
###############################

def lambda_handler(event, context):
    # Obtener la fecha actual
    current_time = datetime.datetime.now(datetime.timezone.utc)

    # Crear un cliente de IAM y de SES
    iam_client = boto3.client('iam')
    ses_client = boto3.client('ses')

    # Inicializar las listas de usuarios inactivos y activos
    inactive_users = []
    active_users = []

    # Obtener una lista de todos los usuarios de IAM
    users = iam_client.list_users()['Users']

    j = 0 #solo para el test lambda

    # Recorrer cada usuario
    for user in users:
        # Obtener la última actividad del usuario

        try:
            last_activity = user['PasswordLastUsed']
        except KeyError:
            last_activity = None

        # Verificar si el usuario tiene una última actividad registrada
        if last_activity is not None:
            # Calcular la diferencia en días, horas y minutos entre la última actividad y la fecha actual
            delta = current_time - last_activity
            delta_days = delta.days
            delta_hours = delta.seconds // 3600

            # Si la diferencia en días es mayor a 90, agregar el usuario a la lista de inactivos
            if delta_days > 90:
                inactive_users.append(
                    {'Nombre de usuario': user["UserName"], 'Última actividad': f'{delta_days} días, {delta_hours} horas'}
                )
                j += 1
                print(f'user sended {j}')

            # En caso contrario, agregar el usuario a la lista de activos, pero no hay activos xd
            else:
                active_users.append(
                    f'{user["UserName"]}: {delta_days} días, {delta_hours} horas'
                )

    subject = 'Usuarios inactivos por más de 90 días' #  <------ reemplazar con asunto especifico
    sender = 'dchavez@morris-labs.com' # <------ reemplazar con el correo electrónico de envío
    recipients = 'dchavez@morris-labs.com' # <------ reemplazar con la lista [] de destinatarios 

    # si hay al menos un usuario inactivo, enviar un mensaje a través de SES con la lista de inactivos y activos
    if inactive_users:
        #objeto MIMEMultipart
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = recipients

        # cuerpo del mensaje
        body = '<table><tr><th colspan="2" style="text-align: left; padding: 8px; background-color: #ddd; border: 1px solid black;">Usuarios inactivos por más de 90 días:</th></tr>'
        body += '<tr><th style="border: 1px solid black; padding: 8px;">Nombre de usuario</th><th style="border: 1px solid black; padding: 8px;">Última actividad</th></tr>'
        for user in inactive_users:
            body += f'<tr><td style="border: 1px solid black; padding: 8px;">{user["Nombre de usuario"]}</td><td style="border: 1px solid black; padding: 8px;">{user["Última actividad"]}</td></tr>'
        body += '</table>'
        message_text = MIMEText(body, 'html')
        message.attach(message_text)

        # funcion para enviar un correo electronico mediante SES
        def send_email(sender, recipients, message):
            ses_client.send_raw_email(
                Source=sender,
                Destinations=[recipients],
                RawMessage={
                    'Data': message.as_string(),
                },
            )
            return True
        send_email(sender, recipients, message)