def leap_year(i1):
    if i1 % 4 == 0 and i1 % 100 != 0:
        return True
    elif i1 % 400 == 0:
        return True
    else:
        return False
