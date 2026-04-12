# Summary

Publicly available IAHLT UD Hebrew Treebank's Knesset section (https://www.iahlt.org/)

# Introduction

UD_Hebrew-IAHLTknesset is a manually annotated UD Treebank of spoken Hebrew data, with approximately 67K words/2800 sentences taken from transcribed proceedings of the Israeli Parliament, the Knesset. The data contains a subset of sentences from the proceedings originally extracted for modeling factuality, and represent sometimes contiguous chunks of 100 parliament discussions, but not necessarily enitre or fully contiguous ones (see the document identifiers under `# newdoc id` annotations). Where possible, consecutive sentences are given in their original orders, but with possible gaps in the dialogue. Speaker names are provided as well.

## Compatible datasets

The HTB version used in the project was initially converted automatically, then a subset of the converted data was manually validated and adopted as a gold standard for training the model for UD parsing used in Hebrew-IAHLT. The entire parsed data has been manually edited to correct parsing errors, and was automatically QA'ed to apply corrections following updates in the schema. For a fork of UD_Hebrew-HTB (Ha'aretz newswire data) using the same annotation scheme, see:

https://github.com/IAHLT/UD_Hebrew

For an additional UD_Hebrew corpus with the same annotation scheme (Wikipedia articles), see:

https://github.com/UniversalDependencies/UD_Hebrew-IAHLTwiki

## NER annotations

The data additionally contains Named Entity annotations in the IAHLT scheme in the MISC annotation `Entity=`, illustrated in the following excerpt:

```CoNLL-U
# sent_id = 13_ptm_532410-8
# is_chairman = false
# speaker = יגאל ביבי
# turnnumber = 96
# text = בשום סקטור בעולם אין נבחר ציבור שיש לו סמכויות גדולות, בלי שום balance, בלי שום איזון, כפי שיש לראש עיר במדינת ישראל.
1-2	בשום	_	_	_	_	_	_	_	_
1	ב	ב	ADP	ADP	_	3	case	_	_
2	שום	שום	DET	DET	Definite=Cons	3	det	_	_
3	סקטור	סקטור	NOUN	NOUN	Gender=Masc|Number=Sing	6	obl	_	_
4-5	בעולם	_	_	_	_	_	_	_	_
4	ב	ב	ADP	ADP	Definite=Def|PronType=Art	5	case	_	_
5	עולם	עולם	NOUN	NOUN	Gender=Masc|Number=Sing	3	nmod	_	_
6	אין	אין	VERB	VERB	Polarity=Neg	0	root	_	_
7	נבחר	נבחר	NOUN	NOUN	Definite=Cons|Gender=Masc|Number=Sing	6	nsubj	_	_
8	ציבור	ציבור	NOUN	NOUN	Gender=Masc|Number=Sing	7	compound	_	_
9-10	שיש	_	_	_	_	_	_	_	_
9	ש	ש	SCONJ	SCONJ	_	10	mark	_	_
10	יש	יש	VERB	VERB	Polarity=Pos	7	acl:relcl	_	_
11-12	לו	_	_	_	_	_	_	_	_
11	ל	ל	ADP	ADP	_	12	case	_	_
12	ו	הוא	PRON	PRON	Gender=Masc|Number=Sing|Person=3|PronType=Prs	10	obl	_	_
13	סמכויות	סמכות	NOUN	NOUN	Gender=Fem|Number=Plur	10	nsubj	_	_
14	גדולות	גדול	ADJ	ADJ	Gender=Fem|Number=Plur	13	amod	_	SpaceAfter=No
15	,	,	PUNCT	PUNCT	_	18	punct	_	_
16	בלי	בלי	ADP	ADP	_	18	case	_	_
17	שום	שום	DET	DET	Definite=Cons	18	det	_	_
18	balance	balance	NOUN	NOUN	Gender=Masc|Number=Sing	10	obl	_	SpaceAfter=No
19	,	,	PUNCT	PUNCT	_	22	punct	_	_
20	בלי	בלי	ADP	ADP	_	22	case	_	_
21	שום	שום	DET	DET	Definite=Cons	22	det	_	_
22	איזון	איזון	NOUN	NOUN	Gender=Masc|Number=Sing	18	conj	_	SpaceAfter=No
23	,	,	PUNCT	PUNCT	_	26	punct	_	_
24	כפי	כפי	SCONJ	SCONJ	_	26	mark	_	_
25-26	שיש	_	_	_	_	_	_	_	_
25	ש	ש	SCONJ	SCONJ	_	24	fixed	_	_
26	יש	יש	VERB	VERB	Polarity=Pos	10	advcl	_	_
27-28	לראש	_	_	_	_	_	_	_	_
27	ל	ל	ADP	ADP	_	28	case	_	_
28	ראש	ראש	NOUN	NOUN	Definite=Cons|Gender=Masc|Number=Sing	26	obl	_	Entity=(TTL
29	עיר	עיר	NOUN	NOUN	Gender=Fem|Number=Sing	28	compound	_	Entity=TTL)
30-31	במדינת	_	_	_	_	_	_	_	_
30	ב	ב	ADP	ADP	_	31	case	_	_
31	מדינת	מדינה	NOUN	NOUN	Definite=Cons|Gender=Fem|Number=Sing	28	nmod	_	_
32	ישראל	ישראל	PROPN	PROPN	_	31	compound	_	Entity=(GPE)|SpaceAfter=No
33	.	.	PUNCT	PUNCT	_	6	punct	_	_
```
Entity types cover the following categories:

  * ANG - language 
  * DUC - product 
  * EVE - event 
  * FAC - facility 
  * GPE - geo-political entity 
  * LOC - location 
  * ORG - organization 
  * PER - person 
  * TIMEX - time expression 
  * TTL - title
  * WOA - work of art 
  * MISC - miscellaneous 

