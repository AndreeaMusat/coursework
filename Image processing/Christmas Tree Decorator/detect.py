import numpy as np
import sys
import math
import operator
from scipy import misc
from scipy.signal import argrelextrema

first_most_used_color = None
second_most_used_color = None
third_most_used_color = None

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

angles = np.linspace(0, 2 * np.pi, 360)
sins = np.sin(angles)
coss = np.cos(angles)

"""
Convert an image to grayscale by taking the median 
of the 3 RGB channels

Parameters
----------
img : numpy.ndarray
	Img to convert to grayscale

Returns
-------
out_img : numpy.ndarray
	Grayscale image


"""
def rgb_to_grayscale(img):
	out_img = np.mean(img, axis=-1)
	misc.imsave("tmp/black_white.png", out_img)
	return out_img

"""
Return a 2D Gaussian filter of given size and standard deviation

Parameters
----------
dim : Int
	Size of Gaussian filter (width and height)
std : Float
	Standard deviation 

Returns
-------
gaussian_filter : numpy.ndarray
	(dim * dim) matrix with values taken from a 2D Gaussian distribution

"""
def get_gaussian_filter(dim, std):
	if dim % 2 == 0:
		print("Filter size should be odd. Exiting")
		sys.exit(-1)

	k = (dim - 1) / 2
	gaussian_filter = np.array([[-((i - k)*(i - k) + (j - k) * (j - k)) \
							for i in range(dim)] for j in range(dim)])
	gaussian_filter = 1.0 / (2 * std * std * math.pi) * np.exp(gaussian_filter / (2 * std * std))
	return gaussian_filter

"""
Return the horizontal and vertical Sobel filters
"""
def get_sobel_filters():
	horzontal_sobel_filter = np.array([[1], [ 2], [1]]) * np.array([1, 0, -1])
	vertical_sobel_filter = np.array([[1], [0], [-1]]) * np.array([1, 2, 1])
	return (horzontal_sobel_filter, vertical_sobel_filter)

"""
Apply filter to RGB or grayscale image

Parameters
----------
img : numpy.ndarray
	Input image
kernel : numpy.ndarray
	Filter to apply

Returns
-------
out_img : numpy.ndarray
	Result image 
"""
def apply_filter(img, kernel):
	if len(img.shape) > 2:
		height, width, channels = img.shape[0], img.shape[1], img.shape[2]
	else:
		height, width, channels = img.shape[0], img.shape[1], 1

	filter_size = kernel.shape[0]
	k = (filter_size - 1) / 2

	if channels > 1:
		padded_img = np.zeros((height + 2 * k, width + 2 * k, channels))
		for i in range(channels):
			padded_img[k:-k, k:-k, i] = img[:, :, i]
		
		out_img = [[[(padded_img[x:x+filter_size, y:y+filter_size, c] * kernel).sum() \
					for x in range(height)]\
					for y in range(width)]\
					for c in range(channels)]
		return np.array(out_img).T
	else:
		padded_img = np.zeros((height + 2 * k, width + 2 * k))
		padded_img[k:-k, k:-k] = img
		out_img = [[[(padded_img[x:x+filter_size, y:y+filter_size] * kernel).sum()\
					 for x in range(height)]\
					 for y in range(width)]]
		return np.array(out_img).T[:, :, 0]

