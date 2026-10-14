# src/validation.py


def check_grashof(l1, l2, l3, l4):

    # Check the Grashof condition:
    # s + l <= p + q
    
    links = [l1, l2, l3, l4]

    shortest = min(links)
    longest = max(links)

    remaining_sum = (sum(links)- shortest- longest)

    return (shortest + longest <= remaining_sum)


def mechanism_can_close(l1, l2, l3, l4):
    
    # Basic geometric validation.
    # The longest link cannot be longer than the sum of the other three links.
 
    links = [l1, l2, l3, l4]

    longest = max(links)

    return (longest <= sum(links) - longest)