import codecs
import re
import sys

import numpy
from pandas import DataFrame
from pkg_resources import resource_listdir, resource_string
from sklearn.cross_validation import KFold
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


def get_emails(classification):
    package = 'hammerspam.resources'

    for file in resource_listdir(package, classification):
        try:
            email = resource_string(f'{package}.{classification}', file)
            email = codecs.decode(email, 'utf-8', errors='ignore')
            email = re.split(r'^[\r\n]{1,2}', email, maxsplit=1, flags=re.M)
            email = email[1].strip()
            email = re.sub('<[^<]+?>', '', email)
            yield file, email
        except IndexError:
            print(f'Failed to parse {file}.', file=sys.stderr)
        except IsADirectoryError:
            print(f'Skipping directory {file}.', file=sys.stderr)


def main():
    indexes = []
    rows = []
    for file, text in get_emails('ham'):
        indexes.append(file)
        rows.append({'text': text, 'class': 'ham'})

    for file, text in get_emails('spam'):
        indexes.append(file)
        rows.append({'text': text, 'class': 'spam'})

    data_frame = DataFrame(data=rows, index=indexes)
    data_frame = data_frame.reindex(numpy.random.permutation(data_frame.index))

    pipeline = Pipeline([
        ('count_vectorizer', CountVectorizer(ngram_range=(1, 2))),
        ('classifier', MultinomialNB())
    ])

    k_fold = KFold(n=len(data_frame), n_folds=6)
    scores = []
    confusion = numpy.array([[0, 0], [0, 0]])
    for train_indices, test_indices in k_fold:
        train_text = data_frame.iloc[train_indices]['text'].values
        train_y = data_frame.iloc[train_indices]['class'].values.astype(str)

        test_text = data_frame.iloc[test_indices]['text'].values
        test_y = data_frame.iloc[test_indices]['class'].values.astype(str)

        pipeline.fit(train_text, train_y)
        predictions = pipeline.predict(test_text)

        confusion += confusion_matrix(test_y, predictions)
        score = f1_score(test_y, predictions, pos_label='spam')
        scores.append(score)

    joblib.dump(pipeline, 'hammerspam/resources/models/model.pkl', compress=1)

    print('Total emails classified:', len(data_frame))
    print('Score:', sum(scores) / len(scores))
    print('Confusion matrix:')
    print(confusion)


if __name__ == '__main__':
    main()
