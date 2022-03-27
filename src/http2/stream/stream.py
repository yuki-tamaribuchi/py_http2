class Stream:
	def __init__(self, state:int, stream_identifier:int, priority:int, stream_dependency:int, weight:int):
		self.state = state
		self.stream_identifier = stream_identifier
		self.priority = priority
		self.stream_dependency = stream_dependency
		self.weight = weight