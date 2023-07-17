import requests
from datetime import datetime

class crm :

    def actualizar(numero_orden,central,status,mms,num_serial):
        
        crm = '10.1.177.197'
        fecha = datetime.now().strftime('%Y-%m-%d')

        url = 'http://'+crm+'/api/ordenes/actualizar'
        payload = {
            "service_cod": "ACLIGPON01",
            "service_pass": "acligpon2021*",
            "num_orden": numero_orden,
            "central": central,
            "fecha_movimiento": fecha,
            "estatus": status,
            "messagge": mms,
            "num_serial": num_serial
        }

        response = requests.post(url, data=payload, verify=False)

        return response

