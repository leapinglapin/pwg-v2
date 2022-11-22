from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

# Create your views here.
from django.template.response import TemplateResponse
from django.urls import reverse

from user_list.forms import UserListForm, UserListCSVImportForm
from user_list.models import UserList, UserListEntry, EmailInvitation
from partner.models import get_partner_or_401


def manage_lists(request, partner_slug):
    partner = get_partner_or_401(request, partner_slug)
    lists = UserList.objects.filter(partner=partner)
    context = {
        'partner': partner,
        'lists': lists,
    }
    return TemplateResponse(request, "user_list/manage_lists.html", context=context)


def view_user_list(request, partner_slug, list_id):
    partner = get_partner_or_401(request, partner_slug)
    ulist = UserList.objects.get(id=list_id)
    form = UserListCSVImportForm(instance=ulist)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserListCSVImportForm(request.POST, instance=ulist)
        print(form)
        # check whether it's valid:
        if form.is_valid():
            ulist = form.save(partner=partner)
            print(ulist)
            # redirect to a new URL:
    users = UserListEntry.objects.filter(user_list=ulist).order_by('user')
    context = {
        'form': form,
        'partner': partner,
        'list': ulist,
        'user_list_entries': users,
        'invitations': EmailInvitation.objects.filter(user_list=ulist).order_by('original__plaintext'),
        'emails': users.filter(opt_into_emails=True).values_list('user__email').distinct()
    }
    return TemplateResponse(request, "user_list/view_user_list.html", context=context)


def create_edit_list(request, partner_slug, list_id=None):
    partner = get_partner_or_401(request, partner_slug)
    ulist = None
    if list_id:
        ulist = UserList.objects.get(id=list_id)
    form = UserListForm(instance=ulist)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserListForm(request.POST, instance=ulist)
        # check whether it's valid:
        if form.is_valid():
            ulist = form.save(partner=partner)
            # redirect to a new URL:
            return HttpResponseRedirect(
                reverse("view_user_list", kwargs={'partner_slug': partner.slug, 'list_id': ulist.id}))
    context = {
        'form': form,
        'partner': partner,
    }
    return TemplateResponse(request, "create_from_form.html", context=context)


def remove_user_endpoint(request, partner_slug, ule_id):
    ule = UserListEntry.objects.get(id=ule_id)
    partner = get_partner_or_401(request, partner_slug, [ule.user_list])

    ule.delete()
    return HttpResponse(status=200)


def delete_invitation_endpoint(request, partner_slug, inv_id):
    print(inv_id)
    print(type(inv_id))
    inv = EmailInvitation.objects.get(id=inv_id)
    partner = get_partner_or_401(request, partner_slug, [inv.user_list])

    inv.delete()
    return HttpResponse(status=200)
