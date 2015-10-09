import re
import time
from datetime import timedelta

unit_mapping = (
	("weeks", "weeks",),
	("week", "weeks",),
	("w", "weeks",),
	("days", "days",),
	("day", "days",),
	("d", "days",),
	("hours", "hours",),
	("hour", "hours",),
	("h", "hours",),
	("minutes", "minutes",),
	("minute", "minutes",),
	("mins", "minutes",),
	("min", "minutes",),
	("m", "minutes",),
	("seconds", "seconds",),
	("second", "seconds",),
	("secs", "seconds",),
	("sec", "seconds",),
	("s", "seconds",),
	("milliseconds", "milliseconds",),
	("millisecond", "milliseconds",),
	("microseconds", "microseconds",),
	("microsecond", "microseconds",),
	)
unit_lookup = {}
for tup in unit_mapping:
	unit_lookup[tup[0]] = tup[1]

timedelta_pattern = (''.join(['((?P<%s>\d+)\s?%s[-\s:]?)?'
						   % (key[0], key[0],) for key in unit_mapping]))
timedelta_pattern = '^%s$' % (timedelta_pattern,)
timedelta_regex = re.compile(timedelta_pattern)

# CAVEAT: The input must be ordered so that larger units come
#         first, e.g., "1d 1h 1m" works, but "1h 1d 1m" won't.
def parse_timedelta(input):
	'''
	>>> print(parse_timedelta("3w"))
	21 days, 0:00:00
	>>> print(parse_timedelta("3w 12h 57m"))
	21 days, 12:57:00
	>>> print(parse_timedelta("3 weeks 12hour 57m 10 secs 123456 microseconds"))
	21 days, 12:57:10.123456
	>>> print(parse_timedelta("5w:12h:57m"))
	35 days, 12:57:00
	>>> print(parse_timedelta("5w:2h:1m"))
	35 days, 2:01:00
	>>> print(parse_timedelta("30 days"))
	30 days, 0:00:00
	>>> print(parse_timedelta("3w blah"))
	None
	>>> print(parse_timedelta("3w "))
	21 days, 0:00:00
	>>> print(parse_timedelta("3w  "))
	None
	>>> print(parse_timedelta("3w"))
	21 days, 0:00:00
	>>> print(parse_timedelta(" 3w"))
	None
	>>> print(parse_timedelta("abc 3w"))
	None
	>>> print(parse_timedelta("3w 5d"))
	26 days, 0:00:00
	>>> print(parse_timedelta("3w 5b"))
	None
	'''
	tdelta = None
	match_obj = timedelta_regex.match(input)
	if match_obj is not None:
		kwargs = {}
		for key, val in match_obj.groupdict(default='0').items():
			kwargs.setdefault(unit_lookup[key], 0)
			kwargs[unit_lookup[key]] += int(val)
		tdelta = timedelta(**kwargs)
	return tdelta

#
def time_format_elapsed(time_then):
   return time_format_scaled(time.time() - time_then)[0]

#
def time_format_scaled(time_amt):

   if time_amt > (60 * 60 * 24 * 365.25): # s * m * h * 365 = years
      units = 'years'
      scale = 60.0 * 60.0 * 24.0 * 365.25
   elif time_amt > (60 * 60 * 24 * 30.4375): # s * m * h * 30 = months
      units = 'months'
      scale = 60.0 * 60.0 * 24.0 * 30.4375
   elif time_amt > (60 * 60 * 24): # secs * mins * hours = days
      units = 'days'
      scale = 60.0 * 60.0 * 24.0
   elif time_amt > (60 * 60): # secs * mins = hours
      units = 'hours'
      scale = 60.0 * 60.0
   elif time_amt > 60:
      units = 'mins.'
      scale = 60.0
   else:
      units = 'secs.'
      scale = 1.0
   time_fmtd = '%.2f %s' % (time_amt / scale, units,)
   return time_fmtd, scale, units

if __name__ == "__main__":
	import doctest
	doctest.testmod()
	print('Testing complete!')

