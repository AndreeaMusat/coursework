import numpy as np
import math
import sys
from scipy import misc
from scipy.signal import wiener

# Transform rgb(a) image to grayscale
def rgb_to_grayscale(img):
	out_img = np.mean(img, axis=-1)
	return out_img

def normalize_bw_img(img):
	min_val = np.min(img)
	max_val = np.max(img)
	img = 255.0 * (img - min_val) / (max_val - min_val)
	img = img.astype(int)
	return img

# Get a 2D Gaussian filter of size dim and standard deviation std
def get_gaussian_filter(dim, std):
	if dim % 2 == 0:
		print("Filter size should be odd. Exiting")
		sys.exit(-1)

	k = (dim - 1) / 2
	gaussian_filter = np.array([[-((i - k)*(i - k) + (j - k) * (j - k)) \
							for i in range(dim)] for j in range(dim)])
	gaussian_filter = 1.0 / (2 * std * std * np.pi) * np.exp(gaussian_filter / (2 * std * std))
	return gaussian_filter

def get_motion_filter(dim, alpha=45):
	motion_filter = np.zeros((dim, dim))
	xs, ys = np.arange(dim), np.arange(dim)
	motion_filter[xs, ys] = 255
	misc.imsave("motion_filter.png", motion_filter)
	return motion_filter

# Apply filter on rgb or grayscale image (stride = 1)
def apply_filter(img, kernel):
	if len(img.shape) > 2:
		height, width, channels = img.shape[0], img.shape[1], img.shape[2]
	else:
		height, width, channels = img.shape[0], img.shape[1], 1

	filter_size = kernel.shape[0]
	k = int((filter_size - 1) / 2)

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

def blur_image(img, method, kernel_size, jfilter=False):
	if kernel_size % 2 == 0 or kernel_size == 1:
		print("[Error] Kernel size should be odd and greater than 1.")
		sys.exit(-1)

	if method == 'gaussian':
		gaussian_filter = get_gaussian_filter(kernel_size, 1.5)
		if jfilter:
			return gaussian_filter
		res = apply_filter(img, gaussian_filter)
		return gaussian_filter, res

	if method == "motion":
		motion_filter = get_motion_filter(kernel_size)
		if jfilter:
			return motion_filter
		res = apply_filter(img, motion_filter)
		return motion_filter, res

	if method == "uniform":
		sq = kernel_size * kernel_size * 1.0
		uniform_filter = np.ones((kernel_size, kernel_size)) / sq
		if jfilter:
			return uniform_filter
		res = apply_filter(img, uniform_filter)
		return uniform_filter, res

def add_noise(img, method, param):
	if method == "gaussian":
		mean = np.mean(img)
		variance = param
		sigma = variance ** 0.5
		gaussian_noise = np.random.normal(mean, sigma, img.shape)
		img = img + gaussian_noise
		return img

	if method == "salt_and_pepper":
		salt_vs_pepper = 0.5
		ratio = 1.0 / param
		num_salt = int(salt_vs_pepper * ratio * img.size)
		num_pepper = int((1 - salt_vs_pepper) * ratio * img.size)
		all_pixels = [(i, j) for i in range(img.shape[0]) \
							 for j in range(img.shape[1])]

		salt_pixels_indices = np.random.choice(img.size, num_salt, replace=False)
		salt_pixels = np.array(all_pixels)[salt_pixels_indices]
		rest_pixels_indices = list(np.setdiff1d(range(0, len(all_pixels)), salt_pixels_indices))
		pepper_pixels_indices = np.random.choice(len(rest_pixels_indices), num_pepper, replace=False)
		rest_pixels = np.array(all_pixels)[rest_pixels_indices]
		pepper_pixels = np.array(rest_pixels)[pepper_pixels_indices]
		
		salt_pixels = list(salt_pixels)
		salt_pixels = [tuple(x) for x in salt_pixels]
		pepper_pixels = list(pepper_pixels)
		pepper_pixels = [tuple(x) for x in pepper_pixels]
		
		res = normalize_bw_img(np.copy(img))
		for salt in salt_pixels:
			res[salt[0], salt[1]] = 255
		for pepper in pepper_pixels:
			res[pepper[0], pepper[1]] = 0
		return res

	if method == "poisson":
		vals = len(np.unique(img))
		vals = 2 ** np.ceil(np.log2(vals))
		noisy = np.random.poisson(img * vals) / float(vals)
		return noisy

	if method == "speckle":
		row,col = img.shape
		gauss = np.random.randn(row,col)
		gauss = gauss.reshape(row,col)        
		noisy = img + img * 1.0 / param * gauss
		return noisy

