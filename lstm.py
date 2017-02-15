from __future__ import absolute_import, division, print_function

import os, sys
import pickle
from six.moves import urllib

import tflearn
from tflearn.data_utils import *

path = 'corpus.txt'
char_idx_file = 'char_idx.pickle'
maxlen = 20

if not os.path.isfile(path):
    print("Invalid path. Use 'python twitter_corpus.py' to generate a text corpus from a twitter feed")
    sys.exit(0)

char_idx = None
if os.path.isfile(char_idx_file):
  print('Loading previous char_idx')
  char_idx = pickle.load(open(char_idx_file, 'rb'))

X, Y, char_idx = \
    textfile_to_semi_redundant_sequences(path, seq_maxlen=maxlen, redun_step=3, pre_defined_char_idx=char_idx)

pickle.dump(char_idx, open(char_idx_file,'wb'))

g = tflearn.input_data([None, maxlen, len(char_idx)])
g = tflearn.lstm(g, 512, return_seq=True)
g = tflearn.dropout(g, 0.5)
g = tflearn.lstm(g, 512, return_seq=True)
g = tflearn.dropout(g, 0.5)
g = tflearn.lstm(g, 512)
g = tflearn.dropout(g, 0.5)
g = tflearn.fully_connected(g, len(char_idx), activation='softmax')
g = tflearn.regression(g, optimizer='adam', loss='categorical_crossentropy',
                       learning_rate=0.001)

m = tflearn.SequenceGenerator(g, dictionary=char_idx,
                              seq_maxlen=maxlen,
                              clip_gradients=5.0,
                              checkpoint_path='model_trump')

f = open('log.txt', 'w')
for i in range(50):
    seed = random_sequence_from_textfile(path, maxlen)
    m.fit(X, Y, validation_set=0.1, batch_size=128,
          n_epoch=1, run_id='trump')
    f.write("-- TESTING...")
    f.write("-- Test with temperature of 1.0 --")
    f.write(m.generate(600, temperature=1.0, seq_seed=seed))
    f.write("-- Test with temperature of 0.5 --")
    f.write(m.generate(600, temperature=0.5, seq_seed=seed))
f.close()