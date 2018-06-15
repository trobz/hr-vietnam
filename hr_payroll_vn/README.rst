.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3
================
HR Payroll
================

This module extends the feature payroll management
* Allow to define Global Salary Rule, these rules are calculated only one time based on
total value of payslip lines generated for each contracts

* Handle a special case with several consecutive active contracts in payslip period.
- Example: There are 2 consecutive valid contracts of employee A in 03/2014
    - Contract 1 from 12/01/2014 to 11/03/2014
    - Contract 2 from 12/03/2014 to 11/03/2015
    - Compute payslip 03/2014:
        - Calculate worked days and inputs on payslip based on these contracts
        - Generate payslip lines based on salary structure defined on these contracts
  
Installation
============

To install this module, you need to install:

* Native odoo modules
    - hr_payroll
    
* Trobz modules
    - hr_contract_vn
    - hr_holiday_vn

Usage
=====

To use this module, you need to:

* Go to Employees > Contracts
- Define the labor contracts and all information that need for payroll calculation:
    

* Go to Employees > Employees
- Know the hired date of an employee

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