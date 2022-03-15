import unittest

from textflint.common import logger
from textflint.input.dataset import Dataset
from textflint.generation.generator.nli_generator import NLIGenerator

sample1 = {'hypothesis': 'MR zhang has 10 students',
        'premise': 'Mr zhang has 20 students',
        'y': 'contradiction'}
sample2 = {'hypothesis': 'They like eating apples ',
        'premise': 'They like eating apples and bananas',
        'y': 'entailment'}
sample3 = {'hypothesis': 'There are two little boys smiling.',
        'premise': 'Two little boys are smiling and laughing while one is '
                   'standing and one is in a bouncy seat',
        'y': 'entailment'}

sample4 = {'hypothesis': '! @ # $ % ^ & * ( )',
        'premise': '! @ # $ % ^ & * ( )',
        'y': 'neutral'}

data_samples = [sample1, sample2, sample3, sample4]
dataset = Dataset(task='NLI')
dataset.load(data_samples)
gene = NLIGenerator()


class TestNLIGenerator(unittest.TestCase):

    def test_generate(self):
        # test task transformation, ignore NliOverlap because it
        # does't rely on the original data
        trans_methods = ["SwapAnt", "AddSent", "NumWord"]
        gene = NLIGenerator(trans_methods=trans_methods,
                            sub_methods=[])
        for original_samples, trans_rst, trans_type in gene.generate(dataset):

            for index in range(len(original_samples)):
                logger.info(original_samples[index].dump())
                logger.info(trans_rst[index].dump())
                # test whether the sample changed or not
                self.assertTrue(original_samples[index].hypothesis.field_value
                                != trans_rst[index].hypothesis.field_value or
                                original_samples[index].premise.field_value
                                != trans_rst[index].premise.field_value)

                # NliAntonymSwap makes the label to be 'contradiction'
                if trans_type == 'SwapAnt':
                    self.assertEqual('contradiction',
                                     trans_rst[index].y.field_value)

                # NliLength will add a sentence to hypothesis so
                # is longer than before
                if trans_type == 'AddSent':
                    self.assertTrue(
                        len(trans_rst[index].hypothesis.words)
                        > len(original_samples[index].hypothesis.words))

        # test part of UT transformations
        gene = NLIGenerator(trans_methods=['WordCase'],
                            sub_methods=[])
        for original_samples, trans_rst, trans_type in gene.generate(dataset):
            self.assertEqual(4, len(original_samples))
            for index in range(len(original_samples)):
                for trans_word, ori_word in \
                        zip(trans_rst[index].get_words('hypothesis'),
                        original_samples[index].get_words('hypothesis')):
                    self.assertEqual(trans_word, ori_word.upper())
                for trans_word, ori_word in \
                        zip(trans_rst[index].get_words('premise'),
                            original_samples[index].get_words('premise')):
                    self.assertEqual(trans_word, ori_word.upper())
        gene = NLIGenerator(
            trans_methods=['SwapNum'], sub_methods=[])
        for original_samples, trans_rst, trans_type in gene.generate(dataset):
            self.assertEqual(1, len(original_samples))
            for index in range(len(original_samples)):
                for trans_word, ori_word in \
                        zip(trans_rst[index].get_words('hypothesis'),
                            original_samples[index].get_words('hypothesis')):
                    if ori_word.isdigit():
                        self.assertTrue(ori_word != trans_word)
                for trans_word, ori_word in \
                        zip(trans_rst[index].get_words('premise'),
                            original_samples[index].get_words('premise')):
                    if ori_word.isdigit():
                        self.assertTrue(ori_word != trans_word)

        # test wrong trans_methods
        gene = NLIGenerator(
            trans_methods=["wrong_transform_method"],
            sub_methods=[])
        self.assertRaises(ValueError, next, gene.generate(dataset))
        gene = NLIGenerator(trans_methods=["AddSubtree"],
                            sub_methods=[])
        self.assertRaises(ValueError, next, gene.generate(dataset))
        gene = NLIGenerator(trans_methods="OOV", sub_methods=[])
        self.assertRaises(ValueError, next, gene.generate(dataset))


if __name__ == "__main__":
    unittest.main()
