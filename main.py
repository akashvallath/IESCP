from flask import Flask
from flask_restful import Resource, Api, fields, marshal_with

app = Flask(__name__)

import config

import models
from models import Influencer, Sponsor, Campaign

import routes

api = Api(app)

sponsor_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'companyname': fields.String
}
influencer_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'email': fields.String,
    'niche': fields.String
}
campaign_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'typeofcampaign': fields.String,
    'budget': fields.Integer,
    'communication':fields.String,
    'deadline': fields.DateTime,
    'description':fields.String
}

class SponsorAPI(Resource):
    @marshal_with(sponsor_fields)
    def get(self, id):
        sponsors = Sponsor.query.get(id)
        return sponsors

class InfluencerAPI(Resource):
    @marshal_with(influencer_fields)
    def get(self, id):
        influencers = Influencer.query.get(id)
        return influencers
    
class CampaignAPI(Resource):
    @marshal_with(campaign_fields)
    def get(self, id):
        campaigns = Campaign.query.get(id)
        return campaigns

api.add_resource(SponsorAPI, '/api/<int:id>/sponsor')
api.add_resource(InfluencerAPI, '/api/<int:id>/influencer')
api.add_resource(CampaignAPI, '/api/<int:id>/campaign')
