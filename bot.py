from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


from auth import token

#from auth.py import token
import subprocess
import csv
import logging
import sqlite3
from sqlite3 import IntegrityError
#from questionaris import p
from repositori_questionaris import q

#from xlsxwriter.workbook import Workbook

# GLOBAL VARIABLES

nomUser =""
pathdb = '/Users/miquelmunoz/Desktop/BOT/UsersDetails.db'
llistaSantPau = []
llistaQC = []
llista_preguntes = []
nom_taula = None

QUESTI, CREAR_PREG, CREAR_RESP, CHECK_RESP, REGISTRE_NOU , BUTTON_ALTA, CHECK_PREGUNTES , INSERT_DICC , GUARDAR_RESPOSTES = range (9)

nume_p_actual = None
nume_preguntes_total = None
num_r_actual = None
num_respostes_total = None
nou_dicc = None
nom_nou_questi = None
nova_pregunta = None
llista_noves_respostes = None
llista_respostes_insert = None

num = 0
index = None

######################################################
#Registre de logs per pantalla de les comandes rebudes
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Nedone_bot')
######################################################

#############################################################
#############################################################
#COORDINADORS
#-------------
#Tota aquesta part per es perque un coordinador pugui crear un questionari (en format taula a la BD), basat en preguntes i respostes.
#-----------------------------------------------------------

def crearQuestionari(bot, update, args):

    global nume_p_actual
    global nou_dicc
    global nom_nou_questi

    #li donem el valor 1 perque sigui el index de la primera pregunta
    nume_p_actual = 1

    #creem un diccionari buit
    nou_dicc = {}

    nom_nou_questi = None

    #printem q 
    logger.info('He rebut una comanda crearQuestionari')
    print("printem q abans de començar : ")
    print(q)
 

    if args:

        nom_nou_questi = args[0]
        bot.send_message(chat_id=update.message.chat_id,text="Has iniciat la creació d'un nou questionari amb el nom: " )
        update.message.reply_text(str(args[0]))

        if nom_nou_questi in q.keys():
    
            update.message.reply_text("ja existeix un qüestionari amb aquest nom, si us plau escolleix un altre nom per exemple: santpau2020 ")
    
        else:
    
            nou_dicc= {nom_nou_questi : {}}
            print(nou_dicc)
            update.message.reply_text("quantes preguntes tindra el qüestionari?")
        
            return CHECK_PREGUNTES

    else:
        update.message.reply_text("S'ha de pasar un nom de qüestionari a la funció /cq per poder crear un nou qüestionari, exemple: ")
        update.message.reply_text("/cq santpau2020")

def check_preguntes(bot,update):

    global nume_preguntes_total

    print("printem el numero de preguntes que tindrà el qüestionari: " + update.message.text)

    try: 
        if isinstance(int(update.message.text),int):

            nume_preguntes_total=int(update.message.text)
            update.message.reply_text("introdueix la pregunta 1")
            return CREAR_PREG

    except:

        update.message.reply_text("El valor introduit no es un número enter. Torna a introduir el numero de preguntes que vols que tingui el qüestionari.")

def crear_preguntes(bot,update):
    global nume_p_actual
    global nume_preguntes_total
    global num_respostes_total
    global nova_pregunta
    global llista_noves_respostes

    #cada vegada que creem una nova pregunta resetejem el numero de respostes que tindra aquella pregunta i buidem la llista de preguntes que afegirem posteriorment al diccionari
    num_respostes_total = None
    llista_noves_respostes = []


    print ("la pregunta " + str(nume_p_actual) +" es " + update.message.text)
    #guardem el valor de la pregunta que volem guardar a nova_pregunta
    nova_pregunta = update.message.text

    update.message.reply_text("introdueix quantes respostes tindra la pregunta " + str(nume_p_actual))
    return CHECK_RESP

def check_respostes(bot, update):
    global nume_p_actual
    global num_respostes_total
    global num_r_actual

    num_r_actual = 1

    try: 
        if isinstance(int(update.message.text),int):

            print("hi haura " + update.message.text + " respostes a la pregunta " + str(nume_p_actual))
            num_respostes_total=int(update.message.text)
            update.message.reply_text("introdueix la resposta " + str(num_r_actual))

            return CREAR_RESP

    except:

        update.message.reply_text("El valor introduit no es un número enter. Torna a introduir el numero de respostes que vols que tingui la pregunta " + str(nume_p_actual))

