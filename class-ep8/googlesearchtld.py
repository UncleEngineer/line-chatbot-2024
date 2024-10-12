from googlesearch import search

query = input("Enter your search query: ")

for i in search(query, tld="com", num=10, stop=10, pause=2):
    print(i)
