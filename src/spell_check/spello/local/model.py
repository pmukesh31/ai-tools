from request import ModelRequest
from spello.model import SpellCorrectionModel

from collections import Counter


freq_dict_paths = {
    'ory': 'freq_dict.txt',
    'eng': 'freq_dict_eng.txt'
}

spello_model_paths = {
    'ory': 'spello_model.pkl',
    'eng': 'spello_model_eng.pkl'
}

class TextCorrector:
    # def __init__(self, freq_dict_paths):
    def __init__(self, freq_dict_paths):
        self.models = {
            'ory': self.create_spello_model(freq_dict_paths['ory'], 'or'),
            'eng': self.create_spello_model(freq_dict_paths['eng'], 'en')
        }

        self.freq_dict_paths = freq_dict_paths

        # Set the default language
        self.set_language('ory')

    def set_language(self, lang):
        # Switch the model and vocabulary based on language
        self.model = self.models[lang]

    def load_freq_dict(self, freq_dict_path):
        freq_dict = {}

        # read the frequency dictionary file
        with open(freq_dict_path, 'r') as f:
            freq_file = f.read().splitlines()

        # create a dictionary from the frequency file
        for line in freq_file:
            word, freq = line.split()
            freq_dict[word] = int(freq)

        return freq_dict

    def create_spello_model(self, freq_dict_path, language):
        # load the frequency dictionary
        freq_dict = self.load_freq_dict(freq_dict_path)

        # create the spello model and train it
        spello_model = SpellCorrectionModel(language=language)
        spello_model.train(freq_dict)
        # print('Loading model')

        return spello_model

    def make_correct_text(self, text, correction_dict):
        corrected_list = text.split()
        for i in range(len(corrected_list)):
            word = corrected_list[i]
            if word in correction_dict:
                corrected_list[i] = correction_dict[word]

        corrected_text = ' '.join(corrected_list)

        return corrected_text

    def correct_text_with_spello(self, text):
        result = self.model.spell_correct(text)

        corrected_text = result['spell_corrected_text']
        correction_dict = result['correction_dict']

        corrected_text = self.make_correct_text(corrected_text, correction_dict)

        return corrected_text

    def make_updation_counter(self, text):

        if type(text) == list:
            text = ' '.join(text)

        # remove punctuations from the text
        text = ''.join(e for e in text if e.isalnum() or e.isspace())
        words = text.split()

        # create a dictionary of words and their frequencies
        dict = Counter(words)

        return dict

    def update_model(self, lang, text):
        # update the frequency dictionary
        current_freq_dict_counter = Counter(self.load_freq_dict(self.freq_dict_paths[lang]))
        new_freq_dict_counter = self.make_updation_counter(text)

        # merge the two frequency dictionaries
        freq_dict_counter = current_freq_dict_counter + new_freq_dict_counter

        freq_dict = {}
        for word, freq in freq_dict_counter.items():
            freq_dict[word] = int(freq)

        with open(self.freq_dict_paths[lang], 'w') as f:
            for word, freq in freq_dict.items():
                f.write(word + ' ' + str(freq) + '\n')

        # retrain the model with the updated frequency dictionary
        self.models[lang].train(freq_dict)

        return 'Model updated successfully'

class Model():
    def __init__(self, context, freq_dict_paths):
        self.context = context
        # self.text_corrector = TextCorrector(freq_dict_paths)
        self.text_corrector = TextCorrector(freq_dict_paths)

    async def inference(self, request: ModelRequest):
        # Set the correct language model based on the request
        self.text_corrector.set_language(request.lang)

        corrected_text = self.text_corrector.correct_text_with_spello(
            request.text
        )
        return corrected_text

    async def update(self, request: ModelRequest):
        # Set the correct language model based on the request
        self.text_corrector.set_language(request.lang)

        # Update the model with the new data
        self.text_corrector.update_model(request.lang, request.text)

        return 'Model updated successfully'