"""
Perform an edge detection on a given RGB image and return 
the edges as a mask

Parameters
----------
input_img : numpy.ndarray
	RGB image stored in a numpy array
blue : Boolean
	True if a Gaussian filter should be applied to denoise the image

Returns
t1 : numpy.ndarray
	B&W mask containing the edges
-------
"""
def canny_edge_detection(input_img):
	k = 1
	edge_image = np.zeros(input_img.shape)

	# grayscale conversion
	grayscale_img = rgb_to_grayscale(input_img)

	# create Gaussian filter and apply it to the input image
	gaussian_filter = get_gaussian_filter(2 * k + 1, 1)
	blurred_img = apply_filter(grayscale_img, gaussian_filter)
	misc.imsave("tmp/blurred_img.png", blurred_img)

	# now apply sobel filters to get horzontal (Gx) and vertical derivatives
	sobel_filters = get_sobel_filters()
	Gx = apply_filter(grayscale_img, sobel_filters[0])
	Gy = apply_filter(grayscale_img, sobel_filters[1])
	misc.imsave("tmp/horizontal_derivative.png", Gx)
	misc.imsave("tmp/vertical_derivative.png", Gy)

	# compute edge gradient and direction and save them
	G = np.sqrt(np.square(Gx) + np.square(Gy))
	theta = np.arctan2(Gy, Gx)
	misc.imsave("tmp/edge_gradient.png", G)
	misc.imsave("tmp/edge_direction.png", theta)

	# adjust the gradient direction
	theta = theta + 2 * np.pi
	theta = theta - (theta / (2 * np.pi)).astype(int) * 2 * np.pi
	theta[theta > np.pi] -= np.pi
	theta[(theta >= 0) & (theta < np.pi / 8)] = 0.0
	theta[(theta >= 7 * np.pi / 8) & (theta <= np.pi)] = 0.0
	theta[(theta >= np.pi / 8) & (theta < 3 * np.pi / 8)] = np.pi / 4
	theta[(theta >= 3 * np.pi / 8) & (theta < 5 * np.pi / 8)] = np.pi / 2
	theta[(theta >= 5 * np.pi / 8) & (theta < 7 * np.pi / 8)] = 3 * np.pi / 4
	misc.imsave("tmp/adjusted_edge_direction.png", theta)

	directions = {}
	directions[0] = [(0, 1), (0, -1)]
	directions[3 * np.pi / 4] = [(-1, 1), (1, -1)]
	directions[np.pi / 2] = [(1, 0), (-1, 0)]
	directions[np.pi / 4] = [(-1, -1), (1, 1)]

	# non maxima suppression
	new_G = np.copy(G)
	for i in range(1, theta.shape[0] - 1):
		for j in range(1, theta.shape[1] - 1):
			neigh1 = (i + directions[theta[i, j]][0][0], j + directions[theta[i, j]][0][1])
			neigh2 = (i + directions[theta[i, j]][1][0], j + directions[theta[i, j]][1][1])
			if G[neigh1] > G[i, j] or G[neigh2] > G[i, j]:
				new_G[i, j] = 0
			elif G[i, j] > G[neigh1] and G[i, j] > G[neigh2]:
				new_G[neigh1] = 0
				new_G[neigh2] = 0
	misc.imsave("tmp/thinned_edges.png", new_G)

	t1 = np.copy(new_G)
	t1[t1 >= 10] = 255
	t1[t1 < 10] = 0
	misc.imsave("tmp/edges.png", t1)
	return t1

# Return indices of pixels on a scaled circle of given radius and center
# +- an error (delta) and within some limits
def get_points_on_circle(radius, center, scale, delta, limits_x, limits_y):
	x_coords = np.array([])
	y_coords = np.array([])
	for r in range(max(0, radius - delta), radius + delta + 1):
		x_coords = np.append(x_coords, np.rint(scale * r * sins) + center[0])
		y_coords = np.append(y_coords, np.rint(scale * r * coss) + center[1])

	x_coords = x_coords.astype(int)
	y_coords = y_coords.astype(int)

	valid_indices = np.where((x_coords >= limits_x[0]) & (x_coords < limits_x[1]) & 
							 (y_coords >= limits_y[0]) & (y_coords < limits_y[1]))
	valid_x_coords = x_coords[valid_indices]
	valid_y_coords = y_coords[valid_indices]
	return (valid_x_coords, valid_y_coords)

