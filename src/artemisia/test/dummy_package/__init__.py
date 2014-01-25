

def get_size_modifier():
    def size_modifier(value_point):
        value_point['size'] = 12
        return value_point
    return size_modifier