# Domain Hunter
# Read the file README for a better understanding of this code and more notes.
# Written by Andrew Graham
# Originally written Feb 11 2023, but later modified and uploaded to GitHub Jun 1-2 2023.

# Edit these variables---------------------------------------------------------
# Domain Length (must be at least 5 letters)
domain_length = 5
# Count of domains to check per API call (500 max)
chunk_size = 500
# Price in USD you are willing to pay for a domain
max_price = 1000000
# Define the top-level domain ('com', 'net'...)
tld = 'com'
# -----------------------------------------------------------------------------


# Prep the API and word frequency table----------------------------------------
import requests
import time
import json
import pandas as pd

# Read the keys from their file and prep for the API call.
with open('GodaddyKeys.txt') as f:
    GodaddyKeys = f.readlines()
api_key = GodaddyKeys[0].strip()
secret_key = GodaddyKeys[1].strip()
url = "https://api.godaddy.com/v1/domains/available"
headers = {"Authorization": "sso-key {}:{}".format(api_key, secret_key)}

# Load and prep the word_freq dataframe
# Only use the first 100000 words because around there the words start
# appearing ridiculous.
# Words shorter than domain_length are too short to be useful.
word_freq = pd.read_csv('unigram_freq.csv')
word_freq['len'] = word_freq['word'].str.len()
word_freq = word_freq.iloc[:100000]
word_freq = word_freq[word_freq['len'] >= domain_length]
word_freq.drop(columns=(['len']), inplace=True)
word_freq.reset_index(inplace=True)
# -----------------------------------------------------------------------------


# Generating Pronounceable Words------------------------------------------------
# To make pronounceable words, we will overlap two existing words making sure
# they have at least 3 letters of overlap and ensuring that the start of one
# word is the start of our generated word and the end of the other word is the
# end of our generated word. For example, sURName and bURNt can make surnt.
# Create two dataframes (word_starts and word_ends__) which contain the start
# and end of words where the end of the start and the start of the end are the
# overlap portions. The column start_len in word_starts is the length of
# letters, but in word_ends__ is the length of the word_starts letters needed
# to create a word of domain_length (foreign key). word_ends__ letters column
# does not have the overlap letters so I can join them easily later.
# Note: If I was regularly using this, I would store the output of this cell in
# a separate file so I don't have to generate this each time, but seeing as I'm
# only running this once per domain length, that's unnecessary for me, but
# may be useful for others. There are also opportunities to improve the
# efficiency here, but for a one-time run, it's more efficient to not optimize
# the code.
word_starts = pd.DataFrame(columns=['a_letters', 'a_count', 'overlap', 'start_len'])
word_ends__ = pd.DataFrame(columns=['b_letters', 'b_count', 'overlap', 'start_len'])
print('Words to process:', len(word_freq))
for index, val in word_freq.iterrows():
    if index % 1000 == 0:
        print('Words processed:', index)
    character_len = 3
    while character_len <= domain_length and character_len <= len(val['word']):
        word_starts.loc[len(word_starts), word_starts.columns] = val['word'][:character_len], \
                                                                  val['count'], \
                                                                  val['word'][:character_len][-3:], \
                                                                  character_len
        if -1 * character_len + 3 != 0:  # if -1*character_len+3 == 0, you end up
            # indexing [-0:] which rather than returning nothing, returns
            # everything
            word_ends__.loc[len(word_ends__), word_ends__.columns] = val['word'][-1 * character_len + 3:], \
                                                                      val['count'], \
                                                                      val['word'][-1 * character_len:][:3], \
                                                                      domain_length + 3 - character_len
        character_len += 1

# Some sets of letters will appear multiple times from having been in multiple
# words; I need to combine them.
word_starts = word_starts.groupby(['a_letters', 'overlap', 'start_len']).sum()
word_ends__ = word_ends__.groupby(['b_letters', 'overlap', 'start_len']).sum()
word_starts.reset_index(inplace=True)
word_ends__.reset_index(inplace=True)
# Merge the word starts with the word end and score their frequency based on
# the min of the frequency of each.
generated_words = word_starts.merge(word_ends__, on=['overlap', 'start_len'], how='inner').drop(
    columns=['overlap', 'start_len'])
generated_words['word'] = generated_words['a_letters'] + generated_words['b_letters']
generated_words['frequency'] = generated_words[['a_count', 'b_count']].min(axis=1)
generated_words.drop(columns=['a_letters', 'b_letters', 'a_count', 'b_count'], inplace=True)
generated_words.sort_values('frequency', ascending=False, inplace=True)
# What value is set for keep doesn't matter.
generated_words.drop_duplicates('word', keep='last', inplace=True)
# -----------------------------------------------------------------------------


# Break into Chunks------------------------------------------------------------
all_domains = list(map(('{}.' + tld).format, list(generated_words['word'])))
# Break all_domains into chunks
def split_up(array, size):
    for i in range(0, len(array), size):
        yield array[i:i + size]
domain_chunks = list(split_up(all_domains, chunk_size))
# -----------------------------------------------------------------------------


# Run through API and return results-------------------------------------------
counter = 0
found_domains = {}
print('')
print('Working through chunks and checking availability.')
print('The GoDaddy API is imperfect, and some of the results it says are available are not.')
print('If you have seen enough results, manually stop the kernel.')
for domains in domain_chunks:
    counter += 1
    # Get availability by calling availability API
    availability_res = requests.post(url, json=domains, headers=headers)
    # Get only available domains with price range
    for domain in json.loads(availability_res.text)["domains"]:
        if domain["available"]:
            price = float(domain["price"]) / 1000000
            if price <= max_price:
                print("{:30} : {:10}".format(domain["domain"], price))
                found_domains[domain["domain"]] = price
    print('Completed {} of {}'.format(str(counter), str(len(domain_chunks))),
          '-' * (30 - (len(str(counter) + str(len(domain_chunks))))))

    # API call frequency should be ~ 30 calls per minute
    time.sleep(2)
# -----------------------------------------------------------------------------
