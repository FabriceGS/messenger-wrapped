"""
Run this script after downloading Messenger data from
January 1 2020 - December 1 2020 (or some later date in 2020)
in JSON format. Put the `messages` folder in the `2020messengerwrapped`
directory.

In this directory: run `python generate_messenger_wrapped.py`
to generate the file that index.html will use to generate
your 2020 Messenger Wrapped!
"""

# for next year...might want to do a chart of simply most message sent

import json
import os
import string
import datetime
import matplotlib.pyplot as plt 
import numpy as np
from PIL import Image

MESSENGER_DIR = './messages/inbox'

if __name__ == "__main__":
  messages_dict = {"Meta": {"summary_stats": {"messages_sent": 0, "reacts_received": 0, "reacts_given": 0, "reactors": {}}}}
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
              messages_dict[name] = {"summary_stats": {"messages_sent": 0, "reacts_received": 0, "reacts_given": 0, "reactors": {}}}

          # messages & reacts
          for m in data['messages']:
            sender_name = m['sender_name'].split()[0]


            # per year
            year = str(datetime.datetime.utcfromtimestamp(int(m["timestamp_ms"]) / 1000).strftime('%Y'))
            # TODO add one to year
            if year == "2025":
              continue

            # Print Venkat messages
            # if year == "2024" and sender_name == "Venkat":
            #   reactors = []
            #   if "reactions" in m:
            #     for reactor in m["reactions"]:
            #       reactors.append(reactor["actor"].split()[0])
            #   date_of_message = str(datetime.datetime.utcfromtimestamp(int(m["timestamp_ms"]) / 1000).strftime('%Y-%m-%d'))
            #   if "content" in m:
            #       date_of_message = str(datetime.datetime.utcfromtimestamp(int(m["timestamp_ms"]) / 1000).strftime('%Y-%m-%d'))
            #       message_content = m["content"].encode('latin1').decode('utf-8') 
            #       print("~~~~", sender_name, date_of_message, reactors, "~~~~", "\n", message_content)
            #   else:
            #     image_name = m["photos"][0]["uri"].split("/")[-1]
            #     img = Image.open('./messages/inbox/cantonderegio_1664884170444440/photos/' + image_name)
            #     img.show()
            #     print("~~~~", sender_name, date_of_message, reactors, "~~~~", "\n", image_name)


            years.add(year)
            if year not in messages_dict[sender_name]:
              messages_dict[sender_name][year] = {"messages_sent": 0, "reacts_received": 0, "reacts_given": 0, "reactors": {}}
            messages_dict[sender_name][year]["messages_sent"] += 1

            # overall
            messages_dict[sender_name]["summary_stats"]["messages_sent"] += 1
            if "reactions" in m:
              # TODO add one to year
              if len(m["reactions"]) == 5 and year == "2024":
                if "content" in m:
                  date_of_message = str(datetime.datetime.utcfromtimestamp(int(m["timestamp_ms"]) / 1000).strftime('%Y-%m-%d'))
                  message_content = m["content"].encode('latin1').decode('utf-8') 
                  print("~~~~", sender_name, date_of_message, "~~~~", "\n", message_content)
                # uncomment below to see top reacted images
                else:
                  image_name = m["photos"][0]["uri"].split("/")[-1]
                  # img = Image.open('./messages/inbox/cantonderegio_1664884170444440/photos/' + image_name)
                  # img.show()

              messages_dict[sender_name]["summary_stats"]["reacts_received"] += len(m["reactions"])
              messages_dict[sender_name][year]["reacts_received"] += len(m["reactions"])
              for reaction in m["reactions"]:
                reactor = reaction["actor"].split()[0]
                messages_dict[reactor]["summary_stats"]["reacts_given"] += 1
                if year not in messages_dict[reactor]:
                  messages_dict[reactor][year] = {"messages_sent": 0, "reacts_received": 0, "reacts_given": 0, "reactors": {}}
                messages_dict[reactor][year]["reacts_given"] += 1

                # reactors list
                if reactor not in messages_dict[sender_name]["summary_stats"]["reactors"]:
                  messages_dict[sender_name]["summary_stats"]["reactors"][reactor] = 1
                else:
                  messages_dict[sender_name]["summary_stats"]["reactors"][reactor] += 1

                if reactor not in messages_dict[sender_name][year]["reactors"]:
                  messages_dict[sender_name][year]["reactors"][reactor] = 1
                else:
                  messages_dict[sender_name][year]["reactors"][reactor] += 1



  # add zeros for anyone who didn't speak for a whole year
  for key, value in messages_dict.items():
      for year in years:
        if year not in value:
          messages_dict[key][year] = {"messages_sent": 0, "reacts_received": 0, "reacts_given": 0, "reactors": {}}
  
  #total messages sent per year
  total_messages_sent = {}
  for year in years:
    total = 0
    for key, value in messages_dict.items():
      total += value[year]["messages_sent"]
    total_messages_sent[year] = total 


  # Each person's lovers
  # CUT: I cut this out bc it was a bit complicated, but could add back.
  lovers_dict = {}
  for key1, value1 in messages_dict.items():
    name = key1
    y = []
    for key2, value2 in sorted(value1.items()):
      year = key2
      if year not in lovers_dict:
        lovers_dict[year] = {}
      # if key2 == "summary_stats":
        # each persons react totals per person
        # print(name, ": ", sorted(value2["reactors"].items(), key=lambda item: item[1], reverse=True))

        # for each person, the percent of a given person's total reacts they received
      reactions_dict = {}
      for key3, value3 in sorted(value2["reactors"].items()):
        reactor = key3
        reactions = value3
        reactions_dict[reactor] = round((reactions / max(0.0001, messages_dict[reactor][year]["reacts_given"])) * 100, 2)
      lovers_by_year = sorted(reactions_dict.items(), key=lambda item: item[1], reverse=True)
      # print(name, ": ", sorted(reactions_dict.items(), key=lambda item: item[1], reverse=True))
      lovers_dict[year][name] = lovers_by_year
  for key1, value1 in lovers_dict.items():
      # print("~~~~", key1, "~~~~") # year
      for key2, value2 in value1.items():
        # print(key2, value2)
        pass

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

      #most popular / reacted
      if value2["messages_sent"] != 0:
        result = value2["reacts_received"] / value2["messages_sent"]

      y.append(result) #change this to get a different chart
  #   plt.plot(sorted(years), y, label=name)
  # plt.xlabel("Year") 
  # plt.ylabel("Reacts / Messages") 
  # # Change this name to match giving/popular
  # plt.title('Most Reacted') 
  # plt.legend(loc="upper left")
  # plt.show() 

  # print(json.dumps(messages_dict, sort_keys=True, indent=4))
