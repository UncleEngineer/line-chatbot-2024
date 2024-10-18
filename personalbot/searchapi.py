import requests
from decouple import config
import json
ZENSERP_API = config('ZENSERP_API')

def search_zenserp(search_query, location="Bangkok,Thailand"):
  headers = { 
    "apikey": ZENSERP_API}

  # search_query = input("What do you want to search? ")
  # print("Searching : " + search_query)

  params = (
     ("q",search_query),
     ("location",location),
  );

  response = requests.get('https://app.zenserp.com/api/v2/search', headers=headers, params=params);
  # print(response.status_code)
  # print(response.text)

  results_list = []

  if response.status_code == 200:
      # Pase data to json
      data = response.json()
      # Check if there are any results
      if 'organic' in data:
          results = data['organic'][:3] # get top 3

          # Prettify the results
          for i, item in enumerate(results, 1):
              title = item.get('title')
              url = item.get('url')
              description = item.get('description') or item.get('snippet')  # Fall back to snippet if no description

              # Construct the formatted result string
              result_str = f"Search Result {i}:\n"
              result_str += f"Title: {title}\n"
              result_str += f"URL: {url}\n"
              result_str += f"Description: {description}\n"
              result_str += "-" * 50  # Separator line between results

              results_list.append(result_str)

              # Print each prettified result
              # print(result_str)


  else:
      # Print response error
      print(f"Error: {response.status_code}, {response.text}")
  
  return "\n".join(results_list)


