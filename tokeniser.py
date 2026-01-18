import tiktoken

encoder = tiktoken.encoding_for_model('gpt-4o')

print("Vacab size : ", encoder.n_vocab)


print("Vocab size:", encoder.n_vocab)

text = "Hello bhai, kaise ho?"
tokens = encoder.encode(text)

print("Tokens:", tokens)    #  [13225, 11387, 1361, 11, 1908, 1096, 2021, 30]
print("Total tokens:", len(tokens))


decoded = encoder.decode([13225, 11387, 1361, 11, 1908, 1096, 2021, 30])
print("Decoded message : ", decoded)


