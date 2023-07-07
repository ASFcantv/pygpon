from zeep import Client
from zeep.transports import Transport

# Crear un cliente SOAP basado en el archivo WSDL
client = Client('http://10.120.19.143:7782/services/AAAInterfaceBusinessMgrService?wsdl', transport=Transport())

user='wsuser'
password='{2,3}82C8DDE8E330398012D568F4B57F5F2AD8704D34C8A3129D525D47AEC0C82ED8'


"""
##### ResetSubscriberSession #####

CommandId='ResetSubscriberSession'
# Construir el mensaje de solicitud
request_header = {
    'CommandId': CommandId,
    'Version': '1',
    'TransactionId': '',
    'SequenceId': '1',
    'RequestType': 'Event',
    'SessionEntity': {
        'Name': user,
        'Password': password,
        'TimeStampSN': ''
    },
    'SerialNo': '1',
}

request_body = {
    'SubscriberID': 'scr-bras-03--172.-01005100701559@aba',
}

# Llamar a la operación del servicio web
response = client.service.ResetSubscriberSession(RequestHeader=request_header, ResetSubscriberSessionRequest=request_body)

# Imprimir la respuesta
print(response)

##### ResetSubscriberSession #####




##### NewAAASubscriber #####

CommandId='NewAAASubscriber'
# Construir el mensaje de solicitud
request_header = {
    'CommandId': CommandId,
    'Version': '1',
    'TransactionId': '',
    'SequenceId': '1',
    'RequestType': 'Event',
    'SessionEntity': {
        'Name': user,
        'Password': password,
        'TimeStampSN': ''
    },
    'SerialNo': '1',
}

request_body = {
    'SubscriberID': 'scr-bras-03--172.-01005100701559@aba',
    'AAASubscriberInfo':{
    	'PayAccount':'', #Nro Contrato
    	'ContactTeleNo':'', #Numero contacto
    	'':''
    },
    'AAASubscriberServiceInfo': {
    	'AccessType': '1090204',
    	'ChargingType': '1',
    	'IMSI':'' #CEDULA O RIF
    },
    'AAALocationServiceInfo': {
    	'ProductID': '300'
    }
}

# Llamar a la operación del servicio web
response = client.service.NewAAASubscriber(RequestHeader=request_header, NewAAASubscriberRequest=request_body)

# Imprimir la respuesta
print(response)"""

##### NewAAASubscriber #####




##### QueryAAASubscriber #####

CommandId='QueryAAASubscriber'
# Construir el mensaje de solicitud
request_header = {
    'CommandId': CommandId,
    'Version': '1',
    'TransactionId': '',
    'SequenceId': '1',
    'RequestType': 'Event',
    'SessionEntity': {
        'Name': user,
        'Password': password,
        'TimeStampSN': ''
    },
    'SerialNo': '1',
}

request_body = {
    'SubscriberID': 'scr-bras-03--172.-01005100701559@aba',
}

# Llamar a la operación del servicio web
response = client.service.QueryAAASubscriber(RequestHeader=request_header, QueryAAASubscriberRequest=request_body)

# Imprimir la respuesta
print(response)

##### QueryAAASubscriber #####


"""
##### ReplaceLocationService #####

CommandId='ReplaceLocationService'
# Construir el mensaje de solicitud
request_header = {
    'CommandId': CommandId,
    'Version': '1',
    'TransactionId': '',
    'SequenceId': '1',
    'RequestType': 'Event',
    'SessionEntity': {
        'Name': user,
        'Password': password,
        'TimeStampSN': ''
    },
    'SerialNo': '1',
}

request_body = {
    'SubscriberID': 'scr-bras-03--172.-01005100701559@aba',
    'AAALocationServiceInfo': {
    	'ProductID': '160',
    },
    'NewAAALocationServiceInfo': {
    	'ProductID': '300'
    }
}

# Llamar a la operación del servicio web
response = client.service.ReplaceLocationService(RequestHeader=request_header, ReplaceLocationServiceRequest=request_body)

# Imprimir la respuesta
print(response)

##### ReplaceLocationService #####




##### ModifyLocationService #####

CommandId='ModifyLocationService'
# Construir el mensaje de solicitud
request_header = {
    'CommandId': CommandId,
    'Version': '1',
    'TransactionId': '',
    'SequenceId': '1',
    'RequestType': 'Event',
    'SessionEntity': {
        'Name': user,
        'Password': password,
        'TimeStampSN': ''
    },
    'SerialNo': '1',
}

request_body = {
    'SubscriberID': 'scr-bras-03--172.-01005100701559@aba',
    'AccessType': '1090204',
    'AAALocationServiceInfo': {
    	'ProductID': '160',
    }
}

# Llamar a la operación del servicio web
response = client.service.ModifyLocationService(RequestHeader=request_header, ModifyLocationServiceRequest=request_body)

# Imprimir la respuesta
print(response)

##### ModifyLocationService #####




##### DeleteAAASubscriber #####

CommandId='DeleteAAASubscriber'
# Construir el mensaje de solicitud
request_header = {
    'CommandId': CommandId,
    'Version': '1',
    'TransactionId': '',
    'SequenceId': '1',
    'RequestType': 'Event',
    'SessionEntity': {
        'Name': user,
        'Password': password,
        'TimeStampSN': ''
    },
    'SerialNo': '1',
}

request_body = {
    'SubscriberID': 'scr-bras-03--172.-01005100701559@aba'
}

# Llamar a la operación del servicio web
response = client.service.DeleteAAASubscriber(RequestHeader=request_header, DeleteAAASubscriberRequest=request_body)

# Imprimir la respuesta
print(response)

##### DeleteAAASubscriber #####

"""
























##### ModifyAAASubscriber #####

CommandId='ModifyAAASubscriber'
# Construir el mensaje de solicitud
request_header = {
    'CommandId': CommandId,
    'Version': '1',
    'TransactionId': '',
    'SequenceId': '1',
    'RequestType': 'Event',
    'SessionEntity': {
        'Name': user,
        'Password': password,
        'TimeStampSN': ''
    },
    'SerialNo': '1',
}

request_body = {
    'SubscriberID': 'scr-bras-03--172.-01005100701559@aba'
}

# Llamar a la operación del servicio web
response = client.service.ModifyAAASubscriber(RequestHeader=request_header, ModifyAAASubscriberRequest=request_body)

# Imprimir la respuesta
print(response)

##### ModifyAAASubscriber #####

IMSI


