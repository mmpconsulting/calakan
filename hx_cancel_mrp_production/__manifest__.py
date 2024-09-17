# -*- coding: utf-8 -*-
#############################################################################
#
#    HorizonX Technologies
#
#    Copyright (C) 2024-TODAY HorizonX Technologies (<https://www.thehorizonx.in>)
#    Author: Harshit Nariya (<https://www.thehorizonx.in>)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'Cancel Manufacturing Order',
    'summary': 'This module adds functionality for users to cancel manufacturing orders that are already completed.',
    'description': """
        This module adds functionality for users to cancel manufacturing orders 
        that are already marked as completed, improving workflow flexibility.
    """,
    'category': 'Manufacturing',
    'version': '16.0.1.0.0',
    # Author Details
    'company': 'HorizonX Technologies',
    'author': 'HorizonX Technologies',
    'maintainer': 'HorizonX Technologies',
    'website': 'https://www.thehorizonx.in',
    'support': 'support@thehorizonx.in',
    # Dependency
    'depends': [
        'mrp',
    ],
    # Data, Security & Views
    'data': [
        'data/ir_actions_server.xml',
        'security/res_groups.xml',
        'views/mrp_production_views.xml',
    ],
    # License
    'license': 'AGPL-3',
    # Other
    'images': ['static/description/banner.png'],
    'application': False,
    'installable': True,
}
