from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.template.response import TemplateResponse

from game_info.models import Game, Faction, Attribute
from shop.models import Product, Item


def games(request):
    games = Game.objects.all().order_by('name')
    featured_games = games.filter(featured=True)

    context = {'games': games,
               'featured_games': featured_games,
               }

    return TemplateResponse(request, "game_info/index.html", context=context)


def game_info(request, game_slug):
    game = get_object_or_404(Game, slug=game_slug)
    products = Product.objects.filter_visible().filter(games=game)
    items = None
    featured_items = None
    if products:
        items = Item.objects.filter(product__in=products)
        featured_items = items.filter(featured=True)[:5]
    context = {'game': game,
               'items': items,
               'featured_items': featured_items,
               }
    return TemplateResponse(request, "game_info/game.html", context=context)


def faction_info(request, faction_id):
    faction = get_object_or_404(Faction, id=faction_id)
    products = Product.objects.filter_visible().filter(factions=faction)
    items = None
    featured_items = None
    if products:
        items = Item.objects.filter(product__in=products)
        featured_items = items.filter(featured=True)[:5]
    context = {'faction': faction,
               'items': items,
               'featured_items': featured_items,
               }
    return TemplateResponse(request, "game_info/faction.html", context=context)


def attribute_info(request, attribute_id):
    attribute = get_object_or_404(Attribute, id=attribute_id)
    products = Product.objects.filter_visible().filter(attributes=attribute)
    items = None
    featured_items = None

    if products:
        items = Item.objects.filter(product__in=products)
        featured_items = items.filter(featured=True)[:5]

    context = {'attribute': attribute,
               'items': items,
               'featured_items': featured_items,

               }
    return TemplateResponse(request, "game_info/attribute.html", context=context)
