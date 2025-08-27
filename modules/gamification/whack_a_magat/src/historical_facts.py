"""
Historical Facts Provider for Anti-Fascist Education
WSP-Compliant implementation
"""

import random
from typing import List, Dict, Optional
from datetime import datetime

class HistoricalFactsProvider:
    """
    Provides historical parallels between 1933 and modern times
    Educational content about fascism and authoritarianism
    """
    
    def __init__(self):
        self._load_facts()
    
    def _load_facts(self):
        """Load historical facts and parallels"""
        self.facts = [
            {
                "year": "1933",
                "event": "Hitler appointed Chancellor with only 33% support",
                "modern": "2016: Trump won with minority popular vote",
                "category": "electoral"
            },
            {
                "year": "1933",
                "event": "Enabling Act gave Hitler dictatorial powers",
                "modern": "2025: Project 2025 seeks similar executive expansion",
                "category": "power_grab"
            },
            {
                "year": "1933",
                "event": "Jews blamed for Germany's problems",
                "modern": "Today: Immigrants scapegoated for economic issues",
                "category": "scapegoating"
            },
            {
                "year": "1933",
                "event": "'Lügenpresse' (lying press) propaganda",
                "modern": "Today: 'Fake news' attacks on media",
                "category": "propaganda"
            },
            {
                "year": "1933",
                "event": "Book burnings at universities",
                "modern": "Today: Book bans in schools and libraries",
                "category": "censorship"
            },
            {
                "year": "1933",
                "event": "SA Brownshirts used street violence",
                "modern": "Today: Proud Boys and militia intimidation",
                "category": "violence"
            },
            {
                "year": "1933",
                "event": "Reichstag Fire used to suspend civil liberties",
                "modern": "2001: 9/11 used to pass Patriot Act",
                "category": "emergency_powers"
            },
            {
                "year": "1933",
                "event": "Trade unions banned and leaders arrested",
                "modern": "Today: Union-busting and right-to-work laws",
                "category": "labor"
            },
            {
                "year": "1933",
                "event": "Gleichschaltung - forced coordination of society",
                "modern": "Today: Culture war to control institutions",
                "category": "control"
            },
            {
                "year": "1934",
                "event": "Night of Long Knives - purge of SA leadership",
                "modern": "Today: Loyalty tests and purges in government",
                "category": "purges"
            },
            {
                "year": "1935",
                "event": "Nuremberg Laws stripped Jews of citizenship",
                "modern": "Today: Attempts to end birthright citizenship",
                "category": "citizenship"
            },
            {
                "year": "1938",
                "event": "Kristallnacht - coordinated violence against Jews",
                "modern": "2017: Charlottesville 'Unite the Right' rally",
                "category": "violence"
            }
        ]
        
        self.warning_signs = [
            "📍 Powerful and continuing nationalism",
            "📍 Disdain for human rights",
            "📍 Identification of enemies as unifying cause",
            "📍 Supremacy of military",
            "📍 Rampant sexism",
            "📍 Controlled mass media",
            "📍 Obsession with national security",
            "📍 Religion and government intertwined",
            "📍 Corporate power protected",
            "📍 Labor power suppressed",
            "📍 Disdain for intellectuals and arts",
            "📍 Obsession with crime and punishment",
            "📍 Rampant cronyism and corruption",
            "📍 Fraudulent elections"
        ]
        
        self.quotes = [
            {
                "quote": "When fascism comes to America, it will be wrapped in the flag and carrying a cross.",
                "author": "Attributed to Sinclair Lewis",
                "year": "1935"
            },
            {
                "quote": "Those who cannot remember the past are condemned to repeat it.",
                "author": "George Santayana",
                "year": "1905"
            },
            {
                "quote": "First they came for the socialists, and I did not speak out—because I was not a socialist...",
                "author": "Martin Niemöller",
                "year": "1946"
            },
            {
                "quote": "The ideal subject of totalitarian rule is not the convinced Nazi or Communist, but people for whom the distinction between fact and fiction, true and false, no longer exists.",
                "author": "Hannah Arendt",
                "year": "1951"
            },
            {
                "quote": "Fascism should more appropriately be called Corporatism because it is a merger of state and corporate power.",
                "author": "Attributed to Benito Mussolini",
                "year": "1930s"
            }
        ]
    
    def get_random_fact(self) -> str:
        """Get a random historical parallel"""
        fact = random.choice(self.facts)
        
        message = f"📜 **HISTORICAL PARALLEL**\n"
        message += f"{fact['year']}: {fact['event']}\n"
        message += f"→ {fact['modern']}\n\n"
        message += "Those who don't learn from history are doomed to repeat it."
        
        return message
    
    def get_fact_by_category(self, category: str) -> Optional[str]:
        """Get a fact from specific category"""
        category_facts = [f for f in self.facts if f['category'] == category]
        
        if not category_facts:
            return None
        
        fact = random.choice(category_facts)
        
        message = f"📜 **{category.upper().replace('_', ' ')}**\n"
        message += f"{fact['year']}: {fact['event']}\n"
        message += f"→ {fact['modern']}"
        
        return message
    
    def get_warning_signs(self, count: int = 3) -> str:
        """Get random warning signs of fascism"""
        signs = random.sample(self.warning_signs, min(count, len(self.warning_signs)))
        
        message = "⚠️ **WARNING SIGNS OF FASCISM**\n"
        for sign in signs:
            message += f"{sign}\n"
        
        return message
    
    def get_quote(self) -> str:
        """Get a random anti-fascist quote"""
        quote_data = random.choice(self.quotes)
        
        message = f"💭 **WISDOM FROM HISTORY**\n"
        message += f'"{quote_data["quote"]}"\n'
        message += f"— {quote_data['author']} ({quote_data['year']})"
        
        return message
    
    def get_timeline(self, start_year: str = "1933", end_year: str = "1939") -> str:
        """Get timeline of events"""
        timeline_facts = [f for f in self.facts if start_year <= f['year'] <= end_year]
        timeline_facts.sort(key=lambda x: x['year'])
        
        message = f"📅 **TIMELINE {start_year}-{end_year}**\n"
        for fact in timeline_facts[:5]:  # Limit to 5 for readability
            message += f"{fact['year']}: {fact['event']}\n"
        
        return message