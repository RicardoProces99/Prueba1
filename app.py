import os
from flask import Flask, render_template, request, send_from_directory,url_for, session, redirect
import cv2
import shutil
import numpy as np


app = Flask(__name__)
# Aqui se guarda todo lo de la app
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


app.config['UPLOAD_FOLDER'] = os.path.join(APP_ROOT, 'images')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route("/")
def index():
    session.clear()
    return render_template("upload.html")

@app.route('/images/<filename>')
def uploadfile(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route('/home')
def home():
    return render_template("completed.html", imgSrc="images/" + session.get('imgSrc') , message=session.get('message'))

@app.route("/upload" , methods = ['POST'])
def upload():
    # Se suben las imagenes a una carpeta "images" dentro de la app root.
    target = os.path.join(APP_ROOT, 'images')

    if request.method == 'POST':

        if not os.path.isdir(target):
            os.mkdir(target)

        for file in request.files.getlist("file"):
            filename = file.filename

            destination = "/".join((target, filename))

            file.save(destination)

            filename = destination

            org = open(filename, 'rb')

            base = os.path.basename(filename)

            dir = os.path.dirname(filename)

            filename_cp = os.path.splitext(base)[0]

            filename_cp = "cp_"+filename_cp+os.path.splitext(base)[1]

            destination2 = dir+"/"+filename_cp
            file.save(destination2)

            cpy = open (destination2, 'wb')
            shutil.copyfileobj(org, cpy)

            session['image'] = filename
            session['filename'] = filename
            session['imgSrc'] = os.path.basename(destination)
            session['cimgsrc'] = os.path.basename(destination2)
            session['cpimg'] = destination2

            print("session", session)

    return render_template("completed.html",imgSrc="images/"+session.get('imgSrc'))

# En completed es imgp/nr
@app.route("/imgp/nr", methods=['post'])
def nr():
    print(session)

    img = cv2.imread(session.get('cpimg'), 0)
    #threshold = 40
    #Procesamiento
    filas=img.shape[0]
    columnas=img.shape[1]
    salida=np.zeros((filas,columnas))
    # print(filas)
    # print(columnas)
    # print('display')

    #DILATACION DUAL AL MAXIMO
    for i in range (1,filas-1,1):
        for j in range (1,columnas-1,1):
            ventana=img[i-1:i+2,j-1:j+2]  #crea la ventana 3x3
            salida[i,j]=np.max(ventana) # si no se incluye el ",axis", devuelve el maximo de los maximos
    # # plt.figure(1)
    # # plt.imshow(salida, cmap='gray')
    img=salida-img
    # # plt.figure(2)
    # # plt.imshow(bordes, cmap='gray')  
	#cv2.imwrite(filename,bordes)
    
    #threshold = float(request.form['slider'])
    #cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY, img)
    print (session['cpimg'])
    cv2.imwrite(session.get('cpimg'),img)
    session['message'] = "Procesamiento 1 listo!"
    session['imgSrc'] = os.path.basename(session['cpimg'])
    return redirect(url_for('home', op='nr'))


@app.route("/imgp/nr2", methods=['post'])
def proc2():
    print(session)

    img = cv2.imread(session.get('cpimg'), 0)
    #threshold = 40
    #Procesamiento
    filas=img.shape[0]
    columnas=img.shape[1]
    # print(filas)
    # print(columnas)
    # print('display')
    salida2=np.zeros((filas,columnas))

    #EROSIÓN DUAL AL MINIMO
    for i in range (1,filas-1,1):
        for j in range (1,columnas-1,1):
            ventana=img[i-1:i+2,j-1:j+2]  #crea la ventana 3x3
            salida2[i,j]=np.min(ventana) 

    # plt.figure(3)
    # plt.imshow(salida2, cmap='gray')
    #img=img-salida2
    img = salida2
    # plt.figure(4)
    # plt.imshow(bordes2, cmap='gray') 
	#cv2.imwrite(filename,bordes)
    
    #threshold = float(request.form['slider'])
    #cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY, img)
    print (session['cpimg'])
    cv2.imwrite(session.get('cpimg'),img)
    session['message'] = "Procesamiento 2 listo!"
    session['imgSrc'] = os.path.basename(session['cpimg'])
    return redirect(url_for('home', op='nr2'))

if __name__ =="__main__":
    app.secret_key = "abcdefghijklmnopqrstuvwxyz"
    app.run(port = 4555, debug = True)