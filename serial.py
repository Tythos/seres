"""Serial objects are responsible for:
* Maintaining specific catalogues of Format and Protocol parsers
* Serializing and deserializing Python objects to and from dictionary equivalents

Eventually, the second item will need to support more complex types, such as
user-defined enumerations. For now, the following field values are supported in the basic
release:
* Three primitives
    * Logicals
    * Numerics
    * Strings
* Two data structures
    * Dictionaries
	* Lists
	
Serial objects also define the method by which specific inbound/outbound operations are
mapped to specific Format and Protocol parsers, usually by matching REST URI patterns.
Therefore, the Serial instance is the primary user interface to the seres inobund/outbound
data pipeline.
"""

import types
import sys
import seres.formats
import seres.protocols

if sys.version_info.major == 2:
	def is_class_type(c):
		return type(c) == types.ClassType
else:
	def is_class_type(c):
		return isinstance(c, type)

class Serial():
	def __init__(self):
		self._formats = get_default_formats()
		self._protocols = get_default_protocols()
		
	def inbound(self, ru):
		# Step 1: Fetch plaintext from given RestUri using matching protocol
		p = self.get_filter(self._protocols, ru)
		plaintext = p.inbound(ru)
		
		# Step 2: Parse plaintext into dictionaries using matching formats
		f = self.get_filter(self._formats, ru)
		dicts = f.inbound(plaintext)
		
		# Step 3: Deserialize objects from dictionaries and return
		return self.deserialize(ru)
	
	def outbound(self, ru, objects):
		# Step 1: Serialize objects into list of dictionaries
		dicts = self.serialize(objects)
		
		# Step 2: Transcribe dictionaries into a plaintext representation using the matching format
		f = self.get_filter(self._formats, ru)
		plaintext = f.outbound(dicts)
		
		# Step 3: Write plaintext to resource using the matching protocol
		p = self.get_filter(self._protocols, ru)
		p.outbound(ru, plaintext)
		
	def deserialize(self, dicts):
		# Populate instantiations of each object using _seres_class property
		return []
		
	def serialize(self, objs):
		# Convert list of objects into a list of dicts
		return []

	def get_filter(self, filters, ru):
		# Return the first entry with a matching patterns
		ndx = -1
		for i, f in enumerate(filters):
			if f.pattern.is_match(ru):
				ndx = i
				break
		if ndx < 0:
			Exception("Could not find filter matching " + ru.get_full_uri())
		return filters[ndx]
			
	def add_format(self, f):
		# Insert at beginning to ensure more specialized filters are caught first
		self._formats.insert(0, f)
		
	def add_protocol(self, p):
		# Insert at beginning to ensure more specialized filters are caught first
		self._protocols.insert(0, p)
		
def get_default_formats():
	# Iterate through the contents of seres.formats to initialize and return default
	# instantiations of all Format objects
	formats = []
	for f in dir(seres.formats):
		c = getattr(seres.formats, f)
		if is_class_type(c):
			if issubclass(c, seres.formats.Format) and c is not getattr(seres.formats, 'Format'):
				formats.append(c())
	return formats

def get_default_protocols():
	# Iterate through the contents of seres.protocols to initialize and return default
	# instantiations of all Protocol objects
	protocols = []
	for p in dir(seres.protocols):
		c = getattr(seres.protocols, p)
		if is_class_type(c):
			if issubclass(c, seres.protocols.Protocol) and c is not getattr(seres.protocols, 'Protocol'):
				protocols.append(c())
	return protocols
	
if __name__ == "__main__":
	raise Exception("No command-line interface is currently implemented")
