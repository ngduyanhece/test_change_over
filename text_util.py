import re
import os
import CaboCha
import pandas
from nltk.corpus import stopwords
from py_rake3 import build_stop_word_regex
# from janome.tokenizer import Tokenizer
import time


def remove_special_chars(text):
    remove_tag = r'。|◎|■|▼|◆|▽|・|･|\.|●|①|②|③|;|,|、|★|☆|＊|\+|◇|:|※|／／｜～|：' \
                 r'|－|-|\*|…|│|＋|←|→|\?|└|（※）|「|」|⇔|「|」|『|』|\u3000|' \
                 r'!|♪|！|~|％|%|～|\?|\／|\/|&|=|⇒|└|xx|>|<|\（|\）|\)|\(|【|】|＜|＞' \
                 r'|≪|≫|\[|\]|\r|\n|\t|\'|_|e.g|\{|\}|\#|\@|\$'
    text = re.sub(remove_tag, ' ', text)
    text = re.sub('\s\s+', ' ', text.strip())
    return text

def only_cabocha_tokenzie(text):
    #print("cabocha")
    # start_time=time.clock()
    text=remove_special_chars(text)
    c = CaboCha.Parser()
    tree = c.parse(text)
    text_tokens = []
    for i in range(tree.token_size()):
        text_token = tree.token(i)
        text_item = text_token.surface
        # print("surface",text_item)
        if len(text_item) >= 2 :
            text_tokens.append(text_item)
        else:
            if isEng(text_item):
                text_tokens.append(text_item)
    # print("cabocha_tokenize",time.clock()-start_time)
    # print(text_tokens)
    return text_tokens  # [x for x in text_tokens if len(x)>0]

def cabocha_tokenize(text):
    text = re.sub("[A-Za-z]", " ", (text.strip()).lower())
    stopword_pattern = build_stop_word_regex(stopwords.words('japanese'))
    tmp = re.sub(stopword_pattern, '', text.strip())
    c = CaboCha.Parser()
    # tree = c.parse(tmp)
    text_tokens = []
    # for i in range(tree.token_size()):
    #     text_token = tree.token(i)
    #     text_item = text_token.surface
    #     if len(text_item) > 1 and text_item not in text_tokens:
    #         text_tokens.append(text_item)
    return text_tokens  # [x for x in text_tokens if len(x)>0]


def isEng(segment):
    hasJ = False
    segment = re.sub('\s+', '', segment)
    for cha in segment:
        if (ord(cha) > 128):
            hasJ = True
            break
    return (not hasJ)


def cabocha_tokenize_je(text):
    # text = re.sub("[A-Za-z]", " ", (text.strip()).lower())
    stopword_pattern = build_stop_word_regex(stopwords.words('japanese'))
    tmp = re.sub(stopword_pattern, '', text.strip())
    # c = CaboCha.Parser()
    # tree = c.parse(tmp)
    text_tokens = []
    # for i in range(tree.token_size()):
    #     text_token = tree.token(i)
    #     text_item = text_token.surface
    #     if len(text_item) >= 3:
    #         text_tokens.append(text_item)
    #     else:
    #         if (isEng(text_item)):
    #             text_tokens.append(text_item)

    return text_tokens  # [x for x in text_tokens if len(x)>0]


# def janome_tokenize(text):
#     text = re.sub("[A-Za-z]", " ", (text.strip()).lower())
#     stopword_pattern = build_stop_word_regex(stopwords.words('japanese'))
#     tmp = re.sub(stopword_pattern, '', text.strip())
#     t = Tokenizer()
#     tokens = t.tokenize(text, wakati=True)
#     # tree = c.parse(tmp)
#     # text_tokens = []
#     # for i in range(tree.token_size()):
#     #     text_token = tree.token(i)
#     #     text_item = text_token.surface
#     #     text_tokens.append(text_item)
#     return tokens  # [x for x in text_tokens if len(x)>0]

