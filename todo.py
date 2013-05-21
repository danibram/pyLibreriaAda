#!/usr/bin/env python2.7

import cv2.cv as cv
import cv2
import tesseract
import math
import numpy as np
import os
import glob
import sys
import re 			#regex
import csv 			
import datetime		


## DEBUG AND INFO
DEBUG = 0
DEBUG_CHILD = 0
DEBUG_ORDENACION = 0
DEBUG_CREACION_LISTA = 0

DEBUG_VENCIMIENTO = 0
DEBUG_ALBARAN = 0

DEBUG_COMPROBACIONES = 0
FAST_DEBUG = 1 #
INFO = 1
INFO_DATOS = 1

##
OK = 0

SAFE = 1 
EXPORTAR = 1


EXP_FOLDER = "csv" 
##


def cv2array(im):
	depth2dtype = {
		cv.IPL_DEPTH_8U: 'uint8',
		cv.IPL_DEPTH_8S: 'int8',
		cv.IPL_DEPTH_16U: 'uint16',
		cv.IPL_DEPTH_16S: 'int16',
		cv.IPL_DEPTH_32S: 'int32',
		cv.IPL_DEPTH_32F: 'float32',
		cv.IPL_DEPTH_64F: 'float64',
	}

	arrdtype=im.depth
	a = np.fromstring(
		 im.tostring(),
		 dtype=depth2dtype[im.depth],
		 count=im.width*im.height*im.nChannels)
	a.shape = (im.height,im.width,im.nChannels)
	return a

def array2cv(a):
	dtype2depth = {
		'uint8':   cv.IPL_DEPTH_8U,
		'int8':    cv.IPL_DEPTH_8S,
		'uint16':  cv.IPL_DEPTH_16U,
		'int16':   cv.IPL_DEPTH_16S,
		'int32':   cv.IPL_DEPTH_32S,
		'float32': cv.IPL_DEPTH_32F,
		'float64': cv.IPL_DEPTH_64F,
	}
	try:
		nChannels = a.shape[2]
	except:
		nChannels = 1
		cv_im = cv.CreateImageHeader((a.shape[1],a.shape[0]),
		dtype2depth[str(a.dtype)],
		nChannels)
	cv.SetData(cv_im, a.tostring(),
		a.dtype.itemsize*nChannels*a.shape[1])
	return cv_im
  ################################

# Function knows that one contour are inside other
def ischild_ofparent(x,y,w,h,cx,cy):
	xf=x+w
	yf=y+h
	if (x<cx<xf and y<cy<yf):
		return True
	return False
##############################################

def recognizeText(img):
	#api.SetVariable("tessedit_char_whitelist", "0123456789abcdefghijklmnopqrstuvwxyz")
	height,width,channel=img.shape
	#print img.shape
	#print img.dtype.itemsize
	#width_step = width*img.dtype.itemsize
	#print width_step
	#method 1 
	iplimage = cv.CreateImageHeader((width,height), cv.IPL_DEPTH_8U, channel)
	cv.SetData(iplimage, img.tostring(),img.dtype.itemsize * channel * (width))
	tesseract.SetCvImage(iplimage,api)
	text=api.GetUTF8Text()
	conf=api.MeanTextConf()
	img=None
	iplimage = None
	#print "..............."
	print "Revistas: "
	print text
	#print "Cofidence Level: %d %%"%conf
##############################################

##Modulos del programa
#Carga de Archivos
def load_files (folder):
	"""
	## Comprobacion de Sistema Operativo
	sistemaop = sys.platform
	if sistemaop=='darwin':
		backslash = '/'
		print 'Estas usando Mac'
		ficheros = glob.glob(folder + '/*.jpg')
		print 'listing ' + str(len(ficheros)) + ' files'

	elif sistemaop=='linux2':
		backslash = '/'
		print 'Estas en linux'
		ficheros = glob.glob(folder + '/*.jpg')
		print 'listing ' + str(len(ficheros)) + ' files'

	elif sistemaop=='win32' or sistemaop=='win64':
		backslash = '\'
		print 'Estas en Win'
		ficheros = glob.glob(folder + '\*.jpg')
		print 'listing ' + str(len(ficheros)) + ' files'

	else:
		print 'No estas ni en mac ni en win ni en linux(?)'
	"""
	ficheros = os.path.normpath(folder + '/*.jpg')
	ficheros = glob.glob(ficheros)
	print 'listing ' + str(len(ficheros)) + ' files'
	return ficheros


