import numpy as np
import nltk

from typing import List


def select_data(X : np.array, y : np.array, N : int):
	"""
		For every class in y, select N elements
	""" 
	unique_labels = np.unique(y)

	if len(unique_labels) * N >= len(X):
		return X, y

	selected_idx = np.zeros(len(unique_labels) * N, dtype=np.int)

	for i in range(len(unique_labels)):
		crt_label_idx = np.argwhere(y == unique_labels[i])[:N]
		selected_idx[i*N:(i+1)*N] = crt_label_idx[:, 0]
	
	return np.array(X)[selected_idx], np.array(y)[selected_idx]


def text_to_idx(text_data : List, word2idx):
	ans = []

	for doc in text_data:
		sent_text = nltk.sent_tokenize(doc.replace('\n', ' '))
		curr_text = []
		for sent in sent_text:
			tokenized_sent = nltk.word_tokenize(sent)
			curr_sent = [word2idx[word] for word in tokenized_sent if word in word2idx]
			curr_text += curr_sent
		ans.append(curr_text)
	
	return ans




