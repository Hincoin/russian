import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
target = __import__("openrussian")
import unittest


class TestWordForms(unittest.TestCase):
	def test_past_tense_verbs(self):
		''' Test that we can correctly resolve past-tense verbs into their infinitive form. '''
		past_tense = {
			'говорил' : 'говорить',
			'говорила' : 'говорить',
			'говорили' : 'говорить',
			'пошли' : 'пойти',
			'закончил' : 'закончить' 
		}

		for past, infinitive in past_tense.items():
			link, _ = target.russify_words_impl([past])[0]

			self.assertTrue(infinitive in link, "{} failed.. {} is not in {}".format(past, infinitive, link))

	def test_future_tense_verbs(self):
		''' Test that we can correctly resolve future tense verbs into their perfective form.'''
		future_tense = {
			'поговорю' : 'поговорить',
			'поговоришь' : 'поговорить',
			'поговорит' : 'поговорить',
			'пойдём' : 'пойти',
			'закончите' : 'закончить' 
		}

		for fut, infinitive in future_tense.items():
			link, _ = target.russify_words_impl([fut])[0]

			self.assertTrue(infinitive in link, "{} failed.. {} is not in {}".format(fut, infinitive, link))

	def test_case_changes(self):
		''' Test that we can resolve case changes of a word into its dictionary form '''
		case_changes = {
			'красивого' : 'красивый',
			'красивому'	: 'красивый',
			'красивым' : 'красивый',
			'красивую' : 'красивый',
			'рисы' : 'рис',
			'рисов' : 'рис',
			'рисом' : 'рис'
		}

		for case, nominative in case_changes.items():
			link, _ = target.russify_words_impl([case])[0]
			self.assertTrue(nominative in link, "{} failed.. {} is not in {}".format(case, nominative, link))



if __name__ == '__main__':
	unittest.main()

