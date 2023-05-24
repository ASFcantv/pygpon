from aaa import *
from olt import *
from getpass import getpass
import sys
import psycopg2
import psycopg2.extensions
import numpy
from db import conexion
from  multiprocessing import Pool


#ips del olt traidas desde la ejecucion del archivo disparador.sh
ips = sys.argv[1:]
indices=len(ips)


def aprovisionar(ip_olt):
    try:
        with conexion.cursor() as cur:
            
            #consulta de las ordenes en estatus null filtrado por la ip del olt
            sql = """SELECT o.* FROM ordens o
            JOIN puertopons ps ON ps.id=o.puerto_pon
            JOIN target_ports tp ON tp.id = ps.id_target_ports
            JOIN olts ol ON ol.id = tp.olt_id
            WHERE o.status IS NULL AND ol.ip_olt=%s ;
            """
            cur.execute(sql,[ip_olt])
            ordenes = cur.fetchall()
                    
            if ordenes!=None:
        
                array = numpy.array(ordenes)
                result_rows, result_columns = array.shape#saber tamaño de columanas y filas del array

                i=0

                while i<result_rows:
                    
                    id = ordenes[i][0]                    
                    serial_modem = ordenes[0][11]
                    numero_identificador = ordenes[0][25]
                    
                    #consulta tabla aaa_user para obtener los datos del aprovisionamiento en el AAA
                    sql = """SELECT * FROM aaa_users WHERE "contactTeleNo"=%s;"""
                    cur.execute(sql,[numero_identificador])
                    aaa_user = cur.fetchone()
                    imsi = aaa_user[0]
                    subscriberid = aaa_user[13]
                    product_id = aaa_user[9]

                    #aprovisionar AAA
                    #aaa.crear(imsi,numero_identificador,subscriberid,product_id)
                    
                                
                    #consulta tabla comands para obtener los datos del aprovisionamiento en el OLT
                    sql = """SELECT * FROM comands WHERE serial_modem = %s;"""
                    cur.execute(sql,[serial_modem])
                    comand = cur.fetchone()
                    
                    slot = comand[6]
                    puerto = comand[7]
                    ont_id = comand[8]
                    descripcion = comand[9]
                    lineprofile = comand[10]
                    srvprofile = comand[11]
                    serviceport = comand[13]
                    vlan= str(int(slot) + 200)
                    c_vlan = comand[15]
                    v_up = comand[16]
                    v_down = comand[17]

                    #aprovisionar OLT
                    #olt.crear(ip_olt,slot,puerto,ont_id,serial_modem,lineprofile,srvprofile,descripcion,serviceport,vlan,c_vlan,v_up,v_down)
    
                    i+=1
                    return i        
    finally:
        conexion.close()

if __name__ == '__main__':
    p = Pool(processes=indices)    
    datos = p.map(aprovisionar,ips)



    


