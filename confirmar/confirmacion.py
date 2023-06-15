
import paramiko
import time
from getpass import getpass
import sys
import psycopg2
import psycopg2.extensions
import numpy
from db import conexion
from pathlib import Path
from xml.etree import ElementTree
import xmltodict
import json
import logging
from datetime import datetime as dt
import socket
import requests

now=dt.now()
name_log = './logs/aprov/'+now.strftime("%Y%m%d%H")+'.log'

#ips del olt traidas desde la ejecucion del archivo disparador.sh
ip_olt = 'ip'
user="AprovCantv" 
password="Apr0vC@ntv#21$"

try:
    with conexion.cursor() as cur:
        
        #consulta de las ordenes en estatus null filtrado por la ip del olt
        sql = """SELECTc.serial_modem
        FROM ordens o
        JOIN comands c ON c.serial_modem=o.serial_modem
        JOIN aaa_users a ON a."contactTeleNo"=o.numero_identificador
        JOIN tao_details td ON o.id_tao=td.id_tao
        JOIN olts ol ON ol.id=td.olt_id
        WHERE o.status%s  AND ol.ip_olt=%s ;
        """
        cur.execute(sql,[8,ip_olt])
        ordenes = cur.fetchall()
                
        array = numpy.array(ordenes)
        result_rows, result_columns = array.shape#saber tamaño de columanas y filas del array

        x=0
        while x<result_rows:

            serial = ordenes[x][0]

            #instanciar cliente ssh
            cliente = paramiko.SSHClient()
            cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #conexion ssh
            cliente.connect(hostname=ip_olt,username=user,password=password)
            #bloque del comando
            devices_access = cliente.invoke_shell()
            devices_access.send("enable\n")
            time.sleep(1)
            devices_access.send("config\n")
            time.sleep(1)
            devices_access.send("undo smart\n")
            time.sleep(1)
            devices_access.send("undo interactive\n")
            time.sleep(1)
            devices_access.send("display ont info by-sn "+serial+" \n")
            time.sleep(5)
            devices_access.send("\n")
            time.sleep(2)
            devices_access.send("\n")
            time.sleep(2)
            devices_access.send("quit \n")
            time.sleep(1)
            devices_access.send("quit\n")

            time.sleep(1)
            output = devices_access.recv(6000)        
            response=output.decode('ascii')
            
            cliente.close()

            if response.find('The required ONT does not exist')>-1:
                query = "UPDATE ordens SET descripcion=%s,status=%s WHERE serial_modem=%s"
                cur.execute(query,['error: no se pudo aprovisionar',2,serial])
            else:
                query = "UPDATE ordens SET descripcion=%s,status=%s WHERE serial_modem=%s"
                cur.execute(query,[None,3,serial])


finally:
    conexion.close()