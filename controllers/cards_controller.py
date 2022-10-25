from flask import Blueprint, request
from init import db
from datetime import date
from models.card import Card, CardSchema


cards_bp = Blueprint('cards', __name__, url_prefix='/cards')

@cards_bp.route('/')
# @jwt_required()
def all_cards():
    # return 'all_cards route'
    # user_id = get_jwt_identity()
    # stmt = db.select(User).filter_by(id=user_id)
    # user = db.session.scalar(stmt)
    # if not user.is_admin:
    #     return {'error': 'You must be an admin'}, 401
    #select * from cards;
    # cards = Card.query.all()
    # print(cards.__dict__)
    stmt = db.select(Card).order_by(Card.priority, Card.title)
    cards = db.session.scalars(stmt)
    return CardSchema(many=True).dump(cards)

@cards_bp.route('/<int:id>/', methods=['PUT', 'PATCH'])
def update_one_card(id):
    stmt = db.select(Card).filter_by(id=id)
    card = db.session.scalar(stmt)
    if card:
        card.title = request.json.get('title') or card.title
        card.description = request.json.get('description') or card.description
        card.status = request.json.get('status') or card.status
        card.priority = request.json.get('priority') or card.priority
        db.session.commit()
        return CardSchema().dump(card)
    else:
        return {'error' : 'Card not fund with id {id}'}, 404

@cards_bp.route('/<int:id>/', methods=['DELETE'])
def delete_one_card(id):
    stmt = db.select(Card).filter_by(id=id)
    card = db.session.scalar(stmt)
    if card:
        db.session.delete(card)
        db.session.commit()
        return {'message': f'Card "{card.title}" has been successfully deleted'}
    else:
        return {'error' : 'Card not fund with id {id}'}, 404

@cards_bp.route('/<int:id>/')
def one_card(id):
    stmt = db.select(Card).filter_by(id=id)
    card = db.session.scalar(stmt)
    if card:
        return CardSchema().dump(card)
    else:
        return {'error' : 'Card not fund with id {id}'}, 404

@cards_bp.route('/', methods=['POST'])
def create_card():
    card= Card(
        title = request.json['title'],
        description = request.json['description'],
        status = request.json['status'],
        priority = request.json['priority'],
        date = date.today()
        )

    db.session.add(card)
    db.session.commit()
    return CardSchema().dump(card), 201