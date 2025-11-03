"""
Historical Facts: 1933 Nazi Germany -> 2025 MAGA America Parallels
Educational content comparing the rise of fascism then and now
WSP-Compliant: Facts for stream education
"""

import random
from typing import List, Dict, Optional
from datetime import datetime

class HistoricalFacts:
    """Provides educational facts comparing 1933 Nazi rise to 2025 MAGA movement"""
    
    def __init__(self):
        # Powerful historical parallels between 1933 and 2025
        self.parallels = [
            {
                "1933": "Hitler blamed Germany's problems on Jews, communists, and 'enemies within'",
                "2025": "Trump blames America's problems on immigrants, 'radical left', and 'deep state'",
                "category": "Scapegoating"
            },
            {
                "1933": "Reichstag Fire used to suspend civil liberties and attack political opponents",
                "2025": "January 6th used to claim victimhood while attacking democratic institutions",
                "category": "False Flags"
            },
            {
                "1933": "Hitler called press 'Lügenpresse' (lying press) to discredit criticism",
                "2025": "Trump calls media 'fake news' and 'enemy of the people'",
                "category": "Media Attacks"
            },
            {
                "1933": "SA brownshirts intimidated voters and attacked opponents",
                "2025": "Proud Boys and militias intimidate voters and threaten violence",
                "category": "Paramilitary Groups"
            },
            {
                "1933": "Book burnings to eliminate 'un-German' ideas and LGBTQ research",
                "2025": "Book bans targeting LGBTQ content and critical race theory",
                "category": "Censorship"
            },
            {
                "1933": "Enabling Act gave Hitler power to bypass parliament",
                "2025": "Project 2025 plans to expand executive power and purge civil service",
                "category": "Power Consolidation"
            },
            {
                "1933": "Jews stripped of citizenship with Nuremberg Laws",
                "2025": "Plans to end birthright citizenship and mass deportations",
                "category": "Citizenship Attacks"
            },
            {
                "1933": "Hitler promised to 'make Germany great again' after WWI humiliation",
                "2025": "MAGA promises to restore mythical past American greatness",
                "category": "False Nostalgia"
            },
            {
                "1933": "Nazi rallies with theatrical staging and cult of personality",
                "2025": "Trump rallies with identical staging and messianic worship",
                "category": "Cult of Personality"
            },
            {
                "1933": "Courts packed with Nazi loyalists to rubber-stamp policies",
                "2025": "Supreme Court packed with ideologues overturning precedents",
                "category": "Judicial Capture"
            },
            {
                "1933": "Trade unions banned and replaced with state-controlled organizations",
                "2025": "Attacks on unions while promoting corporate authoritarianism",
                "category": "Labor Suppression"
            },
            {
                "1933": "Concentration camps for political prisoners started immediately",
                "2025": "ICE detention camps and plans for mass internment facilities",
                "category": "Detention Systems"
            },
            {
                "1933": "Nazi ideology taught in schools as 'racial science'",
                "2025": "PragerU propaganda and whitewashed history in schools",
                "category": "Education Control"
            },
            {
                "1933": "'Germany First' isolationism while secretly planning expansion",
                "2025": "'America First' isolationism while threatening allies",
                "category": "Isolationism"
            },
            {
                "1933": "Gleichschaltung - coordination of all aspects of society under Nazi control",
                "2025": "Project 2025's plan to control all federal agencies",
                "category": "Total Control"
            },
            {
                "1933": "Hitler never won majority vote but seized power through legal manipulation",
                "2025": "Trump lost popular vote twice but uses Electoral College and gerrymandering",
                "category": "Minority Rule"
            },
            {
                "1933": "Nazis burned Institut für Sexualwissenschaft, erasing trans research",
                "2025": "Anti-trans legislation and elimination of gender-affirming care",
                "category": "LGBTQ Persecution"
            },
            {
                "1933": "'Blood and Soil' mythology of racial purity",
                "2025": "'Great Replacement' conspiracy theory and white nationalism",
                "category": "Racial Mythology"
            },
            {
                "1933": "Gestapo secret police monitoring citizens",
                "2025": "Surveillance state expansion and targeting of activists",
                "category": "Police State"
            },
            {
                "1933": "Concordat with Catholic Church for religious cover",
                "2025": "Christian Nationalism providing religious cover for fascism",
                "category": "Religious Exploitation"
            }
        ]
        
        # Quick zingers for chat
        self.quick_facts = [
            "1933: Hitler never won a majority. 2025: Neither did Trump.",
            "1933: Lügenpresse. 2025: Fake News. Same fascist playbook.",
            "1933: Brownshirts. 2025: Proud Boys. Different uniforms, same violence.",
            "1933: Reichstag Fire false flag. 2025: January 6th 'tourist visit'.",
            "1933: Book burnings. 2025: Book bans. History rhymes.",
            "1933: Jews blamed for everything. 2025: Immigrants blamed for everything.",
            "1933: Make Germany Great Again. 2025: MAGA. Coincidence?",
            "1933: Enabling Act. 2025: Project 2025. Democracy dies by design.",
            "1933: Concentration camps. 2025: ICE detention centers. It starts slowly.",
            "1933: Courts packed with loyalists. 2025: Supreme Court 6-3. Check.",
            "1933: Hitler youth indoctrination. 2025: PragerU in schools.",
            "1933: Night of Long Knives coming. 2025: 'Retribution' promised.",
            "1933: Democratic parties banned. 2025: 'Enemy within' rhetoric.",
            "1933: Press credentials revoked. 2025: Press kicked out of briefings.",
            "1933: Oath to Hitler personally. 2025: Loyalty pledges to Trump.",
            "Those who don't learn from 1933 are doomed to repeat it in 2025.",
            "1933: They came for the communists. 2025: They're coming for 'antifa'.",
            "1933: Burned trans research. 2025: Banning trans existence.",
            "1933: Germany First. 2025: America First. Fascism is always 'first'.",
            "1933: Emergency powers never ended. 2025: 'Only I can fix it'."
        ]
        
        # Warnings that proved prophetic
        self.warnings = [
            "They thought Hitler was a clown who could be controlled. They were wrong.",
            "German conservatives thought they could use Hitler. He used them.",
            "By the time Germans realized, it was too late to stop it peacefully.",
            "The courts won't save you when they're packed with fascists.",
            "Fascism arrives as your friend, with a flag and a cross.",
            "First they came for the trans kids, and I said nothing...",
            "A failed coup without consequences is just practice.",
            "When someone tells you they'll be a dictator, believe them.",
            "Democratic institutions are only as strong as those defending them.",
            "The time to stop fascism is BEFORE it takes power."
        ]
    
    def get_random_parallel(self) -> Dict:
        """Get a random historical parallel"""
        return random.choice(self.parallels)
    
    def get_quick_fact(self) -> str:
        """Get a quick fact for chat"""
        return random.choice(self.quick_facts)
    
    def get_warning(self) -> str:
        """Get a historical warning"""
        return random.choice(self.warnings)
    
    def format_parallel_for_chat(self, parallel: Dict) -> str:
        """Format a parallel for chat display"""
        return f"[BOOKS] [{parallel['category']}] 1933: {parallel['1933']} -> 2025: {parallel['2025']}"
    
    def get_fact_by_category(self, category: str) -> Optional[Dict]:
        """Get a fact from specific category"""
        facts = [p for p in self.parallels if p['category'].lower() == category.lower()]
        return random.choice(facts) if facts else None
    
    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        return list(set(p['category'] for p in self.parallels))


# Module-level instance for easy access
_facts = HistoricalFacts()

def get_random_fact() -> str:
    """Get a random quick fact"""
    return _facts.get_quick_fact()

def get_parallel() -> str:
    """Get a formatted historical parallel"""
    parallel = _facts.get_random_parallel()
    return _facts.format_parallel_for_chat(parallel)

def get_warning() -> str:
    """Get a historical warning"""
    return _facts.get_warning()

def get_categories() -> List[str]:
    """Get available categories"""
    return _facts.get_categories()