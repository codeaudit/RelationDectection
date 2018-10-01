'''
This code is based on the Pytorch Orientaion:
https://pytorch.org/tutorials/beginner/nlp/sequence_models_tutorial.html#sphx-glr-beginner-nlp-sequence-models-tutorial-py
Original Author: Robert Guthrie
'''

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

torch.manual_seed(1)

class BiLSTM(nn.Module):

    def __init__(self, embedding_dim, hidden_dim, vocab_size, vocab_embedding):
        super(BiLSTM, self).__init__()
        self.hidden_dim = hidden_dim

        self.word_embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.word_embeddings.weight.data.copy_(torch.from_numpy(vocab_embedding))

        # The LSTM takes word embeddings as inputs, and outputs hidden states
        # with dimensionality hidden_dim.
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, bidirectional=True)

        self.maxpool = nn.MaxPool1d(hidden_dim*2)
        self.hidden = self.init_hidden()

    def init_hidden(self):
        # Before we've done anything, we dont have any hidden state.
        # Refer to the Pytorch documentation to see exactly
        # why they have this dimensionality.
        # The axes semantics are (num_layers, minibatch_size, hidden_dim)
        return (torch.zeros(2, 1, self.hidden_dim),
                torch.zeros(2, 1, self.hidden_dim))

    def forward(self, sentence):
        embeds = self.word_embeddings(sentence)
        lstm_out, self.hidden = self.lstm(
            embeds.view(len(sentence), 1, -1), self.hidden)
        #maxpool_hidden = self.maxpool(lstm_out.view(1,len(sentence), -1))
        #print(len(self.hidden))
        return self.hidden[0].view(-1, self.hidden_dim*2)

class SimilarityModel(nn.Module):
    def __init__(self, embedding_dim, hidden_dim, vocab_size, vocab_embedding):
        super(SimilarityModel, self).__init__()
        self.sentence_biLstm = BiLSTM(embedding_dim, hidden_dim, vocab_size,
                                      vocab_embedding)
        self.relation_biLstm = BiLSTM(embedding_dim, hidden_dim, vocab_size,
                                      vocab_embedding)

    def init_hidden(self):
        self.sentence_biLstm.init_hidden()
        self.relation_biLstm.init_hidden()

    def forward(self, question, relation):
        sentence_embedding = self.sentence_biLstm(question)
        relation_embedding = self.relation_biLstm(relation)
        #print('sentence_embedding size', sentence_embedding.size())
        #print('relation_embedding size', relation_embedding.size())
        #print('sentence_embedding', sentence_embedding)
        #print('relation_embedding', relation_embedding)
        cos = nn.CosineSimilarity(dim=1)
        return cos(sentence_embedding, relation_embedding)