####################################


#Preprocesing for parents
def preprocesing_parents (img):

	##Procesado
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	#thresholg for OCR
	ret2,thresh2 = cv2.threshold(gray,100,255,1)
	#threshold for detection contour
	ret,thresh = cv2.threshold(gray,100,255,1)
	#Create an erode element for operatio
	
	erosion_x = 1
	erosion_y = 1
	erosion_size_x = 6
	erosion_size_y = 6
	erosion_type = cv2.MORPH_ELLIPSE
	element = cv2.getStructuringElement(erosion_type,
	( erosion_size_x + erosion_x, erosion_size_y + erosion_y ),
	( erosion_x, erosion_y ) 
	)
	# Remove some small noise if any.
	dilate = cv2.dilate(thresh,element)
	erosion_x = 1
	erosion_y = 1
	erosion_size_x = 2
	erosion_size_y = 2
	erosion_type = cv2.MORPH_CROSS
	element = cv2.getStructuringElement(erosion_type,
	( erosion_size_x + erosion_x, erosion_size_y + erosion_y ),
	( erosion_x, erosion_y ) 
	)
	erode = cv2.erode(dilate,element)
	erode = cv2.Canny(erode, 200, 250)
	#cv2.imshow('canny',erode)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()
	return erode
###############################################

#Preprocesing for childs
def preprocesing_childs (img):

	##Procesado
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	#thresholg for OCR
	ret2,thresh2 = cv2.threshold(gray,100,255,1)
	#threshold for detection contour
	ret,thresh = cv2.threshold(gray,100,255,1)
	#Create an erode element for operatio
	
	erosion_x = 1
	erosion_y = 1
	erosion_size_x = 6
	erosion_size_y = 6
	erosion_type = cv2.MORPH_ELLIPSE
	element = cv2.getStructuringElement(erosion_type,
	( erosion_size_x + erosion_x, erosion_size_y + erosion_y ),
	( erosion_x, erosion_y ) 
	)
	# Remove some small noise if any.
	dilate = cv2.dilate(thresh,element)
	#cv2.imshow('canny',erode)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()
	return dilate
###############################################

#Calcula si es un albaran de reposicion
def reposicion (img):

	height,width,channel=img.shape
	crop = img[0:100,0:width]

	gray = cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY)
	ret2,thresh2 = cv2.threshold(gray,100,255,1)
	pix_zero = cv2.countNonZero(thresh2)
	#print pix_zero
	if (pix_zero > 7000):
		return True
	#crop = cv2.resize(crop,dsize=(1200,400),interpolation=cv.CV_INTER_LINEAR)
	#cv2.imshow('img',crop)
	#cv2.waitKey(500)""
	return False
###############################################
def calc_parents (contours,hierarchy,img):
	parents = []
	hierarchy = hierarchy[0] # get the actual inner list of hierarchy descriptions
	# For each contour, find the bounding rectangle and draw it
	i = 0
	if (DEBUG):
		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		mask = np.zeros(gray.shape,np.uint8)
	for component in zip(contours, hierarchy):
		currentContour = component[0]
		currentHierarchy = component[1]
		x,y,w,h = cv2.boundingRect(currentContour)
		if currentHierarchy[3] < 0 and cv2.contourArea(currentContour)>9000:
			if (DEBUG):
				cv2.drawContours(mask,[currentContour],0,200,-1)
			parents.append(i)
		i = i+1
	if (DEBUG):
		res = cv2.bitwise_and(img,img,mask=mask)
		dst = cv2.resize(res,dsize=(1200,1000),interpolation=cv.CV_INTER_LINEAR)
		cv2.imshow('parents',dst)
		cv2.waitKey(0)
		cv2.destroyAllWindows()
	return parents
