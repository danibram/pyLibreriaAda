import tesseract
import cv2
import cv2.cv as cv
import os
import re #RegEx

## Carga de archivos
def get_image_array():
	folder = "albaranes2"
	# List files in "albaranes" folder
	ficheros = os.listdir(folder) 
	print ficheros
	imarray = []
	for col,indice in enumerate(ficheros):
		ruta = folder+"/"+ficheros[col]
		image1=cv2.imread(ruta)
		print "Cargando %s"%ruta
		height1,width1,channel1=image1.shape
		print image1.shape
		cvmat_image=cv.fromarray(image1)
		iplimage =cv.GetImage(cvmat_image)
		print iplimage
		imarray.append(iplimage)
	return imarray

api = tesseract.TessBaseAPI()
api.Init(".","tmp3",tesseract.OEM_DEFAULT)
#############################################################
#api.SetVariable("global_tessdata_manager_debug_level","True")		#Increase verbosity (Debug)
api.SetVariable("global_load_punc_dawg","False")					#Ignore punctuation patterns
#api.SetVariable("global_load_number_dawg","False")					#Ignore number patterns
api.SetVariable("language_model_penalty_non_freq_dict_word","0.2") 	#Penalty for words not in the frequent word dictionary(0.1 Default)
#api.SetVariable()
#api.SetVariable()
#api.SetVariable()
api.SetPageSegMode(tesseract.PSM_SINGLE_BLOCK)
"""
Opciones de SetPageSegMode
PSM_OSD_ONLY 				Orientation and script detection only.
PSM_AUTO_OSD 				Automatic page segmentation with orientation and script detection. (OSD)
PSM_AUTO_ONLY 				Automatic page segmentation, but no OSD, or OCR.
PSM_AUTO 					Fully automatic page segmentation, but no OSD.
PSM_SINGLE_COLUMN 			Assume a single column of text of variable sizes.
PSM_SINGLE_BLOCK_VERT_TEXT 	Assume a single uniform block of vertically aligned text.
PSM_SINGLE_BLOCK 			Assume a single uniform block of text. (Default.)
PSM_SINGLE_LINE 			Treat the image as a single text line.
PSM_SINGLE_WORD 			Treat the image as a single word.
PSM_CIRCLE_WORD 			Treat the image as a single word in a circle.
PSM_SINGLE_CHAR 			Treat the image as a single character.
PSM_COUNT 					Number of enum entries.
"""
arresc = [3,17,20]		#Se necesita para cada albaran, posicion de los escandallos

#Nombre, parametro hueco, formato tabla
arrcol  = [
	['v'			,0,  2],	#0
	['c'			,2,  3],	#1
	['nombre'		,0, 20],	#2
	['num'			,0,  8],	#3
	['iva'			,1,  8],	#4
	['req'			,1,  8],	#5
	['pvp'			,0,  8],	#6
	['s/iva'		,1,  8],	#7
	['desc'			,1,  8],	#8
	['neto'			,1,  8],	#9
	['num'			,2,  8],	#10
	['codigo'		,2, 10]]	#11

datos   = []			#Matriz revistas
dato    = []			#Lista auxiliar
arrescs = []			#Matriz escandallos

imarray = get_image_array()
#############################################################
##OCR
#############################################################

api = tesseract.TessBaseAPI()
api.Init(".","tmp3",tesseract.OEM_DEFAULT)
#############################################################
#api.SetVariable("global_tessdata_manager_debug_level","True")		#Increase verbosity (Debug)
api.SetVariable("global_load_punc_dawg","False")					#Ignore punctuation patterns
#api.SetVariable("global_load_number_dawg","False")					#Ignore number patterns
api.SetVariable("language_model_penalty_non_freq_dict_word","0.2") 	#Penalty for words not in the frequent word dictionary(0.1 Default)
#api.SetVariable()
#api.SetVariable()
#api.SetVariable()
api.SetPageSegMode(tesseract.PSM_SINGLE_BLOCK)