def crear_respostes(bot, update):

    global nume_p_actual
    global num_respostes_total
    global nume_preguntes_total
    global num_r_actual
    global nova_pregunta
    global llista_noves_respostes
    global nou_dicc
    global nom_nou_questi

    #cada cop que entrem en aquesta funcio cridada per un Message Handler el update.message.text ja conté el valor d'una resposta, pel que enmmagatzemem aquest valor per afegirlo posteriorment al diccionari
    print("resposta " + str(num_r_actual) + ": " + str(update.message.text))
    llista_noves_respostes.append(update.message.text)
    print(llista_noves_respostes)

    if num_r_actual < num_respostes_total:   

        num_r_actual = num_r_actual + 1
        update.message.reply_text("introdueix la resposta " + str(num_r_actual))

    else:
        #guardem la pregunta actual amb les seves respostes al nou_dicc abans de consulta la següent pregunta
        dicc_temporal = { nova_pregunta : llista_noves_respostes }
        nou_dicc[nom_nou_questi].update(dicc_temporal)
        print (nou_dicc)
        #augmentem l'index de les preguntes per pasar a la seguent
        nume_p_actual = nume_p_actual + 1

        if nume_p_actual <= nume_preguntes_total:

            #passem a la seguent pregunta
            update.message.reply_text("introdueix la pregunta " + str(nume_p_actual))
            return CREAR_PREG

        else:
                print("hem escrit totes les preguntes.")
                update.message.reply_text("hem creat el questionari")
                update.message.reply_text(repr(nou_dicc))

                keyboard = [[InlineKeyboardButton("SI", callback_data='SIII0'),InlineKeyboardButton("NO", callback_data='NOOO0')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
    
                update.message.reply_text("estas segur/a que el vols guardar?", reply_markup=reply_markup)
                
                return INSERT_DICC

def insert_diccionari(bot,update):

    global nou_dicc
    global nom_nou_questi
    
    query = update.callback_query

    respo1 ='SIII0'
    respo2 ='NOOO0'

    if query.data==respo1:
    
        query.edit_message_text(text="Has sel·leccionat SI. Guardem el questionari.")
        print("La resposta es: SI") 
        #afegim al repositori de questionaris el nou questionari

        #actualitzem el fitxer repositori_questionaris per afegir el nou questionari i poder-lo carregar en el futur, sino es perderia al parar el programa python
        q.update(nou_dicc)
        print(q)
        #the repr function will return a string which is the exact definition of your dict 
        f = open("/Users/miquelmunoz/Desktop/BOT/repositori_questionaris.py","w")
        f.write("q = " + repr(q) + "\n")
        f.close()

        #creem la nova taula a la BD per que quan un usuari cridi el qüestionari poguem emmagatzemar les dades del usuari

        #mydict = {'user': 'Bot', 'version': 0.15, 'items': 43, 'methods': 'standard', 'time': 1536304833437, 'logs': 'no', 'status': 'completed'}
        mydict = {'user': 'Bot', 'version': 0.15, 'items': 43, 'methods': 'standard', 'time': 1536304833437, 'logs': 'no', 'status': 'completed'}

        columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in mydict.keys())
        values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in mydict.values())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % ('mytable', columns, values)
        print(sql)


        columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in nou_dicc[nom_nou_questi].keys())
        values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in nou_dicc[nom_nou_questi].values())
        sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % (nom_nou_questi, columns, values)
        print(sql)
        sql2 = "CREATE TABLE IF NOT EXISTS %s ( chat_id INTEGER PRIMARY KEY,name TEXT NOT NULL, %s );" % (nom_nou_questi, columns)
        print(sql2)
        connexioDB(sql2)

            
    elif query.data==respo2:
        query.edit_message_text(text="Has sel·leccionat NO. Per tant eliminem aquest qüestionari.")
        print("La resposta es: NO") 