###############################################
def ordenacion(childs,contour_ord):
	distancesx = []
	distancesy = []
	#saco las distancias x e y a un vector
	if (DEBUG_ORDENACION):
		print childs
	for i,child in enumerate(childs):
		x,y,w,h = cv2.boundingRect(contour_ord[child])
		distancesx.append(x)
		distancesy.append(y)
	if (DEBUG_ORDENACION):
		print 'distances x y'
		print distancesx
		print distancesy
		print 'ordenacion'
	#algoritmo burbuja para ordenar
	for pasada in range(0, len(childs)-1): 
		for i in range(0,len(childs)-1): 
			if ((distancesy[i] + 10) > distancesy[i+1] > (distancesy[i] - 10)):
				if  distancesx[i+1] < distancesx[i]:
					childs[i], childs[i+1] = childs[i+1], childs[i]
					distancesx[i], distancesx[i+1] = distancesx[i+1], distancesx[i]
					distancesy[i], distancesy[i+1] = distancesy[i+1], distancesy[i]
					if (DEBUG_ORDENACION):
						print 'intercambio fijo y var x' + str(i)
						print childs
			elif (distancesy[i] > distancesy[i+1]):
				if  distancesy[i+1] < distancesy[i]:
					childs[i], childs[i+1] = childs[i+1], childs[i]
					distancesx[i], distancesx[i+1] = distancesx[i+1], distancesx[i]
					distancesy[i], distancesy[i+1] = distancesy[i+1], distancesy[i]
					if (DEBUG_ORDENACION):
						print 'intercambio x variable y' + str(i)
						print childs
			elif ((distancesx[i] + 10) > distancesx[i+1] > (distancesx[i] - 10)):
				if  distancesy[i+1] < distancesy[i]:
					childs[i], childs[i+1] = childs[i+1], childs[i]
					distancesx[i], distancesx[i+1] = distancesx[i+1], distancesx[i]
					distancesy[i], distancesy[i+1] = distancesy[i+1], distancesy[i]
					if (DEBUG_ORDENACION):
						print 'intercambio fijo x variable y' + str(i)
						print childs
	return childs
