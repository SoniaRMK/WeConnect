from flask_restful.reqparse import RequestParser

from resources import *
from models.reviews import Review
from models.businesses import Business
from models.users import User


"""Validating the arguments"""
review_validation = RequestParser(bundle_errors=True)
review_validation.add_argument("review_msg", type=str, required=True, 
                                help="Review Message is missing")
review_validation.add_argument("review_title", type=str, required=True, 
                                help="Review title is missing")

class ReviewBusiness(Resource):
    """Class for adding and viewing reviews"""
    @swag_from("../APIdocs/AddReview.yml")
    @token_required
    def post(self, bizid):
        """Add a review to a business""" 

        user_id = request.data['user']
        business = Business.query.get(bizid)
        if not business:
            message = {'message': "Business you're trying to review isn't registered!"}
            resp = jsonify(message)
            resp.status_code = 404
            return resp
        if business.user_id == user_id:
            message = {'message': "You cannot review a business you registered!!"}
            resp = jsonify(message)
            resp.status_code = 401
            return resp
        else:
            review = Review(review_title = review_validation.parse_args().\
                            review_title.title().strip(), 
                            review_msg = review_validation.parse_args().review_msg.strip(), 
                            business_id = bizid, user_id = user_id)
            db.session.add(review)
            db.session.commit()
            message = {'message': "Review added successfully!!"}
            resp = jsonify(message)
            resp.status_code = 200
            return resp

    """Get all reviews of a business"""
    @token_required
    @swag_from("../APIdocs/ViewReviews.yml")
    def get(self, bizid):
        """Gets all reviews added to a specified business"""
        business = Business.query.get(bizid)
        if not business:
            resp = Business.businesses_not_found_message(business)
        reviews = Review.query.filter_by(business_id=bizid).all()
        if not reviews:   
            message = {'message': "Business doesn't have reviews yet!!"}
            resp = jsonify(message)
            resp.status_code = 404
        output = []
        for rev in reviews:
            username = User.query.filter_by(id=rev.user_id).first().user_name
            businessname = Business.query.filter_by(id=bizid).first().business_name
            review_item = {
                'Review Title': rev.review_title,
                'Review Message': rev.review_msg,
                'Business Name': businessname,
                'Reviewd By': username
                 }
            output.append(review_item)
            message = {'Reviews': output}
            resp = jsonify(message)
            resp.status_code = 200
        return resp
        