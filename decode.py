import base64

# Copia el contenido del correo que recibiste y pégalo aquí
encoded_message = b'TG9zIHNpZ3VpZW50ZXMgdXN1YXJpb3MgaGFuIGVzdGFkbyBpbmFjdGl2b3MgcG9yIG3DoXMgZGUg\nOTAgZMOtYXM6CiAtIGFuZHJlcy5nYWxsYXJkbzogMTMyNyBkw61hcywgMCBob3JhcwogLSBDaGVj\naGU6IDIyOSBkw61hcywgNiBob3JhcwogLSBlbXBpZXphOiAxNTQ0IGTDrWFzLCA1IGhvcmFzCiAt\nIGlnbmFjaW8uc290bzogMTYyNyBkw61hcywgMiBob3JhcwogLSBpZ25hY2lvc3o6IDEyOTggZMOt\nYXMsIDYgaG9yYXMKIC0gbnZlbmVnYXMub2xpdmE6IDE1MjUgZMOtYXMsIDMgaG9yYXMKIC0gcGFw\nYXJnYTogMjg2MiBkw61hcywgNiBob3JhcwogLSByb2RyaWdvLm1lcmlubzogNDU5IGTDrWFzLCA0\nIGhvcmFzCiAtIHNvcG9ydGU6IDcxMiBkw61hcywgNSBob3JhcwogLSBzdGFnaW5nX3VzZXI6IDEy\nMyBkw61hcywgNiBob3Jhcwo='

# Decodifica el mensaje
decoded_message = base64.b64decode(encoded_message)

# Imprime el mensaje decodificado
print(decoded_message.decode())
