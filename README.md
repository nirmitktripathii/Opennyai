<a href="https://github.com/OpenNyAI/Opennyai"><img src="https://github.com/OpenNyAI/Opennyai/raw/master/asset/final-logo-01.jpeg" width="190" height="65" align="right" /></a>

# Opennyai : An efficient NLP Pipeline for Indian Legal documents

[![PyPI version](https://badge.fury.io/py/opennyai.svg)](https://pypi.org/project/opennyai/)
[![python version](https://img.shields.io/badge/Python-%3E=3.9-blue)](https://github.com/OpenNyAI/Opennyai)

Opennyai is a natural language preprocessing framework made with SpaCy. Its pipeline has achieved State-of-the-Art
performance on Named entity recognition on Indian legal NER.
Try [demo](https://huggingface.co/opennyaiorg/en_legal_ner_trf)

# 🔧 Installation

To get started using opennyai simply install it using pip by running the following line in your terminal:

```bash
pip install opennyai
```

Note: if you want to utilize spacy with GPU please install [Cupy](https://anaconda.org/conda-forge/cupy)
/[cudatoolkit](https://anaconda.org/anaconda/cudatoolkit) dependency of appropriate version. For spacy installation with
cupy refer to [page](https://spacy.io/usage)

Remember you need spacy of 3.2.4 version for models to work perfectly.

# 👩‍💻 Usage

To use the NER model you first have to select and load model from given list.

* en_legal_ner_trf (This model provides the highest accuracy)
* en_legal_ner_sm (This model provides the highest efficiency)

To download and load a model simply execute:

```python
import opennyai.ner as InLegalNER

nlp = InLegalNER.load('en_legal_ner_trf',
                      sentence_splitter_model_name='en_core_web_trf')  # available sentence splitter models are ['en_core_web_md', 'en_core_web_sm', 'en_core_web_trf']
text = 'Section 319 Cr.P.C. contemplates a situation where the evidence adduced by the prosecution for Respondent No.3-G. Sambiah on 20th June 1984'
doc = nlp(text, do_sentence_level=False,
          do_postprocess=False)  # set do_sentence_level=True if you pass whole judgement 
identified_entites = [(ent, ent.label_) for ent in doc.ents]
```

Result:

```
[(Section 319, 'PROVISION'),
 (Cr.P.C., 'STATUTE'),
 (G. Sambiah, 'RESPONDENT'),
 (20th June 1984, 'DATE')]
 ```

To get result in json format with span information:

```python
json_result = InLegalNER.get_json_from_spacy_doc(doc)
```
