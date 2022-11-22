from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from djmoney.forms import MoneyField
from treewidget.fields import TreeModelMultipleChoiceField

from game_info.models import Game, Faction
from partner.models import Partner
from shop.models import Product, ProductImage, Item, Category, MadeToOrder, InventoryItem, CustomChargeItem, Publisher
from django.forms import widgets


class AddProductForm(forms.ModelForm):
    categories = TreeModelMultipleChoiceField(required=False, queryset=Category.objects.all(),
                                              settings={
                                                  'show_buttons': True, 'filtered': True},
                                              )

    categories.widget.attrs.update({'class': 'max-w-full'})

    publisher = forms.ModelChoiceField(Publisher.objects.all().order_by('name'), required=False)
    games = forms.ModelMultipleChoiceField(Game.objects.all().order_by('name'), required=False)
    factions = forms.ModelMultipleChoiceField(Faction.objects.all().order_by('name'), required=False)

    class Meta:
        model = Product
        fields = ['name', 'page_is_draft',
                  'release_date', 'visible_on_release', 'purchasable_on_release', 'listed_on_release',
                  'preorder_or_secondary_release_date',
                  'visible_on_preorder_secondary', 'purchasable_on_preorder_secondary', 'listed_on_preorder_secondary',
                  'description',
                  'categories', 'barcode', 'msrp', 'map', 'weight', 'in_store_pickup_only',
                  'games', 'editions', 'formats', 'factions', 'attributes', 'publisher', 'all_retail'
                  ]
        widgets = {
            'release_date': AdminDateWidget(),
            'preorder_or_secondary_release_date': AdminDateWidget()
        }


class AddInventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['current_inventory', 'allow_backorders',
                  'price', 'default_price', 'featured', 'preallocated']

    def __init__(self, *args, **kwargs):
        partner = kwargs.pop('partner')
        product = kwargs.pop('product')
        super().__init__(*args, **kwargs)
        if partner and product:
            self.fields['price'].initial = product.get_price_from_rule(partner)
            self.fields['default_price'].initial = product.get_price_from_rule(
                partner)


class UploadImage(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text']


def invert_order_string(order_str):
    return order_str[1:] if order_str.startswith('-') else '-' + order_str


class FiltersForm(forms.Form):
    search = forms.CharField(required=False)
    in_stock_only = forms.BooleanField(required=False)

    SORT_RELEASE_DATE = "-release_date"
    SORT_PRICE = "price"
    SORT_ALPHABETICAL = "name"

    SORT_OPTIONS = (
        (SORT_RELEASE_DATE, "Release Date, New-Old"),
        (invert_order_string(SORT_RELEASE_DATE), "Release Date, Old-New"),
        (SORT_ALPHABETICAL, "Name, A-Z"),
        (invert_order_string(SORT_ALPHABETICAL), "Name, Z-A"),
        # (SORT_PRICE, "Price")
    )

    order_by = forms.ChoiceField(
        choices=SORT_OPTIONS, required=False, initial=SORT_RELEASE_DATE)

    featured_products_only = forms.BooleanField(required=False)

    page_size = forms.IntegerField(
        required=False, widget=widgets.NumberInput(), initial=10)
    page_number = forms.IntegerField(
        required=False, widget=widgets.HiddenInput(), initial=1)

    categories = TreeModelMultipleChoiceField(required=False, queryset=Category.objects.all(),
                                              settings={
                                                  'show_buttons': False, 'filtered': True},
                                              )

    partner = forms.ModelChoiceField(Partner.objects.filter(hide=False).order_by('name'),
                                     to_field_name='slug', required=False)

    product_type = forms.MultipleChoiceField(choices=Item.PRODUCT_TYPES, widget=widgets.CheckboxSelectMultiple(),
                                             required=False)
    price_minimum = MoneyField(required=False)
    price_maximum = MoneyField(required=False)

    publisher = forms.ModelChoiceField(Publisher.objects.all().order_by('name'), required=False)
    game = forms.ModelChoiceField(Game.objects.all().order_by('name'), required=False)
    faction = forms.ModelChoiceField(Faction.objects.all().order_by('name'), required=False)

    def __init__(self, *args, **kwargs):
        manage = kwargs.pop('manage')
        super(FiltersForm, self).__init__(*args, **kwargs)

        partner = self.data.get('partner')

        publisher = self.data.get('publisher')
        game = self.data.get('game')
        if publisher:
            self.fields['game'].queryset = Game.objects.filter(publisher=publisher).order_by('name')
            self.fields['faction'].queryset = Faction.objects.filter(game__publisher=publisher).order_by('name')
        if game:
            self.fields['faction'].queryset = Faction.objects.filter(game=game).order_by('name')

        if manage:
            self.fields['out_of_stock_only'] = forms.BooleanField(required=False)
            self.fields['out_of_stock_only'].initial = False
            self.fields['sold_out_only'] = forms.BooleanField(required=False)
            self.fields['sold_out_only'].initial = False


class AddMTOItemForm(forms.ModelForm):
    class Meta:
        model = MadeToOrder
        fields = ['needs_quote', 'digital_purchase_necessary', 'approx_lead', 'current_inventory', 'price',
                  'default_price']


class CreateCustomChargeForm(forms.ModelForm):
    email = forms.CharField()

    class Meta:
        model = CustomChargeItem
        fields = ['product', 'price', 'description']

    def __init__(self, *args, **kwargs):
        partner = kwargs.pop('partner')

        super(CreateCustomChargeForm, self).__init__(*args, **kwargs)
        self.fields['product'].required = False
        self.fields['product'].queryset = (Product.objects.filter(all_retail=True) | Product.objects.filter(
            partner=partner)).order_by('name').distinct()

    def clean(self):
        cleaned_data = super().clean()
        try:
            user = User.objects.get(email=cleaned_data['email'])
        except Exception:
            raise ValidationError("Customer for email address does not exist")
