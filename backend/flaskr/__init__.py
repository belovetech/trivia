import json
import os
from flask import Flask, current_app, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Question Pagination


def paginate_questions(request, selection):
    """paginate questions page"""
    pages = request.args.get('page', 1, type=int)
    start = (pages - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_questions = [question.format() for question in selection]
    current_questions = formatted_questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # Set up CORS. Allow '*' for all origins.
    CORS(app, resources={'/': {'origins': '*'}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Header
    @app.after_request
    def after_request(response):
        """Set access control."""
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorisation,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        """Handles GET request for getting all categories"""

        # get all categories and add to dictionary
        categories = Category.query.order_by(Category.id).all()
        categories_dic = {}

        for category in categories:
            categories_dic[category.id] = category.type

        if len(categories_dic) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories_dic
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        """Handles GET request for getting all questions"""

        selections = Question.query.order_by(Question.id).all()
        current_question = paginate_questions(request, selections)

        # get all categories and add to dictionary
        categories = Category.query.order_by(Category.id).all()
        categories_dic = {}

        for category in categories:
            categories_dic[category.id] = category.type

        if not current_question:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_question,
            'total_questions': len(selections),
            'categories': categories_dic
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """Handles DELETE request for deleting question based on id"""

        try:
            # get question by id
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            # delete the question
            question.delete()

            selections = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selections)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_question,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route('/questions', methods=['POST'])
    def create_question():
        """Handels Post request for creating new question"""

        # load the requests body
        body = request.get_json()

        # if search term is present
        if (body.get('searchTerm')):
            search_term = body.get('searchTerm')

            selections = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            if (len(selections) == 0):
                abort(404)

            current_question = paginate_questions(request, selections)

            return jsonify({
                'success': True,
                'questions': current_question,
                'total_questions': len(selections)
            })
        else:

            new_question = body.get('question', None)
            new_answer = body.get('answer', None)
            new_category = body.get('category', None)
            new_difficulty = body.get('difficulty', None)

            if new_question is None or new_answer is None or new_category is None or new_difficulty is None:
                abort(422)

        try:
            question = Question(question=new_question, answer=new_answer,
                                category=new_category, difficulty=new_difficulty)

            question.insert()

            # get all questions and paginate
            selections = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selections)

            return jsonify({
                'success': True,
                'created': question.id,
                'question_created': question.question,
                'questions': current_question,
                'total_questions': len(Question.query.all())
            })

        except:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        """Handles Get request for getting questions based on category"""

        # get the category id
        category = Category.query.filter_by(
            id=id).one_or_none()

        if category is None:
            abort(400)

        # get the match questions and paginate
        selections = Question.query.filter_by(
            category=category.id).all()
        current_questions = paginate_questions(request, selections)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'current_category': category.type
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def get_random_quiz_question():
        """Handles POST request for playing quiz"""
        body = request.get_json()

        previous = body.get('previous_questions')

        category = body.get('quiz_category')

        if category is None or previous is None:
            abort(400)

        # load all questions if 'ALL' is selected
        if category['id'] == 0:
            questions = Question.query.all()
        else:
            # load quetion for a given category
            questions = Question.query.filter_by(category=category['id']).all()

        total_questions = len(questions)

        # picks a random question
        def get_random_quiz_question():
            return questions[random.randrange(0, total_questions, 1)]

        # checks to see if the question has been given before
        def is_used(question):
            used = False
            for que in previous:
                if que == question.id:
                    used = True
            return used

        # get random question
        question = get_random_quiz_question()

        while (is_used(question)):
            question = get_random_quiz_question()

            # if all questions have been used return no question
            if (len(previous) == total_questions):
                return jsonify({
                    'success': True
                })

        return jsonify({
            'success': True,
            'question': question.format()
        })

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    # Error handling
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resources not found'
        }), 404

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unproccessable'
        }), 422

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'method not allowed'
        }), 405

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
        }), 500

    return app
