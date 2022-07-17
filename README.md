## OpenRussian link generator

Helper program to automatically add links to openrussian.org for vocab files and words. 

### Prerequisites

This python script requires the `requests` package: 

```
pip install requests
```
### Usage


#### Files
You can supply a CSV file with the `--file` switch: 

```
python3 openrussian.py --file <path_to_file>
```

A new file is written in the same path as the input. 
The new file will have `_links` appended to it. For example: 

```
 % python3 openrussian.py --file samples/A2\ verbs.csv 
 ....
 Done writing to samples/A2 verbs_links.csv
 ```
The new file is saved as `samples/A2 verbs_links.csv`.


#### Words
Alternatively, you can specify invididual words with `--word`. 
The words may be either in English or in Russian.

For example:
```
% python3 openrussian.py --word coffee               
https://en.openrussian.org/ru/кофе

% python3 openrussian.py --word coffee --word milk --word breakfast
https://en.openrussian.org/ru/кофе
https://en.openrussian.org/ru/молоко
https://en.openrussian.org/ru/завтрак
```


### Tests
Unit tests can be run from the root of the repo. E.g.:

```
% python3 -m unittest discover -s tests -v    
test_basic_english (test_english_translation.TestEnglishTranslations)
Test that basic english words can convert to openrussian links ... ok
test_case_changes (test_word_forms.TestWordForms)
Test that we can resolve case changes of a word into its dictionary form ... ok
test_future_tense_verbs (test_word_forms.TestWordForms)
Test that we can correctly resolve future tense verbs into their perfective form. ... ok
test_past_tense_verbs (test_word_forms.TestWordForms)
Test that we can correctly resolve past-tense verbs into their infinitive form. ... ok

----------------------------------------------------------------------
Ran 4 tests in 14.075s

OK
```
