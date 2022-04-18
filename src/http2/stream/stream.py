from ..table.table import Table
from ..frame.data import Data

class Stream:
	def __init__(self, state:int, stream_identifier:int, priority:int=None, stream_dependency:int=None, weight:int=16):
		self.state = state
		self.stream_identifier = stream_identifier
		self.priority = priority
		self.stream_dependency = stream_dependency
		self.weight = weight
		self.request_headers_table = Table()
		self.response_headers_table = Table()
		self.request_data = None
		self.response_data = None

	
	def add_request_headers_to_table(self, headers):
		for field in headers.fields:
			if field.field_type == 0:
				self.request_headers_table.add_static_field(field.index)
			elif field.field_type == 1:
				self.request_headers_table.add_dynamic_field(field.value, index=field.index)
			elif field.field_type == 2:
				self.request_headers_table.add_dynamic_field(field.value, name=field.name)
			elif field.field_type == 3:
				self.request_headers_table.add_fields_without_indexing(field.value, index=field.index)
			elif field.field_type == 4:
				self.request_headers_table.add_fields_without_indexing(field.value, name=field.name)
			elif field.field_type in [5, 6]:
				print("Literal Header Field Never Indexed is not implemented")
				raise Exception
			elif field.field_type == 7:
				self.request_headers_table.set_max_table_size(field.max_size)

	
	def create_response_data_frame(self, padding_length, is_end_stream):
		return Data(
			data=self.response_data,
			padding_length=padding_length,
			is_end_stream=is_end_stream
		)