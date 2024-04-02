import kenlm  
from request import ModelRequest, ModelUpdateRequest
import Levenshtein

from symspellpy import SymSpell, Verbosity

from collections import Counter

model_paths = {
    'ory': '5gram_model.bin',
    'eng': '5gram_model_eng.bin'
}

vocab_paths = {
    'ory': 'lexicon.txt',
    'eng': 'lexicon_eng.txt'
}

freq_dict_paths = {
    'ory': 'freq_dict.txt',
    'eng': 'freq_dict_eng.txt'
}


class TextCorrector:
    def __init__(self, model_paths, vocab_paths, freq_dict_paths):
        # Initialize both models and vocabularies
        self.models = {
            'ory': kenlm.Model(model_paths['ory']),
            'eng': kenlm.Model(model_paths['eng'])
        }
        self.vocabs = {
            'ory': self.create_vocab_lexicon(vocab_paths['ory']),
            'eng': self.create_vocab_lexicon(vocab_paths['eng'])
        }

        self.symspell_models = {
            'ory': self.create_symspell_model(freq_dict_paths['ory']),
            'eng': self.create_symspell_model(freq_dict_paths['eng'])
        }
        # Set the default language
        self.set_language('ory')

    def set_language(self, lang):
        # Switch the model and vocabulary based on language
        self.model = self.models[lang]
        self.vocab = self.vocabs[lang]
        self.symspell_model = self.symspell_models[lang]

    def create_vocab_lexicon(self, lexicon_path):
        vocabulary = []
        with open(lexicon_path, 'r', encoding='utf-8') as file:
            for line in file:
                word = line.split()[0]
                vocabulary.append(word)
        return vocabulary

    def create_symspell_model(self, freq_dict_path):
        sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        sym_spell.load_dictionary(freq_dict_path, term_index=0, count_index=1, separator=' ')
        return sym_spell

    # def generate_candidates(self, word, max_distance=1):
    #     len_range = range(len(word) - max_distance, len(word) + max_distance + 1)
    #     filtered_vocab = [vocab_word for vocab_word in self.vocab if len(vocab_word) in len_range]
    #     return [vocab_word for vocab_word in filtered_vocab if 0 <= Levenshtein.distance(word, vocab_word) <= max_distance]

    def generate_candidates(self, word, max_distance=1):
        suggestions = self.symspell_model.lookup(word, Verbosity.CLOSEST, max_distance)
        return [suggestion.term for suggestion in suggestions]

    def beam_search(self, chunk, BEAM_WIDTH=5, SCORE_THRESHOLD=1.5, max_distance=1):
        original_score = self.model.score(' '.join(chunk))

        initial_candidates = self.generate_candidates(chunk[0], max_distance=1)
        if not initial_candidates:
            initial_candidates = [chunk[0]]

        beam = [{'sentence': candidate, 'score': self.model.score(candidate)} for candidate in initial_candidates]
        beam = sorted(beam, key=lambda x: x['score'], reverse=True)[:BEAM_WIDTH]

        for word in chunk[1:]:
            candidates = self.generate_candidates(word, max_distance=1)
            if not candidates:
                candidates = [word]

            new_beam = []

            for candidate in candidates:
                for beam_sentence in beam:
                    new_sentence = beam_sentence['sentence'] + ' ' + candidate
                    is_valid = all([1 >= Levenshtein.distance(w1, w2) for w1, w2 in zip(new_sentence.split(), chunk)])
                    if is_valid:
                        score = self.model.score(new_sentence)
                        new_beam.append({'sentence': new_sentence, 'score': score})

            beam = sorted(new_beam, key=lambda x: x['score'], reverse=True)[:BEAM_WIDTH]

        if (beam[0]['score'] - original_score) < SCORE_THRESHOLD:
            return ' '.join(chunk)

        return beam[0]['sentence']

    def correct_text_with_beam_search(self, text, BEAM_WIDTH=5, SCORE_THRESHOLD=1.5, max_distance=1):
        words = text.split()
        corrected_sentences = []

        chunks = [words[i:i + 5] for i in range(0, len(words), 5)]
        
        for chunk in chunks:
            best_sentence = self.beam_search(chunk, BEAM_WIDTH, SCORE_THRESHOLD, max_distance)
            corrected_sentences.append(best_sentence)

        return ' '.join(corrected_sentences)
    
    def load_freq_dict(self, freq_dict_path):
        freq_dict = {}
        with open(freq_dict_path, 'r') as f:
            for line in f:
                word, freq = line.split()
                freq_dict[word] = int(freq)
        return freq_dict
    
    def make_updation_counter(self, text):

        if type(text) == list:
            text = ' '.join(text)

        # remove punctuations from the text
        text = ''.join(e for e in text if e.isalnum() or e.isspace())
        words = text.split()

        # create a dictionary of words and their frequencies
        dict = Counter(words)

        return dict
    
    def update_symspell_model(self, lang, text):
        # update the frequency dictionary
        current_freq_dict_counter = Counter(self.load_freq_dict(freq_dict_paths[lang]))
        new_freq_dict_counter = self.make_updation_counter(text)

        # merge the two frequency dictionaries
        freq_dict_counter = current_freq_dict_counter + new_freq_dict_counter

        freq_dict = {}
        for word, freq in freq_dict_counter.items():
            freq_dict[word] = int(freq)

        with open(freq_dict_paths[lang], 'w') as f:
            for word, freq in freq_dict.items():
                f.write(word + ' ' + str(freq) + '\n')

        # retrain the model with the updated frequency dictionary
        self.symspell_models[lang] = self.create_symspell_model(freq_dict_paths[lang])

        return 'Model updated successfully'


class Model():
    def __init__(self, context, model_paths, vocab_paths, freq_dict_paths):
        self.context = context
        self.text_corrector = TextCorrector(model_paths, vocab_paths, freq_dict_paths)

    async def inference(self, request: ModelRequest):
        # Set the correct language model based on the request
        self.text_corrector.set_language(request.lang)

        corrected_text = self.text_corrector.correct_text_with_beam_search(
            request.text,
            BEAM_WIDTH=request.BEAM_WIDTH,
            SCORE_THRESHOLD=request.SCORE_THRESHOLD,
            max_distance=request.max_distance
        )
        return corrected_text
    
    async def update_symspell(self, request: ModelUpdateRequest):
        # Set the correct language model based on the request
        self.text_corrector.set_language(request.lang)

        # Update the model with the new data
        self.text_corrector.update_symspell_model(request.lang, request.text)

        return 'Model updated successfully'