"""
Color an entire connected component of pixels.

Parameters
----------
image : numpy.ndarray
	Input image
point : 2-tuple
	Starting point of BFS
current_color : 3-tuple
	Current color of the pixels in the connected component
new_color : 3-tuple
	New color 
Returns
-------

"""
def flood_fill(image, point, current_color, new_color):
	queue = []
	queue.append(point)
	
	visited = np.zeros((image.shape[0], image.shape[1]))

	while len(queue) > 0:
		curr_point = queue.pop(0)
		curr_point = ((int(curr_point[0]), int(curr_point[1])))

		if visited[curr_point] == 1:
			continue
		visited[curr_point] = 1

		if list(image[curr_point][0:3]) != list(current_color[0:3]):
			continue

		for ch in range(len(new_color)):
			image[curr_point + (ch, )] = new_color[ch] 

		# get indices of neighbouring pixels 
		neighs_indices = [(i, j) for i in range(max(0, curr_point[0] - 1), min(image.shape[0], curr_point[0] + 2))\
								 for j in range(max(0, curr_point[1] - 1), min(image.shape[1], curr_point[1] + 2))\
								 if (i, j) != curr_point]

		queue = queue + neighs_indices

def hough_circle_detection(input_img, edge_img, min_radius=10, max_radius=60, step=1):
	edge_pixel_val = np.max(edge_img)

	# accumulator matrix for votes
	votes_acc = np.zeros((edge_img.shape[0] / step, \
						  edge_img.shape[1] / step, \
						  max_radius - min_radius + 1))

	img_height, img_width = edge_img.shape[0], edge_img.shape[1]
	edge_pixels_indices = [(i, j) for i in range(1, img_height - 1) \
								  for j in range(1, img_width - 1) \
								  if edge_img[i, j] == edge_pixel_val]

	new_edge_img = np.zeros(edge_img.shape + (3,))
	for i in range(3):
		new_edge_img[:, :, i] = edge_img

	# [center x, center y, radius, response]
	all_circles = []
	for radius in range(min_radius, max_radius + 1, 1):
		for pixel in edge_pixels_indices:
			limits = (0, int(img_height / step)), (0, int(img_width / step))
			valid_xs, valid_ys = get_points_on_circle(radius, pixel, 1.0 / step, 0, *limits)
			if valid_xs.size > 0:
				votes_acc[valid_xs, valid_ys, radius - min_radius] += 1

		name = "tmp/votes_" + str(radius) + ".png"
		misc.imsave(name, votes_acc[:, :, radius - min_radius])

		# now for the pixels having maximum response, draw the circle on the original image
		max_response = np.amax(votes_acc[:, :, radius - min_radius])
		mask = np.zeros((step, step))
		mask[mask.shape[0] / 2, mask.shape[1] / 2] = 1
		crt_votes = np.kron(votes_acc[:, :, radius - min_radius], mask)

		print("radius = %d, max response = %d" % (radius, max_response))

		circle_xs, circle_ys = np.where(crt_votes == max_response)
		crt_img = np.copy(input_img)
		for i in range(circle_xs.size):

			limits = ((0, img_height), (0, img_width))
			valid_xs, valid_ys = get_points_on_circle(radius, (circle_xs[i], circle_ys[i]), 1, 2, *limits)
			
			all_circles.append([circle_xs[i], circle_ys[i], radius, max_response])

			if valid_xs.size > 0:
				crt_img[valid_xs, valid_ys, 0] = 0
				crt_img[valid_xs, valid_ys, 1] = 0	
				crt_img[valid_xs, valid_ys, 2] = 0
				
			name = "tmp/detected_circles_" + str(radius) + ".png"
			misc.imsave(name, crt_img)

	XC, YC, R, RESPONSE = range(4)
	for circle in all_circles:

		# heuristic
		if circle[R] > 30 and circle[RESPONSE] < 70:
			continue
		if circle[R] <= 30 and circle[RESPONSE] < 60:
			continue
		
		limits = ((0, img_height), (0, img_width))
		valid_xs, valid_ys = get_points_on_circle(circle[R], (circle[XC], circle[YC]), 1, 5, *limits)

		# make edge pixels on the circle red
		cond = (new_edge_img[valid_xs, valid_ys, 0] == edge_pixel_val) &\
			   (new_edge_img[valid_xs, valid_ys, 1] == edge_pixel_val) &\
			   (new_edge_img[valid_xs, valid_ys, 2] == edge_pixel_val)

		valid_xs = valid_xs[cond]
		valid_ys = valid_ys[cond]
		
		if valid_xs.size > 0:
			for ch in range(3):
				new_edge_img[valid_xs, valid_ys, ch] = RED[ch]
				input_img[valid_xs, valid_ys, ch] = RED[ch]

			current_color = tuple(list(input_img[circle[XC], circle[YC]])[0:3])

			# fill the circle using red
			flood_fill(input_img, (circle[XC], circle[YC]), current_color, RED)

		misc.imsave("tmp/new_edge.png", new_edge_img)
		misc.imsave("tmp/result.png", input_img)

	return (input_img, new_edge_img)