#Aquesta funcio ens permetra descarrregarnos un fitxer tipus csv amb les dades d'una taula de la Base de Dades.

def descarregartaula(bot, update, args):

    if args:

        taula_a_descarregar = args[0]
        bot.send_message(chat_id=update.message.chat_id,text="la taula que et vols descarregar es: " )
        update.message.reply_text(str(args[0]))
        
        if taula_a_descarregar in q.keys():
            crearCSV(taula_a_descarregar)
            descarregarCSV(bot,update,taula_a_descarregar)
            #Post the file using multipart/form-data 
        else:
            bot.send_message(chat_id=update.message.chat_id,text="No existeix cap qüestionari amb aquest nom.")

    else:
        update.message.reply_text("S'ha de pasar un nom de taula a descarregar, exemple: ")
        update.message.reply_text("/dq santpau2020")


def veure_questionaris_creats(bot,update):
    for i in q.keys():
        bot.send_message(chat_id=update.message.chat_id,text=i)


#################################################################################   
#################################################################################
#################################################################################
#USUARIS
#--------

#Funcio Alta Usuari
def alta(bot, update):

    global nomUser

    comprovarUser=searchUser(update.message.chat_id)

    if comprovarUser==0:
        bot.send_message(
        chat_id=update.message.chat_id,
        text="Ja estas donat d'alta al Bot de la Colla Jove."
            )

    else:
        logger.info('He rebut una comanda alta amb un nou usuari amb chat_id: ' + str(update.message.chat_id))

        bot.send_message(
        chat_id=update.message.chat_id,
        text="Verifica que el teu Nom i Primer Cognom son els següents:\n" + 
            "Nom:" + update.message.chat.first_name + "\n" +
            "Cognom:" + update.message.chat.last_name + "\n"
            )

        nomUser=str(update.message.chat.first_name + " " + update.message.chat.last_name)
        print("nomUser es: " + nomUser)

        #llançem el botó OK/NOK
        buttonOK(bot, update)
        #activem l'esolta del ButtonAlta 
        return BUTTON_ALTA    

#Definim la funcio del boto buttonAlta i com tractar la opció seleccionada
def buttonAlta(bot, update):
    
    global nomUser

    query = update.callback_query
    
    if query.data=="OK":

        query.edit_message_text(text="S'ha confirmat el nom d'usuari.")
        print(query.message.chat_id)
        print("emmagatzarem el nom: " + nomUser)
        insertUser(query.message.chat_id,nomUser)
        
        
    else:
        query.edit_message_text(text="Introdueix el teu nom sense accents de la manera següent: \n"
            "exemple: \n"
            "Magi Fortuny"
            )
        #Si un usuari que s'esta donant d'alta no vol que el seu nom i cognom al Registre siguin els que te definits al telegram li donem la posibilitat de modificarlos (exemple en el meu telegram soc Pako Pill i no Miquel Muñoz)                           
        #En aquest cas concret d'alta d'usuari creem un Handler que esta esperant que li passem nom o nom per guardar el nom i cognom del usuari
        #dispatcher.add_handler(MessageHandler(Filters.text, registreNouUser))
        return REGISTRE_NOU

#emmagatzemem el nom del usuari en una variable i validem que el nom introduit es correcte per l'usuari
def registreNouUser(bot, update):

    global nomUser
    """Echo the user message."""

    update.message.reply_text("el nom introduit es: " + update.message.text)
    nomUser=str(update.message.text)

    #Creem els Botons de OK/NOK PER CREAR LA ALTA
    buttonOK(bot, update)
    #dispatcher.add_handler(CallbackQueryHandler(buttonAlta,pattern='^OK|NOK'))



    print("printem el nou nom: "+nomUser)

    return BUTTON_ALTA

