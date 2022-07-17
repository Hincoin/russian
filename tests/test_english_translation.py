import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../")
target = __import__("openrussian")
import unittest

class TestEnglishTranslations(unittest.TestCase):
	def test_basic_english(self):
		''' Test that basic english words can convert to openrussian links'''

		words = {
			'rice' : 'рис',
			'car' : 'машина',
			'flower' : 'цветок',
			'pen' : 'ручка',
			'city' : 'город'
		}

		for en,ru in words.items():
			link, _ = target.russify_words_impl([en])[0]
			self.assertTrue(ru in link, "{} failed... {} is not in {}".format(en, ru, link))

	


if __name__ == '__main__':
	unittest.main()