def split_to_sentences(para):
    paragraphs = []
    paragraph = trim_paragraph(para)
    # print("origin", paragraph)
    paragraph, sentences = remove_parentheses(paragraph)
    new_sentences = []
    recursive_split_paragraph(paragraph, new_sentences)
    sentences = sentences + new_sentences

    # sentences = [x for x in sentences if len(x) > 1]
    paragraphs = paragraphs + sentences
    return paragraphs


def split2sentences(para):
    paras = []
    # para = remove_numbers(para)
    paras = remove_special_chars(para).split(" ")
    return paras


def trim_paragraph(paragraph):
    paragraph = paragraph.strip()
    paragraph = re.sub(r'\s+', '', paragraph)
    paragraph = remove_conjunction(paragraph)
    paragraph = re.sub(r'【|】', ' ', paragraph)
    paragraph = paragraph.replace("｜", ",")
    paragraph = paragraph.replace("&amp;", "&")
    paragraph = paragraph.replace("&AMP;", "&")
    return paragraph


def remove_conjunction(text):
    text = re.sub(r'(＜.*?＞)|(《.*?》)|(≪.*?≫)', '', text)  # (【.*?】)|(「.*?」)|
    return text


def remove_parentheses(paragraph):
    words_in_parentheses = []
    tag_key = re.compile('\（(.*?)\）')  # .*?
    tag_key1 = re.compile('\((.*?)\）')
    tag_key2 = re.compile('\((.*?)\)')
    # tag_key3= re.compile('\（(.*?)\）')
    word_in_bracket = tag_key.findall(paragraph)
    if len(word_in_bracket) == 0:
        word_in_bracket = tag_key1.findall(paragraph)
    if len(word_in_bracket) == 0:
        word_in_bracket = tag_key2.findall(paragraph)
    # if len(word_in_bracket)==0:
    #     word_in_bracket=tag_key3.findall(paragraph)
    if len(word_in_bracket) > 0:
        paragraph = re.sub("\（|\）|\)|\(", "", paragraph)
        # print(word_in_bracket)
        for word in word_in_bracket:
            paragraph = paragraph.replace(word, "")

        for word in word_in_bracket:
            # word = re.sub(r'[+-]?\d+(?:\.\d+)?\w*\/*\w*％*%*', "", word)
            sub_word_in_brackets = []
            recursive_split_paragraph(word, sub_word_in_brackets)
            # re.sub('。|;|,|、|■|◇|:|・|！', ' ', word).split(" ")

            if (sub_word_in_brackets):
                words_in_parentheses = words_in_parentheses + sub_word_in_brackets
            else:
                words_in_parentheses.append(word)
                # print("word_in_bracket", word)
        # print("sentence after remove", words_in_parentheses)

        slash_tag = r'\w{2}\／\w{2}|\w{2}\/\w{2}|\w{2}/\w{2}'
        slash_tag_remove = r'\／|\/'
        valid_words = []
        for word in words_in_parentheses:
            if not word.isalpha():
                words_in_parentheses.remove(word)
            if len(re.findall(slash_tag, word)) > 0:
                # print("find slash")
                if word in words_in_parentheses:
                    words_in_parentheses.remove(word)
                tems = re.sub(slash_tag_remove, " ", word).split(" ")
                for tem in tems:
                    valid_word = remove_special_characters(tem)
                    valid_words.append(valid_word)
        words_in_parentheses = words_in_parentheses + valid_words
    return paragraph, words_in_parentheses