#Creem el format del boto OK/NOK
def buttonOK(bot,update):
    #Creem els Botons de OK/NOK PER CREAR LA ALTA
    keyboard = [[InlineKeyboardButton("OK", callback_data='OK'),
                    InlineKeyboardButton("NOK", callback_data='NOK')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Prem el botó OK si es correcte, o NOK si es erroni.', reply_markup=reply_markup)

##Visualitzem el questionari sol·licitat per que l'usuari el pugui omplir 
#aquesta funcionalitat la farem amb dues funcions mostrarQ i questi

#inicialitza el questionari que volem mostrar i mostra la primera pregunta
def mostrarQ(bot, update, args):
 
    global index
    global nom_taula
    global llista_preguntes
    global llista_respostes_insert

    if args:

        comprovarUser=searchUser(update.message.chat_id)
    
        index = 0
        nom_taula = args[0]
        
        #comprovem que el usuari esta donat d'alta i que el questionari que volem omplir existeix.
        if (comprovarUser==0 and nom_taula in q.keys()):

            logger.info('He rebut una comanda /q')
            nom_i_cognom = update.message.chat.first_name + " " + update.message.chat.last_name
            llista_respostes_insert = [ update.message.chat_id , nom_i_cognom ]
            print( "llista respostes insert: " + str(llista_respostes_insert) )
            
            #montarem el questionari passat per parametre que tambe sera el nom de la taula de la BD a omplir
            print("nom_taula: " + nom_taula)
    
            #aixo es una mica guarro en veritat hauria de comparar quin diccionari del diccionari{} 
            #volem mostrar pero com no hem sortia anem pasant fins que coincidexi amb un, sino existeix no mostrará res. 
            for key,value in q.items():
                #print("clau: ",key  , "valor: ",value)
                if key == nom_taula:
    
                    llista_preguntes = []
    
                    for preg,resp in value.items(): 
                        #print("clau: ", preg ,"valor: ", resp , "longitud valor: " , len(resp) )
                        llista_preguntes.append(preg)
            
                        keyboard = []
                    
                    for i in q[nom_taula][llista_preguntes[index]]:
        
                        keyboard.append(InlineKeyboardButton(i, callback_data=i))
            
                    reply_markup=InlineKeyboardMarkup(build_menu(keyboard,n_cols=1)) #n_cols = 1 is for single column and mutliple rows
                    #reply_markup=InlineKeyboardMarkup(keyboard)
                    bot.send_message(chat_id=update.message.chat_id, text=llista_preguntes[index],reply_markup=reply_markup)
                    print("llista preguntes: " , llista_preguntes)
                    print("les respostes de la pregunta ", llista_preguntes[index],"son: " , q[nom_taula][llista_preguntes[index]])
                    
                    return QUESTI
        
        else:
            update.message.reply_text("Usuari no donat d'alta o qüestionari introduït inexisitent.")


    else:
        update.message.reply_text("S'ha de pasar un nom de qüestionari a la funció /q per poder carregar un qüestionari, exemple: ")
        update.message.reply_text("/q prova2")

#mostra la resta de preguntes del questionari fins a finalizatarlo
def questi(bot,update):

    global llista_preguntes
    global llista_respostes_insert
    global index
    global nom_taula

    query = update.callback_query

    print("Has sel·leccionat: ",query.data)

    llista_respostes_insert.append(query.data)


    index=index+1
    print(" sumem 1 a index per fer la seguent pregunta, index: " , index)
    print("")

    if index < len(llista_preguntes):

        keyboard = []
        
        for i in q[nom_taula][llista_preguntes[index]]:

            keyboard.append(InlineKeyboardButton(i, callback_data=i))

        reply_markup=InlineKeyboardMarkup(build_menu(keyboard,n_cols=1)) #n_cols = 1 is for single column and mutliple rows
        #reply_markup=InlineKeyboardMarkup(keyboard)
        bot.edit_message_text(chat_id=query.message.chat_id,message_id=query.message.message_id,text=llista_preguntes[index])
        bot.edit_message_reply_markup(chat_id=query.message.chat_id,message_id=query.message.message_id,reply_markup=reply_markup)
        print("les respostes de la pregunta ", llista_preguntes[index],"son: " , q[nom_taula][llista_preguntes[index]])

    else:
        print("Has sel·leccionat: ",query.data)
        index = 0
        bot.edit_message_text(chat_id=query.message.chat_id,message_id=query.message.message_id,text=u"S'ha acabat el questionari.")
        print("S'ha acabat el questionari.")     

        keyboard = [[InlineKeyboardButton("SI", callback_data='SIIII0'),InlineKeyboardButton("NO", callback_data='NOOOO0')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        bot.edit_message_text(chat_id=query.message.chat_id,message_id=query.message.message_id,text="estas segur/a que vols guardar?")
        bot.edit_message_reply_markup(chat_id=query.message.chat_id,message_id=query.message.message_id,reply_markup=reply_markup)
        
        return GUARDAR_RESPOSTES

#Dona l'opcio de guardar o eliminar les respostes del questionari contestat per l'usuari
def guardar_respostes (bot,update):

    global llista_respostes_insert
    global nom_taula

    #print("llista respostes insert: " + str(llista_respostes_insert))

    query = update.callback_query

    respo1 ='SIIII0'
    respo2 ='NOOOO0'

    if query.data==respo1:
    
        query.edit_message_text(text="Has sel·leccionat SI. Guardem les respostes.")
        print("La resposta es: SI") 
        print("llista respostes insert: " + str(llista_respostes_insert))

        columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in q[nom_taula].keys())
        values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in llista_respostes_insert)
        sql = "INSERT INTO %s ( chat_id , name , %s ) VALUES ( %s );" % (nom_taula, columns, values)
        print(sql)
        result=insertData(sql)

        if result == "OK":
            query.edit_message_text(text="Les dades s'ha guardat correctament.")
        elif result == "UNIQUE":
            query.edit_message_text(text="Només pots fer el qüestionari una vegada i ja l'havies fet. Pillin/a!!")
        else:
            query.edit_message_text(text="Hi ha hagut un error a la Base de Dades, prova-ho més tard, i sinó funciona reporta-ho al grup de Marketing.")            


    elif query.data==respo2:
        query.edit_message_text(text="Has sel·leccionat NO. Eliminem les respostes.")
        print("La resposta es: NO") 

def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
  menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
  if header_buttons:
    menu.insert(0, header_buttons)
  if footer_buttons:
    menu.append(footer_buttons)
  return menu 

        
#################################################################################
#################################################################################
#################################################################################

#Funcio inicialitzacio i presentacio del Bot        
def start(bot, update):

    global num

    num=0
    
    comprovarUser=searchUser(update.message.chat_id)


    if comprovarUser==0:
        logger.info('He rebut una comanda start')
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Soc un bot de proves i em dic NedoneBot, espero que disfrutis."
        )
        
#Funcio ajuda
def help(bot, update):

    comprovarUser=searchUser(update.message.chat_id)

    if comprovarUser==0:
        logger.info('He rebut una comanda help')
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Soc NedoneBot, en que et puc ajudar?"
        )
        print(update.message.chat_id)

