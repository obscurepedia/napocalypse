"""
Advanced Playbook Service
Handles module selection and drip delivery scheduling
"""

from datetime import datetime, timedelta
from typing import List, Dict
from database import db, Customer, Order, ModuleAssigned


class AdvancedPlaybookService:
    """Manages Advanced Playbook module delivery"""
    
    def __init__(self):
        self.delivery_schedule = {
            0: 'immediate',  # Day 7 (purchase day) - Module 1
            7: 'week_2',     # Day 14 - Module 2
            14: 'week_3',    # Day 21 - Module 3
            21: 'week_4',    # Day 28 - Module 4
            25: 'completion' # Day 32 - Completion email
        }
    
    def select_modules_for_customer(self, customer_id: int) -> List[str]:
        """
        Select which 4 modules customer gets based on their quiz responses
        
        Returns:
            List of 4 module names in delivery order
        """
        # Get customer's assigned modules from original purchase
        modules_assigned = ModuleAssigned.query.filter_by(
            customer_id=customer_id
        ).all()
        
        module_names = [m.module_name for m in modules_assigned]
        
        # Determine the 4 modules to deliver
        selected_modules = []
        
        # Module 1: Method module (always first)
        method_module = self._get_method_module(module_names)
        if method_module:
            selected_modules.append(method_module)
        
        # Module 2: Challenge module (always second)
        challenge_module = self._get_challenge_module(module_names)
        if challenge_module:
            selected_modules.append(challenge_module)
        
        # Module 3: Nap training (always third)
        selected_modules.append('module_10_nap_training')
        
        # Module 4: Early morning or additional challenge (always fourth)
        additional_module = self._get_additional_module(module_names)
        if additional_module:
            selected_modules.append(additional_module)
        else:
            selected_modules.append('module_11_early_morning')
        
        return selected_modules
    
    def _get_method_module(self, modules: List[str]) -> str:
        """Get the method module (CIO or Gentle)"""
        if 'module_5_cio' in modules:
            return 'module_5_cio'
        elif 'module_6_gentle' in modules:
            return 'module_6_gentle'
        return 'module_5_cio'  # Default
    
    def _get_challenge_module(self, modules: List[str]) -> str:
        """Get the primary challenge module"""
        challenge_modules = [
            'module_7_feeding',
            'module_9_motion_rocking',
            'module_12_pacifier'
        ]
        
        for module in challenge_modules:
            if module in modules:
                return module
        
        return 'module_7_feeding'  # Default
    
    def _get_additional_module(self, modules: List[str]) -> str:
        """Get additional module if applicable"""
        additional_modules = [
            'module_8_room_sharing',
            'module_11_early_morning',
            'module_12_pacifier'
        ]
        
        for module in additional_modules:
            if module in modules and module not in [
                self._get_method_module(modules),
                self._get_challenge_module(modules)
            ]:
                return module
        
        return None
    
    def schedule_deliveries(self, customer_id: int, upsell_order_id: int, 
                          purchase_date: datetime) -> Dict:
        """
        Schedule all 4 module deliveries + completion email
        
        Args:
            customer_id: Customer ID
            upsell_order_id: Upsell order ID
            purchase_date: When they purchased the upsell
            
        Returns:
            Dict with scheduled delivery dates
        """
        from database import AdvancedPlaybookDelivery
        
        # Get modules for this customer
        modules = self.select_modules_for_customer(customer_id)
        
        # Schedule deliveries
        schedule = {}
        
        # Immediate delivery (Day 7 - purchase day)
        delivery_1 = AdvancedPlaybookDelivery(
            customer_id=customer_id,
            upsell_order_id=upsell_order_id,
            module_number=1,
            module_name=modules[0],
            scheduled_date=purchase_date.date(),
            status='pending'
        )
        db.session.add(delivery_1)
        schedule['module_1'] = purchase_date.date()
        
        # Week 2 (Day 14)
        delivery_2 = AdvancedPlaybookDelivery(
            customer_id=customer_id,
            upsell_order_id=upsell_order_id,
            module_number=2,
            module_name=modules[1],
            scheduled_date=(purchase_date + timedelta(days=7)).date(),
            status='pending'
        )
        db.session.add(delivery_2)
        schedule['module_2'] = (purchase_date + timedelta(days=7)).date()
        
        # Week 3 (Day 21)
        delivery_3 = AdvancedPlaybookDelivery(
            customer_id=customer_id,
            upsell_order_id=upsell_order_id,
            module_number=3,
            module_name=modules[2],
            scheduled_date=(purchase_date + timedelta(days=14)).date(),
            status='pending'
        )
        db.session.add(delivery_3)
        schedule['module_3'] = (purchase_date + timedelta(days=14)).date()
        
        # Week 4 (Day 28)
        delivery_4 = AdvancedPlaybookDelivery(
            customer_id=customer_id,
            upsell_order_id=upsell_order_id,
            module_number=4,
            module_name=modules[3],
            scheduled_date=(purchase_date + timedelta(days=21)).date(),
            status='pending'
        )
        db.session.add(delivery_4)
        schedule['module_4'] = (purchase_date + timedelta(days=21)).date()
        
        # Completion email (Day 32)
        completion = AdvancedPlaybookDelivery(
            customer_id=customer_id,
            upsell_order_id=upsell_order_id,
            module_number=5,
            module_name='completion',
            scheduled_date=(purchase_date + timedelta(days=25)).date(),
            status='pending'
        )
        db.session.add(completion)
        schedule['completion'] = (purchase_date + timedelta(days=25)).date()
        
        db.session.commit()
        
        return schedule
    
    def get_module_info(self, module_name: str) -> Dict:
        """Get human-readable info about a module"""
        from services.module_selector import get_module_info
        return get_module_info(module_name)


def schedule_advanced_playbook_delivery(customer_id: int, upsell_order_id: int, 
                                       purchase_date: datetime = None):
    """
    Convenience function to schedule Advanced Playbook delivery
    
    Args:
        customer_id: Customer ID
        upsell_order_id: Upsell order ID
        purchase_date: When they purchased (defaults to now)
    """
    if purchase_date is None:
        purchase_date = datetime.utcnow()
    
    service = AdvancedPlaybookService()
    schedule = service.schedule_deliveries(customer_id, upsell_order_id, purchase_date)
    
    return schedule