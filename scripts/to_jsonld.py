import json

from pyld import jsonld
import rdflib

import sys

import rdflib.term

# Check if a filename was passed as an argument
if len(sys.argv) < 2:
    print("Usage: python script.py <filename> <frame>")
    sys.exit(1)

# Get the filename from the command line arguments
filename = sys.argv[1]
fn_context = sys.argv[2]
fn_frame = sys.argv[3]

fh = open(fn_context)
context = json.load(fh)
fh.close()

fh = open(fn_frame)
frame = json.load(fh)
frame["@context"] = context
fh.close()

# Read the file and print its lines
# try:

d = rdflib.Dataset()
rdflib.term.bind(rdflib.XSD.dateTime, None)
d.parse(filename)
nquads = d.serialize(format="nquads")
out = jsonld.from_rdf(nquads, {"format": "application/n-quads"})
# print(frame)
out = jsonld.compact(out, context)
out = jsonld.frame(out, frame, {"omitDefault": False})
print(json.dumps(out, indent=2))


# except FileNotFoundError:
#     print(f"Error: The file '{filename}' does not exist.")
# except Exception as e:
#     print(f"An error occurred: {e}")
