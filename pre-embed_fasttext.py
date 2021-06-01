from numpy.random import seed
seed(3)
#from tensorflow import set_random_seed
#set_random_seed(3)
#import tensorflow as tf
#from tensorflow.keras.models import Model
#from tensorflow.keras.layers import Dense, LSTM, Dropout, Input, Bidirectional, Lambda, TimeDistributed, Masking, Average
#from keras_contrib.layers import CRF
#from tensorflow.keras import optimizers
#import keras.backend as K
import csv
import numpy as np
import argparse
from sklearn.metrics import confusion_matrix, f1_score
#from allennlp.commands.elmo import ElmoEmbedder
from math import ceil
from extra.apply_vecmap_transform import vecmap
from posutils import load_data, pad_labels, apply_vecmap, normalize
import pickle
#from tensorflow.keras import activations
#from tensorflow.keras.layers import LeakyReLU

def embed_fasttext(sentences, embeddings, xlingual):
    max_seqlen = max(len(s) for s in sentences) if sentences else 0
    if max_seqlen == 0:
        return []
    #embedded = np.full((len(sentences), max_seqlen, 300), fill_value=-999.)
    emb = []
    for s in sentences:
        emb.append([embeddings[w] if w in embeddings else -999.*np.ones(300) for w in s])
#    for x,sentence in enumerate(emb):
#        seqlen = len(sentence)
#        embedded[x, 0:seqlen, :] = sentence
#    if xlingual:
#        embedded = apply_mapping(embedded)

    return emb

def load_fasttext(emb_file):
    embeddings = {}
    with open(emb_file, 'r') as embs:
        embs.readline()
        for line in embs:
            line = line.strip().split()
            try:
                embeddings[line[0]] = np.array([float(i) for i in line[1:]])
            except:
                continue
    return embeddings


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--train_file", default=None, type=str, required=True)
    parser.add_argument("--embs", default=None, type=str, required=True, help="fasttext embeddings")
    parser.add_argument("--bs", default=128, type=int, help="batch size")
    args = parser.parse_args()

    def generate_batch_data(inputfile, batch_size, args):
        fasttext = load_fasttext(args.embs)
        xlingual = False
        x,y = load_data(inputfile)
        xemb = []
        print("INPUT SIZES X AND Y", len(x), len(y))
        assert len(x) == len(y)
        newxval = []
        for i in range(len(y)):
            newxval.append(x[i])
            if i > 0 and i % batch_size == 0:
                xemb += embed_fasttext(newxval, fasttext, xlingual)
                #xemb += xv
                newxval = []
        if len(newxval) > 0:
            xemb += embed_fasttext(newxval, fasttext, xlingual)
        return xemb

    embs = generate_batch_data(args.train_file, args.bs, args)
    with open(args.train_file+'.ft-embs.pickle', 'wb') as f:
        pickle.dump(embs, f, pickle.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    main()    
