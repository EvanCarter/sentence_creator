Use this with your own gemini token (should be easy to switch to whatever model you want) to create sentences based on vocab words. 

Create an input file such like `input_words.csv`
with the format 
| foreign_word, |
| muchos,       |
| años,         |
| despues,      |
| conocer,      |
| hielo,        |

The code will then batch the words and send them off to gemini for example sentences which will be written to an output csv. After that it will be easy to load into a SRS program like anki. 



