def split_by_n(line, n):
    """

    :param line:
    :param n:
    :return:
    """
    values = []
    line = line[:-1]
    length = len(line)
    for i in range(0, length, n):
        if i+n < length:
            values.append(fl_int(line[i:i+n]))
        else:
            values.append(fl_int(line[i:]))
    return values


def split_by_n_str(line, n):
    """
    Splits line in to a list of n length strings. This differs from _split_by_n() which returns fl_int()
    :param line:  string
    :param n: int
    :return: list of strings
    """
    values = []
    line = line[:-1]
    length = len(line)
    for i in range(0, length, n):
        if i+n < length:
            values.append(line[i:i+n])
        else:
            values.append(line[i:])
    return values


# TODO - combine with split_by_n()
def split_block_obs(line, n):
    """
    Is aware of blank blocks and will return '' in addition to a float or int. Also used for iefa.
    :param line: line to process
    :param n: int - size of block
    :return: list or int, float, or ''
    """
    values = []
    line = line[:-1]
    length = len(line)
    for i in range(0, length, n):
        if i+n < length:
            new_value = line[i:i+n].strip()
        else:
            new_value = line[i:].strip()
        if new_value == '':
            values.append(new_value)
        else:
            values.append(fl_int(new_value))

    return values


def fl_int(value):
    """ Converts string to either float or int depending on presence of decimal point.
    The RAS geo file does not have a decimal place if it is not needed. weird.
    :param value: string to convert
    :return: returns int or float
    """
    x = float(value)
    if x.is_integer():
        x = int(x)
    return x


def print_list_by_group(values, width, num_columns):
    """
    Returns string of items in list values padded left to width in width, with num_columns of items per line.
    Lines are separated by newlines. No error thrown if value[i] width exceeds width.

    :param values: list of values to convert to string
    :param width: width of white space padded columns
    :param num_columns: number of columns per line
    :return: string broken into multiple lines with \n
    """
    length = len(values)
    s = ''
    for row in range(0, length, num_columns):
        # Make sure we don't overrun length of values if len(values) % num_columns != 0
        last_column = length - row
        if last_column > num_columns:
            last_column = num_columns
        # Loop through and add every item in the row
        for column in range(0, last_column):
            temp = ('{:>'+str(width)+'}').format(values[row + column])

            # Strip leading 0 from 0.12345 - with or without spaces or '-'
            if temp[:2] == '0.':
                #temp = temp[1:]
                temp = ' ' + temp[1:]
            temp = temp.replace(' 0.', '  .')
            temp = temp.replace('-0.', ' -.')

            s += temp
        # End of row, add newline
        s += '\n'
    return s


def pad_left(guts, pad_number):
    """
    pads guts (left) with spaces up to pad_number
    :param guts: anything
    :param pad_number: int
    :return: string
    """
    return ('{:>'+str(pad_number)+'}').format(guts)


