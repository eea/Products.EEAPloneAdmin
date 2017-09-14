===============
EEA Plone Admin
===============
.. image:: http://ci.eionet.europa.eu/job/eea/job/Products.EEAPloneAdmin/job/master/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea/job/Products.EEAPloneAdmin/job/master/display/redirect

EEA Plone Admin is a product that adds a customization policy to a Plone 4 portal.
The policy contains methods for Plone configuration.

Contents
========

.. contents::


Installation
============

Place EEAPloneAdmin in the Products directory of your Zope instance
and restart the server.

In Plone go to the 'Site Setup' page and click on the 'Add/Remove
Products' link.

Choose EEAPloneAdmin (check its checkbox) and click the 'Install' button.

You may have to empty your browser cache to see the effects of the
product installation/uninstallation.

Uninstall -- This can be done from the same management screen.

Selecting a skin
----------------

Depending on the value given to SELECTSKIN (in config.py), the skin will be
selected (or not) as default one while installing the product. If you need
to switch from a default skin to another, go to the 'Site Setup' page, and
choose 'Skins' (as portal manager). You can also decide from that page if
members can choose their preferred skin and, in that case, if the skin
cookie should be persistent.

Note -- Don't forget to perform a full refresh of the page or reload all
images (not from browser cache) after selecting a skin.
In Firefox, you can do so by pressing the 'shift' key while reloading the
page. In IE, use the key combination <Ctrl-F5>.


Source code
===========

- Latest source code (Plone 4 compatible):
  https://github.com/eea/Products.EEAPloneAdmin


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Plone Admin (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Funding
=======

EEA_ - European Environment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
