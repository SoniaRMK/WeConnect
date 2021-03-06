import re
from flask_restful.reqparse import RequestParser

from models.businesses import Business
from models.users import User
from resources import *


#Validating the arguments
business_validation = RequestParser(bundle_errors=True)
business_validation.add_argument("business_name", type=str, required=True,
                                help="Business Name is missing")
business_validation.add_argument("category", type=str, required=True,
                                help="Category is missing")
business_validation.add_argument("location", type=str, required=True,
                                help="Location is missing")
business_validation.add_argument("business_profile", type=str, required=True,
                                help="Business Profile is missing")

#Validating search by name q and filtering by location and category
q_request_parser = RequestParser(bundle_errors=True)
q_request_parser.add_argument("q", type=str, required=False,
                                help="Search term is missing")
q_request_parser.add_argument("page", type=int, required=False,
                                help="Page is missing")
q_request_parser.add_argument("location", type=str, required=False,
                                help="Business location filter is missing")
q_request_parser.add_argument("category", type=str, required=False,
                                help="Business category filter is missing")

class BusinessInputValidator():

    @staticmethod
    def business_input_validator(business_name, location, category):
        if ("  " in business_name):
            message = {'message':'Too many spaces in between the business name!'}
            resp = jsonify(message)
            resp.status_code = 403
        elif ("  " in location):
            message = {'message':'Too many spaces in between the location name!'}
            resp = jsonify(message)
            resp.status_code = 403
        elif ("  " in category):
            message = {'message':'Too many spaces in between the category name!'}
            resp = jsonify(message)
            resp.status_code = 403   
        elif len(business_name)>60:
            message = {'message':'Business name should not be longer than 60!'}
            resp = jsonify(message)
            resp.status_code = 403
        elif len(category)>60:
            message = {'message':'Category should not be longer than 60!'}
            resp = jsonify(message)
            resp.status_code = 403
        elif len(location)>60:
            message = {'message':'Location should not be longer than 60!'}
            resp = jsonify(message)
            resp.status_code = 403
        return resp
    
    @staticmethod
    def businesses_not_found(business):
        """Return Message when no business is found""" 
        resp = Business.businesses_not_found_message(business)
        return resp
    
    @staticmethod
    def user_unathorised(user_id):
        """Return Message when user is not allowed to perform a certain task""" 
        message = {'message':"You can't Edit a business you didn't register!!"}
        resp = jsonify(message)
        resp.status_code = 401
        return resp
class BusinessOne(Resource):
    """Class for getting, updating and deleting a business"""

    @swag_from("../APIdocs/ViewBusiness.yml")
    @token_required
    def get(self, bizid):
        """gets a  business"""

        business = Business.query.get(bizid)
        if not business:
            response = BusinessInputValidator.\
            businesses_not_found(business)
            return response
        
        userid = business.user_id
        user = User.query.filter_by(id=userid).first()
        username = user.user_name

        output = {}
        output['id'] = business.id
        output['BusinessName'] = business.business_name
        output['BusinessProfile'] = business.business_profile
        output['Location'] = business.location
        output['Category'] = business.category
        output['CreatedBy'] =  username
        
        message = {'business': output}
        resp = jsonify(message)
        resp.status_code = 200
        return resp

    @swag_from("../APIdocs/DeleteBusiness.yml")
    @token_required
    def delete(self, bizid):
        """deletes a business"""

        userid = request.data['user']
        business = Business.query.get(bizid)
        if business is None:
            message = {'message':'Business not registered yet!'}
            resp = jsonify(message)
            resp.status_code = 404
        elif business.user_id != userid:
            message = {'message':"You can't delete a business you didn't register!!"}
            resp = jsonify(message)
            resp.status_code = 401
        else:
            db.session.delete(business)
            db.session.commit()
            message = {'message':'Business successfully Deleted!'}
            resp = jsonify(message)
            resp.status_code = 200
        return resp
        
    @swag_from("../APIdocs/UpdateBusiness.yml")
    @token_required
    def put(self, bizid):
        """edits a  business"""
        userid = request.data['user']
        business = Business.query.get(bizid)
        if not business:
            response = BusinessInputValidator.\
            businesses_not_found(business)
            return response
        if business.user_id != userid:
            response = BusinessInputValidator.user_unathorised(business.user_id)
            return response
        business.business_name=(business_validation.parse_args()\
                                .business_name).strip()
        business.business_profile=(business_validation.parse_args()\
                                .business_profile).strip()
        business.location=(business_validation.parse_args()\
                                .location).title().strip()
        business.category=(business_validation.parse_args()\
                                .category).title().strip()
        
        if ("  " in business.business_name):
            response = BusinessInputValidator.\
            business_input_validator(business.business_name,
                                    business.location, business.category)
        elif ("  " in business.location):
            response = BusinessInputValidator.\
            business_input_validator(business.business_name,
                                    business.location, business.category)
        elif ("  " in business.category):
            response = BusinessInputValidator.\
            business_input_validator(business.business_name,
                                    business.location, business.category)
        elif len(business.business_name)>60:
            response = BusinessInputValidator.\
            business_input_validator(business.business_name,
                                    business.location, business.category)
        elif len(business.category)>60:
            response = BusinessInputValidator.\
            business_input_validator(business.business_name,
                                    business.location, business.category)
        elif len(business.location)>60:
            response = BusinessInputValidator.\
            business_input_validator(business.business_name,
                                    business.location, business.category)
        else:
            try:
                db.session.commit()
                message = {'message':'Business successfully Updated!'}
                response = jsonify(message)
                response.status_code = 200
            except:
                message = {'message':'The new Business name is already taken,\
                            Choose another name!'}
                response = jsonify(message)
                response.status_code = 409
        return response       

class BusinessList(Resource):
    """class to create a business and get all businesses""" 
    
    @swag_from("../APIdocs/CreateBusiness.yml")
    @token_required
    def post(self):
        """creates a new business"""

        user = request.data['user']
        business_name=(business_validation.parse_args().business_name).title().strip()
        business_profile=(business_validation.parse_args().business_profile).strip()
        location=(business_validation.parse_args().location).title().strip()
        category=(business_validation.parse_args().category).title().strip()
        user_id=user
        if ("  " in business_name):
            response = BusinessInputValidator.\
            business_input_validator(business_name, location, category)
        elif ("  " in location):
            response = BusinessInputValidator.\
            business_input_validator(business_name, location, category)
        elif ("  " in category):
            response = BusinessInputValidator.\
            business_input_validator(business_name, location, category)
        elif len(business_name)>60:
            response = BusinessInputValidator.\
            business_input_validator(business_name, location, category)
        elif len(category)>60:
            response = BusinessInputValidator.\
            business_input_validator(business_name, location, category)
        elif len(location)>60:
            response = BusinessInputValidator.\
            business_input_validator(business_name, location, category)
        else:
            business = Business(business_name, business_profile,
                                location, category, user_id)
            try:
                db.session.add(business)
                db.session.commit()
                message = {'message':'Business registered!'}
                response = jsonify(message)
                response.status_code = 201
            except:
                message = {'message':'Business already Exists!'}
                response = jsonify(message)
                response.status_code = 409 
        db.session.close()
        return response 
    
    @token_required
    @swag_from("../APIdocs/ViewBusinesses.yml")
    def get(self):
        """Get all businesses registered"""

        search_term=request.args.get('q', None)
        page=request.args.get('page', 1, type = int)
        location_name=request.args.get('location', None)
        category_name=request.args.get('category', None)
        search_results = Business.search_businesses(search_term=search_term,
                                location=location_name, category=category_name, page=page)
        return search_results
        