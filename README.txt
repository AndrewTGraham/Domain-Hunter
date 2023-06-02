Written by Andrew Graham
Originally written Feb 11 2023, but later modified and uploaded to github Jun 1-2 2023.

Purpose
This code will create pronouncable worklike strings and check if they are available and within your price range. All of the 4 letter alphabetic domains are claimed. When looking for 5 or 6 letter alphabetic domains, many domains are available but most of them are nonpronouncable like zxmpp.com. However, there are still a few pronouncable domains available, but they are hard to find. Using this script, I have identified and purchased the following domains in Feb '24:
dairn.com
marnt.com
surnt.com
suths.com

Methodology
To make pronouncable words, we will overlap two existing words making sure they have atleast 3 letters of overlap and ensuring that the start of one word is the start of our generated word and the end of the other word is the end of our generated word. For example sURName and bURNt can make surnt.

English Word Frequency Data
The English Word Frequency dataset (unigram_freq.csv) contains the counts of the 333,333 most commonly-used single words on the English language web, as derived from the Google Web Trillion Word Corpus. Uploaded to Kaggle by RACHAEL TATMAN. https://www.kaggle.com/datasets/rtatman/english-word-frequency

Godaddy API
This uses the free Godaddy API. Make an account, and receive an api key and a secret key. Save them in a txt file called GodaddyKeys.txt with the api key in the first line, the secret key in the second line, and nothing else.