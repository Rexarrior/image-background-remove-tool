price = [
    (2 * 1024*1024, 1),
    (5 * 1024*1024, 2),
    (8 * 1024*1024, 3),
    (10 * 1024*1024, 4),
    (15 * 1024*1024, 5),
    (20 * 1024*1024, 6),
    (1024 * 1024*1024, 6), # todo: max cost?
] 
def calc_credit_needed(img_size_b: int) -> int:
    for size, credit in price:
        if img_size_b <= size:
            return credit
    raise ValueError("Unavailable image size!")