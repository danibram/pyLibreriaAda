import cv2
import numpy as np
import sys
import os.path

if(len(sys.argv) != 3):
	print "%s input_file output_file" % (sys.argv[0])
	sys.exit()
else:
	input_file = sys.argv[1]
	output_file = sys.argv[2]

if(not os.path.isfile(input_file)):
	print "No such file '%s'" % (input_file)
	sys.exit()

DEBUGGING = 1

# Determine pixel intensity
# Apparently human eyes register colors differently.
# TVs use this formula to determine
# pixel intensity = 0.30R + 0.59G + 0.11B 
def I(x,y):
	global img, img_y, img_x
	if(y >= img_y or x >= img_x):
		#print "pixel out of bounds ("+str(y)+","+str(x)+")"
		return 0
	pixel = img[y][x]
	return 0.30 * pixel[2] + 0.59 * pixel[1]  + 0.11 * pixel[0]

# A quick test to check whether the contour is
# a connected shape
def connected(cnt):
	first = cnt[0][0]
	last = cnt[len(cnt)-1][0]
	return abs(first[0] - last[0]) <= 1 and abs(first[1] - last[1]) <= 1

# Helper function to return a given contour
def c(idx):
	global contours
	return contours[idx]

# Count the number of real children
def count_children (idx, h, cnt):
	# No children
	if(h[idx][2] < 0):
		return 0
	else:
		#If the first child is a countor we care about
		# then count it, otherwise don't
		if(keep(c(h[idx][2]))):
			count = 1
		else:
			count = 0 

		# Also count all of the child's siblings and their children
		count += count_siblings(h[idx][2], h, cnt, True)
		return count 

# Quick check to test if the contour is a child
def is_child (idx, h, cnt):
	return get_parent(idx,h, cnt) > 0 

# Get the first parent of the contour that we care about
def get_parent (idx, h, cnt):
	parent = h[idx][3]
	while(not keep(c(parent)) and parent > 0):
		parent = h[parent][3]

	return parent 

# Count the number of relevant siblings of a contour
def count_siblings (idx, h, cnt, inc_children = False):
	# Include the children if neccessary
	if(inc_children):
		count = count_children(idx,h,cnt) 
	else:
		count = 0

	# Look behind
	p = h[idx][0] 
	while(p > 0):
		if(keep(c(p))):
			count+=1
		if(inc_children):
			count += count_children(p,h, cnt)
		p = h[p][0]

	# Look ahead
	n = h[idx][1]
	while(n > 0):
		if(keep(c(n))):
			count+=1
		if(inc_children):
			count += count_children(p,h,cnt)
		n = h[n][1]
	return count 

# Whether we care about this contour
def keep(cnt):
	return keep_box(cnt) and connected(cnt)

# Whether we should keep the containing box of this
# contour based on it's shape
def keep_box(cnt):
	x,y,w,h = cv2.boundingRect(cnt)

	# width and height need to be floats
	w *= 1.0
	h *= 1.0
	
	# Test it's shape - if it's too oblong or tall it's
	# probably not a real character
	if(w/h < 0.1 or w/h > 10):
		if(DEBUGGING):
			print "\t Rejected because of shape: ("+str(x)+","+str(y)+","+str(w)+","+str(h)+")" + str(w/h)
		return False

	# Test whether the box is too wide 
	if(w > img_x/5):
		if(DEBUGGING):
			print "\t Rejected because of width: " + str(w)
		return False

	# Test whether the box is too tall 
	if(h > img_y/5):
		if(DEBUGGING):
			print "\t Rejected because of height: " + str(h)
		return False

	return True


def include_box(idx,h,cnt):
	if(DEBUGGING):
		print str(idx)+":"
		if(is_child(idx,h,cnt)):
			print "\tIs a child"
			print "\tparent "+str(get_parent(idx,h,cnt))+" has " + str(count_children(get_parent(idx,h,cnt),h,cnt)) + " children"
			print "\thas " + str(count_children(idx,h,cnt)) + " children"

	if(is_child(idx,h,cnt) and count_children(get_parent(idx,h,cnt),h,cnt) <= 2):
		if(DEBUGGING):
			print "\t skipping: is an interior to a letter"
		return False 

	if(count_children(idx,h,cnt) > 2):
		if(DEBUGGING):
			print "\t skipping, is a container of letters"
		return False 

	if(DEBUGGING):
		print "\t keeping"
	return True 

