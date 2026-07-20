"""
Script to create PHP questions and 10 Test Series in the database.
Covers PHP Beginner, Easy, Intermediate, Hard, Advanced OOP, Web/Sessions, PDO, etc.
"""

from datetime import datetime, timezone
from decimal import Decimal
import app.models.question_option
import app.models.topic
import app.models.series_question
import app.models.question
import app.models.test_series
import app.models.user
from app.database import SessionLocal
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.series_question import SeriesQuestion
from app.models.test_series import TestSeries
from app.models.topic import Topic


def seed_php_data():
    db = SessionLocal()
    try:
        print("Starting 10 PHP Test Series creation...")

        # 1. Create or get Topics for PHP
        topic_data = [
            ("PHP - Beginner", "#777BB4"),
            ("PHP - Easy", "#4F5B93"),
            ("PHP - Intermediate", "#314685"),
            ("PHP - Hard", "#1B2A57"),
            ("PHP - Advanced", "#0F172A"),
        ]

        topics_map = {}
        for name, color in topic_data:
            existing = db.query(Topic).filter(Topic.name == name).first()
            if not existing:
                t = Topic(name=name, color=color, org_id=1, is_active=True)
                db.add(t)
                db.flush()
                topics_map[name] = t.id
                print(f"Created topic: {name} (ID: {t.id})")
            else:
                topics_map[name] = existing.id
                print(f"Existing topic found: {name} (ID: {existing.id})")

        # 2. Define 10 PHP Test Series with Questions & Options
        test_series_definitions = [
            # -------------------------------------------------------------
            # SERIES 1: PHP - Beginner: Basics & Syntax
            # -------------------------------------------------------------
            {
                "title": "PHP - Beginner: Basics & Syntax",
                "topic": "PHP - Beginner",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>Which of the following is the standard opening tag for PHP scripts?</p>",
                        "opts": [
                            ("<?php", True),
                            ('<script language="php">', False),
                            ("<?php code ?>", False),
                            ("<php>", False),
                        ],
                    },
                    {
                        "q": "<p>In PHP, all variable names must begin with which character?</p>",
                        "opts": [
                            ("$ (Dollar sign)", True),
                            ("@ (At sign)", False),
                            ("% (Percent sign)", False),
                            ("# (Hash sign)", False),
                        ],
                    },
                    {
                        "q": "<p>Which statement/function is used to print output to the screen in PHP?</p>",
                        "opts": [
                            ("echo", True),
                            ("print_text()", False),
                            ("write()", False),
                            ("Console.write()", False),
                        ],
                    },
                    {
                        "q": "<p>Which operator is used to concatenate two strings in PHP?</p>",
                        "opts": [
                            (". (Dot)", True),
                            ("+ (Plus)", False),
                            ("& (Ampersand)", False),
                            (", (Comma)", False),
                        ],
                    },
                    {
                        "q": "<p>How do you write a single-line comment in PHP?</p>",
                        "opts": [
                            ("// or #", True),
                            ("<!-- comment -->", False),
                            ("/* comment */", False),
                            ("-- comment", False),
                        ],
                    },
                    {
                        "q": "<p>Are variable names in PHP case-sensitive?</p>",
                        "opts": [
                            ("Yes ($var and $VAR are different variables)", True),
                            ("No ($var and $VAR are identical)", False),
                            ("Only in function definitions", False),
                            ("Only when strict_types is enabled", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 2: PHP - Easy: Data Types & Operators
            # -------------------------------------------------------------
            {
                "title": "PHP - Easy: Data Types & Operators",
                "topic": "PHP - Easy",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>What does the strict comparison operator (===) evaluate in PHP?</p>",
                        "opts": [
                            ("Both value and data type match", True),
                            ("Only value matches", False),
                            ("Only memory reference matches", False),
                            ("Variable names match", False),
                        ],
                    },
                    {
                        "q": "<p>What value does the spaceship operator ($a <=> $b) return when $a is smaller than $b?</p>",
                        "opts": [
                            ("-1", True),
                            ("0", False),
                            ("1", False),
                            ("false", False),
                        ],
                    },
                    {
                        "q": "<p>Which of the following is NOT a scalar data type in PHP?</p>",
                        "opts": [
                            ("array", True),
                            ("string", False),
                            ("integer", False),
                            ("boolean", False),
                        ],
                    },
                    {
                        "q": "<p>What is the Null Coalescing Operator introduced in PHP 7?</p>",
                        "opts": [
                            ("??", True),
                            ("?:", False),
                            ("?", False),
                            ("||", False),
                        ],
                    },
                    {
                        "q": "<p>What is the evaluation of the expression: !(true && false)?</p>",
                        "opts": [
                            ("true", True),
                            ("false", False),
                            ("null", False),
                            ("syntax error", False),
                        ],
                    },
                    {
                        "q": "<p>Which operator is used to increment a variable's value by 1 in PHP?</p>",
                        "opts": [
                            ("++", True),
                            ("+=", False),
                            ("add()", False),
                            ("**", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 3: PHP - Easy: Control Structures & Loops
            # -------------------------------------------------------------
            {
                "title": "PHP - Easy: Control Structures & Loops",
                "topic": "PHP - Easy",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>Which loop in PHP is guaranteed to execute its code block at least once?</p>",
                        "opts": [
                            ("do-while loop", True),
                            ("while loop", False),
                            ("for loop", False),
                            ("foreach loop", False),
                        ],
                    },
                    {
                        "q": "<p>Which control structure introduced in PHP 8 returns values and uses strict type checking?</p>",
                        "opts": [
                            ("match expression", True),
                            ("switch statement", False),
                            ("if-else", False),
                            ("select-case", False),
                        ],
                    },
                    {
                        "q": "<p>Which loop construct is specifically designed to iterate over arrays in PHP?</p>",
                        "opts": [
                            ("foreach", True),
                            ("for", False),
                            ("while", False),
                            ("repeat-until", False),
                        ],
                    },
                    {
                        "q": "<p>Which statement immediately halts the execution of a loop in PHP?</p>",
                        "opts": [
                            ("break", True),
                            ("continue", False),
                            ("exit", False),
                            ("stop", False),
                        ],
                    },
                    {
                        "q": "<p>Which statement skips the remaining code of the current iteration and starts the next iteration?</p>",
                        "opts": [
                            ("continue", True),
                            ("break", False),
                            ("skip", False),
                            ("next", False),
                        ],
                    },
                    {
                        "q": "<p>In a switch statement, which keyword is executed when no case condition matches?</p>",
                        "opts": [
                            ("default", True),
                            ("else", False),
                            ("otherwise", False),
                            ("fallback", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 4: PHP - Intermediate: Functions & Scope
            # -------------------------------------------------------------
            {
                "title": "PHP - Intermediate: Functions & Scope",
                "topic": "PHP - Intermediate",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>How do you declare a parameter to be passed by reference in a PHP function?</p>",
                        "opts": [
                            ("Prepend & to parameter (e.g., function foo(&$param))", True),
                            ("Prepend * to parameter", False),
                            ("Use the ref keyword", False),
                            ("Use global keyword inside function", False),
                        ],
                    },
                    {
                        "q": "<p>Which keyword allows an anonymous function (closure) to inherit variables from its parent scope?</p>",
                        "opts": [
                            ("use", True),
                            ("import", False),
                            ("global", False),
                            ("with", False),
                        ],
                    },
                    {
                        "q": "<p>Which keyword allows a function to access a variable defined outside in the global scope?</p>",
                        "opts": [
                            ("global", True),
                            ("extern", False),
                            ("super", False),
                            ("parent", False),
                        ],
                    },
                    {
                        "q": "<p>What exception type is thrown when type hints are violated in strict_types mode?</p>",
                        "opts": [
                            ("TypeError", True),
                            ("InvalidArgumentException", False),
                            ("ParseError", False),
                            ("ValueError", False),
                        ],
                    },
                    {
                        "q": "<p>What operator is used for variadic functions (variadic arguments) in PHP?</p>",
                        "opts": [
                            ("... (Splat operator)", True),
                            ("&&", False),
                            ("::", False),
                            ("->", False),
                        ],
                    },
                    {
                        "q": "<p>Which built-in PHP function checks whether a function has been defined?</p>",
                        "opts": [
                            ("function_exists()", True),
                            ("is_callable()", False),
                            ("method_exists()", False),
                            ("is_function()", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 5: PHP - Intermediate: Arrays & Array Functions
            # -------------------------------------------------------------
            {
                "title": "PHP - Intermediate: Arrays & Array Functions",
                "topic": "PHP - Intermediate",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>Which PHP function returns the total count of elements in an array?</p>",
                        "opts": [
                            ("count()", True),
                            ("length()", False),
                            ("array_length()", False),
                            ("total()", False),
                        ],
                    },
                    {
                        "q": "<p>How is an associative key-value pair specified in a PHP array definition?</p>",
                        "opts": [
                            ("'key' => 'value'", True),
                            ("'key' : 'value'", False),
                            ("'key' = 'value'", False),
                            ("'key' -> 'value'", False),
                        ],
                    },
                    {
                        "q": "<p>Which function merges two or more arrays into a single combined array?</p>",
                        "opts": [
                            ("array_merge()", True),
                            ("array_combine()", False),
                            ("array_push()", False),
                            ("array_concat()", False),
                        ],
                    },
                    {
                        "q": "<p>Which function applies a callback to each element of an array and returns the transformed array?</p>",
                        "opts": [
                            ("array_map()", True),
                            ("array_filter()", False),
                            ("array_walk()", False),
                            ("array_reduce()", False),
                        ],
                    },
                    {
                        "q": "<p>Which function checks whether a given value exists within an array?</p>",
                        "opts": [
                            ("in_array()", True),
                            ("array_key_exists()", False),
                            ("array_search()", False),
                            ("array_contains()", False),
                        ],
                    },
                    {
                        "q": "<p>Which sorting function sorts an associative array in ascending order by value, maintaining index correlation?</p>",
                        "opts": [
                            ("asort()", True),
                            ("ksort()", False),
                            ("sort()", False),
                            ("usort()", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 6: PHP - Intermediate: Strings & Regex
            # -------------------------------------------------------------
            {
                "title": "PHP - Intermediate: Strings & Regex",
                "topic": "PHP - Intermediate",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>What is the key difference between single ('') and double (\"\") quotes in PHP string literals?</p>",
                        "opts": [
                            ("Double quotes parse variables inside them; single quotes treat them as literal text", True),
                            ("Single quotes parse variables; double quotes do not", False),
                            ("Single quotes are multi-line only", False),
                            ("There is no behavioral difference", False),
                        ],
                    },
                    {
                        "q": "<p>Which PHP function measures and returns the length of a string in bytes/characters?</p>",
                        "opts": [
                            ("strlen()", True),
                            ("str_length()", False),
                            ("string_len()", False),
                            ("count()", False),
                        ],
                    },
                    {
                        "q": "<p>Which function splits a string into an array based on a delimiter?</p>",
                        "opts": [
                            ("explode()", True),
                            ("implode()", False),
                            ("str_split()", False),
                            ("split()", False),
                        ],
                    },
                    {
                        "q": "<p>Which function joins an array of strings into a single string with a glue separator?</p>",
                        "opts": [
                            ("implode()", True),
                            ("explode()", False),
                            ("concat()", False),
                            ("array_to_string()", False),
                        ],
                    },
                    {
                        "q": "<p>Which function executes a regular expression search on a string in PHP?</p>",
                        "opts": [
                            ("preg_match()", True),
                            ("regex_match()", False),
                            ("str_match()", False),
                            ("match_regex()", False),
                        ],
                    },
                    {
                        "q": "<p>Which function replaces all occurrences of a search substring with a replacement string?</p>",
                        "opts": [
                            ("str_replace()", True),
                            ("string_replace()", False),
                            ("preg_replace()", False),
                            ("replace()", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 7: PHP - Hard: Object-Oriented Programming (OOP)
            # -------------------------------------------------------------
            {
                "title": "PHP - Hard: Object-Oriented Programming (OOP)",
                "topic": "PHP - Hard",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>What is the standard constructor method name for classes in PHP?</p>",
                        "opts": [
                            ("__construct()", True),
                            ("className()", False),
                            ("_init()", False),
                            ("__create()", False),
                        ],
                    },
                    {
                        "q": "<p>Which visibility keyword restricts access ONLY to the class that defines the property/method?</p>",
                        "opts": [
                            ("private", True),
                            ("protected", False),
                            ("public", False),
                            ("internal", False),
                        ],
                    },
                    {
                        "q": "<p>Which visibility modifier allows property access within the class and child classes that inherit it?</p>",
                        "opts": [
                            ("protected", True),
                            ("private", False),
                            ("public", False),
                            ("package", False),
                        ],
                    },
                    {
                        "q": "<p>Which keyword is used by a child class to inherit from a parent class in PHP?</p>",
                        "opts": [
                            ("extends", True),
                            ("implements", False),
                            ("inherits", False),
                            ("using", False),
                        ],
                    },
                    {
                        "q": "<p>Which keyword is used when a class promises to conform to an Interface definition?</p>",
                        "opts": [
                            ("implements", True),
                            ("extends", False),
                            ("uses", False),
                            ("instanceof", False),
                        ],
                    },
                    {
                        "q": "<p>Can an abstract class in PHP be instantiated directly using the 'new' operator?</p>",
                        "opts": [
                            ("No, abstract classes cannot be instantiated", True),
                            ("Yes, if it contains no abstract methods", False),
                            ("Yes, if instantiated inside a static method", False),
                            ("Only inside traits", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 8: PHP - Hard: Advanced OOP & Traits
            # -------------------------------------------------------------
            {
                "title": "PHP - Hard: Advanced OOP & Traits",
                "topic": "PHP - Hard",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>Which scope resolution operator (Paamayim Nekudotayim) accesses static members and constants?</p>",
                        "opts": [
                            (":: (Double colon)", True),
                            ("-> (Single arrow)", False),
                            ("=> (Double arrow)", False),
                            (". (Dot)", False),
                        ],
                    },
                    {
                        "q": "<p>What is the difference between self:: and static:: in inherited static methods?</p>",
                        "opts": [
                            ("static:: uses Late Static Binding to resolve the called class at runtime", True),
                            ("self:: uses Late Static Binding", False),
                            ("There is no difference", False),
                            ("self:: cannot be used in static context", False),
                        ],
                    },
                    {
                        "q": "<p>Which PHP feature enables horizontal code reuse across independent class hierarchies?</p>",
                        "opts": [
                            ("Traits (trait)", True),
                            ("Interfaces", False),
                            ("Abstract Classes", False),
                            ("Namespaces", False),
                        ],
                    },
                    {
                        "q": "<p>Which magic method is triggered when an object is treated as a string (e.g. echo $obj)?</p>",
                        "opts": [
                            ("__toString()", True),
                            ("__stringify()", False),
                            ("__invoke()", False),
                            ("__serialize()", False),
                        ],
                    },
                    {
                        "q": "<p>What happens when a method is declared with the 'final' keyword?</p>",
                        "opts": [
                            ("Child classes are prevented from overriding the method", True),
                            ("The method cannot be called statically", False),
                            ("The method must return void", False),
                            ("The class cannot be instantiated", False),
                        ],
                    },
                    {
                        "q": "<p>What feature introduced in PHP 8.1 defines enumerated types with a fixed list of cases?</p>",
                        "opts": [
                            ("Enums (enum)", True),
                            ("Const Arrays", False),
                            ("Sealed Classes", False),
                            ("Union Types", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 9: PHP - Advanced: Web, Sessions & Forms
            # -------------------------------------------------------------
            {
                "title": "PHP - Advanced: Web, Sessions & Forms",
                "topic": "PHP - Advanced",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>Which superglobal array stores parameters submitted via HTTP POST requests?</p>",
                        "opts": [
                            ("$_POST", True),
                            ("$_GET", False),
                            ("$_REQUEST", False),
                            ("$_SERVER", False),
                        ],
                    },
                    {
                        "q": "<p>Which function MUST be invoked before writing or reading from $_SESSION?</p>",
                        "opts": [
                            ("session_start()", True),
                            ("start_session()", False),
                            ("session_init()", False),
                            ("session_open()", False),
                        ],
                    },
                    {
                        "q": "<p>How do you issue a HTTP 302 location redirect header in PHP?</p>",
                        "opts": [
                            ('header("Location: https://example.com");', True),
                            ('redirect("https://example.com");', False),
                            ('http_redirect("https://example.com");', False),
                            ('response_send("https://example.com");', False),
                        ],
                    },
                    {
                        "q": "<p>Which superglobal holds metadata and temporary paths for uploaded files?</p>",
                        "opts": [
                            ("$_FILES", True),
                            ("$_UPLOAD", False),
                            ("$_POST", False),
                            ("$_FILE", False),
                        ],
                    },
                    {
                        "q": "<p>Which built-in function is recommended to sanitize and validate user input variables?</p>",
                        "opts": [
                            ("filter_var()", True),
                            ("sanitize_var()", False),
                            ("clean_input()", False),
                            ("validate_string()", False),
                        ],
                    },
                    {
                        "q": "<p>Which function sends an HTTP cookie to the user's browser?</p>",
                        "opts": [
                            ("setcookie()", True),
                            ("$_COOKIE[] =", False),
                            ("cookie_create()", False),
                            ("make_cookie()", False),
                        ],
                    },
                ],
            },
            # -------------------------------------------------------------
            # SERIES 10: PHP - Advanced: Exception Handling & Database (PDO)
            # -------------------------------------------------------------
            {
                "title": "PHP - Advanced: Exception Handling & Database (PDO)",
                "topic": "PHP - Advanced",
                "duration": 600,
                "questions": [
                    {
                        "q": "<p>What is the root interface/class for all throwables in PHP exception handling?</p>",
                        "opts": [
                            ("Throwable / Exception", True),
                            ("ErrorClass", False),
                            ("BaseException", False),
                            ("RuntimeException", False),
                        ],
                    },
                    {
                        "q": "<p>In a try-catch-finally construct, when does the code inside 'finally' execute?</p>",
                        "opts": [
                            ("Always, regardless of whether an exception was thrown or caught", True),
                            ("Only when an exception is thrown", False),
                            ("Only when no exception is thrown", False),
                            ("Only if an unhandled error occurs", False),
                        ],
                    },
                    {
                        "q": "<p>Why are Prepared Statements essential in PDO / MySQLi database applications?</p>",
                        "opts": [
                            ("They protect against SQL Injection by separating SQL logic from user input", True),
                            ("They make connections 10 times faster", False),
                            ("They automatically encrypt database tables", False),
                            ("They remove the need for primary keys", False),
                        ],
                    },
                    {
                        "q": "<p>What does the PDO abbreviation stand for in PHP web development?</p>",
                        "opts": [
                            ("PHP Data Objects", True),
                            ("Public Database Operations", False),
                            ("PHP Direct Output", False),
                            ("Processed Data Objects", False),
                        ],
                    },
                    {
                        "q": "<p>How do you configure PDO to throw exceptions whenever a database error occurs?</p>",
                        "opts": [
                            ("$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);", True),
                            ("$pdo->setExceptionMode(true);", False),
                            ("$pdo->enableErrors();", False),
                            ('$pdo->error_type = "exception";', False),
                        ],
                    },
                    {
                        "q": "<p>Which method executes a previously prepared SQL statement in PDO?</p>",
                        "opts": [
                            ("$stmt->execute()", True),
                            ("$stmt->run()", False),
                            ("$stmt->query()", False),
                            ("$stmt->fetch()", False),
                        ],
                    },
                ],
            },
        ]

        # 3. Insert Questions and Test Series
        valid_until_dt = datetime(2030, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

        for s_idx, series_data in enumerate(test_series_definitions, start=1):
            print(f"\n--- Creating Series {s_idx}/10: {series_data['title']} ---")
            
            # Step A: Insert Questions and Options
            question_ids = []
            topic_id = topics_map[series_data["topic"]]

            for q_data in series_data["questions"]:
                question_obj = Question(
                    question=q_data["q"],
                    organization_id=1,
                    user_id=1,
                    is_global=True,
                    marks=Decimal("1.00"),
                    is_active=True,
                    topic_id=topic_id,
                )
                db.add(question_obj)
                db.flush()

                for opt_text, is_corr in q_data["opts"]:
                    option_obj = QuestionOption(
                        q_id=question_obj.id,
                        ans=opt_text,
                        is_correct=is_corr,
                    )
                    db.add(option_obj)
                
                question_ids.append(question_obj.id)

            db.flush()

            # Step B: Insert Test Series
            test_series = TestSeries(
                name=series_data["title"],
                access_type="public",
                valid_until=valid_until_dt,
                duration_seconds=series_data["duration"],
                is_active=True,
                org_id=1,
                created_by=1,
            )
            db.add(test_series)
            db.flush()

            # Step C: Link Questions via SeriesQuestion association
            for pos, q_id in enumerate(question_ids, start=1):
                sq = SeriesQuestion(
                    series_id=test_series.id,
                    question_id=q_id,
                    position=pos,
                )
                db.add(sq)

            db.commit()
            print(f"Successfully created Series '{series_data['title']}' (ID: {test_series.id}) with {len(question_ids)} questions.")

        print("\nAll 10 PHP Test Series and questions successfully seeded into the database!")

    except Exception as e:
        db.rollback()
        print(f"Error during PHP seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_php_data()
