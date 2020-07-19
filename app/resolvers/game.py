import logging
from logging import log
from gql import mutate, query
from sqlalchemy.orm import load_only

from app import types
from app.db.models import GameSession
from app.redis import redis, ENCODING

logger = logging.getLogger(__name__)


@mutate
async def start_game(*_, input: dict):
    obj_in = types.StartGameInput(**input)
    await GameSession.objects.create(obj_in.dict())
    return True


@mutate
async def end_game(*_, input: dict):
    # obj_in = types.EndGameInput(**input)
    # session = (
    #     await GameSession.objects.filter_by(user_id=input['user_id']).order_by(desc('id')).first()
    # )
    # if session:
    #     await GameSession.objects.filter_by(id=session.id).update(obj_in.dict())
    #     key = f'jump:user_id:{session.user_id}'
    #     id_score = await redis.get(key, encoding=ENCODING)
    #     if not id_score:
    #         await redis.zadd('jump_rank', obj_in.score, session.user_id)
    #         await redis.set(key, f'{session.id}:{obj_in.score}')
    #     else:
    #         score = int(id_score.split(':')[1])
    #         if score < obj_in.score:
    #             await redis.zadd('jump_rank', obj_in.score, session.user_id)
    #             await redis.set(key, f'{session.id}:{obj_in.score}')
    obj_in = types.EndGameInput(**input)
    await GameSession.objects.filter_by(user_id=input['user_id']).update(obj_in.dict())
    await redis.zadd('jump_rank', obj_in.score, input['user_id'])
    logger.info(f'{input["user_id"]} end game')
    return True


@query
async def ranking_list(*_, user_id: str):
    top_three = await redis.zrevrange('jump_rank', 0, 2, encoding=ENCODING)
    if not top_three:
        return None

    self_ranking = None
    rankings = list(range(1, len(top_three) + 1))
    if user_id not in top_three:
        self_ranking = await redis.zrevrank('jump_rank', user_id)
        if self_ranking:
            rankings.append(self_ranking + 1)
            top_three.append(user_id)

    logger.info(f'top three: {top_three}')
    logger.info(f'{user_id} ranking: {self_ranking}')

    sessions = (
        await GameSession.objects.filter(GameSession.user_id.in_(top_three))
        .options(load_only('id', 'user_id', 'score', 'avatar'))
        .all()
    )
    if not sessions:
        return None

    m = {session.user_id: session for session in sessions}
    data = []
    for ranking, user_id in zip(rankings, top_three):
        session = m[user_id]
        data.append(
            types.Ranking(
                ranking=ranking, user_id=user_id, avatar=session.avatar, score=session.score
            )
        )
    return data


# @query
# async def ranking_list(*_, user_id: str):
#     r = await redis.get(f'jump:user_id:{user_id}', encoding=ENCODING)
#     if not r:
#         return None

#     top_three = await redis.zrevrange('jump_rank', 0, 2, encoding=ENCODING)
#     if not top_three:
#         return None

#     self_ranking = None
#     if user_id not in top_three:
#         self_ranking = await redis.zrevrank('jump_rank', user_id)
#         top_three.append(user_id)
#     tasks = []
#     for user_id in top_three:
#         tasks.append(redis.get(f'jump:user_id:{user_id}', encoding=ENCODING))
#     id_scores = await asyncio.gather(*tasks)
#     session_ids = [int(value.split(':')[0]) for value in id_scores]
#     sessions = (
#         await GameSession.objects.filter(GameSession.id.in_(session_ids))
#         .options(load_only('id', 'user_id', 'score', 'avatar'))
#         .all()
#     )
#     if not sessions:
#         return None

#     m = {session.user_id: session for session in sessions}
#     data = []
#     rankings = [1, 2, 3]
#     if self_ranking is not None:
#         rankings.append(int(self_ranking) + 1)
#     for ranking, user_id in zip(rankings, top_three):
#         session = m[user_id]
#         data.append(
#             types.Ranking(
#                 ranking=ranking, user_id=user_id, avatar=session.avatar, score=session.score
#             )
#         )
#     return data

