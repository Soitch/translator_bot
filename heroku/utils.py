import pickle
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import WordPunctTokenizer
from fairseq.models.transformer import TransformerModel
# from fairseq.models.lstm import LSTMModel

stemmer = SnowballStemmer('russian')
tokenizer = WordPunctTokenizer()

translator_text = {'khak_rus': '*_Хакас\-орыс_*\nСӧс/чоохтағ пазыңар:',
                   'rus_khak': '*_Русско\-хакасский_*\nВведите слово/предложение:'}

many_symbols_text = {'khak_rus': '*_❗️ Иң кӧп символларның саны \= 150_*',
                     'rus_khak': '*_❗️ Максимальное количество символов \= 150_*'}


def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


word_dict_khak_rus = load_obj('files/word_dict_khak2ru')
word_dict_rus_khak = load_obj('files/word_dict_ru2khak')
word_dict = {'khak_rus': word_dict_khak_rus,
             'rus_khak': word_dict_rus_khak}


khak_rus = TransformerModel.from_pretrained('files',
                                            checkpoint_file='khak2ru_bt.pt',
                                            data_name_or_path='files',
                                            bpe='subword_nmt',
                                            bpe_codes='files/bpe.codes')

rus_khak = TransformerModel.from_pretrained('files',
                                            checkpoint_file='ru2khak_bt.pt',
                                            data_name_or_path='files',
                                            bpe='subword_nmt',
                                            bpe_codes='files/bpe.codes')


translator_model = {'khak_rus': khak_rus,
                    'rus_khak': rus_khak}


def translate_word(word, translator):
    result = None
    if word in word_dict[translator]:
        result = word_dict[translator][word]
    elif translator == 'rus_khak':
        root = stemmer.stem(word)
        if root in word_dict[translator]:
            result = word_dict[translator][root]

    if type(result) is dict:
        output = []
        for input_word in result:
            translation = ', '.join(result[input_word])
            output.append(f'{input_word}: {translation}')
        output_sentence = '\n'.join(output)
    elif type(result) is set:
        output_sentence = ', '.join(result)
    elif result is None:
        output_sentence = f'*{word}'
    else:
        output_sentence = result

    return output_sentence
