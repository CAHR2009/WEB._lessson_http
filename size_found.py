def found_size_function(long, latt, organization):
    organization = organization.split(',')
    delta = list(map(lambda x: x if x > 0 else -x, [float(long) - float(organization[0]),
                                                    float(latt) - float(organization[1])]))
    hypitinuse = (delta[0] ** 2 + delta[1] ** 2) ** 0.5
    return str(hypitinuse * 111)[:10]