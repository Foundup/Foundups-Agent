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
                    username TEXT DEFAULT 'Unknown',
                    total_score INTEGER DEFAULT 0,
                    questions_answered INTEGER DEFAULT 0,
                    quiz_wins INTEGER DEFAULT 0,
                    avg_difficulty REAL DEFAULT 0,
                    last_played TIMESTAMP,
                    last_quiz_time TIMESTAMP,
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

            # MIGRATION: Add missing columns to existing databases
            try:
                cursor.execute("PRAGMA table_info(quiz_scores)")
                columns = {col[1] for col in cursor.fetchall()}

                if 'username' not in columns:
                    cursor.execute("ALTER TABLE quiz_scores ADD COLUMN username TEXT DEFAULT 'Unknown'")
                    logger.info("📚 MIGRATION: Added 'username' column to quiz_scores")

                if 'quiz_wins' not in columns:
                    cursor.execute("ALTER TABLE quiz_scores ADD COLUMN quiz_wins INTEGER DEFAULT 0")
                    logger.info("📚 MIGRATION: Added 'quiz_wins' column to quiz_scores")

                if 'last_quiz_time' not in columns:
                    cursor.execute("ALTER TABLE quiz_scores ADD COLUMN last_quiz_time TIMESTAMP")
                    logger.info("📚 MIGRATION: Added 'last_quiz_time' column to quiz_scores")

                conn.commit()
            except Exception as e:
                logger.warning(f"📚 Migration check failed (non-critical): {e}")

            conn.commit()
    
    def _load_questions(self):
        """Load quiz questions and F-scale items"""
        # Educational quiz questions about fascism and Trump appointments
        self.quiz_questions = [
            # Trump 2025 Cabinet vs Nazi 1933 Parallels
            QuizQuestion(
                question="Which Fox News host with zero experience is Trump's Defense Secretary pick?",
                options=["Pete Hegseth", "Tucker Carlson", "Sean Hannity", "Jesse Watters"],
                correct_index=0,
                explanation="Pete Hegseth defended war criminals. 1933: Werner von Blomberg purged Jewish officers.",
                category="trump_appointments",
                difficulty=2
            ),
            QuizQuestion(
                question="Who is Trump's AG pick that was investigated for sex trafficking?",
                options=["Jim Jordan", "Matt Gaetz", "Josh Hawley", "Ted Cruz"],
                correct_index=1,
                explanation="Matt Gaetz under federal investigation. 1933: Wilhelm Frick ignored SA violence.",
                category="trump_appointments",
                difficulty=2
            ),
            QuizQuestion(
                question="Which Putin sympathizer with zero intelligence experience is DNI pick?",
                options=["Tulsi Gabbard", "Marjorie Taylor Greene", "Lauren Boebert", "Kari Lake"],
                correct_index=0,
                explanation="Tulsi Gabbard parrots Russian propaganda. 1933: Ribbentrop loved authoritarians.",
                category="trump_appointments",
                difficulty=2
            ),
            QuizQuestion(
                question="Which billionaire got a made-up department to slash regulations?",
                options=["Jeff Bezos", "Bill Gates", "Elon Musk", "Mark Zuckerberg"],
                correct_index=2,
                explanation="Elon Musk's DOGE. 1933: Industrialists like Krupp got special treatment.",
                category="trump_appointments",
                difficulty=1
            ),
            QuizQuestion(
                question="Who is the brain-worm infected anti-vaxxer picked for HHS?",
                options=["Dr. Oz", "RFK Jr", "Rand Paul", "Scott Atlas"],
                correct_index=1,
                explanation="RFK Jr promotes health conspiracies. 1933: Nazis promoted racial pseudoscience.",
                category="trump_appointments",
                difficulty=2
            ),
            # Historical parallels
            QuizQuestion(
                question="In 1933, the Reichstag Fire was used to suspend civil liberties. What 2001 event had similar effects in the US?",
                options=["9/11 attacks", "Dot-com crash", "Enron scandal", "Florida recount"],
                correct_index=0,
                explanation="Both events were used to expand government power and restrict civil liberties through emergency measures.",
                category="historical_parallels",
                difficulty=2
            ),
            # Nazi Nickname Parallels - Who would they be in 1933?
            QuizQuestion(
                question="Pete Hegseth (Fox News warrior wannabe) would be which Nazi in 1933?",
                options=[
                    "Werner von Blomberg - The 'Rubber Lion' bootlicker general",
                    "Hermann Göring - The morphine addict",
                    "Rudolf Hess - The crazy deputy",
                    "Martin Bormann - The shadow manipulator"
                ],
                correct_index=0,
                explanation="Both are military bootlickers with no real combat command experience who defend war crimes.",
                category="nazi_parallels",
                difficulty=2
            ),
            QuizQuestion(
                question="Matt Gaetz (sex trafficker) is the 2025 version of which Nazi?",
                options=[
                    "Ernst Röhm - The violent gay SA leader",
                    "Julius Streicher - The perverted pornographer propagandist",
                    "Reinhard Heydrich - The Butcher of Prague",
                    "Wilhelm Frick - The bureaucratic enabler"
                ],
                correct_index=1,
                explanation="Both are sexual degenerates who use their position for perversion and propaganda.",
                category="nazi_parallels",
                difficulty=2
            ),
            QuizQuestion(
                question="Elon Musk would be which Nazi industrialist bootlicker?",
                options=[
                    "Fritz Thyssen - The steel magnate who funded Hitler",
                    "Gustav Krupp - The weapons manufacturer",
                    "Hugo Boss - The uniform designer",
                    "Ferdinand Porsche - The Volkswagen creator"
                ],
                correct_index=0,
                explanation="Both are wealthy industrialists who platform fascists thinking they can control them.",
                category="nazi_parallels",
                difficulty=2
            ),
            QuizQuestion(
                question="Tulsi Gabbard (Putin's puppet) is most like which Nazi foreign minister?",
                options=[
                    "Joachim von Ribbentrop - The champagne salesman turned diplomat",
                    "Alfred Rosenberg - The racial theorist",
                    "Joseph Goebbels - The propaganda minister",
                    "Heinrich Himmler - The SS leader"
                ],
                correct_index=0,
                explanation="Both are unqualified foreign policy disasters who love enemy dictators.",
                category="nazi_parallels",
                difficulty=2
            ),
            QuizQuestion(
                question="RFK Jr (brain worm conspiracy theorist) matches which Nazi quack?",
                options=[
                    "Dr. Theodor Morell - Hitler's quack doctor pushing meth",
                    "Dr. Josef Mengele - The Angel of Death",
                    "Dr. Karl Brandt - The euthanasia program leader",
                    "Julius Streicher - The conspiracy theory publisher"
                ],
                correct_index=0,
                explanation="Both are medical quacks pushing dangerous pseudoscience and conspiracy theories.",
                category="nazi_parallels",
                difficulty=2
            ),
            QuizQuestion(
                question="Stephen Miller (the dead-eyed immigration ghoul) is which Nazi?",
                options=[
                    "Adolf Eichmann - The bureaucrat of death",
                    "Heinrich Himmler - The SS architect",
                    "Reinhard Heydrich - The Final Solution planner",
                    "All of the above"
                ],
                correct_index=3,
                explanation="Miller combines the worst of all Nazi deportation architects.",
                category="nazi_parallels",
                difficulty=1
            ),
            QuizQuestion(
                question="JD Vance said 'Trump is America's Hitler' then became VP. Who's his 1933 parallel?",
                options=[
                    "Franz von Papen - Thought he could control Hitler as VP",
                    "Hermann Göring - The opportunist",
                    "Rudolf Hess - The true believer",
                    "Martin Bormann - The backstabber"
                ],
                correct_index=0,
                explanation="Both thought they were smarter than the fascist leader and could control them.",
                category="nazi_parallels",
                difficulty=2
            ),
            QuizQuestion(
                question="Elon Musk (Space Karen) is running DOGE. His Nazi parallel?",
                options=[
                    "Albert Speer - Hitler's architect & armaments minister",
                    "Fritz Thyssen - Industrial magnate who funded Hitler",
                    "Both - tech-obsessed enabler AND wealthy fool",
                    "Wernher von Braun - The rocket scientist"
                ],
                correct_index=2,
                explanation="Musk combines Speer's tech obsession with Thyssen's wealthy idiocy.",
                category="nazi_parallels",
                difficulty=2
            ),
            QuizQuestion(
                question="Kash Patel (QAnon FBI nominee) with enemy lists is which Nazi?",
                options=[
                    "Reinhard Heydrich - The Hangman with death lists",
                    "Heinrich Müller - Gestapo chief",
                    "Roland Freisler - The screaming judge",
                    "Wilhelm Frick - Interior minister"
                ],
                correct_index=0,
                explanation="Both are vindictive intelligence chiefs obsessed with enemy lists.",
                category="nazi_parallels",
                difficulty=2
            ),
            QuizQuestion(
                question="Tom Homan (Trump's 'Border Czar') promising mass deportation is?",
                options=[
                    "Adolf Eichmann - Organized deportation logistics",
                    "Heinrich Himmler - Built the camps",
                    "Reinhard Heydrich - Planned the operations",
                    "Hermann Göring - Gave the orders"
                ],
                correct_index=0,
                explanation="Both are bureaucratic architects of mass deportation operations.",
                category="nazi_parallels",
                difficulty=1
            ),
            QuizQuestion(
                question="Vivek Ramaswamy co-leading DOGE to gut government is?",
                options=[
                    "Martin Bormann - The Brown Eminence",
                    "Rudolf Hess - The deputy",
                    "Robert Ley - The labor destroyer",
                    "Alfred Rosenberg - The philosopher"
                ],
                correct_index=0,
                explanation="Both are ambitious bureaucrats destroying government from within.",
                category="nazi_parallels",
                difficulty=3
            ),
            QuizQuestion(
                question="Marco Rubio (Little Marco) as Secretary of State is?",
                options=[
                    "Constantin von Neurath - Conservative fig leaf",
                    "Joachim von Ribbentrop - The champagne salesman",
                    "Franz von Papen - The enabler",
                    "Wilhelm Keitel - The yes-man"
                ],
                correct_index=0,
                explanation="Both are establishment conservatives who legitimize extremism.",
                category="nazi_parallels",
                difficulty=2
            ),
            QuizQuestion(
                question="Kristi Noem (puppy killer) running DHS/ICE camps is?",
                options=[
                    "Ilse Koch - The Beast of Buchenwald",
                    "Heinrich Himmler - The SS architect",
                    "Irma Grese - The Beautiful Beast",
                    "Rudolf Höss - Auschwitz commandant"
                ],
                correct_index=1,
                explanation="Both oversee internal security apparatus and detention camps.",
                category="nazi_parallels",
                difficulty=2
            ),
            QuizQuestion(
                question="Trump's nickname in Nazi Germany would be?",
                options=[
                    "Der Orangeführer - The Orange Leader",
                    "Der Große Lügner - The Big Liar",
                    "Der Goldene Idiot - The Golden Idiot",
                    "All of the above"
                ],
                correct_index=3,
                explanation="Trump embodies multiple Nazi leader failures: narcissism, lies, and stupidity.",
                category="nazi_parallels",
                difficulty=1
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
    
    def start_quiz(self, user_id: str, compact_mode: bool = False) -> Tuple[QuizQuestion, str]:
        """
        Start a new quiz for a user

        Args:
            user_id: User identifier
            compact_mode: If True, format for YouTube Live Chat (200 char limit)

        Returns: (question, formatted_message)
        """
        question = random.choice(self.quiz_questions)

        self.sessions[user_id] = QuizSession(
            user_id=user_id,
            current_question=question,
            started_at=datetime.now()
        )

        if compact_mode:
            # YouTube Live Chat optimized format (200 char limit)
            # Format: "📚 Q: [question]? 1) [opt1] 2) [opt2] 3) [opt3] 4) [opt4] !answer #"
            message = f"📚 Q: {question.question}? "
            for i, option in enumerate(question.options):
                # Shorten options to first few words
                short_opt = ' '.join(option.split()[:3])  # First 3 words
                message += f"{i+1}) {short_opt} "
            message += "!answer #"

            # Final check: if still too long, truncate question
            if len(message) > 197:  # 200 - "..."
                max_question_len = 30  # Drastically shorten question
                short_question = question.question[:max_question_len]
                message = f"📚 Q: {short_question}? "
                for i, option in enumerate(question.options):
                    short_opt = ' '.join(option.split()[:2])  # First 2 words only
                    message += f"{i+1}) {short_opt} "
                message += "!answer #"
        else:
            # Original format for platforms with longer limits
            message = f"📚 FASCISM AWARENESS QUIZ\n"
            message += f"Difficulty: {'⭐' * question.difficulty}\n"
            message += f"Category: {question.category.replace('_', ' ').title()}\n\n"
            message += f"Question: {question.question}\n\n"

            for i, option in enumerate(question.options):
                message += f"{i+1}. {option}\n"

            message += f"\nReply with !answer [number] to answer"

        return question, message
    
    def answer_quiz(self, user_id: str, answer_index: int, username: str = "Unknown") -> Tuple[bool, str]:
        """
        Process a quiz answer
        Awards 500 MAGADOOM XP for FIRST correct answer!
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
            # Check if this is user's FIRST correct answer
            from .whack import get_profile, _profiles_repo

            # Check quiz history
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT questions_answered FROM quiz_scores WHERE user_id = ?", (user_id,))
                result = cursor.fetchone()
                is_first_correct = (result is None or result[0] == 0)

            # Award MASSIVE XP for first correct answer (equivalent to 24h ban!)
            if is_first_correct:
                xp_awarded = 500  # FIRST ANSWER BONUS!
                profile = get_profile(user_id, username)
                profile.score += xp_awarded  # All-time XP
                profile.monthly_score += xp_awarded  # Monthly leaderboard
                _profiles_repo.save(profile)  # Save and update rank

                message = f"✅ CORRECT! 🎉 FIRST QUIZ WIN! (+{xp_awarded} MAGADOOM XP!)\n"
                message += f"📖 {question.explanation}\n"
                message += f"🏆 Your MAGADOOM Rank: {profile.rank} (Total XP: {profile.score})"
            else:
                # Regular correct answer (no XP, just educational)
                session.score += question.difficulty
                message = f"✅ CORRECT! (+{question.difficulty} education points)\n"
                message += f"📖 {question.explanation}\n"
                message += f"📚 Quiz session score: {session.score}"
        else:
            correct_option = question.options[question.correct_index]
            message = f"❌ INCORRECT! The answer was: {correct_option}\n"
            message += f"📖 {question.explanation}"

        # Update database (track wins for leaderboard)
        session.questions_answered += 1
        self._update_quiz_score(
            user_id,
            question.difficulty if is_correct else 0,
            question.difficulty,
            username=username,
            is_win=is_correct  # Track every correct answer as a "win"
        )

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
        
        message = f"📊 F-SCALE AUTHORITARIAN TEST\n"
        message += f"Rate your agreement (1-5):\n"
        message += f'"{question.question}"\n\n'
        message += "1 = Strongly Disagree\n"
        message += "2 = Disagree\n"
        message += "3 = Neutral\n"
        message += "4 = Agree\n"
        message += "5 = Strongly Agree\n\n"
        message += "Reply with !rate [1-5]"
        
        return question, message
    
    def handle_quiz_command(self, user_id: str, username: str, args: str) -> str:
        """Handle quiz commands and answers"""
        if not args:
            # Check cooldown (unless owner)
            if not self._check_quiz_cooldown(user_id, username):
                cooldown_msg = self._get_cooldown_message(user_id)
                return cooldown_msg

            # Start a new quiz (YouTube Live Chat = 200 char limit)
            question, message = self.start_quiz(user_id, compact_mode=True)
            return message

        # Check if it's an answer (number)
        try:
            answer_index = int(args) - 1  # Convert to 0-based
            is_correct, message = self.answer_quiz(user_id, answer_index, username)

            # NO BONUS - Fixed double scoring bug!
            # XP is awarded inside answer_quiz() for MAGADOOM integration

            return message
        except (ValueError, IndexError):
            return "Invalid answer! Use /quiz to get a question, then reply with 1, 2, 3, or 4"
    
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
        
        message = f"📊 EDUCATIONAL STATS\n"
        
        if quiz_data:
            accuracy = (quiz_data[0] / (quiz_data[1] * quiz_data[2] or 1)) * 100
            message += f"\nQuiz Performance:\n"
            message += f"• Total Score: {quiz_data[0]} points\n"
            message += f"• Questions Answered: {quiz_data[1]}\n"
            message += f"• Accuracy: {accuracy:.1f}%\n"
        
        if fscale_data and fscale_data[1] > 0:
            auth_score = fscale_data[0] / fscale_data[1]
            message += f"\nF-Scale Results:\n"
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

    def get_quiz_leaderboard(self, limit: int = 10) -> str:
        """
        Get quiz leaderboard showing top quiz winners
        Shows: quiz_wins, questions_answered, accuracy%
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if new schema exists
            cursor.execute("PRAGMA table_info(quiz_scores)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'quiz_wins' not in columns or 'username' not in columns:
                return "📚 Quiz leaderboard not available (run a quiz to initialize)"

            # Get top quiz winners
            cursor.execute("""
                SELECT username, quiz_wins, questions_answered, total_score
                FROM quiz_scores
                WHERE quiz_wins > 0
                ORDER BY quiz_wins DESC, questions_answered DESC
                LIMIT ?
            """, (limit,))

            leaders = cursor.fetchall()

        if not leaders:
            return "📚 No quiz winners yet! Be the first to win 500 MAGADOOM XP!"

        message = "📚 QUIZ LEADERBOARD - Top Anti-Fascist Scholars\n\n"

        for i, (username, wins, answered, total_score) in enumerate(leaders, 1):
            accuracy = (wins / answered * 100) if answered > 0 else 0
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."

            message += f"{medal} {username}: {wins} wins ({accuracy:.0f}% accuracy)\n"

        message += "\n💡 First correct answer = 500 MAGADOOM XP!"
        return message
    
    def _update_quiz_score(self, user_id: str, points: int, difficulty: int, username: str = "Unknown", is_win: bool = False):
        """Update quiz score in database (tracks wins for leaderboard)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if username column exists (migration support)
            cursor.execute("PRAGMA table_info(quiz_scores)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'username' in columns and 'quiz_wins' in columns:
                # New schema with username and quiz_wins
                cursor.execute("""
                    INSERT INTO quiz_scores (user_id, username, total_score, questions_answered, quiz_wins, avg_difficulty, last_played)
                    VALUES (?, ?, ?, 1, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id) DO UPDATE SET
                        username = ?,
                        total_score = total_score + ?,
                        questions_answered = questions_answered + 1,
                        quiz_wins = quiz_wins + ?,
                        avg_difficulty = ((avg_difficulty * questions_answered) + ?) / (questions_answered + 1),
                        last_played = CURRENT_TIMESTAMP
                """, (user_id, username, points, 1 if is_win else 0, difficulty,
                      username, points, 1 if is_win else 0, difficulty))
            else:
                # Old schema without username/quiz_wins
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

    def _check_quiz_cooldown(self, user_id: str, username: str) -> bool:
        """
        Check if user can start a new quiz (cooldown protection)
        Owner (Move2Japan, UnDaoDu, Foundups) can ALWAYS trigger for testing
        Returns: True if allowed, False if on cooldown
        """
        # OWNER BYPASS - Can always trigger quiz for testing
        owner_usernames = ["Move2Japan", "UnDaoDu", "Foundups"]
        if username in owner_usernames:
            logger.info(f"👑 Owner {username} bypassing quiz cooldown")
            return True

        # Check last quiz time
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT last_quiz_time FROM quiz_scores WHERE user_id = ?
            """, (user_id,))
            result = cursor.fetchone()

            if result and result[0]:
                from datetime import datetime, timedelta
                last_quiz = datetime.fromisoformat(result[0])
                cooldown_hours = 24  # 24 hour cooldown
                time_since_last = datetime.now() - last_quiz

                if time_since_last < timedelta(hours=cooldown_hours):
                    logger.info(f"⏰ User {username} on quiz cooldown ({time_since_last.total_seconds() / 3600:.1f}h ago)")
                    return False

            # Update last quiz time
            cursor.execute("""
                INSERT INTO quiz_scores (user_id, last_quiz_time)
                VALUES (?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    last_quiz_time = CURRENT_TIMESTAMP
            """, (user_id,))
            conn.commit()

        return True

    def _get_cooldown_message(self, user_id: str) -> str:
        """Get user-friendly cooldown message"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_quiz_time FROM quiz_scores WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()

            if result and result[0]:
                from datetime import datetime, timedelta
                last_quiz = datetime.fromisoformat(result[0])
                time_until_next = timedelta(hours=24) - (datetime.now() - last_quiz)
                hours_left = int(time_until_next.total_seconds() / 3600)

                return f"⏰ Quiz cooldown! You already won 500 XP today. Next quiz in {hours_left}h"

        return "⏰ Quiz on cooldown. Try again later!"