def recursive_split_paragraph(paragraph, valid_sentences, remove_number_bool=True):
    # print(paragraph)
    remove_tag = r'。|◎|■|▼|◆|▽|・|･|\.|●|①|②|③|;|,|、|★|☆|＊|\+|◇|:|※|／／｜～|：|－|-|\*|…|│|＋|←|→|\?|└|（※）|\d{1,}\)|「|」|⇔'  # |
    # r'、|。|…|・|･|\.|●|◆|▼|①|②|③|;|,|、|■|◇|:|※|～|－'
    slash_tag = r'\w{2}／\w{2}|\w{2}/\w{2}'
    slash_tag_remove = r'／|/'
    search_result = re.findall(remove_tag, paragraph)
    # print("search result",search_result)
    # lambda x,paragraph:paragraph.replace(x," "),search_result

    if len(search_result) > 0:
        paragraph = re.sub(remove_tag, " ", paragraph)
        sentences = paragraph.split(" ")
        if sentences:
            for sentence in sentences:
                recursive_split_paragraph(sentence, valid_sentences)
    else:
        # print(paragraph)
        if remove_number_bool:
            paragraph = remove_number_parts(paragraph)
        # print(paragraph)
        paragraph = remove_special_characters(paragraph)
        # print(paragraph)
        if match_number(paragraph):
            if remove_number_bool:
                paragraph = re.sub(r'[+-]?\d+(?:\.\d+)?:*\％*', "", paragraph)
                # print(paragraph)
        slash_tag_results = re.findall(slash_tag, paragraph)
        if len(slash_tag_results) > 0:
            for slash_result in slash_tag_results:
                # print("slash tag",slash_result)
                slash_result = slash_result.strip()
                if len(slash_result) == 3:
                    valid_sentences.append(slash_result)
                    paragraph = paragraph.replace(slash_result, "")
            tems = re.sub(slash_tag_remove, " ", paragraph).split(" ")
            for tem in tems:
                valid_sentences.append(tem)
                # print(paragraph)
        else:
            valid_sentences.append(paragraph)
            # print(valid_sentences)


def remove_special_characters(sentence):
    if "！" in sentence:
        return ""
    remove_characters = r'!|♪|！|~|％|%|～|ec\～|\.|\?|\/|&|=|⇒|└|xx|>|<'
    # r'!|♪|！|★|☆|＊|~|％|\％|%|％|\％|\*|\-|-|\/'
    remove_tag = re.compile(remove_characters)
    sentence = re.sub(remove_characters, '', sentence)
    return sentence


def remove_number_parts(sentence):
    remove_num_regex = r'\：\s?[+-]?\d+(?:\.\d+)?\w{1}％*%*|[+-]?\d+(?:\.\d+)?\w*％*%*\：'
    remove_num_str = re.findall(remove_num_regex, sentence)
    if remove_num_str:
        # print("exist num", sentence)
        for pattern in remove_num_str:
            sentence = sentence.replace(pattern, "")
    return sentence


def match_number(sentence):
    num_regex = r'w*[+-]?\d+(?:\.\d+)?\w*'
    return len(re.findall(num_regex, sentence)) > 0


def remove_numbers(text: str):
    num_regex = r'\：\s?[+-]?\d+(?:\.\d+)?\w{1}％*%*|[+-]?\d+(?:\.\d+)?\w*％*%*\：|[+-]?\d+(?:\.\d+)?|[+-]?\d+(?:\.\d+)?'
    return re.sub(num_regex, '', text)


def isEng(segment):
    hasJ = False
    segment = re.sub('\s+', '', segment)
    for cha in segment:
        if (ord(cha) > 128):
            hasJ = True
            break
    return (not hasJ)


def only_cabocha_tokenzie(text):
    text = remove_special_chars(text)
    # start_time = time.clock()
    # c = CaboCha.Parser()
    # tree = c.parse(text)
    text_tokens = []
    # for i in range(tree.token_size()):
    #     text_token = tree.token(i)
    #     text_item = text_token.surface
    #     if len(text_item) >= 3 or isEng(text_item):
    #         text_tokens.append(text_item)
    # print("cabocha tokenzie", (time.clock() - start_time) / 60)
    return text_tokens  # [x for x in text_tokens if len(x)>0]