for col,iplimage in enumerate(imarray):

	#############################################################
	##OCR
	#############################################################

	tesseract.SetCvImage(iplimage,api)
	#api.SetImage(m_any,width,height,channel1)
	text=api.GetUTF8Text() # easy gg wp :D
	#conf=api.MeanTextConf()
	image=None
	api.Clear()


	#############################################################
	##Procesamiento de texto
	#############################################################


	text = text.replace('\n\n','\n') 	#Clean white lines
	text = text[:-1]					#Remove last char (\n) OCR returns
	text = text.replace('l','1') 		#Misses so often...
	text = text.upper()
	print text
	if col == 0:
		dato = map(int, text.split())
	elif col == 2:
		dato = text.split('\n')
		if len(dato) > 15
			print 'Problema '

	elif col == 3:
		text = text.replace(' ', '')
		dato = map(int, text.split('\n'))

	elif col > 3 and col < 10:
		text = text.replace(',', '.')
		text = text.replace(' ', '') 	#Espacios fuera
		dato = map(float, text.split('\n'))

	elif col= = 10:						#La ultima sub-tabla necesita un trato especial
		text = text.replace('O', '0')
		text = re.sub(r'[^\d\n ]','',text)
		text = text.replace(' 0 ',',')
		text = re.sub(' ?',	  '', text, flags=re.MULTILINE)
		temp = re.sub(',\w*', '', text, flags=re.MULTILINE)
		text = re.sub('\w*,', '', text, flags=re.MULTILINE)
		dato = text.split('\n')
		temp = temp.split('\n')
		temp = map(int, temp)
		#Conociendo el hueco
		dato = map(int, dato)

	else:
		dato = text.split('\n')
	dato.insert(0,arrcol[col][0])
	datos.append(dato)
	del text

#print "Cerramos tesseract, liberamos..."
#api.End() #Terminamos con el OCR
#del api

temp.insert(0,'codigo')
datos.append(temp)

for j, esc in enumerate(arresc):
	for i in range(len((datos))):
		if arrcol[i][1] == 1: datos[i].insert(esc, '')
		elif arrcol[i][1] == 2: 
			copia = datos[i][esc-2] if  i == 10 or i == 11 else ''
			datos[i].insert(esc-2, copia); datos[i].insert(esc-2, copia)
print '\n\n'
#Calculamos las sumas de datos
suma = {}


#Python es maravilloso, transponemos la tabla
datos = zip(*datos)

#Movemos los escandallos a arresc
for i,esc in enumerate(arresc):
	arrescs.append(datos.pop(esc-2-2*i))
	arrescs.append(datos.pop(esc-2-2*i))

#Imprimimos las matrices
print '..............\n# Revistas:'
for i,fila in enumerate(datos):
	print str(i).ljust(3),
	try:
		print ''.join(str(e).decode('utf-8').rjust(arrcol[j][2]) for j,e in enumerate(fila))
	except :
		print ''.join(str(e).rjust(arrcol[j][2]) for j,e in enumerate(fila))
		

print '..............\n# Escandallos:'
for i,fila in enumerate(arrescs):
	print str(i).ljust(3),
	try:
		print ''.join(str(e).decode('utf-8').rjust(arrcol[j][2]) for j,e in enumerate(fila))
	except :
		print ''.join(str(e).rjust(arrcol[j][2]) for j,e in enumerate(fila))

#raw_input("Press Enter to continue...")


"""
Cargamos lista de imagenes
Bucle de Procesamiento
	Segmentado
	(?)Busqueda de huecos en segmento
		Dividir imagen
		Calcular huecos
	o
		Buscar zona blanca
			Cuadrado de anchura ~= segmento

	Guardar imagen segmentos
	Array punteros

	Inicializacion OCR
	Bucle ocr en array de segmentos
		Ejecuta ocr sobre segmento
		Procesado salida ocr (regex, limpieza, etc)
			Segun segmento

		Si conocemos los huecos sera mas facil
		Comprobaciones






"""