import re
import pickle
import hashlib

cluster_pattern = re.compile('^cluster_(\d*)$')


def get_cluster_modifier(name):
    match = cluster_pattern.match(name)
    if match is None:
        raise Exception('The provided name should match the cluster pattern')

    cluster_modulo = int(match.group(1))

    def cluster_modifier(value_point):
        cluster_value = hash_as_int(value_point) % cluster_modulo
        field_name = 'cluster_' + str(cluster_modulo)
        value_point[field_name] = cluster_value
        return value_point
    return cluster_modifier


cluster_from_field_pattern = re.compile('^([\w\d_]*)_cluster_(\d*)$')


def get_cluster_from_field_modifier(name):
    match = cluster_from_field_pattern.match(name)
    if match is None:
        raise Exception('The provided name should match the cluster from '
                        'field pattern')

    cluster_field_name = match.group(1)
    cluster_modulo = int(match.group(2))

    def cluster_from_field_modifier(value_point):
        cluster_value = hash_as_int(value_point[cluster_field_name]) \
            % cluster_modulo
        field_name = cluster_field_name + '_cluster_' + str(cluster_modulo)
        value_point[field_name] = cluster_value
        return value_point
    return cluster_from_field_modifier


def hash_as_int(input_value):
    hash_input = pickle.dumps(input_value)
    md5 = hashlib.md5()
    md5.update(hash_input)
    hash_value = int(md5.hexdigest(), 16)
    return hash_value


modifiers_map = {
    cluster_pattern: get_cluster_modifier,
    cluster_from_field_pattern: get_cluster_from_field_modifier
}