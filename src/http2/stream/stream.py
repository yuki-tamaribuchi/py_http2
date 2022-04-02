class Stream:
	def __init__(self, state:int, stream_identifier:int, priority:int=None, stream_dependency:int=None, weight:int=16):
		self.state = state
		self.stream_identifier = stream_identifier
		self.priority = priority
		self.stream_dependency = stream_dependency
		self.weight = weight