def deblur(convolved_img, kernel, method, param):
	if method == "deconv_approx":
		iterations = param
		err = np.zeros(convolved_img.shape)
		conv1 = np.zeros(convolved_img.shape)
		f = convolved_img
		for i in range(iterations):
			conv1 = apply_filter(f, kernel)
			err = convolved_img - conv1
			f = f + err
		return f

	if method == "wiener":
		return wiener(convolved_img, param, kernel)

def denoise(img, method, param):
	if method == "median":
		result = np.zeros(img.shape)
		k = param
		for i in range(img.shape[0]):
			for j in range(img.shape[1]):
				neighbors = img[max(i-k, 0) : min(i+k, img.shape[0]-1), max(j-k, 0): min(j+k, img.shape[1] - 1)]
				median_val = np.median(neighbors)
				result[i, j] = median_val
		return result

	if method == "gaussian":
		gaussian_filter = get_gaussian_filter(5, param)
		result = apply_filter(img, gaussian_filter)
		return result

def main(args):

	if len(args) < 2:
		print("[Error] Usage: python main.py [blur|noise|denoise|deblur] method image_name")
		sys.exit(-1)

	action = args[1]
	method = args[2]
	input_img_name = args[3]
	param = int(args[4])

	actions = ["blur", "noise", "denoise", "deblur"]
	blur_methods = ["gaussian", "motion", "uniform"]
	noise_methods = ["gaussian", "salt_and_pepper", "poisson", "speckle"]
	denoise_methods = ["median", "gaussian"]
	deblur_methods = ["deconv_approx", "wiener"]

	if action not in actions:
		print("[Error] Possible actions are: ", actions)
		sys.exit(-1)
	if action == "blur" and method not in blur_methods:
		print("[Error] Possible blur methods are: ", blur_methods)
		sys.exit(-1)
	if action == "noise" and method not in noise_methods:
		print("[Error] Possble noise methods are: ", noise_methods)
		sys.exit(-1)
	if action == "denoise" and method not in denoise_methods:
		print("[Error] Possible denoising methods are: ", denoise_methods)
		sys.exit(-1)
	if action == "deblur" and method not in deblur_methods:
		print("[Error] Possible deblurring methods are: ", deblur_methods)
		sys.exit(-1)

	img = misc.imread(input_img_name)

	if action== "blur":
		kernel_size = param
		_, blurred_img = blur_image(img, method, kernel_size)
		img_name = "blurred_" + method + "_" + input_img_name
		misc.imsave(img_name, blurred_img)
		sys.exit(0)

	elif action == "noise":
		noisy = add_noise(img, method, param)
		img_name = "noisy_" + method + "_" + input_img_name
		misc.imsave(img_name, noisy)
		sys.exit(0)

	elif action == "denoise":
		denoised = denoise(img, method, param)
		img_name = "denoised_" + method + "_" + input_img_name
		misc.imsave(img_name, denoised)
		sys.exit(0)

	elif action == "deblur":
		blur_method = args[5]
		blur_param = int(args[6])
		kernel = blur_image(img, blur_method, blur_param, jfilter=True)
		deblurred = deblur(img, kernel, method, param)
		deblurred = normalize_bw_img(deblurred)
		img_name = "deblurred_" + method + "_" + input_img_name
		misc.imsave(img_name, deblurred)
		sys.exit(0)

if __name__ == "__main__":
	main(sys.argv)
