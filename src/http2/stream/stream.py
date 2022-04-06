from ..table.table import Table

class Stream:
	def __init__(self, state:int, stream_identifier:int, priority:int=None, stream_dependency:int=None, weight:int=16):
		self.state = state
		self.stream_identifier = stream_identifier
		self.priority = priority
		self.stream_dependency = stream_dependency
		self.weight = weight
		self.headers_table = Table()
	
	def add_headers_to_table(self, headers):
		for field in headers.fields:
			if field.field_type == 0:
				self.headers_table.add_static_field(field)
			elif field.field_type in [1, 2]:
				self.headers_table.add_dynamic_field(field)
			elif field.field_type in [3, 4]:
				self.headers_table.add_fields_without_indexing(field)
			elif field.field_type in [5, 6]:
				print("Literal Header Field Never Indexed is not implemented")
				raise Exception
			elif field.field_type == 7:
				self.headers_table.set_max_table_size(field)