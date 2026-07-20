"""
Script to create 40 Test Series (240 questions total) for:
1. JavaScript (10 Series)
2. Python (10 Series)
3. C Language (10 Series)
4. OOPs Concepts (10 Series)
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


def seed_all_tech_data():
    db = SessionLocal()
    try:
        print("Starting 40 Test Series creation (JS, Python, C, OOPs)...")

        # 1. Create or get Topics
        topic_data = [
            ("JavaScript", "#F7DF1E"),
            ("Python", "#3776AB"),
            ("C Language", "#A8B9CC"),
            ("OOPs Concepts", "#FF6B6B"),
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

        valid_until_dt = datetime(2030, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

        # Helper function to insert a series
        def insert_series(title, topic_name, questions_list):
            topic_id = topics_map[topic_name]
            question_ids = []

            for q_data in questions_list:
                q_obj = Question(
                    question=q_data["q"],
                    organization_id=1,
                    user_id=1,
                    is_global=True,
                    marks=Decimal("1.00"),
                    is_active=True,
                    topic_id=topic_id,
                )
                db.add(q_obj)
                db.flush()

                for opt_text, is_corr in q_data["opts"]:
                    opt_obj = QuestionOption(
                        q_id=q_obj.id,
                        ans=opt_text,
                        is_correct=is_corr,
                    )
                    db.add(opt_obj)
                
                question_ids.append(q_obj.id)

            db.flush()

            t_series = TestSeries(
                name=title,
                access_type="public",
                valid_until=valid_until_dt,
                duration_seconds=600,
                is_active=True,
                org_id=1,
                created_by=1,
            )
            db.add(t_series)
            db.flush()

            for pos, q_id in enumerate(question_ids, start=1):
                sq = SeriesQuestion(
                    series_id=t_series.id,
                    question_id=q_id,
                    position=pos,
                )
                db.add(sq)

            db.commit()
            print(f"Successfully created: '{title}' (ID: {t_series.id}) with {len(question_ids)} questions.")

        # =========================================================================
        # SECTION 1: JAVASCRIPT (10 TEST SERIES)
        # =========================================================================
        js_series = [
            {
                "title": "JS - Beginner: Variables & Data Types",
                "topic": "JavaScript",
                "questions": [
                    {
                        "q": "<p>Which keyword declares a block-scoped variable in modern JavaScript?</p>",
                        "opts": [("let", True), ("var", False), ("def", False), ("dim", False)]
                    },
                    {
                        "q": "<p>What does the typeof operator return for null in JavaScript?</p>",
                        "opts": [('"object"', True), ('"null"', False), ('"undefined"', False), ('"boolean"', False)]
                    },
                    {
                        "q": "<p>Which of the following is NOT a primitive data type in JavaScript?</p>",
                        "opts": [("Array", True), ("String", False), ("Symbol", False), ("BigInt", False)]
                    },
                    {
                        "q": "<p>How do you create a Template Literal string in ES6?</p>",
                        "opts": [("Using backticks (` `)", True), ("Using single quotes (' ')", False), ("Using double quotes (\" \")", False), ("Using brackets ([ ])", False)]
                    },
                    {
                        "q": "<p>What keyword creates an immutable constant reference in JS?</p>",
                        "opts": [("const", True), ("final", False), ("static", False), ("immutable", False)]
                    },
                    {
                        "q": "<p>What is the output of typeof NaN in JavaScript?</p>",
                        "opts": [('"number"', True), ('"NaN"', False), ('"undefined"', False), ('"object"', False)]
                    }
                ]
            },
            {
                "title": "JS - Easy: Operators & Expressions",
                "topic": "JavaScript",
                "questions": [
                    {
                        "q": "<p>What is the key difference between == and === in JavaScript?</p>",
                        "opts": [("=== checks both value and type without type coercion", True), ("== checks both value and type", False), ("=== converts string to number automatically", False), ("There is no difference", False)]
                    },
                    {
                        "q": "<p>What is the result of '5' + 3 in JavaScript?</p>",
                        "opts": [('"53"', True), ("8", False), ("NaN", False), ("TypeError", False)]
                    },
                    {
                        "q": "<p>What is the result of '5' - 3 in JavaScript?</p>",
                        "opts": [("2", True), ('"53"', False), ("NaN", False), ('"2"', False)]
                    },
                    {
                        "q": "<p>Which operator provides a default value for null or undefined?</p>",
                        "opts": [("?? (Nullish Coalescing)", True), ("|| (Logical OR)", False), ("&& (Logical AND)", False), ("?: (Ternary)", False)]
                    },
                    {
                        "q": "<p>What will Boolean('') evaluate to?</p>",
                        "opts": [("false", True), ("true", False), ("undefined", False), ("null", False)]
                    },
                    {
                        "q": "<p>What is the value of 0 || 'JS' in JavaScript?</p>",
                        "opts": [('"JS"', True), ("0", False), ("false", False), ("true", False)]
                    }
                ]
            },
            {
                "title": "JS - Easy: Control Flow & Loops",
                "topic": "JavaScript",
                "questions": [
                    {
                        "q": "<p>Which loop is best suited for iterating over iterable objects like Arrays and Strings?</p>",
                        "opts": [("for...of", True), ("for...in", False), ("do-while", False), ("repeat-until", False)]
                    },
                    {
                        "q": "<p>Which loop is designed to iterate over enumerable property keys of an Object?</p>",
                        "opts": [("for...in", True), ("for...of", False), ("foreach", False), ("while", False)]
                    },
                    {
                        "q": "<p>What happens when a switch statement misses a break statement?</p>",
                        "opts": [("Execution falls through to the next case", True), ("Syntax error occurs", False), ("Loop terminates immediately", False), ("Returns undefined", False)]
                    },
                    {
                        "q": "<p>Which loop guarantees execution at least once regardless of condition?</p>",
                        "opts": [("do...while", True), ("while", False), ("for", False), ("for...of", False)]
                    },
                    {
                        "q": "<p>Which statement skips the current iteration and jumps to the next?</p>",
                        "opts": [("continue", True), ("break", False), ("skip", False), ("yield", False)]
                    },
                    {
                        "q": "<p>What value is returned by an empty return statement inside a function?</p>",
                        "opts": [("undefined", True), ("null", False), ("0", False), ("false", False)]
                    }
                ]
            },
            {
                "title": "JS - Intermediate: Functions & Arrow Functions",
                "topic": "JavaScript",
                "questions": [
                    {
                        "q": "<p>How do arrow functions bind the 'this' keyword in JavaScript?</p>",
                        "opts": [("Lexically (inheriting 'this' from the enclosing scope)", True), ("Dynamically based on call site", False), ("To global window object always", False), ("Arrow functions do not have access to 'this'", False)]
                    },
                    {
                        "q": "<p>Can arrow functions be used as constructors with the 'new' keyword?</p>",
                        "opts": [("No, arrow functions throw a TypeError if called with 'new'", True), ("Yes, always", False), ("Only if they return an object", False), ("Only in strict mode", False)]
                    },
                    {
                        "q": "<p>Which parameter syntax allows a function to collect arbitrary arguments into an array?</p>",
                        "opts": [("...args (Rest parameter)", True), ("arguments[]", False), ("*args", False), ("&args", False)]
                    },
                    {
                        "q": "<p>What is an IIFE in JavaScript?</p>",
                        "opts": [("Immediately Invoked Function Expression", True), ("Internal Instance Function Execution", False), ("Indexed Inline Function Entity", False), ("Iterative Import Function Element", False)]
                    },
                    {
                        "q": "<p>Do arrow functions have their own built-in 'arguments' object?</p>",
                        "opts": [("No, they do not have their own arguments object", True), ("Yes, identical to normal functions", False), ("Only in non-strict mode", False), ("Only when variadic", False)]
                    },
                    {
                        "q": "<p>What is the default return value of a function that returns nothing explicitly?</p>",
                        "opts": [("undefined", True), ("null", False), ("void", False), ("false", False)]
                    }
                ]
            },
            {
                "title": "JS - Intermediate: Array Methods",
                "topic": "JavaScript",
                "questions": [
                    {
                        "q": "<p>Which array method creates a new array populated with the results of calling a function on every element?</p>",
                        "opts": [("map()", True), ("forEach()", False), ("filter()", False), ("reduce()", False)]
                    },
                    {
                        "q": "<p>Which array method creates a new array with all elements that pass a test condition?</p>",
                        "opts": [("filter()", True), ("map()", False), ("some()", False), ("every()", False)]
                    },
                    {
                        "q": "<p>Which array method executes a reducer function to accumulate array values into a single output?</p>",
                        "opts": [("reduce()", True), ("map()", False), ("concat()", False), ("flat()", False)]
                    },
                    {
                        "q": "<p>Which method modifies an array in-place by adding/removing elements?</p>",
                        "opts": [("splice()", True), ("slice()", False), ("concat()", False), ("filter()", False)]
                    },
                    {
                        "q": "<p>Which method returns a shallow copy of a portion of an array into a new array object?</p>",
                        "opts": [("slice()", True), ("splice()", False), ("shift()", False), ("pop()", False)]
                    },
                    {
                        "q": "<p>Which method returns the first element that satisfies a provided testing function?</p>",
                        "opts": [("find()", True), ("filter()", False), ("indexOf()", False), ("includes()", False)]
                    }
                ]
            },
            {
                "title": "JS - Intermediate: Objects & Prototypes",
                "topic": "JavaScript",
                "questions": [
                    {
                        "q": "<p>What property on objects forms the backbone of JavaScript's prototype inheritance chain?</p>",
                        "opts": [("__proto__ (or Object.getPrototypeOf)", True), ("prototype_chain", False), ("[[Scope]]", False), ("__class__", False)]
                    },
                    {
                        "q": "<p>Which method returns an array of a given object's own enumerable property names?</p>",
                        "opts": [("Object.keys()", True), ("Object.values()", False), ("Object.entries()", False), ("Object.getProperties()", False)]
                    },
                    {
                        "q": "<p>How do you extract properties from an object into variables in ES6?</p>",
                        "opts": [("Object Destructuring ({ a, b } = obj)", True), ("Array Unpacking", False), ("Object Spread", False), ("Object Splice", False)]
                    },
                    {
                        "q": "<p>Which method creates a new object using an existing object as the prototype?</p>",
                        "opts": [("Object.create()", True), ("Object.assign()", False), ("Object.clone()", False), ("Object.extend()", False)]
                    },
                    {
                        "q": "<p>What is the effect of Object.freeze(obj)?</p>",
                        "opts": [("Prevents adding, deleting, or modifying existing properties", True), ("Prevents adding properties only", False), ("Makes properties private", False), ("Deletes all properties", False)]
                    },
                    {
                        "q": "<p>Which method binds a function to a specific 'this' context and returns a new function?</p>",
                        "opts": [("bind()", True), ("call()", False), ("apply()", False), ("attach()", False)]
                    }
                ]
            },
            {
                "title": "JS - Hard: Promises & Async/Await",
                "topic": "JavaScript",
                "questions": [
                    {
                        "q": "<p>What are the three possible states of a JavaScript Promise?</p>",
                        "opts": [("Pending, Fulfilled, Rejected", True), ("Init, Running, Completed", False), ("Start, Waiting, Stopped", False), ("Active, Inactive, Error", False)]
                    },
                    {
                        "q": "<p>Which Promise method resolves when ALL input promises resolve, or rejects if ANY promise rejects?</p>",
                        "opts": [("Promise.all()", True), ("Promise.race()", False), ("Promise.any()", False), ("Promise.allSettled()", False)]
                    },
                    {
                        "q": "<p>What keyword inside an async function pauses execution until a Promise settles?</p>",
                        "opts": [("await", True), ("yield", False), ("wait", False), ("pause", False)]
                    },
                    {
                        "q": "<p>What does an async function always return in JavaScript?</p>",
                        "opts": [("A Promise", True), ("The raw value", False), ("undefined", False), ("A Callback", False)]
                    },
                    {
                        "q": "<p>Which Promise method resolves/rejects as soon as the FIRST promise in an iterable settles?</p>",
                        "opts": [("Promise.race()", True), ("Promise.all()", False), ("Promise.allSettled()", False), ("Promise.every()", False)]
                    },
                    {
                        "q": "<p>Where are Promise microtasks executed relative to Macrotasks (like setTimeout)?</p>",
                        "opts": [("Microtask queue runs immediately after current task and before the next Macrotask", True), ("After all macrotasks complete", False), ("In parallel threads", False), ("At random intervals", False)]
                    }
                ]
            },
            {
                "title": "JS - Hard: Closures, Scope & Hoisting",
                "topic": "JavaScript",
                "questions": [
                    {
                        "q": "<p>What is a Closure in JavaScript?</p>",
                        "opts": [("A function bundled together with references to its surrounding lexical environment", True), ("A method that closes a browser tab", False), ("A private class constructor", False), ("A self-executing HTML script", False)]
                    },
                    {
                        "q": "<p>What is Hoisting in JavaScript?</p>",
                        "opts": [("Moving variable and function declarations to the top of their scope during compilation", True), ("Moving objects into global memory", False), ("Lifting child classes into parent classes", False), ("Compiling JS to C++", False)]
                    },
                    {
                        "q": "<p>What is the Temporal Dead Zone (TDZ) for let and const variables?</p>",
                        "opts": [("The period between entering scope and the variable initialization", True), ("The time before garbage collection runs", False), ("An inactive event listener state", False), ("Dead memory space", False)]
                    },
                    {
                        "q": "<p>Are var variable declarations hoisted in JavaScript?</p>",
                        "opts": [("Yes, hoisted and initialized with undefined", True), ("No, they throw ReferenceError", False), ("Hoisted with null value", False), ("Only inside functions", False)]
                    },
                    {
                        "q": "<p>What is lexical scope?</p>",
                        "opts": [("Scope resolved based on the physical position of code at write time", True), ("Scope resolved dynamically at runtime", False), ("Global window scope only", False), ("Module import scope", False)]
                    },
                    {
                        "q": "<p>What error is thrown when accessing a let variable in its TDZ?</p>",
                        "opts": [("ReferenceError", True), ("TypeError", False), ("SyntaxError", False), ("RangeError", False)]
                    }
                ]
            },
            {
                "title": "JS - Advanced: DOM Manipulation & Events",
                "topic": "JavaScript",
                "questions": [
                    {
                        "q": "<p>Which method attaches an event handler without overwriting existing handlers?</p>",
                        "opts": [("addEventListener()", True), ("onclick =", False), ("attachEvent()", False), ("bindEvent()", False)]
                    },
                    {
                        "q": "<p>What is Event Bubbling in the DOM?</p>",
                        "opts": [("Event propagates upward from target element to parent nodes", True), ("Event propagates downward from document to target", False), ("Event triggers only on target element", False), ("Event executes in background thread", False)]
                    },
                    {
                        "q": "<p>Which event method stops further propagation of an event along the DOM tree?</p>",
                        "opts": [("event.stopPropagation()", True), ("event.preventDefault()", False), ("event.stop()", False), ("event.cancel()", False)]
                    },
                    {
                        "q": "<p>Which method prevents the default browser action associated with an event (e.g. form submission)?</p>",
                        "opts": [("event.preventDefault()", True), ("event.stopPropagation()", False), ("event.disable()", False), ("event.halt()", False)]
                    },
                    {
                        "q": "<p>What is Event Delegation?</p>",
                        "opts": [("Attaching a single event listener to a parent element to handle events on child elements", True), ("Delegating events to Web Workers", False), ("Calling events asynchronously", False), ("Cloning event objects", False)]
                    },
                    {
                        "q": "<p>Which modern DOM method selects the first element matching a CSS selector?</p>",
                        "opts": [("document.querySelector()", True), ("document.getElementBySelector()", False), ("document.find()", False), ("document.css()", False)]
                    }
                ]
            },
            {
                "title": "JS - Advanced: ES6+ Features & Modules",
                "topic": "JavaScript",
                "questions": [
                    {
                        "q": "<p>Which operator enables safely reading deeply nested object properties without erroring?</p>",
                        "opts": [("?. (Optional Chaining)", True), ("?? (Nullish Coalescing)", False), ("!.", False), ("=>", False)]
                    },
                    {
                        "q": "<p>Which ES6 data structure guarantees unique values with no duplicates?</p>",
                        "opts": [("Set", True), ("Map", False), ("WeakMap", False), ("Array", False)]
                    },
                    {
                        "q": "<p>Which data structure holds key-value pairs where keys can be of any data type (including objects)?</p>",
                        "opts": [("Map", True), ("Object", False), ("Set", False), ("Symbol", False)]
                    },
                    {
                        "q": "<p>Which ES6 primitive type is used to generate completely unique identifiers?</p>",
                        "opts": [("Symbol", True), ("BigInt", False), ("UID", False), ("Atom", False)]
                    },
                    {
                        "q": "<p>What special function construct uses function* and yield keywords to return iterators?</p>",
                        "opts": [("Generator Functions", True), ("Async Functions", False), ("Arrow Functions", False), ("Higher-Order Functions", False)]
                    },
                    {
                        "q": "<p>How do you export a single default value from an ES6 module?</p>",
                        "opts": [("export default value;", True), ("module.exports = value;", False), ("export { value as default };", False), ("exports.default = value;", False)]
                    }
                ]
            }
        ]

        # =========================================================================
        # SECTION 2: PYTHON (10 TEST SERIES)
        # =========================================================================
        python_series = [
            {
                "title": "Python - Beginner: Basics & Syntax",
                "topic": "Python",
                "questions": [
                    {
                        "q": "<p>How are code blocks defined in Python instead of curly braces {}?</p>",
                        "opts": [("Indentation (spaces/tabs)", True), ("Keywords begin/end", False), ("Semicolons", False), ("Parentheses", False)]
                    },
                    {
                        "q": "<p>Which function reads string input from the user in Python 3?</p>",
                        "opts": [("input()", True), ("raw_input()", False), ("scan()", False), ("read()", False)]
                    },
                    {
                        "q": "<p>How do you write a single-line comment in Python?</p>",
                        "opts": [("# comment", True), ("// comment", False), ("<!-- comment -->", False), ("/* comment */", False)]
                    },
                    {
                        "q": "<p>Which function outputs text to the standard output in Python?</p>",
                        "opts": [("print()", True), ("echo()", False), ("printf()", False), ("write()", False)]
                    },
                    {
                        "q": "<p>Is Python a statically typed or dynamically typed programming language?</p>",
                        "opts": [("Dynamically typed", True), ("Statically typed", False), ("Untyped", False), ("Compiled only", False)]
                    },
                    {
                        "q": "<p>What extension is used for standard Python code files?</p>",
                        "opts": [(".py", True), (".pt", False), (" pyth", False), (".pyc", False)]
                    }
                ]
            },
            {
                "title": "Python - Easy: Data Types & Operators",
                "topic": "Python",
                "questions": [
                    {
                        "q": "<p>What is the result of floor division 7 // 2 in Python?</p>",
                        "opts": [("3", True), ("3.5", False), ("4", False), ("3.0", False)]
                    },
                    {
                        "q": "<p>What is the exponentiation operator in Python?</p>",
                        "opts": [("**", True), ("^", False), ("^^", False), ("exp()", False)]
                    },
                    {
                        "q": "<p>What data type is returned by the expression 5 / 2 in Python 3?</p>",
                        "opts": [("float (2.5)", True), ("int (2)", False), ("decimal", False), ("complex", False)]
                    },
                    {
                        "q": "<p>Which built-in function converts a compatible value to an integer?</p>",
                        "opts": [("int()", True), ("to_int()", False), ("parse_int()", False), ("cast_int()", False)]
                    },
                    {
                        "q": "<p>What does the bool() function return for 0, None, and empty containers?</p>",
                        "opts": [("False", True), ("True", False), ("None", False), ("0", False)]
                    },
                    {
                        "q": "<p>Which operator checks identity (same memory object) in Python?</p>",
                        "opts": [("is", True), ("==", False), ("equals", False), ("same", False)]
                    }
                ]
            },
            {
                "title": "Python - Easy: Control Flow & Loops",
                "topic": "Python",
                "questions": [
                    {
                        "q": "<p>Which keyword is used for else-if conditions in Python?</p>",
                        "opts": [("elif", True), ("else if", False), ("elseif", False), ("case", False)]
                    },
                    {
                        "q": "<p>What does range(1, 5) produce when iterated in a loop?</p>",
                        "opts": [("1, 2, 3, 4", True), ("1, 2, 3, 4, 5", False), ("0, 1, 2, 3, 4", False), ("1, 5", False)]
                    },
                    {
                        "q": "<p>Which keyword acts as a placeholder for future code without doing anything?</p>",
                        "opts": [("pass", True), ("null", False), ("continue", False), ("none", False)]
                    },
                    {
                        "q": "<p>Can a while loop in Python have an optional 'else' block?</p>",
                        "opts": [("Yes, executes when condition becomes false without break", True), ("No, else only works with if", False), ("Only in Python 2", False), ("Only inside functions", False)]
                    },
                    {
                        "q": "<p>Which statement exits the loop immediately?</p>",
                        "opts": [("break", True), ("continue", False), ("exit()", False), ("stop", False)]
                    },
                    {
                        "q": "<p>Which statement skips to the next iteration of the loop?</p>",
                        "opts": [("continue", True), ("pass", False), ("skip", False), ("next", False)]
                    }
                ]
            },
            {
                "title": "Python - Intermediate: Functions & Lambda",
                "topic": "Python",
                "questions": [
                    {
                        "q": "<p>Which keyword defines a user-defined function in Python?</p>",
                        "opts": [("def", True), ("function", False), ("fn", False), ("sub", False)]
                    },
                    {
                        "q": "<p>How do you collect arbitrary positional arguments in a Python function?</p>",
                        "opts": [("*args", True), ("**kwargs", False), ("...args", False), ("&args", False)]
                    },
                    {
                        "q": "<p>How do you collect arbitrary keyword arguments into a dictionary?</p>",
                        "opts": [("**kwargs", True), ("*args", False), ("$dict", False), ("&kwargs", False)]
                    },
                    {
                        "q": "<p>What keyword creates an anonymous small inline function in Python?</p>",
                        "opts": [("lambda", True), ("anonymous", False), ("inline", False), ("closure", False)]
                    },
                    {
                        "q": "<p>What is the default return value of a function without a return statement?</p>",
                        "opts": [("None", True), ("0", False), ("False", False), ("undefined", False)]
                    },
                    {
                        "q": "<p>Can Python functions return multiple values separated by commas?</p>",
                        "opts": [("Yes, returned as a Tuple", True), ("No, causes syntax error", False), ("Only as a List", False), ("Only in Python 3.10+", False)]
                    }
                ]
            },
            {
                "title": "Python - Intermediate: Data Structures",
                "topic": "Python",
                "questions": [
                    {
                        "q": "<p>Which Python sequence type is immutable (cannot be modified after creation)?</p>",
                        "opts": [("Tuple ()", True), ("List []", False), ("Dictionary {}", False), ("Set {}", False)]
                    },
                    {
                        "q": "<p>What syntax is used for List Comprehension in Python?</p>",
                        "opts": [("[x for x in iterable]", True), ("{x in iterable}", False), ("(x for x in iterable)", False), ("<x for x in iterable>", False)]
                    },
                    {
                        "q": "<p>Which method removes and returns the last element from a list?</p>",
                        "opts": [("pop()", True), ("remove()", False), ("delete()", False), ("shift()", False)]
                    },
                    {
                        "q": "<p>Which data structure stores unique unordered elements in Python?</p>",
                        "opts": [("Set", True), ("List", False), ("Tuple", False), ("Dictionary", False)]
                    },
                    {
                        "q": "<p>Which dictionary method safely retrieves a value for a key with a fallback default?</p>",
                        "opts": [("get(key, default)", True), ("find(key)", False), ("fetch(key)", False), ("lookup(key)", False)]
                    },
                    {
                        "q": "<p>What is the output of list slicing my_list[::-1]?</p>",
                        "opts": [("Reverses the list", True), ("Empties the list", False), ("Copies first element", False), ("Causes IndexError", False)]
                    }
                ]
            },
            {
                "title": "Python - Intermediate: String Manipulation",
                "topic": "Python",
                "questions": [
                    {
                        "q": "<p>How do you create an formatted string (f-string) in Python 3.6+?</p>",
                        "opts": [('f"Hello {name}"', True), ('$"Hello {name}"', False), ('fmt("Hello {name}")', False), ('%"Hello {name}"', False)]
                    },
                    {
                        "q": "<p>Which string method splits a string into a list based on a delimiter?</p>",
                        "opts": [("split()", True), ("explode()", False), ("partition()", False), ("cut()", False)]
                    },
                    {
                        "q": "<p>Which string method joins elements of an iterable into a string using a separator?</p>",
                        "opts": [('" ".join(list)', True), ('list.join(" ")', False), ('implode(" ", list)', False), ('concat(" ", list)', False)]
                    },
                    {
                        "q": "<p>Which method converts all characters in a string to lowercase?</p>",
                        "opts": [("lower()", True), ("toLower()", False), ("lowercase()", False), ("down()", False)]
                    },
                    {
                        "q": "<p>Which method removes leading and trailing whitespaces from a string?</p>",
                        "opts": [("strip()", True), ("trim()", False), ("clean()", False), ("chop()", False)]
                    },
                    {
                        "q": "<p>Are Python strings mutable or immutable?</p>",
                        "opts": [("Immutable", True), ("Mutable", False), ("Depends on length", False), ("Mutable in Python 3", False)]
                    }
                ]
            },
            {
                "title": "Python - Hard: Object-Oriented Python",
                "topic": "Python",
                "questions": [
                    {
                        "q": "<p>What is the constructor method name in Python classes?</p>",
                        "opts": [("__init__", True), ("__construct__", False), ("init()", False), ("new()", False)]
                    },
                    {
                        "q": "<p>What parameter must be explicitly defined as the first argument of instance methods?</p>",
                        "opts": [("self", True), ("this", False), ("me", False), ("class", False)]
                    },
                    {
                        "q": "<p>Which decorator defines a method that operates on the class itself rather than instances?</p>",
                        "opts": [("@classmethod", True), ("@staticmethod", False), ("@property", False), ("@class", False)]
                    },
                    {
                        "q": "<p>How is private attribute naming conventionally signaled in Python (name mangling)?</p>",
                        "opts": [("Double leading underscores (e.g. __private)", True), ("private keyword", False), ("@private decorator", False), ("Dollar sign prefix", False)]
                    },
                    {
                        "q": "<p>Which function calls a parent class method inside a subclass?</p>",
                        "opts": [("super()", True), ("parent()", False), ("base()", False), ("ancestor()", False)]
                    },
                    {
                        "q": "<p>What dunder method defines the string representation of an object intended for developers?</p>",
                        "opts": [("__repr__", True), ("__str__", False), ("__print__", False), ("__format__", False)]
                    }
                ]
            },
            {
                "title": "Python - Hard: Exception Handling & File I/O",
                "topic": "Python",
                "questions": [
                    {
                        "q": "<p>Which statement block handles exceptions in Python?</p>",
                        "opts": [("try...except", True), ("try...catch", False), ("do...catch", False), ("try...handle", False)]
                    },
                    {
                        "q": "<p>Which block in exception handling executes ONLY when NO exceptions were raised?</p>",
                        "opts": [("else", True), ("finally", False), ("then", False), ("pass", False)]
                    },
                    {
                        "q": "<p>Which context manager keyword ensures files are automatically closed after use?</p>",
                        "opts": [("with open() as f:", True), ("using open()", False), ("file.autoClose()", False), ("try open()", False)]
                    },
                    {
                        "q": "<p>Which keyword raises a custom exception in Python?</p>",
                        "opts": [("raise", True), ("throw", False), ("emit", False), ("error", False)]
                    },
                    {
                        "q": "<p>What mode flag opens a file for writing, overwriting existing file content?</p>",
                        "opts": [('"w"', True), ('"r"', False), ('"a"', False), ('"x"', False)]
                    },
                    {
                        "q": "<p>Which base class do all built-in non-system-exiting exceptions inherit from?</p>",
                        "opts": [("Exception", True), ("BaseException", False), ("StandardError", False), ("RuntimeError", False)]
                    }
                ]
            },
            {
                "title": "Python - Advanced: Generators & Decorators",
                "topic": "Python",
                "questions": [
                    {
                        "q": "<p>Which keyword turns a standard function into a Generator function?</p>",
                        "opts": [("yield", True), ("return", False), ("generate", False), ("next", False)]
                    },
                    {
                        "q": "<p>What is a Decorator in Python?</p>",
                        "opts": [("A function that takes another function as an argument and extends its behavior", True), ("A CSS styling module", False), ("A class constructor", False), ("A memory manager", False)]
                    },
                    {
                        "q": "<p>Which built-in function fetches the next item from an iterator?</p>",
                        "opts": [("next()", True), ("get()", False), ("step()", False), ("advance()", False)]
                    },
                    {
                        "q": "<p>What syntax sugar is used to apply a decorator to a function?</p>",
                        "opts": [("@decorator_name", True), ("#decorator_name", False), ("$decorator_name", False), ("%decorator_name", False)]
                    },
                    {
                        "q": "<p>What exception is raised when an iterator has no more items left?</p>",
                        "opts": [("StopIteration", True), ("IndexError", False), ("EOFError", False), ("IteratorError", False)]
                    },
                    {
                        "q": "<p>What decorator from functools preserves original function metadata inside a decorator?</p>",
                        "opts": [("@functools.wraps", True), ("@functools.preserve", False), ("@functools.meta", False), ("@functools.keep", False)]
                    }
                ]
            },
            {
                "title": "Python - Advanced: Standard Library & Concepts",
                "topic": "Python",
                "questions": [
                    {
                        "q": "<p>What is the GIL in CPython implementation?</p>",
                        "opts": [("Global Interpreter Lock (restricts execution to one thread at a time)", True), ("General Interface Library", False), ("Garbage Inspection Loop", False), ("Global Instance Loader", False)]
                    },
                    {
                        "q": "<p>Which module from standard library provides advanced container data types like defaultdict and Counter?</p>",
                        "opts": [("collections", True), ("itertools", False), ("containers", False), ("structures", False)]
                    },
                    {
                        "q": "<p>Which module provides high-performance iterator building blocks like cycle and chain?</p>",
                        "opts": [("itertools", True), ("functools", False), ("generators", False), ("looping", False)]
                    },
                    {
                        "q": "<p>Which decorator introduced in Python 3.7 automatically generates __init__ and __repr__ for data classes?</p>",
                        "opts": [("@dataclass", True), ("@struct", False), ("@model", False), ("@record", False)]
                    },
                    {
                        "q": "<p>What is the purpose of Type Hinting (e.g. def foo(x: int) -> str:)?</p>",
                        "opts": [("Improves code readability and static analysis without enforcing runtime type checks", True), ("Enforces strict runtime type errors", False), ("Compiles Python to C", False), ("Replaces docstrings", False)]
                    },
                    {
                        "q": "<p>Which method performs a deep copy of compound objects in Python?</p>",
                        "opts": [("copy.deepcopy()", True), ("copy.copy()", False), ("object.clone()", False), ("duplicate()", False)]
                    }
                ]
            }
        ]

        # =========================================================================
        # SECTION 3: C LANGUAGE (10 TEST SERIES)
        # =========================================================================
        c_series = [
            {
                "title": "C - Beginner: Basics, Types & Variables",
                "topic": "C Language",
                "questions": [
                    {
                        "q": "<p>Which header file is required for standard input/output functions like printf() and scanf()?</p>",
                        "opts": [("<stdio.h>", True), ("<stdlib.h>", False), ("<conio.h>", False), ("<math.h>", False)]
                    },
                    {
                        "q": "<p>What is the entry point function of every C program?</p>",
                        "opts": [("main()", True), ("start()", False), ("init()", False), ("run()", False)]
                    },
                    {
                        "q": "<p>Which format specifier is used to print an integer in printf()?</p>",
                        "opts": [('"%d" (or "%i")', True), ('"%f"', False), ('"%c"', False), ('"%s"', False)]
                    },
                    {
                        "q": "<p>How do you write a multi-line comment in C?</p>",
                        "opts": [("/* comment */", True), ("// comment", False), ("<!-- comment -->", False), ("# comment", False)]
                    },
                    {
                        "q": "<p>What statement terminates the main() function and returns a status code to the OS?</p>",
                        "opts": [("return 0;", True), ("exit();", False), ("stop;", False), ("break;", False)]
                    },
                    {
                        "q": "<p>What operator returns the memory size in bytes of a type or variable in C?</p>",
                        "opts": [("sizeof", True), ("size()", False), ("lengthof", False), ("bytes()", False)]
                    }
                ]
            },
            {
                "title": "C - Easy: Operators & Expressions",
                "topic": "C Language",
                "questions": [
                    {
                        "q": "<p>What is the result of integer division 5 / 2 in C?</p>",
                        "opts": [("2", True), ("2.5", False), ("3", False), ("2.0", False)]
                    },
                    {
                        "q": "<p>Which operator returns the remainder of integer division?</p>",
                        "opts": [("% (Modulo)", True), ("/", False), ("//", False), ("div", False)]
                    },
                    {
                        "q": "<p>What is the Bitwise AND operator in C?</p>",
                        "opts": [("&", True), ("&&", False), ("|", False), ("^", False)]
                    },
                    {
                        "q": "<p>What is the difference between prefix ++i and postfix i++?</p>",
                        "opts": [("Prefix increments before evaluation; postfix increments after evaluation", True), ("Postfix increments before evaluation", False), ("There is no difference", False), ("Prefix is invalid in C", False)]
                    },
                    {
                        "q": "<p>Which operator is the ternary conditional operator in C?</p>",
                        "opts": [("? :", True), ("if else", False), ("??", False), ("::", False)]
                    },
                    {
                        "q": "<p>What is the Bitwise XOR operator in C?</p>",
                        "opts": [("^", True), ("~", False), ("&", False), ("|", False)]
                    }
                ]
            },
            {
                "title": "C - Easy: Control Statements & Loops",
                "topic": "C Language",
                "questions": [
                    {
                        "q": "<p>Which loop in C evaluates its condition at the bottom, guaranteeing one execution?</p>",
                        "opts": [("do-while loop", True), ("while loop", False), ("for loop", False), ("foreach loop", False)]
                    },
                    {
                        "q": "<p>What statement is essential inside each case of a switch to prevent fall-through?</p>",
                        "opts": [("break;", True), ("continue;", False), ("exit;", False), ("return;", False)]
                    },
                    {
                        "q": "<p>Which control statement immediately exits from a loop or switch block?</p>",
                        "opts": [("break", True), ("continue", False), ("goto", False), ("return", False)]
                    },
                    {
                        "q": "<p>What statement skips the current loop iteration and moves to loop update/condition?</p>",
                        "opts": [("continue", True), ("break", False), ("next", False), ("skip", False)]
                    },
                    {
                        "q": "<p>Can a float data type be used in a switch condition in C?</p>",
                        "opts": [("No, switch expressions must evaluate to integral/character types", True), ("Yes, always", False), ("Yes, if converted", False), ("Only in C99", False)]
                    },
                    {
                        "q": "<p>Which unconditional jump statement transfers control to a labeled statement?</p>",
                        "opts": [("goto", True), ("jump", False), ("branch", False), ("transfer", False)]
                    }
                ]
            },
            {
                "title": "C - Intermediate: Functions & Recursion",
                "topic": "C Language",
                "questions": [
                    {
                        "q": "<p>What is a function prototype in C?</p>",
                        "opts": [("A declaration specifying function return type, name, and parameter types before use", True), ("The actual function definition", False), ("A pointer to function", False), ("A macro definition", False)]
                    },
                    {
                        "q": "<p>By default, how are non-pointer arguments passed to functions in C?</p>",
                        "opts": [("Call by Value (copies of values are passed)", True), ("Call by Reference", False), ("Call by Name", False), ("Call by Address", False)]
                    },
                    {
                        "q": "<p>How do you achieve Call by Reference in C?</p>",
                        "opts": [("Passing pointers (memory addresses) of variables", True), ("Using & in parameter definition", False), ("Using reference keyword", False), ("Using global variables only", False)]
                    },
                    {
                        "q": "<p>What essential condition prevents infinite recursion in recursive functions?</p>",
                        "opts": [("Base Case / Termination Condition", True), ("Loop count", False), ("Default parameter", False), ("Global counter", False)]
                    },
                    {
                        "q": "<p>What error occurs if a recursive function lacks a valid base case?</p>",
                        "opts": [("Stack Overflow", True), ("Heap Corruption", False), ("Segmentation Fault", False), ("Syntax Error", False)]
                    },
                    {
                        "q": "<p>What return type indicates that a function does not return any value in C?</p>",
                        "opts": [("void", True), ("null", False), ("int", False), ("empty", False)]
                    }
                ]
            },
            {
                "title": "C - Intermediate: Arrays & Strings",
                "topic": "C Language",
                "questions": [
                    {
                        "q": "<p>What character marks the end of a C-style string in memory?</p>",
                        "opts": [("'\\0' (Null Terminator)", True), ("'\\n' (Newline)", False), ("'\\t' (Tab)", False), ("EOF", False)]
                    },
                    {
                        "q": "<p>How are arrays indexed in C?</p>",
                        "opts": [("0-based indexing (first element is arr[0])", True), ("1-based indexing", False), ("Dynamic indexing", False), ("Negative indexing", False)]
                    },
                    {
                        "q": "<p>Which string library function calculates the number of characters in a string excluding '\\0'?</p>",
                        "opts": [("strlen()", True), ("sizeof()", False), ("strcount()", False), ("strlength()", False)]
                    },
                    {
                        "q": "<p>Which function compares two strings lexicographically in <string.h>?</p>",
                        "opts": [("strcmp()", True), ("strequal()", False), ("strcmp_case()", False), ("memcmp()", False)]
                    },
                    {
                        "q": "<p>Which function concatenates (appends) one string to another?</p>",
                        "opts": [("strcat()", True), ("stradd()", False), ("strappend()", False), ("strjoin()", False)]
                    },
                    {
                        "q": "<p>What happens if you access an array index beyond its declared bounds in C?</p>",
                        "opts": [("Undefined Behavior (may read garbage or cause Segmentation Fault)", True), ("IndexOutOfBoundsException is thrown", False), ("Returns 0 automatically", False), ("Compiler stops build", False)]
                    }
                ]
            },
            {
                "title": "C - Intermediate: Pointers & Addresses",
                "topic": "C Language",
                "questions": [
                    {
                        "q": "<p>Which operator returns the memory address of a variable in C?</p>",
                        "opts": [("& (Address-of operator)", True), ("* (Dereference operator)", False), ("-> (Arrow)", False), (". (Dot)", False)]
                    },
                    {
                        "q": "<p>Which operator is used to dereference a pointer (access the value at the pointer address)?</p>",
                        "opts": [("* (Indirection/Dereference operator)", True), ("&", False), ("->", False), ("%", False)]
                    },
                    {
                        "q": "<p>What is a NULL pointer in C?</p>",
                        "opts": [("A pointer that does not point to any valid memory location (address 0)", True), ("An uninitialized wild pointer", False), ("A pointer to void", False), ("A deleted pointer", False)]
                    },
                    {
                        "q": "<p>What does adding 1 to a pointer ptr (ptr + 1) do in pointer arithmetic?</p>",
                        "opts": [("Advances address by sizeof(data_type) bytes", True), ("Adds exactly 1 byte to the address", False), ("Increments stored value by 1", False), ("Causes memory error", False)]
                    },
                    {
                        "q": "<p>What is a Void Pointer (void*) in C?</p>",
                        "opts": [("A generic pointer type that can hold address of any data type", True), ("A pointer pointing to nothing", False), ("An invalid pointer", False), ("A pointer to void return function", False)]
                    },
                    {
                        "q": "<p>What is a Wild Pointer?</p>",
                        "opts": [("An uninitialized pointer pointing to an arbitrary unallocated memory location", True), ("A pointer to NULL", False), ("A void pointer", False), ("A dangling pointer", False)]
                    }
                ]
            },
            {
                "title": "C - Hard: Dynamic Memory Allocation",
                "topic": "C Language",
                "questions": [
                    {
                        "q": "<p>Which header file declares dynamic memory allocation functions like malloc() and free()?</p>",
                        "opts": [("<stdlib.h>", True), ("<stdio.h>", False), ("<string.h>", False), ("<memory.h>", False)]
                    },
                    {
                        "q": "<p>Which function allocates uninitialized memory block on Heap and returns a void pointer?</p>",
                        "opts": [("malloc()", True), ("calloc()", False), ("realloc()", False), ("alloc()", False)]
                    },
                    {
                        "q": "<p>How does calloc() differ from malloc()?</p>",
                        "opts": [("calloc() allocates memory and initializes all bytes to ZERO", True), ("calloc() allocates memory on stack", False), ("calloc() is faster than malloc()", False), ("malloc() zeroes out memory", False)]
                    },
                    {
                        "q": "<p>Which function resizes previously allocated heap memory without losing existing data?</p>",
                        "opts": [("realloc()", True), ("malloc()", False), ("resize()", False), ("calloc()", False)]
                    },
                    {
                        "q": "<p>Which function deallocates dynamic memory back to the Heap?</p>",
                        "opts": [("free()", True), ("delete()", False), ("dealloc()", False), ("release()", False)]
                    },
                    {
                        "q": "<p>What is a Memory Leak in C?</p>",
                        "opts": [("Failing to free dynamically allocated heap memory after use", True), ("Accessing array out of bounds", False), ("Dereferencing NULL pointer", False), ("Stack overflow", False)]
                    }
                ]
            },
            {
                "title": "C - Hard: Structures, Unions & Enums",
                "topic": "C Language",
                "questions": [
                    {
                        "q": "<p>Which keyword creates a user-defined composite data type grouping variables under one name?</p>",
                        "opts": [("struct", True), ("union", False), ("class", False), ("typedef", False)]
                    },
                    {
                        "q": "<p>Which operator is used to access structure members using a structure pointer variable?</p>",
                        "opts": [("-> (Arrow operator)", True), (". (Dot operator)", False), ("* (Asterisk)", False), ("::", False)]
                    },
                    {
                        "q": "<p>How does a Union differ from a Structure in C memory layout?</p>",
                        "opts": [("All members of a Union share the exact same memory location (size = largest member)", True), ("Unions cannot hold integers", False), ("Structures share memory for all members", False), ("Unions use heap memory only", False)]
                    },
                    {
                        "q": "<p>Which keyword creates an alias for an existing data type in C?</p>",
                        "opts": [("typedef", True), ("alias", False), ("using", False), ("define", False)]
                    },
                    {
                        "q": "<p>Which keyword defines a type consisting of a set of named integer constants?</p>",
                        "opts": [("enum", True), ("const", False), ("set", False), ("list", False)]
                    },
                    {
                        "q": "<p>Which operator accesses members of a structure variable directly (not via pointer)?</p>",
                        "opts": [(". (Dot operator)", True), ("-> (Arrow operator)", False), ("*", False), ("&", False)]
                    }
                ]
            },
            {
                "title": "C - Advanced: File Handling & Preprocessor",
                "topic": "C Language",
                "questions": [
                    {
                        "q": "<p>Which file pointer type is defined in <stdio.h> for file streams?</p>",
                        "opts": [("FILE*", True), ("fstream", False), ("file_t", False), ("FileHandle", False)]
                    },
                    {
                        "q": "<p>Which function opens a file stream in C?</p>",
                        "opts": [("fopen()", True), ("open()", False), ("file_open()", False), ("read_file()", False)]
                    },
                    {
                        "q": "<p>Which preprocessor directive is used to define macro constants or inline macros?</p>",
                        "opts": [("#define", True), ("#macro", False), ("#const", False), ("#include", False)]
                    },
                    {
                        "q": "<p>Which preprocessor directive prevents double inclusion of header files (header guards)?</p>",
                        "opts": [("#ifndef / #define / #endif", True), ("#import", False), ("#pragma once only", False), ("#guard", False)]
                    },
                    {
                        "q": "<p>Which function writes formatted text into a file stream in C?</p>",
                        "opts": [("fprintf()", True), ("printf()", False), ("fputs()", False), ("fwrite()", False)]
                    },
                    {
                        "q": "<p>What value does fopen() return if a file cannot be opened?</p>",
                        "opts": [("NULL", True), ("-1", False), ("0", False), ("EOF", False)]
                    }
                ]
            },
            {
                "title": "C - Advanced: Storage Classes & Bitwise",
                "topic": "C Language",
                "questions": [
                    {
                        "q": "<p>Which storage class keeps a local variable's value intact between function calls?</p>",
                        "opts": [("static", True), ("auto", False), ("register", False), ("extern", False)]
                    },
                    {
                        "q": "<p>Which storage class hints to compiler to store variable in CPU register for fast access?</p>",
                        "opts": [("register", True), ("static", False), ("extern", False), ("volatile", False)]
                    },
                    {
                        "q": "<p>Which keyword declares a variable defined in another source file or global scope?</p>",
                        "opts": [("extern", True), ("global", False), ("public", False), ("import", False)]
                    },
                    {
                        "q": "<p>Which modifier prevents compiler from optimizing out variable access (used for hardware memory)?</p>",
                        "opts": [("volatile", True), ("const", False), ("static", False), ("restrict", False)]
                    },
                    {
                        "q": "<p>What is the Left Shift bitwise operator (<<) equivalent to for positive integers?</p>",
                        "opts": [("Multiplying by 2 raised to the power of shift count", True), ("Dividing by 2", False), ("Adding shift count", False), ("Bitwise inversion", False)]
                    },
                    {
                        "q": "<p>What is the default storage class for local variables inside functions in C?</p>",
                        "opts": [("auto", True), ("static", False), ("extern", False), ("register", False)]
                    }
                ]
            }
        ]

        # =========================================================================
        # SECTION 4: OOPS CONCEPTS (10 TEST SERIES)
        # =========================================================================
        oops_series = [
            {
                "title": "OOPs - Beginner: Fundamentals & Paradigm",
                "topic": "OOPs Concepts",
                "questions": [
                    {
                        "q": "<p>What are the four core pillars of Object-Oriented Programming (OOP)?</p>",
                        "opts": [("Encapsulation, Abstraction, Inheritance, Polymorphism", True), ("Functions, Variables, Loops, Arrays", False), ("Classes, Objects, Methods, Attributes", False), ("Compilation, Linking, Execution, Debugging", False)]
                    },
                    {
                        "q": "<p>What is a Class in OOP?</p>",
                        "opts": [("A blueprint or template defining state (attributes) and behavior (methods) for objects", True), ("A physical instance in memory", False), ("A built-in data type", False), ("A database table", False)]
                    },
                    {
                        "q": "<p>What is an Object in OOP?</p>",
                        "opts": [("An instance of a class occupying memory space", True), ("A class blueprint", False), ("A header file", False), ("A function definition", False)]
                    },
                    {
                        "q": "<p>How does procedural programming differ primarily from object-oriented programming?</p>",
                        "opts": [("Procedural focuses on step-by-step functions/actions; OOP focuses on data and objects", True), ("Procedural has no functions", False), ("OOP does not allow code reuse", False), ("Procedural is faster always", False)]
                    },
                    {
                        "q": "<p>What term describes the state of an object?</p>",
                        "opts": [("Data stored in instance attributes/fields", True), ("Member functions", False), ("Class inheritance level", False), ("Return values", False)]
                    },
                    {
                        "q": "<p>What term describes the actions/behaviors of an object?</p>",
                        "opts": [("Methods / Member functions", True), ("Properties", False), ("Constants", False), ("Constructors", False)]
                    }
                ]
            },
            {
                "title": "OOPs - Easy: Encapsulation & Access Control",
                "topic": "OOPs Concepts",
                "questions": [
                    {
                        "q": "<p>What is Encapsulation in OOP?</p>",
                        "opts": [("Bundling data and methods into a single unit and restricting direct access to object state", True), ("Deriving child classes from parent", False), ("Defining multiple methods with same name", False), ("Hiding execution logic", False)]
                    },
                    {
                        "q": "<p>Which access specifier restricts property visibility strictly to the defining class?</p>",
                        "opts": [("private", True), ("protected", False), ("public", False), ("package", False)]
                    },
                    {
                        "q": "<p>What methods are standardly used to read and update private fields safely in OOP?</p>",
                        "opts": [("Getters and Setters (Accessors and Mutators)", True), ("Constructors and Destructors", False), ("Static initializers", False), ("Friend functions", False)]
                    },
                    {
                        "q": "<p>Which access modifier allows access within the defining class and its derived subclasses?</p>",
                        "opts": [("protected", True), ("private", False), ("public", False), ("internal", False)]
                    },
                    {
                        "q": "<p>Why is direct access to internal fields usually restricted in clean OOP design?</p>",
                        "opts": [("To enforce data validation, preserve internal invariants, and hide implementation details", True), ("To decrease memory usage", False), ("To prevent class inheritance", False), ("Because private variables execute faster", False)]
                    },
                    {
                        "q": "<p>Which access modifier allows unrestricted access from anywhere in the program?</p>",
                        "opts": [("public", True), ("protected", False), ("private", False), ("package-private", False)]
                    }
                ]
            },
            {
                "title": "OOPs - Easy: Abstraction & Abstract Classes",
                "topic": "OOPs Concepts",
                "questions": [
                    {
                        "q": "<p>What is Abstraction in Object-Oriented Design?</p>",
                        "opts": [("Hiding complex internal implementation details and exposing only essential interfaces", True), ("Hiding variables inside methods", False), ("Creating multiple object instances", False), ("Converting objects to JSON", False)]
                    },
                    {
                        "q": "<p>What is an Abstract Class?</p>",
                        "opts": [("A class that cannot be directly instantiated and may contain abstract methods", True), ("A class with no properties", False), ("A class marked static", False), ("A class that cannot be inherited", False)]
                    },
                    {
                        "q": "<p>What is an Abstract Method?</p>",
                        "opts": [("A method declared without implementation that must be overridden by concrete subclasses", True), ("A method with private body", False), ("A static method", False), ("A constructor method", False)]
                    },
                    {
                        "q": "<p>Can an abstract class contain concrete (implemented) methods alongside abstract methods?</p>",
                        "opts": [("Yes, abstract classes can have both implemented and abstract methods", True), ("No, all methods must be abstract", False), ("No, it can have no methods at all", False), ("Only in C++", False)]
                    },
                    {
                        "q": "<p>What happens if a child class fails to implement all abstract methods of an abstract parent class?</p>",
                        "opts": [("The child class must also be declared abstract (or causes a compilation error)", True), ("It defaults to empty implementation", False), ("It deletes those methods", False), ("Runtime warning only", False)]
                    },
                    {
                        "q": "<p>How does Abstraction differ from Encapsulation?</p>",
                        "opts": [("Abstraction focuses on WHAT the object does; Encapsulation focuses on HOW data is protected", True), ("There is no difference", False), ("Abstraction uses private keyword only", False), ("Encapsulation hides class names", False)]
                    }
                ]
            },
            {
                "title": "OOPs - Intermediate: Inheritance & Hierarchy",
                "topic": "OOPs Concepts",
                "questions": [
                    {
                        "q": "<p>What is Inheritance in OOP?</p>",
                        "opts": [("A mechanism where a child class acquires properties and behaviors of a parent class", True), ("Combining two classes into one", False), ("Overloading method signatures", False), ("Restricting class access", False)]
                    },
                    {
                        "q": "<p>What relationship type does Inheritance represent in OOP modeling?</p>",
                        "opts": [('"IS-A" relationship (e.g. Dog IS-A Mammal)', True), ('"HAS-A" relationship', False), ('"USES-A" relationship', False), ('"DEPENDS-ON" relationship', False)]
                    },
                    {
                        "q": "<p>What is Single Inheritance?</p>",
                        "opts": [("A derived class inherits from exactly one base class", True), ("A base class has only one method", False), ("An object has only one property", False), ("A class cannot be inherited", False)]
                    },
                    {
                        "q": "<p>What is Multilevel Inheritance?</p>",
                        "opts": [("A class inherits from a derived class, forming a chain of inheritance (A -> B -> C)", True), ("A class inherits from multiple parents directly", False), ("A class has multiple constructors", False), ("A class has 10 methods", False)]
                    },
                    {
                        "q": "<p>What is Multiple Inheritance and why do some languages (like Java/C#) disallow it for classes?</p>",
                        "opts": [("Class inheriting from multiple parent classes directly; disallowed to avoid Diamond Problem ambiguity", True), ("Class inheriting 5 levels deep", False), ("Class having multiple objects", False), ("Disallowed because of speed", False)]
                    },
                    {
                        "q": "<p>Which relationship represents Composition (e.g. Car HAS-A Engine)?</p>",
                        "opts": [('"HAS-A" relationship (containing an instance of another class)', True), ('"IS-A" relationship', False), ('"DERIVES-FROM" relationship', False), ('"IMPLEMENTS" relationship', False)]
                    }
                ]
            },
            {
                "title": "OOPs - Intermediate: Polymorphism",
                "topic": "OOPs Concepts",
                "questions": [
                    {
                        "q": "<p>What does the term Polymorphism literally mean?</p>",
                        "opts": [('"Many forms" (ability of an entity to take different forms in different contexts)', True), ('"Data hiding"', False), ('"Single structure"', False), ('"Code duplication"', False)]
                    },
                    {
                        "q": "<p>What is Method Overloading (Compile-time Polymorphism)?</p>",
                        "opts": [("Defining multiple methods in same class with SAME name but DIFFERENT parameter signatures", True), ("Redefining parent method in child class", False), ("Changing method visibility", False), ("Overloading memory", False)]
                    },
                    {
                        "q": "<p>What is Method Overriding (Runtime Polymorphism)?</p>",
                        "opts": [("Subclass providing a specific implementation for a method already defined in parent class", True), ("Defining methods with same name and different parameters", False), ("Hiding parent attributes", False), ("Static method call", False)]
                    },
                    {
                        "q": "<p>How is Method Overriding resolved at runtime in OOP?</p>",
                        "opts": [("Dynamic Method Dispatch (using virtual function tables / vtables)", True), ("Compiler static linking", False), ("Macro expansion", False), ("Source text replacement", False)]
                    },
                    {
                        "q": "<p>Can static methods be overridden dynamically in OOP?</p>",
                        "opts": [("No, static methods belong to class and are bound at compile time (method hiding occurs instead)", True), ("Yes, always", False), ("Yes, if declared virtual", False), ("Only in Python", False)]
                    },
                    {
                        "q": "<p>Which mechanism allows operators like + to work differently based on operand types?</p>",
                        "opts": [("Operator Overloading", True), ("Operator Overriding", False), ("Operator Composition", False), ("Operator Dispatch", False)]
                    }
                ]
            },
            {
                "title": "OOPs - Intermediate: Constructors & Destructors",
                "topic": "OOPs Concepts",
                "questions": [
                    {
                        "q": "<p>What is a Constructor in OOP?</p>",
                        "opts": [("A special member function invoked automatically when an object of a class is instantiated", True), ("A method that deletes objects", False), ("A static utility function", False), ("A compiler tool", False)]
                    },
                    {
                        "q": "<p>What is a Copy Constructor?</p>",
                        "opts": [("A constructor that initializes a new object using an existing object of the same class", True), ("A constructor that clones classes", False), ("A default constructor", False), ("A private constructor", False)]
                    },
                    {
                        "q": "<p>What is a Destructor in OOP?</p>",
                        "opts": [("A special method invoked automatically when an object goes out of scope or is destroyed", True), ("A method to delete class files", False), ("An error handler", False), ("A memory allocation function", False)]
                    },
                    {
                        "q": "<p>In what order are constructors called during inheritance hierarchy instantiation (Parent A -> Child B)?</p>",
                        "opts": [("Parent constructor executes FIRST, followed by Child constructor", True), ("Child executes first", False), ("Both execute simultaneously", False), ("Random order", False)]
                    },
                    {
                        "q": "<p>In what order are destructors executed in inheritance hierarchy?</p>",
                        "opts": [("Child destructor executes FIRST, followed by Parent destructor (reverse order)", True), ("Parent destructor executes first", False), ("Simultaneously", False), ("Destructors do not execute in hierarchy", False)]
                    },
                    {
                        "q": "<p>Can a constructor return a value or specify a return type in languages like C++/Java?</p>",
                        "opts": [("No, constructors have NO return type (not even void)", True), ("Yes, int", False), ("Yes, void", False), ("Yes, object pointer", False)]
                    }
                ]
            },
            {
                "title": "OOPs - Hard: Interfaces & Coupling",
                "topic": "OOPs Concepts",
                "questions": [
                    {
                        "q": "<p>What is an Interface in OOP?</p>",
                        "opts": [("A pure contract specifying WHAT methods a class must implement without providing state/instance fields", True), ("A class with public fields only", False), ("A GUI layout component", False), ("A database schema", False)]
                    },
                    {
                        "q": "<p>What is Loose Coupling in software design?</p>",
                        "opts": [("Minimizing dependencies between components so changes in one do not impact another", True), ("Connecting all classes directly", False), ("Putting all code in one file", False), ("Eliminating interfaces", False)]
                    },
                    {
                        "q": "<p>What is High Cohesion in software architecture?</p>",
                        "opts": [("Designing a class to have a single, tightly-focused responsibility", True), ("Spreading logic across 20 classes", False), ("Mixing UI and DB code in one class", False), ("Using global variables everywhere", False)]
                    },
                    {
                        "q": "<p>How do Interfaces solve the Diamond Problem of multiple inheritance?</p>",
                        "opts": [("By enforcing contracts without state/field multiple inheritance conflicts", True), ("By duplicating code", False), ("By turning errors off", False), ("By making methods private", False)]
                    },
                    {
                        "q": "<p>Can a single class implement multiple interfaces in languages like Java or C#?</p>",
                        "opts": [("Yes, classes can implement multiple interfaces", True), ("No, maximum 1 interface", False), ("Only in abstract classes", False), ("Only using traits", False)]
                    },
                    {
                        "q": "<p>Can interfaces contain instance state fields in standard OOP languages?</p>",
                        "opts": [("No, interfaces standardly contain method declarations and static constants only", True), ("Yes, all fields", False), ("Yes, private fields", False), ("Yes, mutable fields", False)]
                    }
                ]
            },
            {
                "title": "OOPs - Hard: SOLID Principles",
                "topic": "OOPs Concepts",
                "questions": [
                    {
                        "q": "<p>What does the 'S' in SOLID principles stand for?</p>",
                        "opts": [("Single Responsibility Principle (A class should have only one reason to change)", True), ("Single Thread Principle", False), ("System Security Principle", False), ("State Synchronization Principle", False)]
                    },
                    {
                        "q": "<p>What does the 'O' in SOLID principles stand for?</p>",
                        "opts": [("Open/Closed Principle (Software entities should be open for extension, closed for modification)", True), ("Object Oriented Principle", False), ("Operational Order Principle", False), ("Overloading Optimization", False)]
                    },
                    {
                        "q": "<p>What does the 'L' in SOLID principles stand for?</p>",
                        "opts": [("Liskov Substitution Principle (Subtypes must be substitutable for base types without breaking program correctness)", True), ("Linear Scope Principle", False), ("Logical Linking Principle", False), ("Lazy Loading Principle", False)]
                    },
                    {
                        "q": "<p>What does the 'I' in SOLID principles stand for?</p>",
                        "opts": [("Interface Segregation Principle (Clients should not be forced to depend on interfaces they do not use)", True), ("Inheritance Isolation Principle", False), ("Instance Initialization Principle", False), ("Internal Immutability Principle", False)]
                    },
                    {
                        "q": "<p>What does the 'D' in SOLID principles stand for?</p>",
                        "opts": [("Dependency Inversion Principle (Depend upon abstractions, not concrete implementations)", True), ("Data Decoupling Principle", False), ("Dynamic Dispatch Principle", False), ("Destructor Definition Principle", False)]
                    },
                    {
                        "q": "<p>What design technique injects dependent objects into a class rather than letting the class instantiate them directly?</p>",
                        "opts": [("Dependency Injection (DI)", True), ("Object Cloning", False), ("Static Factory", False), ("Class Extension", False)]
                    }
                ]
            },
            {
                "title": "OOPs - Advanced: Creational & Structural Patterns",
                "topic": "OOPs Concepts",
                "questions": [
                    {
                        "q": "<p>Which Creational pattern ensures a class has ONLY ONE instance globally and provides a global access point?</p>",
                        "opts": [("Singleton Pattern", True), ("Factory Pattern", False), ("Builder Pattern", False), ("Prototype Pattern", False)]
                    },
                    {
                        "q": "<p>Which Creational pattern provides an interface for creating objects in a superclass, allowing subclasses to alter the type of created objects?</p>",
                        "opts": [("Factory Method Pattern", True), ("Adapter Pattern", False), ("Decorator Pattern", False), ("Proxy Pattern", False)]
                    },
                    {
                        "q": "<p>Which Structural design pattern allows incompatible interfaces to work together by wrapping an object?</p>",
                        "opts": [("Adapter Pattern", True), ("Singleton Pattern", False), ("Observer Pattern", False), ("Strategy Pattern", False)]
                    },
                    {
                        "q": "<p>Which Structural pattern attaches new behaviors to objects dynamically by placing them inside special wrapper objects?</p>",
                        "opts": [("Decorator Pattern", True), ("Facade Pattern", False), ("Bridge Pattern", False), ("Composite Pattern", False)]
                    },
                    {
                        "q": "<p>Which Creational pattern separates the construction of a complex object from its representation?</p>",
                        "opts": [("Builder Pattern", True), ("Singleton Pattern", False), ("Flyweight Pattern", False), ("Chain of Responsibility", False)]
                    },
                    {
                        "q": "<p>Which Structural pattern provides a simplified interface to a complex library or subsystem?</p>",
                        "opts": [("Facade Pattern", True), ("Proxy Pattern", False), ("Decorator Pattern", False), ("Command Pattern", False)]
                    }
                ]
            },
            {
                "title": "OOPs - Advanced: Behavioral Patterns & Architecture",
                "topic": "OOPs Concepts",
                "questions": [
                    {
                        "q": "<p>Which Behavioral pattern defines a subscription mechanism to notify multiple observer objects of state changes?</p>",
                        "opts": [("Observer Pattern (Publish-Subscribe)", True), ("Strategy Pattern", False), ("Command Pattern", False), ("Iterator Pattern", False)]
                    },
                    {
                        "q": "<p>Which Behavioral pattern defines a family of algorithms, encapsulates each one, and makes them interchangeable at runtime?</p>",
                        "opts": [("Strategy Pattern", True), ("State Pattern", False), ("Template Method Pattern", False), ("Visitor Pattern", False)]
                    },
                    {
                        "q": "<p>Which Architectural pattern divides an application into Model, View, and Controller components?</p>",
                        "opts": [("MVC (Model-View-Controller)", True), ("MVVM", False), ("Monolithic Architecture", False), ("Microservices", False)]
                    },
                    {
                        "q": "<p>Which Behavioral pattern encapsulates a request as an object, allowing parameterization and queuing of requests?</p>",
                        "opts": [("Command Pattern", True), ("Mediator Pattern", False), ("Memento Pattern", False), ("Chain of Responsibility", False)]
                    },
                    {
                        "q": "<p>Which Behavioral pattern allows an object to alter its behavior when its internal state changes (appearing to change its class)?</p>",
                        "opts": [("State Pattern", True), ("Strategy Pattern", False), ("Observer Pattern", False), ("Proxy Pattern", False)]
                    },
                    {
                        "q": "<p>Which Behavioral pattern captures and externalizes an object's internal state so it can be restored later (Undo/Rollback)?</p>",
                        "opts": [("Memento Pattern", True), ("Visitor Pattern", False), ("Flyweight Pattern", False), ("Interpreter Pattern", False)]
                    }
                ]
            }
        ]

        # 2. Run all insertions sequentially
        print("\n=== SEEDING JAVASCRIPT (10 SERIES) ===")
        for s in js_series:
            insert_series(s["title"], s["topic"], s["questions"])

        print("\n=== SEEDING PYTHON (10 SERIES) ===")
        for s in python_series:
            insert_series(s["title"], s["topic"], s["questions"])

        print("\n=== SEEDING C LANGUAGE (10 SERIES) ===")
        for s in c_series:
            insert_series(s["title"], s["topic"], s["questions"])

        print("\n=== SEEDING OOPS CONCEPTS (10 SERIES) ===")
        for s in oops_series:
            insert_series(s["title"], s["topic"], s["questions"])

        print("\nALL 40 TEST SERIES (240 QUESTIONS) SUCCESSFULLY SEEDED INTO DATABASE!")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all_tech_data()
