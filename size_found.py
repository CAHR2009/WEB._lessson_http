def found_size_function(toponym):
    left = list(map(lambda x: float(x), toponym["boundedBy"]["Envelope"]["lowerCorner"].split()))
    right = list(map(lambda x: float(x), toponym["boundedBy"]["Envelope"]["upperCorner"].split()))
    return [str(right[0] - left[0]), str(right[1] - left[1])]