def paint_tree(image, edge_img):
	cnt = 1

	# remove unwanted edges (margin edges)
	edge_img[0, :, :] = 0
	edge_img[:, 0, :] = 0
	edge_img[-1:, :, :] = 0
	edge_img[:, -1, :] = 0

	# group edge pixels 
	for i in range(edge_img.shape[0]):
		for j in range(edge_img.shape[1]):
			if tuple(edge_img[i, j, :]) == WHITE:
				flood_fill(edge_img, (i, j), WHITE, (cnt, cnt, cnt))
				cnt += 1

	misc.imsave("tmp/final_edges.png", edge_img)
	
	max_size_comp = -1
	for i in range(1, cnt):
		comp_xs, comp_ys = np.where(edge_img[:, :, 0] == i)
		max_size_comp = max(max_size_comp, comp_xs.size)

	for i in range(1, cnt):
		comp_xs, comp_ys = np.where(edge_img[:, :, 0] == i)
		
		# ignore maximum size component (tree)
		if comp_xs.size == max_size_comp:
			continue

		# ignore empty component
		if comp_xs.size == 0 or comp_ys.size == 0:
			continue

		centroid_x = int(np.average(comp_xs))
		centroid_y = int(np.average(comp_ys))

		if centroid_x < 0 or centroid_x >= edge_img.shape[0] or\
		   centroid_y < 0 or centroid_y >= edge_img.shape[1]:
			continue

		curr_color = tuple(image[centroid_x, centroid_y, :])[0:3]
		if curr_color == first_most_used_color or\
		   curr_color == second_most_used_color or\
		   curr_color == third_most_used_color:
			continue

		for ch in range(3):
			image[comp_xs, comp_ys, ch] = YELLOW[ch]

		flood_fill(image, (centroid_x, centroid_y), curr_color, YELLOW)

	misc.imsave("detected.png", image)

def get_most_frequent_color(input_img):
	global first_most_used_color, second_most_used_color, third_most_used_color
	colors = set(tuple(v) for m2d in input_img for v in m2d)
	freqs = {}
	for color in colors:
		xs, ys = np.where((input_img[:, :, 0] == color[0]) &\
						   (input_img[:, :, 1] == color[1]) &\
						   (input_img[:, :, 2] == color[2]))
		freqs[color] = xs.size

	first_most_used_color = max(freqs.items(), key=operator.itemgetter(1))[0]
	del freqs[first_most_used_color]
	second_most_used_color = max(freqs.items(), key=operator.itemgetter(1))[0]
	del freqs[second_most_used_color]
	third_most_used_color = max(freqs.items(), key=operator.itemgetter(1))[0]
	
	first_most_used_color = first_most_used_color[0:3]
	second_most_used_color = second_most_used_color[0:3]
	third_most_used_color = third_most_used_color[0:3]

	print(first_most_used_color)
	print(second_most_used_color)
	print(third_most_used_color)

def main(argv):
	input_img = argv[1]
	input_img = misc.imread(input_img)

	if input_img is None:
		print("Could not read input image. Exiting")
		sys.exit(-1)

	get_most_frequent_color(input_img)
	print("Input image shape is ", input_img.shape)

	edge_img = canny_edge_detection(input_img)
	misc.imsave("tmp/edges.png", edge_img)

	result_img, new_edge_img = hough_circle_detection(input_img, edge_img)
	paint_tree(result_img, new_edge_img)

if __name__ == "__main__":
	main(sys.argv)
