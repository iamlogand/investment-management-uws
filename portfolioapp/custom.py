
# Returns positivised number. Useful for situations where the sign is either implied or displayed somewhere other than
#  right before the number.
def positivise_number(num_in):
    if num_in < 0:
        num_out = num_in * -1
    else:
        num_out = num_in
    return num_out


# Returns a number's sign. If plus_sign=False then positive inputs will return None.
def get_number_sign(num_in, plus_sign=True):
    if num_in < 0:
        sign_out = "−"
    elif num_in > 0:
        if plus_sign:
            sign_out = "+"
        else:
            sign_out = ""
    else:
        sign_out = ""
    return sign_out


# Returns a date as a string.
def date_as_string(datetime_object, include_time=True, include_seconds=True):
    date_string = "{0:04d}-{1:02d}-{2:02d}".format(datetime_object.year, datetime_object.month, datetime_object.day)
    if include_time:
        date_string += " {0:02d}:{1:02d}".format(datetime_object.hour, datetime_object.minute)
        if include_seconds:
            date_string += ":{0:02d}".format(datetime_object.second)
    return date_string
