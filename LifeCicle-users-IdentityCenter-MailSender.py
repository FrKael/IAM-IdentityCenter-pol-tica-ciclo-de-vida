import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
###############################
# Lambda para enviar notificaciones por correo electrónico
# a usuarios Identity Center que no han realizado ninguna actividad en 3 meses.
# CloudTrail para rescatar eventos de actividad de usuarios.# Utiliza SES para enviar correos electrónicos 
# formato HTML en el body de la notificación.
###############################

def lambda_handler(event, context):

    # clientes
    client = boto3.client('identitystore')
    clientTrail = boto3.client('cloudtrail')
    ses_client = boto3.client('ses')

    # metodo list_users
    response = client.list_users(IdentityStoreId='d-9067954ab8') # <---- cambiar a id especifico en IAM Identity Center

    # lista para almacenar nombres del usuario
    users = []
    # lista para almacenar los usuarios inactivos
    usuarios_inactivos = []
    
    j = 0 #solo para el test lambda
    # Iterar sobre los usuarios en la respuesta
    for user in response['Users']:
        users.append(user['UserName']) # agregar el nombre de usuario a la lista
        j += 1
        print(f"user sended {j}")

    # Iterar sobre los usuarios
    for usuario in users:
        evento = clientTrail.lookup_events(
            LookupAttributes=[
                {
                    'AttributeKey': 'Username',
                    'AttributeValue': usuario
                },
            ],
            MaxResults=1
        )

        # Comprobar si la lista de eventos está vacía
        if not evento['Events']:
            # Agregar el nombre de usuario a la lista de usuarios sin eventos
            usuarios_inactivos.append(usuario)
        else:
            # Obtener la fecha de la última actividad
            fecha_ultima_actividad = evento['Events'][0]['EventTime'].strftime('%Y-%m-%d')
    subject = 'Usuarios inactivos por más de 90 días en IAM Identity Center' #  <------ reemplazar con asunto especifico
    sender = 'dchavez@morris-labs.com' # <------ reemplazar con el correo electrónico de envío
    recipients = 'dchavez@morris-labs.com' # <------ reemplazar con la lista [] de destinatarios 

    # Definir el body para enviar
    if usuarios_inactivos:
        # Crear tabla HTML para los usuarios inactivos
        body = '<table><tr><th colspan="2" style="text-align: left; padding: 8px; background-color: #ddd; border: 1px solid black;">Usuarios inactivos por más de 90 días:</th></tr>'
        body += '<tr><th style="border: 1px solid black; padding: 8px;">Nombre de usuario</th><th style="border: 1px solid black; padding: 8px;">Última actividad</th></tr>'
        for user_in in usuarios_inactivos:
            body += f'<tr><td style="border: 1px solid black; padding: 8px;">{user_in}</td><td style="border: 1px solid black; padding: 8px;">{fecha_ultima_actividad}</td></tr>'
        body += '</table><br><br>Se recomienda realizar una revisión a los usuarios indicados y proceder con su respectivo procedimiento.'


        # Crear objeto MIMEMultipart para el body
        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = sender 
        message['To'] = recipients

        # Añadir el cuerpo del body como html
        message_text = MIMEText(body, 'html')
        message.attach(message_text)

        # Enviar el correo electrónico
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