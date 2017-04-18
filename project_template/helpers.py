def sort_dict_by_val(d):
    """Get a list of a dict's keys ordered by descending values."""
    return sorted(d, key=d.__getitem__, reverse=True)