#################################################
def calc_child2 (parents):
	childs_ids = []
	image_childs = []
	contours_childs = []
	for jj,parent in enumerate(parents):
		##Crop image
		#Gray
		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		#Create Mask
		mask = np.zeros(gray.shape,np.uint8)
		#Do Masking
		cv2.drawContours(mask,[contours[parent]],0,200,-1)
		#Preprocesing 
		img2 = preprocesing_childs(img)
		#Canny filter
		img2 = cv2.Canny(img2, 80, 120)
		#Apply the mask
		res2 = cv2.bitwise_and(img2,img2,mask=mask)
		#Dilatation for improve de results
		erosion_x = 1
		erosion_y = 1
		erosion_size_x = 3
		erosion_size_y = 3
		erosion_type = cv2.MORPH_ELLIPSE
		element = cv2.getStructuringElement(erosion_type,
		( erosion_size_x + erosion_x, erosion_size_y + erosion_y ),
		( erosion_x, erosion_y ) 
		)
		res2 = cv2.dilate(res2,element)
		#Transform to color img
		res3 = cv2.cvtColor(res2,cv2.COLOR_GRAY2BGR)
		#Find the child Blocks in the parent contour
		contours3,hierarchy3 = cv2.findContours(res2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		
		childs = []
		hierarchy3 = hierarchy3[0] # get the actual inner list of hierarchy descriptions
		# For each contour, find the bounding rectangle and draw it
		i = 0
		if (DEBUG_CHILD):
			mask = np.zeros(gray.shape,np.uint8)
		for component in zip(contours3, hierarchy3):
			currentContour = component[0]
			currentHierarchy = component[1]
			x,y,w,h = cv2.boundingRect(currentContour)
			if currentHierarchy[3] < 0 and cv2.contourArea(currentContour)>3000:
				childs.append(i)
				if (DEBUG_CHILD):
					cv2.drawContours(mask,[currentContour],0,200,-1)
					res = cv2.bitwise_and(img,img,mask=mask)
					dst = cv2.resize(res,dsize=(1200,1000),interpolation=cv.CV_INTER_LINEAR)
					cv2.imshow('parents',dst)
					cv2.waitKey(0)
					cv2.destroyAllWindows()
			i = i+1
		#Recojo parents del bucle y los ordeno
		childs = ordenacion(childs,contours3)
		"""
		for i,child in enumerate(childs):
			mask = np.zeros(gray.shape,np.uint8)
			cv2.drawContours(mask,[contours3[child]],0,200,-1)
			res = cv2.bitwise_and(img,img,mask=mask)
			dst = cv2.resize(res,dsize=(1200,1000),interpolation=cv.CV_INTER_LINEAR)
			cv2.imshow('parents',dst)
			cv2.waitKey(0)
			cv2.destroyAllWindows()
		"""	
		childs_ids.append(childs)
		contours_childs.append(contours3)
	return childs_ids,contours_childs
###############################################
#Preprocesing for parents
def preprocesing_ocr (img2):

	##Procesado
	#gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
	#thresholg for OCR
	ret,threshh = cv2.threshold(img2,100,255,1)
	#Create an erode element for operatio
	
	erosion_x = 1
	erosion_y = 1
	erosion_size_x = 2
	erosion_size_y = 2

	erosion_type = cv2.MORPH_ELLIPSE
	element = cv2.getStructuringElement(erosion_type,
	( erosion_size_x + erosion_x, erosion_size_y + erosion_y ),
	( erosion_x, erosion_y ) 
	)
	# Remove some small noise if any.
	dilate = cv2.dilate(threshh,element)
	erosion_x = 1
	erosion_y = 1
	erosion_size_x = 1
	erosion_size_y = 1
	erosion_type = cv2.MORPH_ELLIPSE
	element = cv2.getStructuringElement(erosion_type,
	( erosion_size_x + erosion_x, erosion_size_y + erosion_y ),
	( erosion_x, erosion_y ) 
	)
	erode = cv2.erode(dilate,element)
	ret,erode = cv2.threshold(erode,0,255,1)
	erode = cv2.blur(erode,(2,2))
	#cv2.imshow('canny',erode)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()
	return erode
###############################################
def recortar(matimg, contorno, offset = [20,10,35,15], DSP = 1, ):
	x,y,w,h = cv2.boundingRect(contorno)
	x += offset[0]; y += offset[1]; w -= offset[2]; h -= offset[3]	#Aplicamos el offset
	res = matimg[y:y+h,x:x+w]											#Recortamos con dicho offset
	if DSP:
		res = preprocesing_ocr(res)
	iplbitmap = []
	iplbitmap.append(cv.CreateImageHeader((res.shape[1], res.shape[0]), cv.IPL_DEPTH_8U, 3))
	cv.SetData(iplbitmap[0], res.tostring(), res.dtype.itemsize * 3 * res.shape[1])
	iplbitmap.append(res)
	return iplbitmap
###############################################
def guardar_csv(tabla, nombre):
	nombre_norm = os.path.normpath(nombre)
	fichero = open(nombre_norm, 'wb')
	writer = csv.writer(fichero, delimiter = ';', skipinitialspace = True)
	writer.writerows(tabla)
	fichero.close()
###############################################
def safe_float(mystr):
	if mystr == '':
		return 0.0
	else:
		return float(mystr)
def safe_int(mystr):
	if mystr == '':
		return 0
	else:
		return int(mystr)
###############################################
###############################################
###############################################


## Carga de archivos
ficheros = load_files('albaranes')


# Open one file
"""
#Inicializamos la api		
api = tesseract.TessBaseAPI()
api.Init(".","spa",tesseract.OEM_DEFAULT)
api.SetPageSegMode(tesseract.PSM_SINGLE_COLUMN)
##########################################
"""

api = tesseract.TessBaseAPI()
api.Init(".","spa",tesseract.OEM_DEFAULT)
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


arrcol  = [
	['albaran'		,0,	 8],
	['v'			,0,  2],	#0
	['c'			,2,  4],	#1
	['nombre'		,0, 16],	#2
	['num'			,0,  8],	#3
	['iva'			,1,  8],	#4
	['req'			,1,  8],	#5
	['pvp'			,0,  8],	#6
	['s/iva'		,1,  8],	#7
	['desc'			,1,  8],	#8
	['neto'			,1,  8],	#9
	['num'			,2,  8],	#10
	['codigo'		,2, 10]]	#11


if (EXPORTAR):
	tabla_revistas = []
	tabla_escandallos = []
	tabla_albaranes = []
	tabla_vencimientos = []
	ahora = datetime.datetime.now()
	##Check if EXP_FOLDER exists
	if not os.path.exists(EXP_FOLDER):
		print "No existe el directorio " + EXP_FOLDER + ". Creado."
		os.makedirs(EXP_FOLDER)
	else:
		print "El script exportara los csv en el directorio " + EXP_FOLDER

if (OK):
	aimprimir = "Procesando... \n[" + '.'*(len(ficheros)+1) + ']' + '\b' * (len(ficheros)+1)
	sys.stdout.write(aimprimir)
	sys.stdout.flush()



###############################################
###############################################
###############################################
for i,fichero in enumerate(ficheros):
###############################################
###############################################
###############################################

	flag_error_cantidad = 0
	error_c_essolucionable = 0
	flag_error_ven_revistas = 0
	flag_error_ven_importe = 0

	if (FAST_DEBUG and not (i % 2)):
		continue

	if (OK):
		flag_error_OK = 0 		#Always 0
	#fichero = ficheros[3]
	if (INFO):
		print 'Analizando ' + fichero + ' (' + str(i+1) + '/' + str(len(ficheros)) + ')'

	img = cv2.imread(fichero)
	img_ocr = preprocesing_ocr(img)
	if reposicion(img):
		if (OK):
			print '\bo',
			sys.stdout.flush()
		if (INFO):
			print "Es albaran de reposicion"
		continue

	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	height,width,channel=img.shape
	rows,cols,channel=img.shape

	

	##Preprocesing
	pre_image = preprocesing_parents(img)
	##Find Contours
	contours,hierarchy = cv2.findContours(pre_image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	#Calculo de los bloques padres
	parents = calc_parents(contours,hierarchy,img)
	parents = ordenacion(parents,contours)

	if (INFO):
		if len(parents) == 4:
			tipo = 'Albaran normal'
		elif len(parents) == 5:
			tipo = 'Albaran con informacion'
		else:
			tipo = 'Desconocido'
		print ' - Parents have ' + str(len(parents)) +' ( '+ tipo +' ) '
		#print parents
	#Calculo de los Bloques hijos
	childs_ids,contours_child = calc_child2(parents)
	if (INFO):
		print ' - Estructura ',
		for i in range(0, len(childs_ids)):
			print '   ' + str(len(childs_ids[i])),
		print ''

	###############################################################
	# Recorte de la tabla de revistas

	
	images_revistas = []
	cuadro_derecha = childs_ids[2]
	contour_derecha = contours_child[2]
	cuadro_revistas = childs_ids[3]
	contour_revistas = contours_child[3]

	if (SAFE and len(cuadro_revistas) < 21):
		if (OK):
			print '\b\bE',
			sys.stdout.flush()
		continue

	for i in range(0,11):
		if i == 10:
			images_revistas.append(recortar(img, contour_derecha[cuadro_derecha[2]])[0])
		else:
				images_revistas.append(recortar(img, contour_revistas[cuadro_revistas[10 + i]])[0])

	############################################
	# Albaran

	images_albaranes = []
	cuadro_albaran = childs_ids[1]
	contour_albaran = contours_child[1]

	for i in range(0,7):
		images_albaranes.append(recortar(img, contour_albaran[cuadro_albaran[i]])[0])

	datos_albaran = []
	for i, iplimage in enumerate(images_albaranes):
		tesseract.SetCvImage(iplimage, api)
		text = api.GetUTF8Text()
		text = text.replace('\n', '')
		text = re.sub('[^\d]', '', text)
		#text = text.replace(' ', '')
		#text = re.sub('(?<=\d) *', '', text)
		datos_albaran.append(text)
	numero_albaran = datos_albaran[2]

	if (DEBUG_ALBARAN):
		print datos_albaran
	del images_albaranes


	############################################
	# Vencimiento

	contour_vencimiento = contour_revistas[cuadro_revistas[20]]
	iplimage = recortar(img, contour_vencimiento, offset = [300,50,315,70])
	"""
	cv2.imshow('asd',iplimage[1])
	cv2.waitKey(0)
	cv2.destroyWindow('asd')
	"""
	datos_vencimiento = []
	tesseract.SetCvImage(iplimage[0], api)
	text = api.GetUTF8Text()
	text = text[:-2]
	text = text.replace('\n\n', '\n')
	text = re.sub('[^\d\n ,/]', '', text)
	text = text.replace(',', '.')
	text = text.replace('  ', ' ')


	if (DEBUG_VENCIMIENTO):
		print 'Cuadro vencimiento:'
		print text
	datos_vencimiento = text.split('\n')
	total_importe  = float(re.sub('[^\d.]', '', datos_vencimiento.pop()))
	total_revistas = int(re.sub('[^\d.]', '',  datos_vencimiento[0]))
	del datos_vencimiento[0]
	suma_revistas = 0
	suma_importe = 0
	aux = []
	if (DEBUG_VENCIMIENTO):
		print '....'
		print datos_vencimiento
	aux_array = []
	aux2_array = []
	for elem in datos_vencimiento:
		aux_array = elem.split(' ')
		aux = aux_array[0].split('/')
		aux_array[0] = aux[0]
		aux_array.insert(1,aux[1])
		suma_revistas += int(aux_array[1])
		suma_importe  += float(aux_array[4])
		aux2_array.append(aux_array)
	datos_vencimiento = aux2_array
	if (DEBUG_VENCIMIENTO):
		print '....'
		print datos_vencimiento
		print '......'



	
	if str(total_importe)  != str(suma_importe):
		flag_error_ven_importe = 1
		if (DEBUG_VENCIMIENTO):	
			print 'Aviso: Importe albaran (' + str(total_importe) + ' vs ' + str(suma_importe) + ')'
	if str(total_revistas) != str(suma_revistas):
		flag_error_ven_revistas = 1
		if (DEBUG_VENCIMIENTO):	
			print 'Aviso: Suma revistas albaran (' + str(total_revistas) + ' vs ' + str(suma_revistas) + ')'

	datos   = []			#Matriz revistas
	dato    = []			#Lista auxiliar
	arrescs = []			#Matriz escandallos
	arresc  = []		#Lista para las posiciones de escandallos

	tesseract.SetCvImage(images_revistas[1],api)
	#api.SetImage(m_any,width,height,channel1)
	text=api.GetUTF8Text() # easy gg wp :D
	#conf=api.MeanTextConf()
	api.Clear()
	text = text.replace('\n\n','\n') 	#Clean white lines
	text = text[:-1]					#Remove last char (\n) OCR returns
	text = text.replace('l','1') 		#Misses so often...
	text = text.replace('o', '0')
	text = text.replace('O', '0')
	#text = re.sub(r'[^\d\n ]','',text)	#Quitamos caracteres chungos

	dato = text.split('\n')
	oldflag = flag = 0
	if (DEBUG_CREACION_LISTA):
		print 'Lista de cantidades: '
		print dato
	if dato:
		cantidad_errores = 0
		for i,e in enumerate(dato):
			if e.isdigit():
				flag = 0
				if (flag != oldflag):
					#print 'Bingo! en ' + str(i) + ' , ' + e
					arresc.append(i+1)					
			elif ('*' in e or len(e) > 2):
				flag = 1
			else:
				dato[i] = 0
				flag_error_cantidad = 1
				cantidad_errores += 1
				if (OK):
					flag_error_OK = 1
				elif (INFO_DATOS):
					print ' - Error en ' + str(i)+ ': ' + str(e)
			oldflag = flag
	numero_filas = len(dato)

	if cantidad_errores == 1:
		error_c_essolucionable = 1

	if (DEBUG_CREACION_LISTA):
		print 'Lista de posiciones de escandallo: ',
		print arresc

	for esc in reversed(arresc):
		del dato[esc-3:esc-1]

	dato_cantidad = map(int, dato)
	dato_cantidad.insert(0,arrcol[2][0])

	for col,iplimage in enumerate(images_revistas):
		if col == 1:
			continue
		#############################################################
		##OCR
		#############################################################

		tesseract.SetCvImage(iplimage,api)
		#api.SetImage(m_any,width,height,channel1)
		text=api.GetUTF8Text() # easy gg wp :D
		#conf=api.MeanTextConf()
		iplimage=None
		api.Clear()

		#############################################################
		##Procesamiento de texto
		#############################################################
			
		#print 'OCR:',
		#print ' ( ' + fichero + ' ) ' + '( Imagen ' + str(col) + ' ) '

		text = text.replace('\n\n','\n') 	#Clean white lines
		text = text[:-1]					#Remove last char (\n) OCR returns
		text = text.replace('l','1') 		#Misses so often...
		text = text.upper()
		#print text
		

		if col == 0:
			text = re.sub('[^123\n]', '', text)
			dato = text.split('\n') 
			#dato = map(int, text.split())

		elif col == 2:
			text = re.sub('(?<=[A-Z])1', 'I', text)
			dato = text.split('\n')

		elif col > 2 and col < 10:
			text = text.replace(',', '.')
			text = re.sub('[^\d\n\.]', '', text)
			dato = text.split ('\n')
			#dato = map(float, text.split('\n'))

		elif col==10:						#La ultima sub-tabla necesita un trato especial
			text = text.replace('O', '0')
			text = re.sub('[^\d\n ]','',text)
			text = text.replace(' 0 ',',')
			text = re.sub(' ?',	  '', text, flags=re.MULTILINE)
			temp = re.sub(',\w*', '', text, flags=re.MULTILINE)
			text = re.sub('\w*,', '', text, flags=re.MULTILINE)
			dato = text.split('\n')
			temp = temp.split('\n')
			#temp = map(int, temp)
			#Conociendo el hueco
			#dato = map(int, dato)

		else:
			dato = text.split('\n')

		for e in  range(numero_filas - len(dato)):
			dato.append(0)

		if (DEBUG_CREACION_LISTA):
			print dato
		dato.insert(0,arrcol[col+1][0])
		datos.append(dato)
		del text

	del images_revistas
	temp.insert(0,'codigo')
	datos.insert(1,dato_cantidad)
	datos.append(temp)

	for j, esc in enumerate(arresc):
		for i in range(len((datos))):
			if arrcol[i+1][1] == 1: datos[i].insert(esc, '')
			elif arrcol[i+1][1] == 2: 
				copia = datos[i][esc-2] if  i == 10 or i == 11 else ''
				datos[i].insert(esc-2, copia); datos[i].insert(esc-2, copia)
	
	#Anadimos el numero de alb
	datos.insert(0, ['albaran'] + [numero_albaran]*len(datos[0]))

	# COMPROBACIONES
	aux3 = 0
	aux2 = 0
	if (DEBUG_COMPROBACIONES):
		print len(datos[2]),
		print datos[2]
		print len(datos[10])
		print datos[10	]
	for i,elem in enumerate(datos[2][1:]):
			aux2 += safe_int(elem)
			aux3 += safe_float(datos[10][i+1])
	suma_local_revistas = aux2
	suma_local_importe  = aux3
	suma_local_referencias = len(datos[0])-1

	if flag_error_cantidad:
		if (INFO):
			print "Error: Cantidad",
		if error_c_essolucionable and not flag_error_ven_revistas:
			for i,elem in enumerate(aux):
				if datos[2][i+1] == 0:
					datos[2][i+1] = total_revistas - suma_local_revistas
			if (INFO):
				print " (Solucionado)"
		else:
			if (INFO):
				print ""
	if flag_error_ven_revistas:
		if (INFO):
			print "Error: Suma cantidades",
		if not flag_error_cantidad:
			if str(suma_revistas) == int(suma_local_revistas):
				total_revistas = suma_local_revistas
			else:
				suma_revistas = suma_local_revistas
			if (INFO):
				print " (Solucionado)"
		else:
			if (INFO):
				print ""
		if (INFO):
			print "Error: Cuadro de vencimiento, revistas"
	if flag_error_ven_importe:

		if (INFO):
			print "Error: Cuadro de vencimiento, importe"

	else:
		if str(total_importe) != str(suma_local_importe):
			if (INFO):
				print "Error: Total albaran (" + str(total_importe) + ' vs ' + str(suma_local_importe) + ')'
	#suma_local_revistas = sum(datos)


	#Python es maravilloso, transponemos la tabla
	datos = zip(*datos)

	#Movemos los escandallos a arresc
	for i,esc in enumerate(arresc):
		arrescs.append(datos.pop(esc-2-2*i))
		arrescs.append(datos.pop(esc-2-2*i))

	if (INFO_DATOS):
		print '..............\nAlbaran ' + datos_albaran[2] + ' del ' + datos_albaran[0] + '. ' + str(suma_local_revistas) + ' revistas: ' + str(suma_local_importe) + ' euros.'
		#Imprimimos las matrices
		print '..............\n# Revistas:'
		for i,fila in enumerate(datos):
			print str(i).ljust(3),
			try:
				print ''.join(str(e).decode('utf-8').rjust(arrcol[j][2]) for j,e in enumerate(fila))
			except :
				print ''.join(str(e).rjust(arrcol[j][2]) for j,e in enumerate(fila))
				
		if arrescs:
			print '\n..............\n# Escandallos:'
			for i,fila in enumerate(arrescs):
				print str(i).ljust(3),
				try:
					print ''.join(str(e).decode('utf-8').rjust(arrcol[j][2]) for j,e in enumerate(fila))
				except :
					print ''.join(str(e).rjust(arrcol[j][2]) for j,e in enumerate(fila))
		print '..........................................................'
	if (EXPORTAR):
		#Escribimos todo en las tablas
		datos_albaran.append(total_revistas)
		datos_albaran.append(total_importe)
		for elem in datos_vencimiento: #Anadimos la fecha
			datos_albaran.append(elem[3])
			elem.insert(0, numero_albaran)
		tabla_vencimientos.extend(datos_vencimiento)
		tabla_albaranes.append(datos_albaran)
		tabla_revistas.extend(datos[1:])
		if arrescs:
			tabla_escandallos.extend(arrescs)

	if (OK and flag_error_OK):
		print '\b*',
		sys.stdout.flush()
	elif (OK):
		print '\bx',
		sys.stdout.flush()

	#for i,child in enumerate(childs):
	#print childs
	#contours_met1(parents)

	#dst = cv2.resize(contours,dsize=(1600,2000),interpolation=cv.CV_INTER_LINEAR)
	#cv2.imshow('img',dst)
	#cv2.waitKey(0)
	#cv2.destroyAllWindows()

###############################################
###############################################
###############################################
###############################################
###############################################
###############################################
api.End()
del api

if (EXPORTAR):
	if (INFO):
		print '.............'
		print 'Guardando :)'
	n_csvalb = EXP_FOLDER + '/alb' + ahora.strftime("%y-%m-%d_%H-%M") + '.csv'
	n_csvrev = EXP_FOLDER + '/rev' + ahora.strftime("%y-%m-%d_%H-%M") + '.csv'
	n_csvesc = EXP_FOLDER + '/esc' + ahora.strftime("%y-%m-%d_%H-%M") + '.csv'
	n_csvven = EXP_FOLDER + '/ven' + ahora.strftime("%y-%m-%d_%H-%M") + '.csv'
	guardar_csv(tabla_albaranes, n_csvalb)
	guardar_csv(tabla_revistas, n_csvrev)
	guardar_csv(tabla_escandallos, n_csvesc)
	guardar_csv(tabla_vencimientos, n_csvven)
	"""
	hojacsv.close
	"""
if (OK):
	print '\b]  Echo!'
raw_input("Presiona cualquier tecla para salir")
##Codigo OCR



		#Se necesita para cada albaran, posicion de los escandallos
