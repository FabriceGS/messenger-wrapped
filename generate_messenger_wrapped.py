"""
Run this script after downloading Messenger data from
January 1 2020 - December 1 2020 (or some later date in 2020)
in JSON format. Put the `messages` folder in the `2020messengerwrapped`
directory.

In this directory: run `python generate_messenger_wrapped.py`
to generate the file that index.html will use to generate
your 2020 Messenger Wrapped!
"""

import json
import os
import string
import datetime
import matplotlib.pyplot as plt 
import numpy as np
from PIL import Image

MESSENGER_DIR = './messages/inbox'

if __name__ == "__main__":
  messages_dict = {"Meta": {"summary_stats": {"messages_sent": 0, "reacts_received": 0, "reacts_given": 0}}}
  # most_reacted_all_time = {}
  years = set()
  for dir, _, files in os.walk(MESSENGER_DIR):
    for file in files:
      if ".json" in file:
        with open(os.path.join(dir, file)) as json_file:
          data = json.load(json_file)

          if not data["title"] == "Canton de Regio":
            continue

          # participants
          for participant in data["participants"]:
            if participant["name"].split()[0] not in messages_dict:
              name = participant["name"].split()[0]
              messages_dict[name] = {"summary_stats": {"messages_sent": 0, "reacts_received": 0, "reacts_given": 0}}

          # messages & reacts
          for m in data['messages']:
            sender_name = m['sender_name'].split()[0]

            # per year
            year = str(datetime.datetime.utcfromtimestamp(int(m["timestamp_ms"]) / 1000).strftime('%Y'))
            if year == "2024":
              continue
            years.add(year)
            if year not in messages_dict[sender_name]:
              messages_dict[sender_name][year] = {"messages_sent": 0, "reacts_received": 0, "reacts_given": 0}
            messages_dict[sender_name][year]["messages_sent"] += 1

            # overall
            messages_dict[sender_name]["summary_stats"]["messages_sent"] += 1
            if "reactions" in m:
              if len(m["reactions"]) == 5 and year == "2023":
                if "content" in m:
                  print(sender_name, ": ", m["content"])
                # else:
                  # image_name = m["photos"][0]["uri"].split("/")[-1]
                  # img = Image.open('./messages/inbox/cantonderegio_1664884170444440/photos/' + image_name)
                  # img.show()

              messages_dict[sender_name]["summary_stats"]["reacts_received"] += len(m["reactions"])
              messages_dict[sender_name][year]["reacts_received"] += len(m["reactions"])
              for reaction in m["reactions"]:
                reactor = reaction["actor"].split()[0]
                messages_dict[reactor]["summary_stats"]["reacts_given"] += 1
                if year not in messages_dict[reactor]:
                  messages_dict[reactor][year] = {"messages_sent": 0, "reacts_received": 0, "reacts_given": 0}
                messages_dict[reactor][year]["reacts_given"] += 1


  # add zeros for anyone who didn't speak for a whole year
  for key, value in messages_dict.items():
      for year in years:
        if year not in value:
          messages_dict[key][year] = {"messages_sent": 0, "reacts_received": 0, "reacts_given": 0}
  
  #total messages sent per year
  total_messages_sent = {}
  for year in years:
    total = 0
    for key, value in messages_dict.items():
      total += value[year]["messages_sent"]
    total_messages_sent[year] = total 


  # graph annual reacts/messages
  for key1, value1 in messages_dict.items():
    name = key1
    y = []
    for key2, value2 in sorted(value1.items()):
      year = key2
      if key2 == "summary_stats":
        continue
      result = 0

      # most giving
      # result = value2["reacts_given"] / (total_messages_sent[year] - value2["messages_sent"])

      #most popular
      if value2["messages_sent"] != 0:
        result = value2["reacts_received"] / value2["messages_sent"]

      y.append(result) #change this to get a different chart
  #   plt.plot(sorted(years), y, label=name)
  # plt.xlabel("Year") 
  # plt.ylabel("Reacts / Messages") 
  # plt.title('Most Popular') 
  # plt.legend(loc="upper left")
  # plt.show() 

  # print(json.dumps(messages_dict, sort_keys=True, indent=4))