#########################################################################################
#########################################################################################
# Funcions contra la Base de dades
#-----------------------------------#


#Creem la connexio de la BD del usuaris de la Colla i les Taules corresponents, si la DB no existeix sqlite te la crea.
#la BD sera guardada a la ruta on estigui el nostre fitxer python

#Nomes es fa servir el primer cop que creem la TAULA USERS

def connexioDB(sql_sentence):
    try:
        #Creem variable per la conexion contra BD
        global pathdb
        global nom_nou_questi
        sqliteConnection = sqlite3.connect(pathdb,check_same_thread=False)
        sqlite_create_table = sql_sentence
        #creem un cursor per la BD
        cursor = sqliteConnection.cursor()
        print("Correctament connectat a SQLite.")
        try:
            cursor.execute(sqlite_create_table)
            sqliteConnection.commit()
            print("Taula SQLite: \" "  + nom_nou_questi + " \" creada.")
        except sqlite3.Error as error:
            print("Error creant sqlite Table  \" " + nom_nou_questi + " \" ", error)

        cursor.close()

    except sqlite3.Error as error:
        print("Error connectant contra sqlite.", error)

    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("La connexio SQLite s'ha tencat.")

#Funcio que mostra el contingut de la taula USERS 
def readTable():

    global pathdb

    try:
        sqliteConnection = sqlite3.connect(pathdb,check_same_thread=False)
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        
        sqlite_select_query = """SELECT * from USERS"""
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        print("Total rows are:  ", len(records))
        print("Printing each row")
        for row in records:
            print("chat_id: ", row[0])
            print("Name: ", row[1]) 
            print("\n")

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")

