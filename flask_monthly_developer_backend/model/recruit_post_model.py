from flask_restx import fields, Namespace

class RecruitPostModel():
    Recruit = Namespace("About recruit post", description="팀 구인과 같은 구인 관련 게시물 작성과 관련된 API")

    recruit_post_model = Recruit.model('recruit post model', {
        'recruit_title': fields.String(description='recruit title', required=True),
        'recruit_author': fields.String(description='recruit author', required=True),
        'recruit_contents': fields.String(description='recruit contents', required=True),
        'recruit_tags': fields.List(fields.String, description='recruit tags', required=False),
        'recruit_state': fields.String(description='recruit state', required=True),
    })