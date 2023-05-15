import boto3
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def lambda_handler(event, context):
    # Obtener la fecha actual
    current_time = datetime.datetime.now(datetime.timezone.utc)

    # Crear un cliente de IAM y de SnS
    iam_client = boto3.client('iam')
    sns_client = boto3.client('sns')

    # Inicializar las listas de usuarios inactivos y activos
    inactive_users = []
    active_users = []

    # Obtener una lista de todos los usuarios de IAM
    users = iam_client.list_users()['Users']

    # Recorrer cada usuario
    j = 0 #solo para el test lambda
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
                    f'{user["UserName"]}: {delta_days} días, {delta_hours} horas'
                )
                j += 1
                print(f'user sended {j}')

            # En caso contrario, agregar el usuario a la lista de activos, pero no hay activos xd
            else:
                active_users.append(
                    f'{user["UserName"]}: {delta_days} días, {delta_hours} horas'
                )

    # Si hay al menos un usuario inactivo, enviar un mensaje a través de SNS con la lista de inactivos y activos
    if inactive_users:
        # Crear el objeto MIMEMultipart
        message = MIMEMultipart()
        message['Subject'] = 'Usuarios inactivos por más de 90 días'
        message['From'] = sender
        message['To'] = ', '.join(recipients)

        # Construir el cuerpo del mensaje
        body = 'Los siguientes usuarios han estado inactivos por más de 90 días:\n\n'
        for user in inactive_users:
            body += f'Nombre de usuario: {user.split(":")[0]}\nÚltima actividad: {user.split(":")[1]}\n\n'

        # Crear el objeto MIMEText con el contenido del mensaje
        message_text = MIMEText(body, 'plain')

        # Adjuntar el objeto MIMEText al objeto MIMEMultipart
        message.attach(message_text)
        
        sns_client.publish(
            TopicArn='arn:aws:sns:us-east-1:225510501094:LifeCycle-users',
            Message=message.as_string()
        )