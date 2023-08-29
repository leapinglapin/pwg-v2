from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from treewidget.fields import TreeModelMultipleChoiceField

from crowdfund.models import Reward
from digitalitems.models import DigitalItem
from game_info.models import Game, Faction
from packs.models import DigitalPack
from shop.models import Category, Publisher


class AddDigitalPackForm(forms.ModelForm):
    categories = TreeModelMultipleChoiceField(required=False, queryset=Category.objects.all(),
                                              settings={
                                                  'show_buttons': True, 'filtered': True},
                                              )

    categories.widget.attrs.update({'class': 'max-w-full'})

    publisher = forms.ModelChoiceField(Publisher.objects.all().order_by('name'), required=False)
    games = forms.ModelMultipleChoiceField(Game.objects.all().order_by('name'), required=False)
    factions = forms.ModelMultipleChoiceField(Faction.objects.all().order_by('name'), required=False)

    class Meta:
        model = DigitalPack
        fields = ['name', 'page_is_draft',
                  'release_date', 'visible_on_release', 'purchasable_on_release', 'listed_on_release',
                  'preorder_or_secondary_release_date',
                  'visible_on_preorder_secondary', 'purchasable_on_preorder_secondary', 'listed_on_preorder_secondary',
                  'description',
                  'pack_contents',
                  'price', 'default_price', 'enable_discounts',
                  'pay_what_you_want',
                  'categories',
                  'games', 'factions', 'attributes',
                  # 'grant_to_user_lists',
                  'grant_to_crowdfund_rewards',
                  ]
        widgets = {
            'release_date': AdminDateWidget(),
            'preorder_or_secondary_release_date': AdminDateWidget(),
        }

    def __init__(self, *args, **kwargs):
        partner = kwargs.pop('partner')
        super(AddDigitalPackForm, self).__init__(*args, **kwargs)
        self.fields['pack_contents'].queryset = DigitalItem.objects.filter(partner=partner).order_by(
            'product__name').order_by('product__release_date')
        self.fields['grant_to_crowdfund_rewards'].required = False
        self.fields['grant_to_crowdfund_rewards'].queryset = Reward.objects.filter(campaign__partner=partner)
