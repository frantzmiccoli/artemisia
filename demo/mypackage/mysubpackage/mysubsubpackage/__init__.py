__author__ = 'frantz'

def get_version_number_modifier():
    def system_number_modifier(value_point):
        system = value_point['system']
        split_system = system.split('-')
        if len(split_system) == 2:
            version_number = int(split_system[-1])
        else:
            version_number = 0
        value_point['version_number'] = version_number
        return value_point
    return system_number_modifier
