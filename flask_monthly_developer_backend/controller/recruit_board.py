import json
# from bson.objectid import ObjectId
from flask import request, redirect, jsonify
from flask_restx import Api, Resource, fields, Namespace, reqparse

from config import db_connector

Recruit = Namespace("Recruit post", description="for recruit")

introduce = Recruit.model('Introduce', {
    'recruit_title': fields.String(description='recruit title', required=True),
    'recruit_author': fields.String(description='recruit author', required=True),
    'recruit_contents': fields.String(description='recruit contents', required=True),
    'recruit_tags': fields.List(fields.String, description='recruit tags', required=False, default = "asdf"),
    'recruit_state': fields.String(description='recruit state', required=True),
})

# 특정 게시글을 검색하기 위한 조건
search_parse = reqparse.RequestParser()
search_parse.add_argument("recruit_number", type = int, help ="게시글 번호")
search_parse.add_argument("recruit_author", type = int, help ="게시글 작성자")

# 새로운 게시글 등록 (작성)
@Recruit.route('/new_post', methods=['POST'])
class RecruitPostCreate(Resource):
    @Recruit.expect(introduce)
    def post(self):
        
        # 응답을 위한 Dict
        new_post_res = {}

        try:
            # 새 글 생성
            recruit_title = request.json.get("recruit_title")  # 제목
            recruit_author = request.json.get("recruit_author")  # 글쓴이
            recruit_contents = request.json.get('recruit_contents')  # 내용
            recruit_tags = request.json.get('recruit_tags')  # tags
            recruit_state = request.json.get('recruit_state')  # 상태

            newpost_recruit = {'recruit_title': recruit_title, 'recruit_author': recruit_author,
                            'recruit_contents': recruit_contents, 'recruit_tags': recruit_tags,
                            'recruit_state': recruit_state}
            
            for k, v in newpost_recruit.items():
                if k != "recruit_tags" and v == None:
                    raise Exception("Missing Parameter")
            
        # 전달받은 Body 중에 누락된 내용이 있다면 Exception 발생
        # 제목, 글쓸이, 내용, 상태는 누락될 수 없음
        except:
            new_post_res = {
                    "req_path": request.path,
                    "req_result": "Missing Parameter"
            }
            return new_post_res
        
        try:
            # mongoDB에 추가
            # post = db.[colletion_name] # Collection에 접근 후
            # post.insert_one(newpost_recruit).inserted_id  #한 개 저장
            post_db = db_connector.mongo.db.recruit_post
            post_db.insert(newpost_recruit)

            new_post_res = {
                "req_path": request.path,
                "req_result": "Done"
            }
            return new_post_res
        # DB 저장 중 오류 발생 시 Exception
        except:
            new_post_res = {
                "req_path": request.path,
                "req_result": "Fail"
            }
            return new_post_res

# 게시글 검색
@Recruit.route('/search')
class RecruitPostSearch(Resource):
    @Recruit.expect(search_parse)
    def get(self):
        print(search_parse.parse_args())
        data = [doc for doc in db_connector.mongo.db.recruit_post.find({}, {"_id":0})]
        return jsonify(data)

# 게시글 수정
@Recruit.route('/update')
class RecruitPostUpdate(Resource):
    @Recruit.expect(introduce)
    def put(self, post_id):
        db_connector.mongo.db.recruit_post.update({"recruit_state": "구인중"}, {"$set": {"recruit_state": "구인완료"}})
        return "is RecruitPostRead"

# 게시글 삭제
@Recruit.route('/delete')
class RecruitPostDelete(Resource):
    @Recruit.expect(introduce)
    def delete(self, post_id):
        db_connector.mongo.db.recruit_post.delete_one({"recruit_state": "구인중"})
        return "is RecruitPostDelete"
