"""
Quiz Engine for Educational Anti-Fascist Games
WSP-Compliant implementation (<500 lines)
"""

import json
import random
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

@dataclass
class QuizQuestion:
    """A quiz question about fascism/authoritarianism"""
    question: str
    options: List[str]
    correct_index: int
    explanation: str
    category: str = "general"
    difficulty: int = 1  # 1-5 scale

@dataclass
class FScaleQuestion:
    """F-scale authoritarian personality test question"""
    question: str
    dimension: str  # authoritarian_submission, aggression, conventionalism
    reverse_scored: bool = False

@dataclass
class QuizSession:
    """Active quiz session for a user"""
    user_id: str
    current_question: Optional[QuizQuestion] = None
    current_fscale: Optional[FScaleQuestion] = None
    score: int = 0
    questions_answered: int = 0
    started_at: datetime = None

class QuizEngine:
    """
    Main quiz engine for educational content
    Handles quizzes, F-scale tests, and scoring
    """
    
    def __init__(self, db_path: str = None):
        # WSP-compliant: Store data within module directory
        if db_path is None:
            module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(module_dir, "data", "quiz_data.db")
        self.db_path = db_path
        self.sessions: Dict[str, QuizSession] = {}
        self._init_database()
        self._load_questions()
    
    def _init_database(self):
        """Initialize SQLite database for quiz persistence"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quiz_scores (
                    user_id TEXT PRIMARY KEY,
                    total_score INTEGER DEFAULT 0,
                    questions_answered INTEGER DEFAULT 0,
                    avg_difficulty REAL DEFAULT 0,
                    last_played TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fscale_results (
                    user_id TEXT PRIMARY KEY,
                    authoritarian_score REAL DEFAULT 0,
                    submission_score REAL DEFAULT 0,
                    aggression_score REAL DEFAULT 0,
                    conventionalism_score REAL DEFAULT 0,
                    questions_answered INTEGER DEFAULT 0,
                    last_tested TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def _load_questions(self):
        """Load quiz questions and F-scale items"""
        # Educational quiz questions about fascism
        self.quiz_questions = [
            QuizQuestion(
                question="In 1933, the Reichstag Fire was used to suspend civil liberties. What 2001 event had similar effects in the US?",
                options=["9/11 attacks", "Dot-com crash", "Enron scandal", "Florida recount"],
                correct_index=0,
                explanation="Both events were used to expand government power and restrict civil liberties through emergency measures.",
                category="historical_parallels",
                difficulty=2
            ),
            QuizQuestion(
                question="The Nazi SA (Brownshirts) used street violence to intimidate opponents. Which modern group uses similar tactics?",
                options=["Greenpeace", "Proud Boys", "ACLU", "Sierra Club"],
                correct_index=1,
                explanation="The Proud Boys use political violence and intimidation tactics similar to the Nazi SA.",
                category="modern_fascism",
                difficulty=1
            ),
            QuizQuestion(
                question="Hitler's Beer Hall Putsch failed in 1923 but wasn't properly punished. What similar event happened in 2021?",
                options=["GameStop squeeze", "January 6 insurrection", "Texas power crisis", "Suez Canal blockage"],
                correct_index=1,
                explanation="Both were failed coup attempts where leaders faced minimal consequences, emboldening future attempts.",
                category="historical_parallels",
                difficulty=2
            ),
            QuizQuestion(
                question="What propaganda technique involves accusing opponents of what you're doing yourself?",
                options=["Gaslighting", "Projection", "Deflection", "Whataboutism"],
                correct_index=1,
                explanation="Projection is a key fascist propaganda technique - accuse others of your own crimes.",
                category="propaganda",
                difficulty=2
            ),
            QuizQuestion(
                question="The Nazi concept of 'Lügenpresse' (lying press) is most similar to which modern term?",
                options=["Breaking news", "Fake news", "Yellow journalism", "Clickbait"],
                correct_index=1,
                explanation="'Fake news' serves the same purpose as 'Lügenpresse' - delegitimizing critical media.",
                category="propaganda",
                difficulty=1
            ),
            QuizQuestion(
                question="Which economic condition most commonly precedes fascist movements?",
                options=["Prosperity", "Inequality", "Deflation", "Trade surplus"],
                correct_index=1,
                explanation="Economic inequality and middle-class anxiety create fertile ground for fascism.",
                category="economics",
                difficulty=3
            ),
            QuizQuestion(
                question="The 'Big Lie' technique was described by Hitler as?",
                options=[
                    "Small lies repeated often",
                    "Lies so big people assume they must be true",
                    "Mixing truth with lies",
                    "Denying obvious facts"
                ],
                correct_index=1,
                explanation="The 'Big Lie' is so audacious that people can't believe someone would fabricate it.",
                category="propaganda",
                difficulty=2
            ),
            QuizQuestion(
                question="Which book burning in 1933 targeted the Institute for Sexual Science?",
                options=["Berlin", "Munich", "Hamburg", "Frankfurt"],
                correct_index=0,
                explanation="The Berlin book burning specifically targeted LGBTQ+ research and advocacy.",
                category="historical_facts",
                difficulty=4
            )
        ]
        
        # F-scale questions for authoritarian personality assessment
        self.fscale_questions = [
            FScaleQuestion(
                question="Obedience and respect for authority are the most important virtues children should learn.",
                dimension="authoritarian_submission"
            ),
            FScaleQuestion(
                question="Our country desperately needs a mighty leader who will do what has to be done to destroy the radical new ways and sinfulness that are ruining us.",
                dimension="authoritarian_aggression"
            ),
            FScaleQuestion(
                question="The real keys to the 'good life' are obedience, discipline, and sticking to the straight and narrow.",
                dimension="conventionalism"
            ),
            FScaleQuestion(
                question="What our country really needs is a strong, determined leader who will crush evil and take us back to our true path.",
                dimension="authoritarian_aggression"
            ),
            FScaleQuestion(
                question="People should pay less attention to the Bible and other old traditional forms of religious guidance, and instead develop their own personal standards of what is moral and immoral.",
                dimension="conventionalism",
                reverse_scored=True
            ),
            FScaleQuestion(
                question="Our country will be destroyed someday if we do not smash the perversions eating away at our moral fiber and traditional beliefs.",
                dimension="authoritarian_aggression"
            ),
            FScaleQuestion(
                question="Everyone should have their own lifestyle, religious beliefs, and sexual preferences, even if it makes them different from everyone else.",
                dimension="conventionalism",
                reverse_scored=True
            ),
            FScaleQuestion(
                question="The only way our country can get through the crisis ahead is to get back to our traditional values, put some tough leaders in power, and silence the troublemakers spreading bad ideas.",
                dimension="authoritarian_submission"
            )
        ]
    
    def start_quiz(self, user_id: str) -> Tuple[QuizQuestion, str]:
        """
        Start a new quiz for a user
        Returns: (question, formatted_message)
        """
        question = random.choice(self.quiz_questions)
        
        self.sessions[user_id] = QuizSession(
            user_id=user_id,
            current_question=question,
            started_at=datetime.now()
        )
        
        message = f"📚 **FASCISM AWARENESS QUIZ**\n"
        message += f"Difficulty: {'⭐' * question.difficulty}\n"
        message += f"Category: {question.category.replace('_', ' ').title()}\n\n"
        message += f"Question: {question.question}\n\n"
        
        for i, option in enumerate(question.options):
            message += f"{i+1}. {option}\n"
        
        message += f"\nReply with !answer [number] to answer"
        
        return question, message
    
    def answer_quiz(self, user_id: str, answer_index: int) -> Tuple[bool, str]:
        """
        Process a quiz answer
        Returns: (is_correct, response_message)
        """
        if user_id not in self.sessions:
            return False, "No active quiz session. Start with !quiz"
        
        session = self.sessions[user_id]
        if not session.current_question:
            return False, "No active question. Start with !quiz"
        
        question = session.current_question
        is_correct = (answer_index == question.correct_index)
        
        if is_correct:
            session.score += question.difficulty
            message = f"✅ **CORRECT!** (+{question.difficulty} points)\n"
        else:
            correct_option = question.options[question.correct_index]
            message = f"❌ **INCORRECT!** The answer was: {correct_option}\n"
        
        message += f"\n📖 {question.explanation}\n"
        message += f"\nYour session score: {session.score} points"
        
        # Update database
        session.questions_answered += 1
        self._update_quiz_score(user_id, question.difficulty if is_correct else 0, question.difficulty)
        
        # Clear current question
        session.current_question = None
        
        return is_correct, message
    
    def start_fscale(self, user_id: str) -> Tuple[FScaleQuestion, str]:
        """
        Start F-scale authoritarian test
        Returns: (question, formatted_message)
        """
        question = random.choice(self.fscale_questions)
        
        if user_id not in self.sessions:
            self.sessions[user_id] = QuizSession(user_id=user_id)
        
        self.sessions[user_id].current_fscale = question
        
        message = f"📊 **F-SCALE AUTHORITARIAN TEST**\n"
        message += f"Rate your agreement (1-5):\n"
        message += f'"{question.question}"\n\n'
        message += "1 = Strongly Disagree\n"
        message += "2 = Disagree\n"
        message += "3 = Neutral\n"
        message += "4 = Agree\n"
        message += "5 = Strongly Agree\n\n"
        message += "Reply with !rate [1-5]"
        
        return question, message
    
    def rate_fscale(self, user_id: str, rating: int) -> str:
        """Process F-scale rating (1-5)"""
        if user_id not in self.sessions or not self.sessions[user_id].current_fscale:
            return "No active F-scale question. Start with !fscale"
        
        question = self.sessions[user_id].current_fscale
        
        # Reverse score if needed
        score = (6 - rating) if question.reverse_scored else rating
        
        # Calculate authoritarian tendency
        auth_level = ""
        if score <= 2:
            auth_level = "Low authoritarian tendency"
        elif score == 3:
            auth_level = "Moderate/neutral"
        else:
            auth_level = "High authoritarian tendency"
        
        self._update_fscale_score(user_id, question.dimension, score)
        
        message = f"📊 Response recorded: {auth_level}\n"
        message += f"Dimension measured: {question.dimension.replace('_', ' ').title()}\n"
        message += "\nHigher scores indicate greater susceptibility to fascist ideology."
        
        self.sessions[user_id].current_fscale = None
        
        return message
    
    def get_stats(self, user_id: str) -> str:
        """Get user's quiz statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get quiz stats
            cursor.execute("""
                SELECT total_score, questions_answered, avg_difficulty
                FROM quiz_scores WHERE user_id = ?
            """, (user_id,))
            quiz_data = cursor.fetchone()
            
            # Get F-scale stats
            cursor.execute("""
                SELECT authoritarian_score, questions_answered
                FROM fscale_results WHERE user_id = ?
            """, (user_id,))
            fscale_data = cursor.fetchone()
        
        message = f"📊 **EDUCATIONAL STATS**\n"
        
        if quiz_data:
            accuracy = (quiz_data[0] / (quiz_data[1] * quiz_data[2] or 1)) * 100
            message += f"\n**Quiz Performance:**\n"
            message += f"• Total Score: {quiz_data[0]} points\n"
            message += f"• Questions Answered: {quiz_data[1]}\n"
            message += f"• Accuracy: {accuracy:.1f}%\n"
        
        if fscale_data and fscale_data[1] > 0:
            auth_score = fscale_data[0] / fscale_data[1]
            message += f"\n**F-Scale Results:**\n"
            message += f"• Authoritarian Score: {auth_score:.2f}/5.0\n"
            message += f"• Questions Answered: {fscale_data[1]}\n"
            
            if auth_score < 2.5:
                message += "• Assessment: Low authoritarian personality\n"
            elif auth_score < 3.5:
                message += "• Assessment: Moderate authoritarian traits\n"
            else:
                message += "• Assessment: High authoritarian personality - stay vigilant!\n"
        
        if not quiz_data and not fscale_data:
            message = "No educational stats yet. Try !quiz or !fscale"
        
        return message
    
    def _update_quiz_score(self, user_id: str, points: int, difficulty: int):
        """Update quiz score in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO quiz_scores (user_id, total_score, questions_answered, avg_difficulty, last_played)
                VALUES (?, ?, 1, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    total_score = total_score + ?,
                    questions_answered = questions_answered + 1,
                    avg_difficulty = ((avg_difficulty * questions_answered) + ?) / (questions_answered + 1),
                    last_played = CURRENT_TIMESTAMP
            """, (user_id, points, difficulty, points, difficulty))
            conn.commit()
    
    def _update_fscale_score(self, user_id: str, dimension: str, score: int):
        """Update F-scale score in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Map dimension to column
            column_map = {
                "authoritarian_submission": "submission_score",
                "authoritarian_aggression": "aggression_score",
                "conventionalism": "conventionalism_score"
            }
            column = column_map.get(dimension, "authoritarian_score")
            
            cursor.execute(f"""
                INSERT INTO fscale_results (user_id, {column}, authoritarian_score, questions_answered, last_tested)
                VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    {column} = {column} + ?,
                    authoritarian_score = authoritarian_score + ?,
                    questions_answered = questions_answered + 1,
                    last_tested = CURRENT_TIMESTAMP
            """, (user_id, score, score, score, score))
            conn.commit()