# Load the image
orig_img = cv2.imread(input_file)

# Add a border to the image for processing's sake
img = cv2.copyMakeBorder(orig_img, 50,50,50,50,cv2.BORDER_CONSTANT)

# Calculate the width and height of the image
img_y = len(img)
img_x = len(img[0])

if(DEBUGGING):
	print "Image is " + str(len(img)) + "x" + str(len(img[0]))

#Split out each channel
blue,green,red = cv2.split(img)

# Run canny edge detection on each channel
blue_edges = cv2.Canny(blue, 200, 250) 
green_edges = cv2.Canny(green, 200, 250) 
red_edges = cv2.Canny(red, 200, 250) 

# Join edges back into image
edges = blue_edges | green_edges | red_edges

# Find the contours
contours,hierarchy = cv2.findContours(edges.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)

hierarchy = hierarchy[0]

if(DEBUGGING):
	processed = edges.copy()
	rejected = edges.copy()

# These are the boxes that we are determing
keepers = []

# For each contour, find the bounding rectangle and decide
# if it's one we care about
for idx,cnt in enumerate(contours):
	if(DEBUGGING):
		print "Processing #%d" % (idx)

	x,y,w,h = cv2.boundingRect(cnt)

	# Check the contour and it's bounding box 
	if(keep(cnt) and include_box(idx,hierarchy,cnt)):
		# It's a winner!
		keepers.append([cnt,[x,y,w,h]])
		if(DEBUGGING):
			cv2.rectangle(processed,(x,y),(x+w,y+h),(100,100,100),1)
			cv2.putText(processed, str(idx), (x,y-5), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255))
	else:
		if(DEBUGGING):
			cv2.rectangle(rejected,(x,y),(x+w,y+h),(100,100,100),1)
			cv2.putText(rejected, str(idx), (x,y-5), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255))

# Make a white copy of our image
new_image = edges.copy()
new_image.fill(255)
boxes = []

# For each box, find the foreground and background intensities
for idx,(cnt,box) in enumerate(keepers):

	# Find the average intensity of the edge pixels to
	# determine the foreground intensity
	fg_int = 0.0
	for p in cnt:
		fg_int += I(p[0][0],p[0][1]) 

	fg_int /= len(cnt)
	if(DEBUGGING):
		print "FG Intensity for #%d = %d" % (idx,fg_int)

	# Find the intensity of three pixels at
	# each corner of the bounding box to determine
	# the background intensity
	bx,by,bw,bh = box	
	bg_int=[I(bx-1,by-1),
		I(bx - 1, by),
		I(bx, by - 1),
		I(bx+bw+1,by-1),
		I(bx+bw,by-1),
		I(bx+bw+1,by),
		I(bx - 1, by + bh + 1),
		I(bx - 1, by + bh),
		I(bx, by + bh + 1),
		I(bx + bw + 1, by + bh + 1),
		I(bx + bw, by + bh + 1),
		I(bx + w + 1, y + h)]

	# Find the median of the background
	# pixels determined above
	bg_int = np.median(bg_int)

	if(DEBUGGING):
		print "BG Intensity for #%d = %d" % (idx,bg_int)

	# Determine if the box should be inverted
	if(fg_int >= bg_int):	
		fg = 255
		bg = 0
	else:
		fg = 0
		bg = 255 

	# Loop through every pixel in the box and color the
	# pixel accordingly
	for x in range(bx,bx+bw):
		for y in range(by,by+bh):
			if(y >= img_y or x >= img_x):
				if(DEBUGGING):
					print "pixel out of bounds (%d,%d)" % (y,x)
				continue
			if(I(x,y) > fg_int):
				new_image[y][x] = bg
			else:
				new_image[y][x] = fg
# blur a bit to improve ocr accurrecy
new_image = cv2.blur(new_image,(2,2))
cv2.imwrite(output_file, new_image)
if(DEBUGGING):
	cv2.imwrite('edges.png',edges)
	cv2.imwrite('processed.png',processed)
	cv2.imwrite('rejected.png',rejected)

