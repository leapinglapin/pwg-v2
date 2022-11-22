def create_factions(game, factions):
    for faction in factions:
        game.factions.get_or_create(name=faction)


def create_subfactions(faction, subfactions):
    for subfaction in subfactions:
        faction.subfactions.get_or_create(name=subfaction, game=faction.game)


def log(f, string):
    print(string)
    f.write(string + "\n")


def validate_barcode(barcode):
    if len(barcode) < 12 or len(barcode) > 14:
        return False
    return True


def remove_barcode_dashes(barcode):
    return barcode.replace("-", "")
