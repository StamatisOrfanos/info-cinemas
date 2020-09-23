def safe_cast(value, type, default=0):
	try:
		return type(value)
	except (ValueError, TypeError):
		return default
