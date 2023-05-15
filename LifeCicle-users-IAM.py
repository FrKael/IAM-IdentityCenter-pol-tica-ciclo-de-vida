import boto3
import datetime


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

            # En caso contrario, agregar el usuario a la lista de activos, pero no hay activos xd
            else:
                active_users.append(
                    f'{user["UserName"]}: {delta_days} días, {delta_hours} horas'
                )

    # Si hay al menos un usuario inactivo, enviar un mensaje a través de SNS con la lista de inactivos y activos
    if inactive_users:
        # Construir el cuerpo del mensaje
        body = 'Los siguientes usuarios han estado inactivos por más de 90 días:\n'
        for user in inactive_users:
            body += f' - {user}\n'
        # body += '\nLos siguientes usuarios han sido activos en los últimos 90 días:\n'
        # for user in active_users:
        #     body += f' - {user}\n'

        sns_client.publish(
            TopicArn='arn:aws:sns:us-east-1:225510501094:LifeCycle-users',
            Message=f"{body}",
            Subject="usuarios inactivos durante 90 días (AWS IAM)"
        )