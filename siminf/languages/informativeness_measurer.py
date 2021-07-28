import itertools
import numpy as np

#from GeneralizedQuantifierModel import SimplifiedQuantifierModel
from siminf.generalized_quantifier_model import SimplifiedQuantifierModel


def measure_informativeness(language, universe_size):
    utility = 0

    for state in range(universe_size):
        words_for_state = set(filter(lambda word: word.meaning[state], language))
        word_amount = len(words_for_state)

        for word in words_for_state:
            word_meaning_size = sum(word.meaning)
            utility += 1 / universe_size / word_amount / word_meaning_size

    return utility

class InformativenessMeasurer(object):

    def __init__(self, universe_size):
        self.universe_size = universe_size

    def __call__(self, language):
        return measure_informativeness(language, self.universe_size)


def distance(s1: SimplifiedQuantifierModel, s2: SimplifiedQuantifierModel):
    AminusBdec = s1.AminusB - s2.AminusB
    AandBdec = s1.AandB - s2.AandB
    BminusAdec = s1.B - s1.AandB - (s2.B - s2.AandB)
    total_increase = (s2.AminusB + s2.B) - (s1.AminusB + s1.B)

    return sum(max(var, 0) for var in [AminusBdec, AandBdec, BminusAdec, total_increase])


class SimMaxInformativenessMeasurer(object):

    def __init__(self, universe):
        self.universe = universe
        self.score = {}
        for (i1,s1),(i2,s2) in itertools.combinations(enumerate(universe),2):
            dist = distance(s1,s2)
            self.score[(i1, i2)] = 1/(dist+1)
            self.score[(i2, i1)] = 1/(dist+1)
        for index in range(len(universe)):
            self.score[(index, index)] = 1

    def __call__(self, language):
        utility = 0

        for index in range(len(self.universe)):
            words_for_state = set(filter(lambda word: word.meaning[index], language))
            word_amount = len(words_for_state)

            for word in words_for_state:
                word_meaning_size = sum(word.meaning)
                for other_index, truth_value in enumerate(word.meaning):
                    if truth_value:
                        score = self.score[(index, other_index)]
                        utility += score / len(self.universe) / word_amount / word_meaning_size

        return utility

def sum_to_one_by_row(matrix):
    #Previous method returned a copy, although here we could keep it by ref?
    matrix = matrix.copy()
    rows_sum = matrix.sum(axis = 1)
    for i in range(matrix.shape[0]):
        if rows_sum[i] == 0:
            matrix[i,:] += 1/matrix.shape[1]
        else:
            matrix[i,:] /= rows_sum[i]
    #return matrix / matrix.sum(axis = 1, keepdims = True)
    return matrix


def compute_agent_matrices(
        language, universe_size,
        num_generations,
        lambda_generation,
        prior_over_states):
    """
    Computes Hearer and Speaker matrices as per Brochhagen
    """

    # Compute first generation here.
    # Not done recursively for memory issues.
    language_size = len(language)
    hearer_matrix = np.zeros((language_size, universe_size))
    speaker_matrix = np.zeros((universe_size, language_size))

    # TODO: OPTIMIZE
    for state in range(universe_size):
        for i, word in enumerate(language):
            if word.meaning[state]:
                #TODO works because function is constant, but state is an int
                hearer_matrix[i, state] = prior_over_states(state)
                speaker_matrix[state,i] = np.exp(lambda_generation)
            else:
                hearer_matrix[i, state] = 0
                speaker_matrix[state,i] = 1

    hearer_matrix = sum_to_one_by_row(hearer_matrix)
    speaker_matrix = sum_to_one_by_row(speaker_matrix)

    # Later generations
    for generation in range(num_generations-1):
        for state in range(universe_size):
            for i in range(language_size):
                hearer_matrix[i, state], speaker_matrix[state,i] = \
                    prior_over_states(state) * speaker_matrix[state, i], \
                    np.exp(lambda_generation * hearer_matrix[i,state])

        hearer_matrix = sum_to_one_by_row(hearer_matrix)
        speaker_matrix = sum_to_one_by_row(speaker_matrix)

    return hearer_matrix, speaker_matrix

class BrochhagenInformativenessMeasurer(object):
    def __init__(self, universe, num_generations = 5, lambda_generation = 400):
        self.universe = universe
        self.num_generations = num_generations
        self.lambda_generation = lambda_generation
        self.utility_function = lambda state1, state2: 1/(1+distance(state1, state2))

        self.prior_over_states = lambda state : 1/len(universe)

    def __call__(self, language):
        informativeness = 0

        hearer_matrix, speaker_matrix = compute_agent_matrices(
            language, len(self.universe),
            self.num_generations, self.lambda_generation,
            self.prior_over_states)

        for state_index, state in enumerate(self.universe):
            for word_index, word in enumerate(language):
                for other_state_index, other_state in enumerate(self.universe):
                    if word.meaning[other_state_index]:
                        informativeness += (self.prior_over_states(state) *
                                            speaker_matrix[state_index, word_index] *
                                            hearer_matrix[word_index, other_state_index] *
                                            self.utility_function(state,other_state))

        return informativeness


def get_informativeness_measurer(name, universe):
    if name == "simmax":
        return SimMaxInformativenessMeasurer(universe)
    if name == "brochhagen":
        return BrochhagenInformativenessMeasurer(universe)
    #TODO excpetion
    assert False
