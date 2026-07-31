MAX_CREDIT_AMOUNT = 500
TOTAL_CREDITS_AMOUNT = MAX_CREDIT_AMOUNT * 10

NUMBER_OF_PLAYERS_PER_ROLE = {
    "goalkeepers": 3,
    "defenders": 8,
    "midfielders": 8,
    "attackers": 6,
}

MAX_CREDIT_PER_ROLE = {
    "goalkeepers": 50,
    "defenders": 50,
    "midfielders": 100,
    "attackers": 300,
}

STANDARD_ROLE_MULTIPLIERS = {
    "goalkeepers": MAX_CREDIT_PER_ROLE["goalkeepers"]/NUMBER_OF_PLAYERS_PER_ROLE["goalkeepers"]/20,
    "defenders": MAX_CREDIT_PER_ROLE["defenders"]/NUMBER_OF_PLAYERS_PER_ROLE["defenders"]/20,
    "midfielders": MAX_CREDIT_PER_ROLE["midfielders"]/NUMBER_OF_PLAYERS_PER_ROLE["midfielders"]/20,
    "attackers": MAX_CREDIT_PER_ROLE["attackers"]/NUMBER_OF_PLAYERS_PER_ROLE["attackers"]/20,
}
