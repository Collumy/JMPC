from compiler.lexer.tokens import Tokens

PLAYER_SELECTION = {
    "default": "default",
    "current": "current",
    "killer": "killer_player",
    "damager": "damager_player",
    "shooter": "shooter_player",
    "victim": "victim_player",
    "random": "random_player",
    "all": "all_players",
}

ENTITY_SELECTION = {
    "default": "default_entity",
    "current": "current",
    "killer": "killer_entity",
    "damager": "damager_entity",
    "shooter": "shooter_entity",
    "projectile": "projectile",
    "victim": "victim_entity",
    "random": "random_entity",
    "all": "all_entities",
    "mobs": "all_mobs",
    "last": "last_entity"
}

SELECTORS = {
    "player": "player",
    "pl": "player",
    "p": "player",

    "entity": "entity",
    "en": "entity",
    "e": "entity",

    "world": "world",
    "w": "world",

    "variable": "variable",
    "var": "variable",
    "v": "variable",
}

VARIABLES = {
    Tokens.VARIABLE,
    Tokens.GAME_VARIABLE,
    Tokens.LINE_VARIABLE,
    Tokens.LOCAL_VARIABLE,
    Tokens.SAVE_VARIABLE
}