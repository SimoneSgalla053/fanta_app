MAX_CREDIT_AMOUNT = 500
TOTAL_CREDITS_AMOUNT = MAX_CREDIT_AMOUNT * 10

NUMBER_OF_PLAYERS_PER_ROLE = {
    "goalkeeper": 3,
    "defender": 8,
    "midfielder": 8,
    "attacker": 6,
}

MAX_CREDIT_PER_ROLE = {
    "goalkeeper": 50,
    "defender": 50,
    "midfielder": 100,
    "attacker": 300,
}

STANDARD_ROLE_MULTIPLIERS = {
    "goalkeeper": MAX_CREDIT_PER_ROLE["goalkeeper"]/NUMBER_OF_PLAYERS_PER_ROLE["goalkeeper"]/20,
    "defender": MAX_CREDIT_PER_ROLE["defender"]/NUMBER_OF_PLAYERS_PER_ROLE["defender"]/20,
    "midfielder": MAX_CREDIT_PER_ROLE["midfielder"]/NUMBER_OF_PLAYERS_PER_ROLE["midfielder"]/20,
    "attacker": MAX_CREDIT_PER_ROLE["attacker"]/NUMBER_OF_PLAYERS_PER_ROLE["attacker"]/20,
}
