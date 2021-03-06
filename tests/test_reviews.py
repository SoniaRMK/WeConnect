import unittest
import json
from resources import app, db
from run import ReviewBusiness, BusinessList, BusinessOne, UserRegister, UserLogin
# from models.models import User


class TestUser(unittest.TestCase):

    def create_app(self):
        """Creates the app for testing"""
        app.config.from_object('config.TestingConfig')
        return app

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.user = {'user_email' : 'soniak@gmail.com', 'user_name': 'Kaynyts000', 
                    'user_password' : 'qWerty123'}
        self.usertwo = {'user_email' : 'kaynuts@gmail.com', 'user_name': 'Kaynuts000', 
                        'user_password' : '12345678'}
        self.business = {'business_name': 'MTN', 'location' : 'Kampala', 'category' : 'Telecomm', 
                         'business_profile': 'Best Telecomm Company'}
        self.review = {"review_title":"Best Telecomm Company", 
                      "review_msg": "Telecommunications"}
        db.session.remove()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def get_token(self):
        """ Generate token for self.user"""
        register = self.app.post('/api/v2/auth/register', 
                                content_type='application/json', 
                                data=json.dumps(self.user))
        login = self.app.post('/api/v2/auth/login', 
                                content_type='application/json', 
                                data=json.dumps(self.user))
        login_data = json.loads(login.data.decode())
        self.access_token = login_data["token"]
        return self.access_token

    def get_token_two(self):
        """ Generate token for self.user"""
        register = self.app.post('/api/v2/auth/register', 
                                content_type='application/json', 
                                data=json.dumps(self.usertwo))
        login = self.app.post('/api/v2/auth/login', 
                                content_type='application/json', 
                                data=json.dumps(self.usertwo))
        login_data = json.loads(login.data.decode())
        self.access_token_two = login_data["token"]
        return self.access_token_two

    def test_get_all_reviews_success(self):
        """Tests getting all reviews for a registered business"""
        response = self.app.post('/api/v2/businesses', 
                            content_type = 'application/json', 
                            headers={'Authorization': 'Bearer ' + self.get_token()}, 
                            data = json.dumps(self.business))
        response = self.app.post('/api/v2/businesses/1/reviews', 
                            content_type = 'application/json', 
                            headers={'Authorization': 'Bearer ' + self.get_token_two()}, 
                            data = json.dumps(self.review))
        review_response = self.app.get('/api/v2/businesses/1/reviews', 
                            headers={'Authorization': 'Bearer ' + self.get_token()}, 
                            content_type = 'application/json')
        self.assertEqual(review_response.status_code, 200)

    def test_get_all_reviews_not_exist(self):
        """Checks whether a business has reviews before retrieval"""
        response = self.app.post('/api/v2/businesses', 
                            content_type = 'application/json', 
                            headers={'Authorization': 'Bearer ' + self.get_token()}, 
                            data = json.dumps(self.business))
        response = self.app.get('/api/v2/businesses/1/reviews', 
                            headers={'Authorization': 'Bearer ' + self.get_token()}, 
                            content_type = 'application/json')
        self.assertEqual(response.status_code, 404)

    def test_add_review_success(self):
        """Tests adding a review to a registered business"""
        response = self.app.post('/api/v2/businesses', 
                            content_type = 'application/json', 
                            headers={'Authorization': 'Bearer ' + self.get_token()}, 
                            data = json.dumps(self.business))
        response = self.app.post('/api/v2/businesses/1/reviews', 
                            content_type = 'application/json', 
                            headers={'Authorization': 'Bearer ' + self.get_token_two()}, 
                            data = json.dumps(self.review))
        self.assertEqual(response.status_code, 200)
    
    def test_add_review_by_business_owner(self):
        """Tests adding a review to a registered business by the same user who created the business"""
        response = self.app.post('/api/v2/businesses', 
                            content_type = 'application/json', 
                            headers={'Authorization': 'Bearer ' + self.get_token()}, 
                            data = json.dumps(self.business))
        response = self.app.post('/api/v2/businesses/1/reviews', 
                            content_type = 'application/json', 
                            headers={'Authorization': 'Bearer ' + self.get_token()}, 
                            data = json.dumps(self.review))
        self.assertEqual(response.status_code, 401)

    def test_add_review_fail(self):
        """Tests adding a review to a business not yet registered"""
        response = self.app.post('/api/v2/businesses/2/reviews', 
                            content_type = 'application/json', 
                            headers={'Authorization': 'Bearer ' + self.get_token()}, 
                            data = json.dumps(self.review))
        self.assertEqual(response.status_code, 404)
       
if __name__ == "__main__":
    unittest.main()
    