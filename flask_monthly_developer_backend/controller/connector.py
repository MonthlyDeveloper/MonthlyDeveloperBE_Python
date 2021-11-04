from flask import request, jsonify
from flask_restx import Api, Resource, fields, Namespace

from config import db_connector

db_ns = Namespace("DB Connect Test", description = "DB 연결을 확인하기 위한 임시 컨트롤러입니다.")

@db_ns.route('/create')
class MongoCreate(Resource):
    def get(self):
        create_test_data = {
            "recruit_title" : "임시 제목",
            "recruit_author": "임시 개발자",
            "recruit_contents": "안녕하세요!",
	        "recruit_tags": ["가나다라"],
	        "recruit_state": "모집완료",
        }
        db_connector.mongo.db.recruit_post.insert(create_test_data)
        return "데이터 추가!"

@db_ns.route('/read')
class MongoRead(Resource):
    def get(self):
        data = [doc for doc in db_connector.mongo.db.recruit_post.find({}, {"_id":0})]
        return jsonify(data)

@db_ns.route('/update')
class MongoUpdate(Resource):
    def get(self):
        db_connector.mongo.db.recruit_post.update({"recruit_state": "구인중"}, {"$set": {"recruit_state": "구인완료"}})
        return "업데이트!"

@db_ns.route('/delete')
class MongoDelete(Resource):
    def get(self):
        db_connector.mongo.db.recruit_post.delete_one({"recruit_state": "구인중"})
        return "데이터 삭제"