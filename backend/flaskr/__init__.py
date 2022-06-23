import json
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Question, Category
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Pagination


def pagination_questions(request, selection):
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
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Header
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Origin", "*"
        )
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorisation, true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,PATCH,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        selections = Category.query.order_by(Category.id).all()
        formatted_category = [category.format() for category in selections]

        return jsonify({
            'success': True,
            'id': formatted_category.id
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
        selections = Question.query.order_by(Question.id).all()
        current_question = pagination_questions(request, selections)
        categories = Category.query.order_by(Category.id).all()
        categories.format()

        if not current_question:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_question,
            'total_questions': len(Question.query.all()),
            # 'current_category': self.current_category,
            'categories': categories
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        body = request.get_json()

        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selections = Question.query.order_by(Question.id).all()
            current_question = pagination_questions(request, selections)

            return jsonify({
                'success': True,
                'id': question_id,
                'questions': current_question,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(question=new_question, answer=new_answer,
                                category=new_category, difficulty=new_difficulty)

            selections = Question.query.order_by(Question.id).all()
            current_question = pagination_questions(request, selections)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_question,
                'total_questions': len(Question.query.all())
            })

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

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

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    # Error handling
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

    return app