#Funcio en la que afegeix un nou usuari a la BD
def insertUser(chat_id, username):
    
    global pathdb

    print("el chatid es: " + str(chat_id))
    print("l'usuari es: " +  str(username))

    try:
        

        sqliteConnection = sqlite3.connect(pathdb,check_same_thread=False)
        cursor = sqliteConnection.cursor()
        print("Successfully Connected to SQLite")

        sqlite_insert_query = """INSERT INTO USERS (chat_id, name) VALUES (?,?)"""

        dadesInsertar= (chat_id , username)

        cursor.execute(sqlite_insert_query, dadesInsertar)
        sqliteConnection.commit()
        print ("la ultima linia insertada es:",cursor.lastrowid)
        print("Record inserted successfully into USERS table ", cursor.rowcount)
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")


#Funcion que afegeix les dades omplertes per un usuari a una taula, es a dir un usuari ha omplert un questionari i guardem les serves respostes.
def insertData(sql_sentence):
    global pathdb

    result = None

    try:
        
        sqliteConnection = sqlite3.connect(pathdb,check_same_thread=False)
        cursor = sqliteConnection.cursor()
        print("Correctament connectat a SQLite.")

        sqlite_insert_query = sql_sentence


        cursor.execute(sqlite_insert_query)
        sqliteConnection.commit()
        print ("la ultima linia insertada es:",cursor.lastrowid)
        print("Guardat correctament.")
        result = "OK"
        cursor.close()

    except IntegrityError as e:
        print("Error de UNIQUE:" , e)
        result = "UNIQUE"

    except sqlite3.Error as error:
        print("Error al insertar dades a la taula sqlite:" , error)
        result = "ERROR"
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("La connexio SQLite s'ha tencat.")

            return result
#Funcio esborrar usuari
def delUser():
    global pathdb
    try:
        sqliteConnection = sqlite3.connect(pathdb,check_same_thread=False)
        cursor = sqliteConnection.cursor()
        print("Successfully Connected to SQLite")

        sqlite_insert_query = """DELETE from USERS where chat_id = 349175213"""

        cursor.execute(sqlite_insert_query)
        sqliteConnection.commit()
        print("Deleted user successfully in USERS table ", cursor.rowcount)
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to delete data into sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("The SQLite connection is closed")

def searchUser(chat_id):


    global pathdb 

    try:
        sqliteConnection = sqlite3.connect(pathdb,check_same_thread=False)
        cursor = sqliteConnection.cursor()
        print("SEARCHUSER:Connected to SQLite")

        sqlite_select_query = """SELECT * from USERS where chat_id = ?"""
        cursor.execute(sqlite_select_query, (chat_id,))
        print("SEARCHUSER: Reading single row  \n")
        data = cursor.fetchone()

        if data is None:

            print("no exsiteix l'usuari amb chat_id: %s"%chat_id)
            resultado=1

        else:

            #print("chat_Id: ", data[0])
            #print("Name: ", data[1])
            resultado=0


        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read single row from sqlite table", error)
        resultado=2


    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("SEARCHUSER: The SQLite connection is closed")

    #print ("el resultat del searchuser es: %s"%resultado)
    return resultado

def searchName(chat_id):

    global pathdb 

    try:
        sqliteConnection = sqlite3.connect(pathdb,check_same_thread=False)
        cursor = sqliteConnection.cursor()
        print("SEARCH_NAME: Connected to SQLite")

        sqlite_select_query = """SELECT * from USERS where chat_id = ?"""
        cursor.execute(sqlite_select_query, (chat_id,))
        print("SEARCH_NAME: Reading single row \n")
        data = cursor.fetchone()
        
        resultado=data[1]

        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read single row from sqlite table", error)
        resultado=2


    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("SEARCH_NAME: The SQLite connection is closed")

    #print ("el resultat del searchuser es: %s"%resultado)
    return resultado

