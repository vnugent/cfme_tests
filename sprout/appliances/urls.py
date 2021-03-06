# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import login, logout, password_change

from appliances import api, views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^check_appliance/(?P<provider_id>[^/]+)/(?P<appliance_name>[^/]+)$',
        views.check_appliance, name="check_appliance"),
    url(r'^check_template/(?P<provider_id>[^/]+)/(?P<template_name>[^/]+)$',
        views.check_template, name="check_template"),
    url(r'^check_pool/(?P<pool_id>[^/]+)',
        views.check_pool, name="check_pool"),
    url(r'^check_pools',
        views.check_pools, name="check_pools"),
    url(r'^api$', csrf_exempt(api.jsonapi)),
    url(r'^api.html$', api.jsonapi_doc, name="jsonapi_doc"),
    url(r'^provider_usage$', views.provider_usage, name="provider_usage"),
    url(r'^providers$', views.providers, name="providers"),
    url(r'^providers/(?P<provider_id>[^/]+)$', views.providers, name="specific_provider"),
    url(r'^providers/([^/]+)/enable$', views.provider_enable_disable,
        {"disabled": False}, name="provider_enable"),
    url(r'^providers/([^/]+)/disable$', views.provider_enable_disable,
        {"disabled": True}, name="provider_disable"),
    url(r'^templates$', views.templates, name="templates"),
    url(r'^templates/(?P<group_id>[^/]+)$', views.templates, name="group_templates"),
    url(r'^templates/(?P<group_id>[^/]+)/(?P<prov_id>[^/]+)$', views.templates,
        name="group_provider_templates"),
    url(r'^my$', views.my_appliances, {"show_user": "my"}, name="my_appliances"),
    url(r'^all$', views.my_appliances, {"show_user": "all"}, name="all_appliances"),
    url(r'^user/(?P<show_user>[a-z_A-Z0-9-]+)?$', views.my_appliances,
        name="user_appliances"),
    url(r'^appliance/(?P<appliance_id>\d+)/(?P<action>[a-z_A-Z0-9-]+)(?:/(?P<x>[a-z_A-Z0-9-]+))?$',
        views.appliance_action, name="appliance_action"),
    url(r'^pool/(?P<pool_id>\d+)/prolong/(?P<minutes>\d+)$',
        views.prolong_lease_pool, name="prolong_lease_pool"),
    url(r'^appliances/dontexpire-pool/(?P<pool_id>\d+)$', views.dont_expire_pool,
        name="dont_expire_pool"),
    url(r'^shepherd$', views.shepherd, name="shepherd"),
    url(r'^login$', login, {'template_name': 'login.html'}, name="login"),
    url(r'^change_password$', password_change, {'template_name': 'password.html'},
        name="password_change"),
    url(r'^change_password/done$', views.go_home, name='password_change_done'),
    url(r'^logout(?:/(?P<next_page>.*?))?$', logout, name="logout"),
    url(r'^pool/request$', views.request_pool, name="request_pool"),
    url(r'^pool/transfer$', views.transfer_pool, name="transfer_pool"),
    url(r'^pool/kill/(?P<pool_id>\d+)$', views.kill_pool, name="kill_pool"),
    url(r'^vms$', views.vms, name="vms_default"),
    url(r'^vms/(?P<current_provider>[a-z_A-Z0-9-]+)$', views.vms, name="vms_at_provider"),
    url(r'^ajax/templates/delete$', views.delete_template_provider,
        name="delete_template_provider"),
    url(r'^ajax/vms/(?P<current_provider>[a-z_A-Z0-9-]+)$', views.vms_table, name="vms_table"),
    url(r'^ajax/versions_for_group$', views.versions_for_group, name="versions_for_group"),
    url(r'^ajax/rename_appliance$', views.rename_appliance, name="rename_appliance"),
    url(r'^ajax/task_result$', views.task_result, name="task_result"),
    url(r'^ajax/date_for_version_group$', views.date_for_group_and_version,
        name="date_for_group_and_version"),
    url(r'^ajax/pool/description$', views.set_pool_description, name="set_pool_description"),
    url(r'^ajax/providers_for_date_group_version$', views.providers_for_date_group_and_version,
        name="providers_for_date_group_and_version"),
    url(r'^ajax/vms/power/([a-z_A-Z0-9-]+)$', views.power_state, name="power_state"),
    url(r'^ajax/vms/buttons/([a-z_A-Z0-9-]+)$', views.power_state_buttons,
        name="power_state_buttons"),
    url(r'^ajax/vms/action/([a-z_A-Z0-9-]+)$', views.vm_action, name="vm_action"),
]
