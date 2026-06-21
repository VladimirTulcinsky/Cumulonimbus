#!/usr/bin/env python3

import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--actionlist', help='actionlist to use')
parser.add_argument('-t', '--target', help='host/ip to target', required=True)
parser.add_argument('-w', '--wordlist', help='wordlist to use')
args = parser.parse_args()

# HTTP methods to probe for each path
methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

# Status codes considered "uninteresting" / not worth reporting
ignored = [204, 401, 403, 404]

actions = []

with open(args.actionlist, "r") as a:
    for line in a:
        try:
            actions.append(line.strip())
        except:
            print("Exception occurred")

# Header row: one column per method
header = "Path             - \t" + "\t".join(methods)
print(header)

with open(args.wordlist, "r") as f:
    for word in f:
        for action in actions:
            print('\r/{word}/{action}'.format(word=word.strip(), action=action), end='')
            url = "{target}/{word}/{action}".format(target=args.target, word=word.strip(), action=action)

            # Issue every configured method against the URL and collect status codes
            results = {}
            for method in methods:
                results[method] = requests.request(method, url=url).status_code

            # Report the path if any method returned an interesting status code
            if any(code not in ignored for code in results.values()):
                print(' \r', end='')
                codes = "\t".join(str(results[method]) for method in methods)
                print("/{word}/{action:10} - \t{codes}".format(word=word.strip(), action=action, codes=codes))

print('\r', end='')
print("Wordlist complete. Goodbye.")