#Crear CSV per descarregar taula de la Base de dades
#per exemple ens podem descarregar un excel del questionari santpau2020 per veure qui assistira a les sortides
def crearCSV(taula_a_descarregar):    
    #Creem el fitxer csv
    global pathdb 

    nom_fitxer=taula_a_descarregar+".csv"
    print (nom_fitxer)

    try:
        sqliteConnection = sqlite3.connect(pathdb,check_same_thread=False)
        cursor = sqliteConnection.cursor()
        print("DESCARREGAR CSV: Connected to SQLite")

        sqlite_select_query = """SELECT * from {}""".format(taula_a_descarregar)
        
        cursor.execute(sqlite_select_query)
        #with open("out.csv", "w", newline='') as csv_file:  # Python 3 version    
        with open(taula_a_descarregar+".csv", "w", newline='') as csv_file:  # Python 3 version 
        #with open("out.csv", "wb") as csv_file:              # Python 2 version
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([i[0] for i in cursor.description]) # write headers
            csv_writer.writerows(cursor)
            cursor.close()

    except sqlite3.Error as error:
        print("Failed to read single row from sqlite table", error)
        resultado=2

    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("SEARCH_NAME: The SQLite connection is closed")



# Descarreguem el fitxer CSV
def descarregarCSV(bot,update,taula_a_descarregar):
 
    chat_id=update.message.chat_id
    bot.sendDocument(chat_id, document=open(taula_a_descarregar+".csv",'rb'))



###############################################################
#OJO aixo esborra la Taula USERS, no un usuari concret
#def deleteTable():
#
#    global pathdb
#
#    try:
#        sqliteConnection = sqlite3.connect(pathdb,check_same_thread=False)
#        cursor = sqliteConnection.cursor()
#        print("Successfully Connected to SQLite")
#
#        sqlite_insert_query = """DROP TABLE SANTPAUTIMBALERS"""
#
#        cursor.execute(sqlite_insert_query)
#        sqliteConnection.commit()
#        print("Table USERS Deleted ")
#        cursor.close()
#
#    except sqlite3.Error as error:
#        print("Failed to delete table", error)
#    finally:
#        if (sqliteConnection):
#            sqliteConnection.close()
#            print("The SQLite connection is closed")


#connection.commit()


######################################################


######################################################
#Main del programa
if __name__ == '__main__':

    #connexioDB()
    #delUser()
    #readTable()
    #searchUser(349175213)

    updater = Updater(token=token)
    dispatcher = updater.dispatcher


    conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start),CommandHandler('cq', crearQuestionari, pass_args=True),CommandHandler('q', mostrarQ, pass_args=True),CommandHandler('alta', alta),CommandHandler('help', help),CommandHandler('dq', descarregartaula, pass_args=True),CommandHandler('vq', veure_questionaris_creats)],
    states={
        QUESTI: [CallbackQueryHandler(questi)],
        INSERT_DICC: [CallbackQueryHandler(insert_diccionari)],
        GUARDAR_RESPOSTES: [CallbackQueryHandler(guardar_respostes)],
        CREAR_PREG: [MessageHandler(Filters.text, crear_preguntes)],
        CREAR_RESP: [MessageHandler(Filters.text, crear_respostes)],
        CHECK_RESP: [MessageHandler(Filters.text, check_respostes)],
        REGISTRE_NOU: [MessageHandler(Filters.text, registreNouUser)],
        CHECK_PREGUNTES: [MessageHandler(Filters.text, check_preguntes)],
        BUTTON_ALTA: [CallbackQueryHandler(buttonAlta,pattern='OK|NOK')]
    },
    fallbacks=[CommandHandler('start', start),CommandHandler('cq', crearQuestionari, pass_args=True),CommandHandler('q', mostrarQ, pass_args=True),CommandHandler('alta', alta),CommandHandler('help', help),CommandHandler('dq', descarregartaula, pass_args=True),CommandHandler('vq', veure_questionaris_creats)]
    )

    dispatcher.add_handler(conv_handler)


    #Exemples de escoltadors de missatges per paraula (Filters.regex) o cualsevol paraula Filters.text
    #dispatcher.add_handler(MessageHandler(Filters.regex('Nom|nom'), registreNouUser))
    #dispatcher.add_handler(MessageHandler(Filters.text, echo))

updater.start_polling()
updater.idle()
######################################################
