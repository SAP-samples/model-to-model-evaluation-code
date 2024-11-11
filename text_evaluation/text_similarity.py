from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
import pandas as pd
import re
import numpy as np


model = SentenceTransformer('sentence-transformers/stsb-mpnet-base-v2')

""" this function returns the cosine similarity betweeen 2 documents using TF-IDF """
def get_cosine(text1,text2):
    corpus = [text1,text2]
    vectorizer = TfidfVectorizer()
    trsfm=vectorizer.fit_transform(corpus)
    cos_sim = cosine_similarity(trsfm[0:1], trsfm)
    cos_sim = cos_sim[0][1]
    cos_sim = round(cos_sim, 2)
    return cos_sim

""" this function returns the cosine similarity betweeen 2 documents using pre-trained BERT model """
def sts_bert(t1,t2):
    try:
        sentences = [t1, t2]
        embedding_1= model.encode(sentences[0], convert_to_tensor=True)
        embedding_2 = model.encode(sentences[1], convert_to_tensor=True)
        score = util.pytorch_cos_sim(embedding_1, embedding_2)
        score = score.tolist()
        score = round(score[0][0], 2)
    except:
        score = 0
    return score

""" this function splits plain text into array of sentences """
def split_into_sentences(paragraph):
    sentence_endings = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s|[.?!](?=[A-Z]|\"|\')'
    sentences = re.split(sentence_endings, paragraph)
    return sentences

""" this function splits string into array of sentences and removes spaces/new lines """
def split_and_clean(text):
    clean_sentences = []
    sentences = split_into_sentences(text)
    for s in sentences:
        if s != "" and s!="\n":
            if len(s) > 1:
                clean_sentences.append(s)
    return clean_sentences

""" this function genertes similarity matrix betweeen two arrays of sentences: list1 - original, list2 - generated """
""" sim_type : cos or bert """
def create_matrix(list1,list2,sim_type):
    final = []
    for l in list1:
        row = []
        for ll in list2:
            if sim_type == "cos":
                val = get_cosine(l,ll)
            else:
                val = sts_bert(l,ll)
            row.append(val)
        final.append(row)
    new = pd.DataFrame(final)
    return new

""" this function returns only matrix values greater than threshold and their indexes """
def find_match(matrix,thold):
    new_matrix = matrix.drop(columns=[col for col in matrix if (matrix[col] <= thold).all()])
    clean_matrix = new_matrix.drop(index=[index for index, row in new_matrix.iterrows() if (row <= thold).all()])
    over_thold = clean_matrix.idxmax()
    return over_thold

""" this function calculates recall """
def find_recall(matrix,thold):
    try:
        shape = matrix.shape
        # get the number of sentences in original text
        all_orig = shape[0]
        matches = find_match(matrix,thold)
        columns = list(matches)
        # get number of sentences in original text that are also present in generated text
        match_orig = len(list(dict.fromkeys(columns)))
        recall = round(match_orig/all_orig,2)
    except:
        recall = 0
    return recall

""" this function calculates precision """
def find_precision(matrix,thold):
    try:
        shape = matrix.shape
        all_gen = shape[1]
        matches = find_match(matrix,thold)
        indexes = list(matches.index)
        match_gen = len(list(dict.fromkeys(indexes)))
        precision = round(match_gen/all_gen,2)
    except:
        precision = 0
    return precision

""" this function takes two texts as input and return precision and recall: text1 - original, text2 - generated """
def get_kpis(text1,text2,sim_type="cos"):
    list1 = split_and_clean(text1)
    list2 = split_and_clean(text2)
    matrix = create_matrix(list1,list2,sim_type)
    if sim_type == "cos":
        thold = 0.2
    else:
        thold = 0.5
    recall = find_recall(matrix,thold)
    precision = find_precision(matrix,thold)
    return recall, precision


import nltk
from nltk.metrics import edit_distance

nltk.download("punkt_tab")


def get_sentences(text_1):
    """
    tekoneizes text in sentences
    """
    return nltk.sent_tokenize(text_1)


def sequence_similarity(sentences_1, sentences_2):
    """
    Calculate a sequence similarity based on normalized edit distance on sentences
    """
    return 1 - (edit_distance(sentences_1, sentences_2) / max(len(sentences_1), len(sentences_2)))


def align_sentences(text1_sentences, text2_sentences, threshold=0.75):
    """
    Given two lists of sentences, adjusts list2 based on similarity to list1.

    Args:
        sentences_1 (list): List of sentences.
        sentences_2 (list): List of sentences.

    Returns:
        list: Adjusted second list of sentences.

    """
    # Adjust text2 sentences
    adjusted_text2_sentences = text2_sentences[:]

    for sentence_1 in text1_sentences:
        best_similarity = 0
        best_index = -1
        for j, sentence_2 in enumerate(text2_sentences):
            similarity = sts_bert(sentence_1, sentence_2)  # Use the custom similarity function
            if similarity > best_similarity:
                best_similarity = similarity
                best_index = j
        if best_similarity >= threshold:
            adjusted_text2_sentences[best_index] = sentence_1

    return adjusted_text2_sentences

def text_similarity_alternative(file_1, file_2, threshold=0.8):
    """
    Args:
        file_1, file_2:  2 input text files.
    Returns:
        float: an overall similarity score.
    """
    sentences_1 = get_sentences(file_1)
    sentences_2 = get_sentences(file_2)
    adjusted_sen2 = align_sentences(sentences_1, sentences_2, threshold=threshold)
    seq_similarity = sequence_similarity(sentences_1, adjusted_sen2)
    overall_sim = 0.5 * sts_bert(file_1, file_2) + 0.5 * seq_similarity
    return overall_sim

def calculate_precision_recall(groundt, generated):
    """
    Calculate precision and recall based on set similarity of aligned sentences.

    Args:
        ground_truth (list): List of sentences from the ground truth.
        generated (list): List of sentences from the generated text.

    Returns:
        tuple: (precision, recall)
    """
    intersection = set(groundt).intersection(set(generated))
    precision = len(intersection) / len(generated) if generated else 0
    recall = len(intersection) / len(groundt) if groundt else 0
    return precision, recall


""" this function takes two texts as input and return precision and recall: text1 - original, text2 - generated """
def get_simple_kpis(list1,list2):
    matrix = create_matrix(list1,list2,"bert")
    recall = find_recall(matrix,0.5)
    precision = find_precision(matrix,0.5)
    return recall, precision

