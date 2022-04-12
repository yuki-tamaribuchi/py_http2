from ..request import Request


class Table:
	STATIC_HEADER_FIELDS = {
		"1": {"name": ":authority", "value": ""},
		"2": {"name": ":method", "value": "GET"},
		"3": {"name": ":method", "value": "POST"},
		"4": {"name": ":path", "value": "/"},
		"5": {"name": ":path", "value": "/index.html"},
		"6": {"name": ":scheme", "value": "http"},
		"7": {"name": ":scheme", "value": "https"},
		"8": {"name": ":status", "value": "200"},
		"9": {"name": ":status", "value": "204"},
		"10": {"name": ":status", "value": "206"},
		"11": {"name": ":status", "value": "304"},
		"12": {"name": ":status", "value": "400"},
		"13": {"name": ":status", "value": "404"},
		"14": {"name": ":status", "value": "500"},
		"15": {"name": "accept-charset", "value": ""},
		"16": {"name": "accept-encoding", "value": "gzip, deflate"},
		"17": {"name": "accept-language", "value": ""},
		"18": {"name": "accept-ranges", "value": ""},
		"19": {"name": "accept", "value": ""},
		"20": {"name": "access-control-allow-origin", "value": ""},
		"21": {"name": "age", "value": ""},
		"22": {"name": "allow", "value": ""},
		"23": {"name": "authorization", "value": ""},
		"24": {"name": "cache-control", "value": ""},
		"25": {"name": "content-disposition", "value": ""},
		"26": {"name": "content-encoding", "value": ""},
		"27": {"name": "content-language", "value": ""},
		"28": {"name": "content-length", "value": ""},
		"29": {"name": "content-location", "value": ""},
		"30": {"name": "content-range", "value": ""},
		"31": {"name": "content-type", "value": ""},
		"32": {"name": "cookie", "value": ""},
		"33": {"name": "date", "value": ""},
		"34": {"name": "etag", "value": ""},
		"35": {"name": "expect", "value": ""},
		"36": {"name": "expires", "value": ""},
		"37": {"name": "from", "value": ""},
		"38": {"name": "host", "value": ""},
		"39": {"name": "if-match", "value": ""},
		"40": {"name": "if-modified-since", "value": ""},
		"41": {"name": "if-none-match", "value": ""},
		"42": {"name": "if-range", "value": ""},
		"43": {"name": "if-unmodified-since", "value": ""},
		"44": {"name": "last-modified", "value": ""},
		"45": {"name": "link", "value": ""},
		"46": {"name": "location", "value": ""},
		"47": {"name": "max-forwards", "value": ""},
		"48": {"name": "proxy-authenticate", "value": ""},
		"49": {"name": "proxy-authorization", "value": ""},
		"50": {"name": "range", "value": ""},
		"51": {"name": "referer", "value": ""},
		"52": {"name": "refresh", "value": ""},
		"53": {"name": "retry-after", "value": ""},
		"54": {"name": "server", "value": ""},
		"55": {"name": "set-cookie", "value": ""},
		"56": {"name": "strict-transport-security", "value": ""},
		"57": {"name": "transfer-encoding", "value": ""},
		"58": {"name": "user-agent", "value": ""},
		"59": {"name": "vary", "value": ""},
		"60": {"name": "via", "value": ""},
		"61": {"name": "www-authenticate", "value": ""}
	}

	def __init__(self):
		self.max_table_size = 4096
		self.current_table_size = 0
		self.used_static_field_indexes = []
		self.dynamic_fileds = {}
		self.fields_without_indexing = {}

	def set_max_table_size(self, max_size):
		self.max_table_size = max_size

	def add_static_field(self, index):
		self.used_static_field_indexes.append(index)

	def add_fields_without_indexing(self, value, index=None, name=None):
		if index:
			self.fields_without_indexing[self.STATIC_HEADER_FIELDS[str(index)]["name"]] = value
		elif name:
			self.fields_without_indexing[name] = value

	def add_dynamic_field(self, value, index=None, name=None):
		new_dynamic_fields = {}
		if index:
			new_dynamic_fields["62"] = {"name": self.STATIC_HEADER_FIELDS[str(index)]["name"], "value": value}
		elif name:
			new_dynamic_fields["62"] = {"name": name, "value": value}

		if len(self.dynamic_fileds)>0:
			for k, v in self.dynamic_fileds.items():
				new_dynamic_fields[str(int(k)+1)] = v
		self.dynamic_fileds = new_dynamic_fields
	

	def load_response(self, status, options):
		is_status_found = False
		for i in range(8, 15):
			if self.STATIC_HEADER_FIELDS[str(i)]["value"] == str(status):
				self.add_static_field(str(i))
				is_status_found = True
				break
		
		if not is_status_found:
			self.add_dynamic_field(str(status), index=8)

		
		if options:
			STATIC_HEADER_FIELDS_NAME_INDEXED = {v["name"]: {"index":k, "value":v["value"]} for k, v in self.STATIC_HEADER_FIELDS.items()}
			for option_k, option_v in options.items():
				#オプション名のlowerが辞書内にある場合
				if option_k.lower() in STATIC_HEADER_FIELDS_NAME_INDEXED:
					#辞書内のvalueとoptionのvalueが同じ場合
					if option_v == STATIC_HEADER_FIELDS_NAME_INDEXED[option_k.lower()]["value"]:
						self.add_static_field(STATIC_HEADER_FIELDS_NAME_INDEXED[option_k.lower()]["index"])
					#辞書内のvalueとoptionのvalueが違う場合
					else:
						self.add_dynamic_field(option_v, index=STATIC_HEADER_FIELDS_NAME_INDEXED[option_k.lower()]["index"])

				#オプション名のlowerが辞書内にない場合
				else:
					self.add_dynamic_field(option_v, name=option_k.lower())
			
		return True


	def create_headers_dict(self):
		headers_dict = {}

		if self.used_static_field_indexes:
			for field in self.used_static_field_indexes:
				k = self.STATIC_HEADER_FIELDS[str(field)]["name"]
				v = self.STATIC_HEADER_FIELDS[str(field)]["value"]
				headers_dict[k] = v

		if self.dynamic_fileds:
			for field in self.dynamic_fileds.values():
				k = field["name"]
				v = field["value"]
				headers_dict[k] = v

		if self.fields_without_indexing:
			for k, v in self.fields_without_indexing.items():
				headers_dict[k] = v
		
		return headers_dict