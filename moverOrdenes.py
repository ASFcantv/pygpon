import requests
from db import conexion
import numpy
from aaa  import *
from leectorCsv import leer
import psycopg2
import psycopg2.extensions
from datetime import datetime as dt
import socket
import logging 


now=dt.now()
login_path="./logs/crear/logmoverOrdenes"+now.strftime("%Y%m%d")+"txt"
logging.basicConfig(filename=login_path, level=logging.DEBUG)

path="C:\laragon\www\scripts  py/archivosOrdenes/Libro1.csv"#direccion del archivo

results=leer(path)
array = numpy.array(results)
result_rows, result_columns = array.shape#saber tamaño de columanas y filas del array

i=1

try:
    while i<result_rows:
        #datos del caso
        num_orden=results[i][0]
        serial_modem=results[i][3]
        numero_identificador=str(results[i][4])

        #consulta de ordenes y datos del agregador
        cursor=conexion.cursor()
        sql="""SELECT o.id,o.descripcion,tp.s_vlan_agregador,tp.slot_agregador,tp.puerto_agregador,a.hostname,o.documento,o.plan,a.id,c.codigo_central 
                FROM ordens o
                JOIN puertopons p ON o.puerto_pon=p.id
                JOIN target_ports tp ON tp.id=p.id_target_ports
                JOIN agregadors a ON a.id=tp.id_agregador 
                JOIN olts ol ON ol.id=tp.olt_id
                JOIN centrals c ON c.id=ol.central_id
                WHERE o.id=%s"""

        cursor.execute(sql,[num_orden])
        orden=cursor.fetchone()
        

        if orden!=None:
            #datos para crear el suscriptor
            id_orden=str(orden[0])
            descripcion=orden[1]
            s_vlan=str(orden[2])
            slot_agr=str(orden[3])
            puerto_agr=str(orden[4])
            hotname_agr=orden[5]
            documento=orden[6]
            plan=orden[7]
            id_brass=orden[8]
            id_central=orden[9]

            #validacion de la descripcion del caso
            if orden[1]=="no se creo en el AAA":
                consulta=cursor.execute('SELECT * FROM aaa_users WHERE "contactTeleNo"=%s',[numero_identificador])
                aaa_users=cursor.fetchone()

                if not aaa_users:

                    try:
                        cursor.execute('SELECT c_vlan from comands WHERE serial_modem=%s',[serial_modem])
                        comand=cursor.fetchone()
                        c_vlan=str(comand[0])

                        #busqueda de planes para el AAA
                        cursor.execute('SELECT id from plans WHERE pcomercial=%s',[plan])
                        plans=cursor.fetchone()
                        cursor.execute('SELECT "idPlan" from aaas WHERE "IDPLANES"=%s',[plans[0]])
                        plaaans=cursor.fetchone()
                        while len(slot_agr)<2:
                            slot_agr="0"+slot_agr
                        while len(puerto_agr)<3:                
                            puerto_agr="0"+puerto_agr
                        while len(s_vlan)<4:
                            s_vlan="0"+s_vlan
                        while  len(c_vlan)<5:
                            c_vlan="0"+c_vlan

                        subscriber_id=hotname_agr+'--172.-'+slot_agr+puerto_agr+s_vlan+c_vlan+'@aba'

                        response=aaa.crear(documento,numero_identificador,subscriber_id,plaaans)

                        if response=='exitoso':

                            logging.debug(response.text+" - "+subscriber_id)
                            cursor.execute('UPDATE ordens SET descripcion=%s WHERE id=%s;',[None,id_orden])  
                            URL="http://200.44.45.149/api/actualizarCrm?numero_orden="+id_orden+"&central="+id_central+"&status=3&message=exitoso"
                            response=requests.post(URL)
                            print("exitoso "+str(id_orden)+"-"+subscriber_id)
                        elif response=='ya existe':
                            URL="http://200.44.45.149/api/ApiEliminarSuscriptor?subscriberId="+subscriber_id
                            response=requests.post(URL)
                            URL = "http://200.44.45.149/api/ApiCrearNuevoSuscriptor?IMSI="+documento+"&contactTeleNo="+numero_identificador+"&payAccount=0&productID="+str(plaaans[0])+"&sequenceId=0&serialNo=0&subscriberID="+subscriber_id
                            response= requests.post(URL)
                            cursor.execute('UPDATE ordens SET descripcion=%s WHERE id=%s;',[None,id_orden])  
                            cursor.execute('UPDATE ordens SET status=%s WHERE id=%s;',[3,id_orden])  
                            logging.debug(response.text+" - "+subscriber_id)
                            print("verificar"+str(id_orden)+"-"+subscriber_id)
                        else:
                            logging.debug(response.text+" - "+subscriber_id)
                            print("error"+str(id_orden)+" - "+subscriber_id)
                    except TypeError:
                            print("error cargando comands "+id_orden)

        i+=1
except:
    logging.debug("error de ejecucion")
    print("ha ocurrido un error en ejecucion")