# Acknowledgments

We would like to thank Gili Golden, Shuly Wintner, and Ella Rabinovich for making the original raw data available. We also thank all the people who contributed to this corpus: Amir Zeldes, Hilla Merhav, Israel Landau, Netanel Dahan, Nick Howell, Noam Ordan, Omer Strass, Shira Wigderson, Yael Minerbi and Yifat Ben Moshe.

## References

For academic citations of the IAHLT UD treebanks, please use:

Zeldes, Amir, Nick Howell, Noam Ordan and Yifat Ben Moshe (2022) [A Second Wave of UD Hebrew Treebanking and Cross-Domain Parsing](https://arxiv.org/abs/2210.07873). In: *Proceedings of EMNLP 2022*. Abu Dhabi, UAE, 4331-4344.

```bibtex
@InProceedings{ZeldesHowellOrdanBenMoshe2022,
  author    = {Amir Zeldes and Nick Howell and Noam Ordan and Yifat Ben Moshe},
  booktitle = {Proceedings of {EMNLP} 2022},
  title     = {A Second Wave of {UD} {H}ebrew Treebanking and Cross-Domain Parsing},
  year      = {2022},
  pages     = {4331--4344},
  address   = {Abu Dhabi, UAE},
  url       = {https://aclanthology.org/2022.emnlp-main.292/},
}
```

For academic citations of the underlying Knesset corpus, please use:

Goldin, Gili, Nick Howell, Noam Ordan, Ella Rabinovich, and Shuly Wintner (2024) [The Knesset Corpus: An Annotated Corpus of Hebrew Parliamentary Proceedings](https://arxiv.org/abs/2405.18115).



# Changelog

* 2025-11-15 v.217
  * Added ExtPos and corrections

* 2024-11-15 v2.15
  * FEATS consistency changes with other Hebrew treebanks
  * Changed :tmod and :npmod subtypes to :unmarked with TemporalNPAdjunct=Yes in misc to preserve tmod info
  * Construction annotations in the [UCxn](https://github.com/LeonieWeissweiler/UCxn) framework added to MISC

     This release adds rule-based annotations of Interrogatives, Conditionals, Existentials, and NPN (noun-preposition-noun) constructions on the head of the respective phrase, plus construction elements. The UCxn v1 notation and categories are documented [here](https://github.com/LeonieWeissweiler/UCxn/blob/main/docs/UCxn-v1.pdf).
* 2024-11-15 v2.15
  * Initial release in Universal Dependencies.


<pre>
=== Machine-readable metadata (DO NOT REMOVE!) ================================
Data available since: UD v2.15
License: CC BY-SA 4.0
Includes text: yes
Parallel: no
Genre: government spoken
Lemmas: manual native
UPOS: manual native
XPOS: not available
Features: manual native
Relations: manual native
Contributors: Zeldes, Amir; Algom, Avner; Ordan, Noam; Ben Moshe, Yifat; Howell, Nick; Wigderson, Shira; Strass, Omer; Landau, Israel; Dahan, Netanel; Minerbi, Yael; Merhav, Hilla; Kowner, Emmanuelle; Wintner, Shuly; Goldin, Gili; Rabinovich, Ella; Gurevich, Vladimir
Contributing: here
Contact: amir.zeldes@georgetown.edu
===============================================================================
</pre>
