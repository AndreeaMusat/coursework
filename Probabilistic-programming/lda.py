import pymc
import numpy as np

import matplotlib.pyplot as plt


class LatentDirichletAllocation(object):
    def __init__(self, n_components: int, max_iter: int, burn_iter: int, n_jobs: int, vocab_size: int):
        """
            n_components : int, the number of topics
            max_iter : int, maximum number of iterations
            n_jobs : int, number of threads used

        """
        self.n_components = n_components
        self.max_iter = max_iter
        self.burn_iter = burn_iter
        self.n_jobs = n_jobs
        self.vocab_size = vocab_size + 1

    def fit(self, text_data, labels=None):
        """
                X : np.array, frequency of each word from the vocabulary for each document
        """
        self.input = text_data
        self.real_label = labels
        self.num_documents = len(text_data)

        # the parameter of the Dirichlet prior on the per-document topic distributions
        self.alphas = np.ones(self.n_components)

        # the parameter of the Dirichlet prior on the per-topic word distribution
        self.betas = np.ones(self.vocab_size)

        # theta[m] is the topic distribution for document m,
        self.thetas = pymc.Container([pymc.CompletedDirichlet('theta_%d' % i, pymc.Dirichlet('tmp_thetas_%d' % i, theta=self.alphas))
                                      for i in range(self.num_documents)])

        # phi[k] is the word distribution for topic k
        self.phis = pymc.Container([pymc.Dirichlet(
            'phis_%d' % i, theta=self.betas) for i in range(self.n_components)])

        # zs[m, n] is the topic for the n-th word in document m
        self.zs = pymc.Container([pymc.Categorical('zs_%d' % i, p=self.thetas[i], size=len(
            text_data[i]), value=np.random.randint(self.n_components, size=len(text_data[i]))) for i in range(self.num_documents)])

        # ws[m, n] is the n-th word in document m
        # This is the only observed variable
        self.ws = pymc.Container([pymc.Categorical('ws_%d_%d' % (d, i), p=pymc.Lambda(
            'prob_%d_%d' % (d, i), lambda z=self.zs[d][i], phi=self.phis: phi[z]), value=text_data[d][i], observed=True)
            for d in range(self.num_documents) for i in range(len(text_data[d]))])

        self.mcmc = pymc.MCMC(pymc.Model([self.thetas, self.phis, self.zs, self.ws]))
        self.mcmc.sample(self.max_iter, burn=self.burn_iter)

    def plot_topics(self, inv_vocabulary):
        topic_word_distrib = self.phis.value

        for i, topic_distrib in enumerate(topic_word_distrib):
            sorted_words = np.argsort(topic_distrib)

            best_words = [inv_vocabulary[i] for i in sorted_words[-15:]]
            keys = [inv_vocabulary[idx] for idx in sorted_words[-30:]]

            print('Most representative words for topic %d are:' % i)
            print(best_words)

            plt.figure(figsize=(12, 12))
            plt.bar(range(30), topic_distrib[sorted_words[-30:]])
            plt.xticks(np.arange(30), keys, rotation=90)
            plt.title('Word distribution for topic %d' % i)
            plt.show()

    def plot_document_topics(self, documents, thetas):
        doc_idx = np.random.permutation(len(documents))

        i, cnt = 0, 0
        while cnt < 10 and i < len(documents):
            if (len(documents[doc_idx[i]]) < 20 or
                    len(documents[doc_idx[i]]) > 500):
                i += 1
                continue

            print(documents[doc_idx[i]])

            curr_topic_distrib = thetas.value[doc_idx[i]][0]
            plt.bar(range(len(curr_topic_distrib)), curr_topic_distrib)
            plt.title('Document topic distribution for document %d' % cnt)
            plt.show()

            i, cnt = i + 1, cnt + 1

    def infer_topic_for_new_documents(self, new_data):
        # we need to infer theta for the new documents
        # self.phis is fixed
        num_new_documents = len(new_data)

        thetas = pymc.Container([pymc.CompletedDirichlet('new_theta_%d' % i, pymc.Dirichlet('new_tmp_thetas_%d' % i, theta=self.alphas))
                                 for i in range(num_new_documents)])

        zs = pymc.Container([pymc.Categorical('new_zs_%d' % i, p=thetas[i], size=len(
            new_data[i]), value=np.random.randint(self.n_components, size=len(new_data[i]))) for i in range(num_new_documents)])

        ws = pymc.Container([pymc.Categorical('new_ws_%d_%d' % (d, i), p=pymc.Lambda(
            'prob_%d_%d' % (d, i), lambda z=zs[d][i], phi=self.phis: phi[z]), value=new_data[d][i], observed=True)
            for d in range(num_new_documents) for i in range(len(new_data[d]))])

        mcmc = pymc.MCMC(pymc.Model([thetas, zs, ws]))
        mcmc.sample(self.max_iter, burn=self.burn_iter)
        return thetas

    def plot_document_similarity(self, documents, labels):
        doc_idx = np.random.permutation(self.num_documents)

        num_selected_documents = 5

        docs = []
        i, cnt = 0, 0
        while cnt < num_selected_documents and i < self.num_documents:
            if (len(documents[doc_idx[i]]) < 20 or
                    len(documents[doc_idx[i]]) > 200):
                i += 1
                continue

            docs.append(i)
            i, cnt = i + 1, cnt + 1

        docs_topics = np.array([self.thetas.value[docs[i]]
                                for i in range(len(docs))])[:, 0, :]
        cosine_sim = np.zeros((num_selected_documents, num_selected_documents))

        for i in range(num_selected_documents):
            for j in range(num_selected_documents):
                cosine_sim[i, j] = np.dot(docs_topics[i], docs_topics[j])
                cosine_sim[i, j] /= (np.linalg.norm(docs_topics[i])
                                     * np.linalg.norm(docs_topics[j]))

        for i in range(num_selected_documents):
            print('\nDocument %d with label %d' % (i, labels[docs[i]]))
            print(documents[docs[i]])
            print('--------------------------------------------------')
            print('\n')

        print('\n\n')
        print(cosine_sim)

        plt.imshow(cosine_sim)
