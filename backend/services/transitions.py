"""
Transitions Service

This service provides transition text between content blocks to create
a smooth, cohesive reading experience.

Transitions are context-aware and adapt based on:
- Which blocks are being connected
- Customer's situation (age, method, challenges)
- Flow of the guide
"""

from typing import Dict, Any


class TransitionGenerator:
    """Generates smooth transitions between content blocks."""
    
    def __init__(self):
        """Initialize the transition generator."""
        self.transitions = self._load_transitions()
    
    def _load_transitions(self) -> Dict[str, Dict[str, str]]:
        """
        Load all transition templates.
        
        Structure:
        {
            'from_block_type': {
                'to_block_type': 'transition text'
            }
        }
        """
        return {
            # From age blocks
            'age': {
                'method': self._age_to_method(),
                'challenge': self._age_to_challenge(),
            },
            
            # From method overview
            'method_overview': {
                'method_implementation': self._method_overview_to_implementation(),
                'challenge': self._method_to_challenge(),
            },
            
            # From method implementation
            'method_implementation': {
                'challenge': self._method_to_challenge(),
                'situation': self._method_to_situation(),
            },
            
            # From challenge blocks
            'challenge': {
                'challenge': self._challenge_to_challenge(),
                'situation': self._challenge_to_situation(),
            },
            
            # From situation blocks
            'situation': {
                'end': self._situation_to_end(),
            }
        }
    
    def get_transition(self, from_block: str, to_block: str, context: Dict[str, Any] = None) -> str:
        """
        Get transition text between two blocks.
        
        Args:
            from_block: Identifier of the block we're transitioning from
            to_block: Identifier of the block we're transitioning to
            context: Optional context for personalization (customer name, baby age, etc.)
            
        Returns:
            Transition text (markdown formatted)
        """
        from_type = self._get_block_type(from_block)
        to_type = self._get_block_type(to_block)
        
        # Get transition template
        transition_template = self.transitions.get(from_type, {}).get(to_type, '')
        
        if not transition_template:
            # Fallback to generic transition
            transition_template = self._generic_transition()
        
        # Personalize if context provided
        if context:
            transition_template = self._personalize_transition(transition_template, context)
        
        return transition_template
    
    def _get_block_type(self, block_id: str) -> str:
        """Determine the type of a block from its identifier."""
        if block_id.startswith('age_'):
            return 'age'
        elif block_id.startswith('method_') and 'overview' in block_id:
            return 'method_overview'
        elif block_id.startswith('method_') and 'implementation' in block_id:
            return 'method_implementation'
        elif block_id.startswith('challenge_'):
            return 'challenge'
        elif block_id.startswith('situation_'):
            return 'situation'
        else:
            return 'unknown'
    
    def _personalize_transition(self, template: str, context: Dict[str, Any]) -> str:
        """Replace placeholders in transition text with personalized information."""
        # Replace common placeholders
        replacements = {
            '{customer_name}': context.get('customer_name', 'you'),
            '{baby_age}': context.get('baby_age', 'your baby'),
            '{method}': context.get('method', 'this method'),
        }
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        return result
    
    # Transition templates
    
    def _age_to_method(self) -> str:
        return """
---

## Choosing Your Sleep Training Method

Now that you understand your baby's developmental stage and sleep needs, it's time to choose the sleep training method that will work best for your family. The method you choose will be your roadmap for the next 1-3 weeks.

There's no "right" method - only the method that fits your parenting philosophy, your baby's temperament, and your family's needs. Let's explore your chosen approach in detail.

"""
    
    def _age_to_challenge(self) -> str:
        return """
---

## Addressing Your Specific Sleep Challenge

Before we dive into the sleep training method, we need to address the specific sleep challenge you're facing. This challenge is likely the main reason your baby isn't sleeping well, and tackling it head-on will set you up for success.

"""
    
    def _method_overview_to_implementation(self) -> str:
        return """
---

## Putting It Into Action: Your Step-by-Step Implementation Plan

You understand the method - now it's time to implement it. This section provides your detailed, night-by-night action plan. Follow these steps exactly, stay consistent, and trust the process.

"""
    
    def _method_to_challenge(self) -> str:
        return """
---

## Addressing Your Specific Sleep Challenge

Now that you have your sleep training method, let's tackle the specific challenge that's been disrupting your baby's sleep. This challenge requires special attention because it's likely the root cause of your current sleep struggles.

The good news: you'll use the same sleep training method you just learned, but with specific strategies tailored to this challenge.

"""
    
    def _method_to_situation(self) -> str:
        return """
---

## Adapting to Your Unique Situation

You have your method and you're ready to implement it. But your living situation requires some special considerations to make sleep training work smoothly. Let's address how to adapt your approach to your specific circumstances.

"""
    
    def _challenge_to_challenge(self) -> str:
        return """
---

## Your Second Challenge: Additional Strategies

You're tackling multiple sleep challenges - that's completely normal. Many babies have more than one sleep association or issue. The good news: the strategies you just learned will help with this challenge too.

Let's address this additional challenge with specific, targeted solutions.

"""
    
    def _challenge_to_situation(self) -> str:
        return """
---

## Making It Work in Your Situation

You have your sleep training method and strategies for your specific challenges. Now let's make sure you can implement everything successfully given your unique living situation.

"""
    
    def _situation_to_end(self) -> str:
        return """
---

## You're Ready to Begin

You now have everything you need to transform your baby's sleep:

✅ Understanding of your baby's developmental stage and sleep needs
✅ A proven sleep training method with step-by-step instructions
✅ Specific strategies for your unique challenges
✅ Adaptations for your living situation

**The most important thing now is to start and stay consistent.** Pick your start date, prepare your environment, and commit to following through for at least one week.

Remember: the crying is temporary (typically 3-7 nights), but the benefits last for years. You're teaching your baby a valuable life skill, and you're giving your whole family the gift of better sleep.

"""
    
    def _generic_transition(self) -> str:
        return """
---

## Next Steps

Let's continue building your personalized sleep training plan.

"""
    
    def get_introduction(self, context: Dict[str, Any]) -> str:
        """
        Generate personalized introduction for the guide.
        
        Args:
            context: Customer information (name, baby age, challenges, etc.)
            
        Returns:
            Personalized introduction text
        """
        customer_name = context.get('customer_name', 'there')
        baby_age = context.get('baby_age_display', 'your baby')
        method = context.get('method_display', 'sleep training')
        main_challenge = context.get('main_challenge_display', 'sleep challenges')
        
        intro = f"""# Your Personalized Sleep Training Guide

Welcome{f', {customer_name}' if customer_name != 'there' else ''}! This guide has been customized specifically for your situation: a {baby_age} old baby who needs help with {main_challenge}.

## What's Inside This Guide

This isn't a generic sleep training book. Every section has been selected based on your quiz responses to give you exactly what you need - nothing more, nothing less.

**Your personalized guide includes:**

- Age-appropriate sleep foundations for your {baby_age} old
- Complete {method} implementation instructions
- Specific strategies for {main_challenge}
- Practical solutions tailored to your situation

## How to Use This Guide

**Read it all the way through first.** Understanding the complete picture will help you implement more effectively.

**Then, follow the steps in order.** Each section builds on the previous one.

**Stay consistent.** The method works, but only if you follow it consistently for at least one week.

**Trust the process.** The first few nights are hard, but improvement comes quickly.

## What to Expect

- **Night 1-2:** The hardest nights. Lots of crying, lots of doubt. This is normal.
- **Night 3-5:** Noticeable improvement. Less crying, longer sleep stretches.
- **Night 6-7:** Significant progress. Baby falling asleep faster, sleeping longer.
- **Week 2+:** Success. Baby sleeping independently, everyone better rested.

The crying is temporary. The benefits last for years.

Let's get started.

---
"""
        return intro
    
    def get_conclusion(self, context: Dict[str, Any]) -> str:
        """
        Generate personalized conclusion for the guide.
        
        Args:
            context: Customer information
            
        Returns:
            Personalized conclusion text
        """
        conclusion = """
---

# Final Thoughts: You've Got This

You've reached the end of your personalized sleep training guide. You now have everything you need to succeed:

## Your Action Plan

**This Week:**
1. Choose your start date (ideally a Friday or Saturday)
2. Prepare your environment (blackout curtains, white noise, etc.)
3. Review your chosen method one more time
4. Commit to consistency for at least 7 nights

**During Sleep Training:**
1. Follow your method exactly as outlined
2. Stay consistent every single time
3. Track your progress (it helps to see improvement)
4. Support each other (if co-parenting)
5. Remember your "why" on tough nights

**After Success:**
1. Maintain your routine and schedule
2. Handle setbacks consistently (illness, travel, etc.)
3. Adjust wake windows as baby grows
4. Trust that your baby has learned this skill

## Remember

- **The crying is temporary** - typically 3-7 nights
- **The benefits last for years** - better sleep for everyone
- **You're not harming your baby** - research proves this
- **You're teaching a valuable skill** - independent sleep
- **Thousands of families have done this** - you can too

## When to Reach Out for Help

Most families succeed with sleep training on their own. But reach out for support if:

- No improvement after 7-10 nights of consistency
- Baby seems to be in pain or distress (not just protesting)
- You're struggling with consistency
- You need emotional support

## The Bottom Line

Sleep training is one of the best investments you can make in your family's wellbeing. Yes, it's hard. Yes, there will be crying. But it's temporary, and the payoff is enormous.

Better sleep means:
- A happier, healthier baby
- More patient, engaged parents
- A more harmonious household
- Energy for the things that matter

You've got all the tools. You've got the knowledge. You've got the plan.

Now it's time to execute.

**Trust yourself. Trust your baby. Trust the process.**

You've got this.

---

## Need More Support?

If you found this guide helpful, we have additional resources for other parenting challenges:

- **Toddler Tantrums Toolkit** - Handling meltdowns with confidence
- **Potty Training Mastery** - Stress-free potty training in days
- **Picky Eating Solutions** - Getting your toddler to eat

Visit napocalypse.com for more information.

---

*Remember: You're not alone in this journey. Thousands of parents have successfully used these methods. You can do this too.*
"""
        return conclusion


# Example usage
if __name__ == "__main__":
    generator = TransitionGenerator()
    
    # Test transitions
    print("=== Age to Method Transition ===")
    print(generator.get_transition('age_7_12_months', 'method_cio_overview'))
    
    print("\n=== Method to Challenge Transition ===")
    print(generator.get_transition('method_cio_implementation', 'challenge_feeding_to_sleep'))
    
    print("\n=== Challenge to Situation Transition ===")
    print(generator.get_transition('challenge_nap_training', 'situation_apartment_living'))
    
    # Test personalized introduction
    print("\n=== Personalized Introduction ===")
    context = {
        'customer_name': 'Sarah',
        'baby_age_display': '8-month',
        'method_display': 'Cry-It-Out',
        'main_challenge_display': 'feeding to sleep'
    }
    print(generator.get_introduction(context))