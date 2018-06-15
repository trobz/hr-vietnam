.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=====================
HR Contract Extension
=====================

This module extends the feature contract management

* Calculate hired date of an employee
    - Display field Hired Date after field Related User in tab HR Settings > Status 
    - The first date at work, get the starting date of the first labor contract for a continuous working period.
      For instance, the Hired Date will be January 1st 2012 if the employee works from Jan 1st 2010 to December 31st 2010,
      then stop working during one year, then has a new contract from Jan 1st 2012 to December 31st 2012, =
      then has a contract from Jan 1st 2013 until now.

* Separate trial contracts and official contracts

* Advanced filters to search and group by contract time
    - Search contract in the past/current/future. Calculated by compare today with the contract duration.
    - Change the color of contracts, grey for the past contracts, blue for future contracts
  
Installation
============

To install this module, you need to install module hr_contract of navtive Odoo

Usage
=====

To use this module, you need to:

* Go to Employees > Contracts
- Use the advanced filters and the changing color of contract records based on contract time

* Go to Employees > Employees
- View the hired date of an employee

Known issues / Roadmap
======================

* ...

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/trobz/hr-vietnam/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Le Hoang An <anlh@trobz.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
